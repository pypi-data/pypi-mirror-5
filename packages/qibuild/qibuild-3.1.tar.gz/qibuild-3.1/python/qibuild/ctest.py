## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Re-implementation of CTest in Python.

Necessary to by-pass some small ctest shortcomings.
"""

import Queue
import datetime
import errno
import os
import re
import shlex
import signal
import sys
import threading
import time
import fnmatch

import qisys
from qisys import ui
import qibuild
import qibuild.config
import qibuild.gcov

class QueueTimeout(Queue.Queue):
    def join(self):
        while self.unfinished_tasks:
            time.sleep(1)


_LOCK = threading.Lock()
_MULTIPLE_JOBS = False


class TestResult:
    """ Just a small class to store the results for a test

    """
    def __init__(self, test_name, test_number, test_count, **kwargs):
        self.test_name = test_name
        self.time = 0
        self.ok = False
        self.not_run = False
        self.out = ""
        self.message = ""
        self.verbose = kwargs.get('verbose', False)
        self.result_dir = kwargs.get('result_dir', None)

        count = "(%2i/%2i)" % (test_number + 1, test_count)
        self.line = [ui.green, " * ", ui.reset, ui.bold, count, ui.blue,
                     self.test_name.ljust(25)]
        _LOCK.acquire()
        ui.info(*self.line, end='')
        if _MULTIPLE_JOBS and sys.stdout.isatty():
            ui.info(ui.blue, '[start]')
            _LOCK.release()

    def print_result(self):
        if _MULTIPLE_JOBS and sys.stdout.isatty():
            _LOCK.acquire()
            ui.info(*self.line, end='')
        try:
            self._print_result()
        except Exception, e:
            ui.warning("Could not print result for", self.test_name, "\n",
                       "error was:", e)
        finally:
            _LOCK.release()

    def _print_result(self):
        """ Helper for print_result """
        if self.ok:
            ui.info(ui.green, "[OK]")
            if self.verbose:
                print self.out
        else:
            ui.info(ui.red, "[FAIL]", self.message)
            if qisys.command.SIGINT_EVENT.is_set():
                pass
            print self.out
        sys.stdout.flush()
        if self.result_dir is not None:
            xml_out = os.path.join(self.result_dir, self.test_name + ".xml")

            if os.path.exists(xml_out) and self.ok:
                # Only trust gtest-generated XML if the test was successful
                pass
            else:
                # If gtest crashes or timesout *after* the XML is written,
                # make sure we have the information in the XML file
                write_xml(xml_out, self)


def parse_valgrind(valgrind_log, tst):
    """
    parse valgrind logs and extract interesting errors.
    """
    leak_fd_regex      = re.compile("==\d+== FILE DESCRIPTORS: (\d+)")
    invalid_read_regex = re.compile("==\d+== Invalid read of size (\d+)")
    with open(valgrind_log, "r") as f:
        lines = f.readlines()

    for l in lines:
        tst.out += l
        r = leak_fd_regex.search(l)
        if r:
            fdopen = int(r.group(1))
            # 4: in/out/err + valgrind_log
            if fdopen > 4:
                tst.ok = False
                tst.message += "Error file descriptors leaks:" + str(fdopen - 4) + "\n"
            continue
        r = invalid_read_regex.search(l)
        if r:
            tst.ok = False
            tst.message += "Invalid read " + r.group(1) + "\n"


class Test:
    def __init__(self, build_dir, test_name, cmd, properties, build_env,
                 test_number, test_count, **kwargs):
        self.build_dir, self.test_name, self.cmd = build_dir, test_name, cmd
        self.properties, self.build_env = properties, build_env
        self.test_number, self.test_count = test_number, test_count

        # keyword arguments
        self.verbose = kwargs.get('verbose', False)
        self.valgrind = kwargs.get('valgrind', False)
        self.nightmare = kwargs.get('nightmare', False)
        self.cpu_mask = kwargs.get('cpu_mask', -1)

    def run(self, output_queue):
        """ Run a test.

        """
        timeout = self.properties.get("TIMEOUT")
        result_dir = os.path.join(self.build_dir, "test-results")
        res = TestResult(self.test_name, self.test_number, self.test_count,
                         verbose=self.verbose, result_dir=result_dir)
        if timeout:
            timeout = int(timeout)
        # we will merge the build env coming from the build worktree
        # config with the env coming from CMake config,
        # assuming that cmake is always right
        env = self.build_env.copy()
        cmake_env = self.properties.get("ENVIRONMENT")
        if cmake_env:
            cmake_env = cmake_env.split(";")
            for key_value in cmake_env:
                key, value = key_value.split("=")
                env[key] = value
        working_dir = self.properties.get("WORKING_DIRECTORY")
        if working_dir:
            cwd = working_dir
        else:
            cwd = self.build_dir
        ncmd = self.cmd
        # Quick hack to re-add color on gtest tests
        if sys.stdout.isatty():
            env["GTEST_COLOR"] = "yes"
        if self.valgrind:
            env['VALGRIND'] = '1'
            timeout *= 10
            valgrind_log = os.path.join(self.build_dir, self.test_name + "valgrind_output.log")
            tmp = ncmd
            ncmd = [ "valgrind", "--track-fds=yes", "--log-file=%s" % valgrind_log ]
            ncmd.extend(tmp)
        if self.cpu_mask != -1:
            tmp = ncmd
            ncmd = ['taskset', str(self.cpu_mask)]
            ncmd.extend(tmp)
        process = qisys.command.Process(ncmd,
            cwd=cwd,
            env=env)
        if self.nightmare:
            ncmd.extend(["--gtest_shuffle", "--gtest_repeat=20"])
            timeout = timeout * 20
        start = datetime.datetime.now()
        process.run(timeout)
        end = datetime.datetime.now()
        delta = end - start
        res.time = float(delta.microseconds) / 10**6 + delta.seconds

        ui.debug('Treating result of', self.cmd)
        res.out = process.out
        # Sometimes the procees did not have any output,
        # but we still want to let the user know it ran
        if not process.out:
            res.out = "<no output>"
        res.ok = process.return_type == qisys.command.Process.OK
        if process.exception is not None:
            exception = process.exception
            mess  = "Could not run test: %s\n" % self.test_name
            mess += "Error was: %s\n" % exception
            mess += "Full command was: %s\n" % " ".join(ncmd)
            if isinstance(exception, OSError):
                # pylint: disable-msg=E1101
                if exception.errno == errno.ENOENT:
                    mess += "Are you sure you have built the tests?"
            res.out = mess + '\n'
        if process.return_type == qisys.command.Process.INTERRUPTED:
            res.message = "Interrupted"
        elif process.return_type == qisys.command.Process.NOT_RUN:
            res.message = "Not run"
            res.not_run = True
        elif process.return_type == qisys.command.Process.TIME_OUT:
            res.message = "Timed out (%is)" % timeout
        elif process.return_type == qisys.command.Process.ZOMBIE:
            res.message = "Zombie (Timeout = %is)" % timeout
        elif process.return_type == qisys.command.Process.FAILED:
            retcode = process.returncode
            if retcode > 0:
                res.message = "Return code: %i" % retcode
            else:
                res.message = qisys.command.str_from_signal(-retcode)
        if self.valgrind:
            if not os.path.isfile(valgrind_log):
                ui.warning("The valgrind log file does not exist")
                return
            parse_valgrind(valgrind_log, res)
        ui.debug('Putting result in result queue.')
        output_queue.put(res)


class TestWorker(threading.Thread):
    def __init__(self, in_queue, out_queue):
        threading.Thread.__init__(self)
        self.daemon = True
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while not qisys.command.SIGINT_EVENT.is_set():
            self.test = self.in_queue.get()
            self.test.run(self.out_queue)
            self.test = None
            self.in_queue.task_done()


class TestResultWorker(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.res = list()
        self.total, self.failed = 0, 0

    def run(self):
        while True:
            item = self.queue.get()
            item.print_result()
            self.res.append(item)
            self.total += 1
            if not item.ok:
                self.failed += 1
            self.queue.task_done()

    def global_result(self):
        return self.res


def sigint_handler(signum, frame):
    def double_sigint(signum, frame):
        ui.warning('Exiting main program without caring (may leave ' + \
                   'zombies and the like).')
        sys.exit(1)
    ui.warning('Received keyboard interrupt. Killing all processes ' + \
               '. This may take few seconds.')
    qisys.command.SIGINT_EVENT.set()
    signal.signal(signal.SIGINT, double_sigint)

def run_tests(project, build_env=None, pattern=None, verbose=False, slow=False,
              dry_run=False, valgrind=False, nightmare=False, test_args=None,
              coverage=False, num_jobs=1, num_cpus=-1):
    """ Called by ``qibuild test``

    :param test_name: If given, only run this test

    :return: a boolean to indicate if test was successful
    """
    if valgrind:
        if not qisys.command.find_program("valgrind"):
            raise Exception("valgrind was not found on the system")
    if coverage:
        if not qisys.command.find_program("gcovr"):
            raise Exception("You must install gcovr before use coverage option!")
    if num_cpus != -1:
        if not qisys.command.find_program("taskset"):
            raise Exception("taskset was not found on the system")
        # get effective CPU count
        cpu_count = int(os.sysconf('SC_NPROCESSORS_ONLN'))
    if not build_env:
        build_env = qibuild.config.get_build_env()
    build_dir = project.build_directory
    signal.signal(signal.SIGINT, sigint_handler)
    all_tests = parse_ctest_test_files(build_dir)
    tests = list()
    slow_tests = list()
    if pattern:
        try:
            pattern = pattern.strip()
            pattern = pattern if pattern.startswith("*") else "*" + pattern
            pattern = pattern if pattern.endswith("*") else pattern + "*"
            tests = [x for x in all_tests if fnmatch.fnmatch(x[0], pattern)]
        except Exception as e:
            mess = "Invalid pattern \"{}\": {}".format(pattern, e)
            raise Exception(mess)
        if not tests:
            mess  = "No tests matching %s\n" % pattern
            mess += "Known tests are:\n"
            for x in all_tests:
                mess += "  * " + x[0] + "\n"
            raise Exception(mess)
    else:
        for test in all_tests:
            (name, cmd_, properties) = test
            cost = properties.get("COST")
            if not slow and cost and float(cost) > 50:
                ui.debug("Skipping test", name, "because cost",
                         "(%s)"% cost, "is greater than 50")
                slow_tests.append(name)
                continue
            tests.append(test)

    if dry_run:
        ui.info(ui.green, "List of tests for", project.name)
        tests.sort()
        for (test_name, _, _) in tests:
            ui.info(ui.green, " * ", ui.reset, test_name)
        return True

    if 1 < num_jobs:
        global _MULTIPLE_JOBS
        _MULTIPLE_JOBS = True

    # Clean up test-results dir
    result_dir = os.path.join(build_dir, "test-results")
    qisys.sh.rm(result_dir)

    if not tests:
        ui.warning("No tests found for project", project.name)
        return

    for test in all_tests:
        if test_args is not None:
            test[1] += test_args.split()

    ui.info(ui.green, "Testing", project.name, "...")
    in_queue, out_queue = QueueTimeout(), Queue.Queue()
    output_worker = TestResultWorker(out_queue)
    thread_list = list()
    output_worker.start()
    for it in range(num_jobs):
        thread_list.append(TestWorker(in_queue, out_queue))
        thread_list[-1].start()
    cur_cpu = 0
    for i, test in enumerate(tests):
        (test_name, cmd, properties) = test
        cpu_mask = -1
        if num_cpus != -1:
          cpu_mask = 0
          for j in range(num_cpus):
            cpu_mask |= 1 << cur_cpu
            cur_cpu = (1 + cur_cpu)%cpu_count
        in_queue.put(Test(build_dir, test_name, cmd, properties, build_env,
                          i, len(tests), valgrind=valgrind, verbose=verbose,
                          nightmare=nightmare, cpu_mask=cpu_mask))
    in_queue.join()
    out_queue.join()
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    results = output_worker.global_result()
    total = len(results)
    failed = [x for x in results if not x.ok]
    if coverage:
        qibuild.gcov.generate_coverage_xml_report(project)
    if not failed:
        ui.info("Ran %i tests" % total)
        if slow_tests and not slow:
            ui.info("Note: %i" % len(slow_tests),
                    "slow tests did not run, use --slow to run them")
        ui.info("All pass. Congrats!")
        return True

    ui.error("Ran %i tests, %i failures" % (total, len(failed)))
    padding = max(len(x.test_name) for x in failed)
    for res in failed:
        ui.info(ui.bold, " -", ui.blue,
                res.test_name.ljust(padding + 5),
                ui.red, res.message)
    return False

def write_xml(xml_out, test_res):
    """ Write a XUnit XML file

    """
    if sys.platform.startswith("win"):
        header = """<?xml version="1.0" encoding="ascii"?>"""
    else:
        header = """<?xml version="1.0" encoding="UTF-8"?>"""
    to_write = header + """
<testsuites tests="1" failures="{num_failures}" disabled="0" errors="0" time="{time}" name="All">
    <testsuite name="{testsuite_name}" tests="1" failures="{num_failures}" disabled="0" errors="0" time="{time}">
    <testcase name="{testcase_name}" status="run">
      {failure}
    </testcase>
  </testsuite>
</testsuites>
"""
    if test_res.ok:
        num_failures = "0"
        failure = ""
    else:
        num_failures = "1"
        failure = """
      <failure message="{message}">
          <![CDATA[ {out} ]]>
    </failure>
"""

    # Arbitrary limit output (~700 lines) to prevent from crashing on read
    test_res.out = test_res.out[-16384:]

    # Remove color before encoding
    if os.getenv("GTEST_COLOR") or sys.stdout.isatty():
        test_res.out = re.sub('\x1b[^m]*m', "", test_res.out)

    # Windows output is most likely code page 850
    if sys.platform.startswith("win"):
        encoding = "ascii"
    else:
        encoding = "utf-8"
    try:
        test_res.out = test_res.out.decode(encoding, "ignore").encode(encoding)
    except UnicodeDecodeError:
        pass

    failure = failure.format(out=test_res.out, message=test_res.message)
    to_write = to_write.format(num_failures=num_failures,
                               testsuite_name="test", # nothing clever to put here :/
                               testcase_name=test_res.test_name,
                               failure=failure,
                               time=test_res.time)

    qisys.sh.mkdir(os.path.dirname(xml_out), recursive=True)
    with open(xml_out, "w") as fp:
        fp.write(to_write)


def parse_ctest_test_files(build_dir):
    """ Recursively parse CTestTestfile.cmake.
    Returns a list of lists of 3 elements:
        [name, cmd, properties]

    """
    tests = list()
    subdirs = list()
    _parse_ctest_test_files(build_dir, tests, subdirs)
    return tests

def _parse_ctest_test_files(root, tests, subdirs):
    """ Helper for parse_ctest_test_files.
    We will fill up the tests and subdirs parameters as we go.

    Warning: CTestTestfile.cmake is at the build directory root only if the root
             CmakeLists.txt call enable_testing and not a sub CmakeLists.txt
    """
    ctest_test_file = os.path.join(root, "CTestTestfile.cmake")
    if not os.path.exists(ctest_test_file):
        return list()
    with open(ctest_test_file, "r") as fp:
        lines = fp.readlines()

    current_test = None
    for i, line in enumerate(lines, start=1):
        match = re.match("SUBDIRS\((.*)\)", line, re.IGNORECASE)
        if match:
            subdir = match.groups()[0]
            subdirs.append(subdir)
            current_test = None
            continue
        match = re.match("ADD_TEST\(([a-zA-Z0-9_-]*) (.*)\)", line, re.IGNORECASE)
        if match:
            groups = match.groups()
            current_test = groups[0]
            args = groups[1]
            test_cmd = shlex.split(args)
            tests.append([current_test, test_cmd, dict()])
            continue
        match = re.match("SET_TESTS_PROPERTIES\(([a-zA-Z0-9_-]*) PROPERTIES (.*)\)", line, re.IGNORECASE)
        if match:
            groups = match.groups()
            if current_test is None:
                mess  = "Expecting ADD_TEST before SET_TESTS_PROPERTIES\n"
                mess += "in %s:%i" % (ctest_test_file, i)
                raise Exception(mess)
            name = groups[0]
            if name != current_test:
                mess  = "SET_TESTS_PROPERTIES called with wrong name\n"
                mess += "Expecting %s, got %s\n" % (current_test, name)
                mess += "in %s:%i" % (ctest_test_file, i)
                raise Exception(mess)
            properties = groups[1]
            properties = shlex.split(properties)
            test_properties = dict()
            for j in range(0, len(properties)/2):
                key = properties[2*j]
                value = properties[2*j+1]
                test_properties[key] = value
            # Just erase everything if there are two calls to set_test_properties()
            tests[-1][2] = test_properties
            current_test = None

    for subdir in subdirs:
        new_root = os.path.join(root, subdir)
        _parse_ctest_test_files(new_root, tests, list())

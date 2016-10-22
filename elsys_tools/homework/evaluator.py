#!/usr/bin/env python3

import os
import sys
from subprocess import Popen, PIPE, TimeoutExpired
import pytoml as toml
import argparse
import logging
import time
import re
import shlex
import math
from enum import Enum

TESTCASE_TIMEOUT = 1
GCC_TEMPLATE = 'gcc -Wall -std=c11 -pedantic {0} -o {1} -lm'
FILENAME_TEMPLATES = ('.*task(\d+)\.[cC]$', '(\d\d)_.*\.[cC]$')


class TaskStatus(Enum):
    SUBMITTED = 1
    UNSUBMITTED = 0


class ExecutionStatus(Enum):
    MISMATCH = 1
    TIMEOUT = 2
    OTHER = 3


def get_args(argv):
    parser = argparse.ArgumentParser(description='Evaluating of student\'s \
    homework')
    parser.add_argument(
        'directory',
        help='student assignment directory to use',
        action='store',
        default=".")
    parser.add_argument(
        'testcases',
        help='test cases file to use',
        type=argparse.FileType('r'))
    parser.add_argument('-t', '--tasks', nargs='+', help='List of tasks to \
        evaluate')
    parser.add_argument('-p', '--parameters', nargs='+', help='List of \
        additional parameters to the compiler')
    parser.add_argument('-l', '--log', default="DEBUG", help='Log level. Can \
        be one of the follo\wing INFO WARN DEBUG.')
    parser.add_argument('--timestamp', dest="timestamp", action='store_true')
    parser.add_argument('--no-timestamp', dest="timestamp",
                        action='store_false')
    parser.add_argument('--failed-output', dest="failed_output",
                        action="store_true")
    parser.add_argument('--no-failed-output', dest="failed_output",
                        action="store_false")
    parser.add_argument('--output-std', dest='output_std', action='store_true')
    parser.set_defaults(timestamp=False, failed_output=False, output_std=False)
    return parser.parse_args(argv)


def setup_logger(args):
    numeric_level = getattr(
        logging,
        args.log.upper(),
        "DEBUG"
    )

    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(level=numeric_level)


def is_valid_taskname(filename):
    for regexp_str in FILENAME_TEMPLATES:
        match = re.match(regexp_str, filename, flags=0)
        if match:
            return True

    return False


def get_task_number_from_filename(filename):
    for regexp_str in FILENAME_TEMPLATES:
        match = re.match(regexp_str, filename, flags=0)
        if match:
            return int(match.group(1))
    return None


def remove_path_from_output(folder, output):
    return output.replace(folder + os.sep, "")


def main(argv=sys.argv[1:], tasks=None, post_processing=None, log=None):
    args = get_args(argv)

    setup_logger(args)

    files = []
    for root, _, filenames in os.walk(args.directory, topdown=False):
        files += [
            (f, os.path.abspath(os.path.join(args.directory, f)))
            for f
            in filenames
            if (os.path.isfile(os.path.join(root, f)) and
                (f.endswith('.c') or f.endswith('.C')))
        ]

    summary = []
    unrecognized_files = []

    if not tasks:
        with open(args.testcases.name, 'rb') as fin:
            tasks = toml.load(fin)

    completed_tasks = []
    tasks_count = len(tasks['task'])
    tasks_evaluated = set()
    for current, abs_path in files:
        task_index = get_task_number_from_filename(current)

        if (task_index is None or
                task_index > tasks_count or
                task_index <= 0):
            unrecognized_files.append({
                "name": current,
                "duplicate": False
            })
            continue

        if task_index in tasks_evaluated:
            unrecognized_files.append({
                "name": current,
                "duplicate": True
            })
            continue

        tasks_evaluated.add(task_index)
        assert(len(tasks_evaluated) <= tasks_count)

        completed_tasks.append(task_index)
        task = (tasks['task'])[task_index - 1]
        task["index"] = task_index

        compiled_name = current.split('.')[0] + ".out"
        exec_path = os.path.abspath(
            os.path.join(args.directory, compiled_name))

        gcc_invoke = GCC_TEMPLATE.format(shlex.quote(abs_path),
                                         shlex.quote(exec_path))

        out, err, code = execute(gcc_invoke, timeout=10)
        msg = out + err

        if code != 0:
            summary.append({
                "status": TaskStatus.SUBMITTED,
                "compiled": False,
                "compiler_exit_code": code,
                "compiler_message": remove_path_from_output(
                    os.path.abspath(args.directory), msg.decode()),
                "task": task
            })
            continue

        testcases = []
        for index, testcase in enumerate(task.get('testcase')):
            try:
                (stdout, stderr, exitcode) = \
                    execute(exec_path,
                            input=testcase['input'].encode('utf-8'))
            except (FileNotFoundError, IOError, Exception):
                # print("EXCEPTION:", str(e))
                testcases.append({
                    "index": index + 1,
                    "success": False,
                    "status": ExecutionStatus.OTHER,
                })
                continue

            output = stdout.decode('latin-1') or ""
            output = " ".join(
                filter(None, [line.strip() for line in output.split('\n')]))
            if exitcode != 0:
                testcases.append({
                    "index": index + 1,
                    "success": False,
                    "status": ExecutionStatus.TIMEOUT,
                    "input": testcase["input"],
                })
                continue

            if output == testcase['output']:
                testcases.append({
                    "index": index + 1,
                    "success": True
                })
            else:
                testcases.append({
                    "index": index + 1,
                    "success": False,
                    "status": ExecutionStatus.MISMATCH,
                    "input": testcase["input"],
                    "output": output,
                    "expected": testcase["output"],
                })

        summary.append({
            "status": TaskStatus.SUBMITTED,
            "compiled": True,
            "task": task,
            "testcases": testcases,
            "compiler_message": remove_path_from_output(
                os.path.abspath(args.directory), msg.decode())
        })

    for unsubmitted in get_unsubmitted_tasks(completed_tasks, tasks["task"]):
        task = tasks['task'][unsubmitted - 1]
        task["index"] = unsubmitted
        summary.append({
            "status": TaskStatus.UNSUBMITTED,
            "compiled": False,
            "task": task
        })

    if post_processing:
        summary = post_processing(summary)

    print_summary(args, summary, unrecognized_files, log)


def get_unsubmitted_tasks(completed_tasks, all_tasks):
    return list(set(range(1, len(all_tasks) + 1)) - set(completed_tasks))


def get_total_points(summary):
    return sum(map(lambda x: x['task']['points'], summary))


def get_points_for_task(task):
    if "testcases" not in task:
        return 0
    correct_tc = sum(testcase["success"] for testcase in task["testcases"])

    points = task['task']['points'] * \
        float(correct_tc) / len(task["testcases"])

    if task["compiler_message"]:
        points -= correct_tc

    return math.ceil(points)


def get_earned_points(summary):
    result = 0
    for task in summary:
        if task.get("testcases") is None:
            continue

        result += get_points_for_task(task)
    return result


def print_as_code(text, log):
    print("```\n{}\n```".format(text), file=log)


def print_testcase_summary(args, testcase, log):
    print("### Testcase {} ".format(testcase["index"]), end="", file=log)

    if testcase["success"]:
        print("passed", file=log)
        return

    print("failed", file=log)
    if args.failed_output and testcase["status"] is ExecutionStatus.MISMATCH:
        print("Input", file=log)
        print_as_code(testcase["input"], log)
        print("", file=log)
        print("Expected", file=log)
        print_as_code(testcase["expected"], log)
        print("", file=log)
        print("Output", file=log)
        print_as_code(testcase["output"], log)
    elif testcase["status"] is ExecutionStatus.TIMEOUT:
        print("Execution took more than {} seconds".format(TESTCASE_TIMEOUT),
              file=log)


def print_task_summary(args, task, log):
    task_ = task["task"]
    print(file=log)

    print(
        "## Task {}: {} [{}/{} points]".format(
            task_["index"],
            task_["name"],
            get_points_for_task(task),
            task_["points"]),
        file=log)
    print("{}".format(task_["desc"]), file=log)
    print("", file=log)

    if task["status"] is TaskStatus.UNSUBMITTED:
        print("### Not submitted", file=log)
        return

    if not task["compiled"]:
        print("Failed compiling", file=log)
        print("", file=log)
        print("Exit code: {}".format(task["compiler_exit_code"]), file=log)
        print("", file=log)
        print("Error", file=log)
        print_as_code(task["compiler_message"], log)
        return

    if task["compiler_message"]:
        print("Compiled with warning(s)", file=log)
        print_as_code(task["compiler_message"], log)

    for testcase in task["testcases"]:
        print_testcase_summary(args, testcase, log)


def print_heading(summary, log, timestamp=False):
    print("# Assignment report", file=log)
    earned_points = get_earned_points(summary)

    if log is not sys.stdout:
        print(earned_points)

    print_as_code("Points earned: {}\nMaximum points: {}".format(
        earned_points,
        get_total_points(summary)
    ), log)

    if timestamp:
        now = time.strftime("%c")
        print(now, file=log)


def print_summary(args, summary, unrecognized_files, log=None):
    log_file = os.path.abspath(os.path.join(args.directory, 'README.md'))
    try:
        opened = False
        if not log:
            if args.output_std:
                log = sys.stdout
            else:
                log = open(log_file, 'w')
                opened = True
    except FileNotFoundError:
        print(0)
        return

    print_heading(summary, log, args.timestamp)
    for task in sorted(summary, key=lambda x: x["task"]["index"]):
        print_task_summary(args, task, log)

    duplicate_files = sorted(
        [x for x in unrecognized_files if x["duplicate"]],
        key=lambda x: x["name"]
    )
    unrecognized_files = sorted(
        [x for x in unrecognized_files if not x["duplicate"]],
        key=lambda x: x["name"]
    )

    if len(unrecognized_files) > 0:
        print("", file=log)
        print("## Unrecognized files", file=log)
    for unrecognized in unrecognized_files:
        print("### {}".format(unrecognized["name"]), file=log)

    if len(duplicate_files) > 0:
        print("", file=log)
        print("## Duplicate entries", file=log)
    for duplicate in duplicate_files:
        print("### {}".format(duplicate["name"]), file=log)

    if opened:
        log.close()


def execute(commandline, input=None, timeout=1):
    proc = Popen(shlex.split(commandline), stdin=PIPE,
                 stdout=PIPE, stderr=PIPE)

    try:
        std_out, std_err = proc.communicate(timeout=timeout, input=input)
    except TimeoutExpired:
        proc.kill()
        std_out, std_err = proc.communicate()

    # print("execute: ", commandline, std_out, std_err, proc.returncode)
    return (std_out, std_err, proc.returncode)

if __name__ == "__main__":
    main()

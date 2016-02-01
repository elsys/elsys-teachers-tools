from os import path, walk
from subprocess import Popen, PIPE, TimeoutExpired
import pytoml as toml
import argparse
import logging
import time
import re
from enum import Enum

TESTCASE_TIMEOUT = 1
GCC_TEMPLATE = 'gcc -Wall -std=c11 -pedantic {0} -o {1} -lm 2>&1'
FILENAME_TEMPLATES = ('.*task(\d)\.[cC]$', '(\d\d+\d+)_.*\.[cC]$')


class TaskStatus(Enum):
    SUBMITTED = 1
    UNSUBMITTED = 0


class ExecutionStatus(Enum):
    MISMATCH = 1
    TIMEOUT = 2
    OTHER = 3


def get_args():
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
    parser.set_defaults(timestamp=False)
    return parser.parse_args()


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


def main():
    args = get_args()

    setup_logger(args)

    files = []
    for root, _, filenames in walk(args.directory, topdown=False):
        files += [
            (f, path.abspath(path.join(args.directory, f)))
            for f
            in filenames
            if (path.isfile(path.join(root, f)) and
                (f.endswith('.c') or f.endswith('.C')))
        ]

    # print(files)

    summary = []

    with open(args.testcases.name, 'rb') as fin:
        tasks = toml.load(fin)

    completed_tasks = []
    for current, abs_path in files:
        task_index = get_task_number_from_filename(current)

        if task_index is not None:
            completed_tasks.append(task_index)
            task = (tasks['task'])[task_index - 1]
            task["index"] = task_index
        else:
            task = {}
            task['name'] = 'Unrecognized'
            task['desc'] = "File name doesn't not match any of filenames conventions"
            task['index'] = -1

        if not is_valid_taskname(current):
            summary.append({
                "status": TaskStatus.SUBMITTED,
                "name_matching": False,
                "file_name": current,
                "task": task
            })
            continue

        compiled_name = current.split('.')[0] + ".out"
        exec_path = path.abspath(path.join(args.directory, compiled_name))

        gcc_invoke = GCC_TEMPLATE.format(abs_path, exec_path)

        out, err, code = execute(gcc_invoke)

        if code != 0:
            summary.append({
                "status": TaskStatus.SUBMITTED,
                "compiled": False,
                "compiler_exit_code": code,
                "compiler_message": out.decode('latin-1'),
                "task": task
            })
            continue

        testcases = []
        for index, testcase in enumerate(task.get('testcase')):
            try:
                p = Popen([exec_path], stdout=PIPE, stderr=PIPE, stdin=PIPE)

                std_out_data, _ = p.communicate(testcase['input'].encode('utf-8'), TESTCASE_TIMEOUT)

                output = std_out_data.decode('latin-1') or ""
                output = output.replace('\n', ' ').strip()

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
            except TimeoutExpired:
                p.kill()
                std_out, std_err = p.communicate()

                testcases.append({
                    "index": index + 1,
                    "success": False,
                    "status": ExecutionStatus.TIMEOUT,
                    "input": testcase["input"],
                })
            except (FileNotFoundError, IOError):
                testcases.append({
                    "index": index + 1,
                    "success": False,
                    "status": ExecutionStatus.OTHER,
                })

        summary.append({
            "status": TaskStatus.SUBMITTED,
            "compiled": True,
            "task": task,
            "testcases": testcases,
        })

    for unsubmitted in list(set(range(1, len(tasks['task']))) - set(completed_tasks)):
        task = tasks['task'][unsubmitted]
        task["index"] = unsubmitted
        summary.append({
            "status": TaskStatus.UNSUBMITTED,
            "compiled": False,
            "task": task
        })

    print_summary(args, summary)


def get_total_points(summary):
    return sum(map(lambda x: x['task']['points'], summary))


def get_earned_points(summary):
    result = 0
    for task in summary:
        correct = (
            sum(map(lambda x: x["success"], task["testcases"])) == len(task["testcases"])
        )
        if correct:
            result += task['task']['points']
    return result


def print_summary(args, summary):
    log_file = path.abspath(path.join(args.directory, 'README.md'))
    now = time.strftime("%c")
    with open(log_file, 'w') as log:

        print("# Assignment report", file=log)
        print("Points earned: {}".format(get_earned_points(summary)), file=log)
        print("", file=log)
        print("Maximum points: {}".format(get_total_points(summary)), file=log)
        if args.timestamp:
            print(now, file=log)

        for task in sorted(summary, key=lambda x: x["task"]["index"]):
            print("## Task {}: {} [{} points]".format(task["task"]["index"], task["task"]["name"], task["task"]["points"]), file=log)
            print("{}".format(task["task"]["desc"]), file=log)
            print("", file=log)

            if 'name_matching' in task:
                print("**Filename: {}**".format(task['file_name']), file=log)
                continue

            if task["status"] is TaskStatus.UNSUBMITTED:
                print("### Not submitted", file=log)
                continue

            if not task["compiled"]:
                print("Failed compiling", file=log)
                print("", file=log)
                print("Exit code: {}".format(task["compiler_exit_code"]), file=log)
                print("", file=log)
                print("Error\n```\n{}\n```\n".format(task["compiler_message"]), file=log)
                print("", file=log)
                continue

            for testcase in task["testcases"]:
                print("### Testcase {} ".format(testcase["index"]), end="", file=log)

                if testcase["success"]:
                    print("passed", file=log)
                    continue

                print("failed", file=log)
                if testcase["status"] is ExecutionStatus.MISMATCH:
                    print("Input\n```\n{}\n```\n".format(testcase["input"]), file=log)
                    print("", file=log)
                    print("Expected\n```\n{}\n```\n".format(testcase["expected"]), file=log)
                    print("", file=log)
                    print("Output\n```\n{}\n```\n".format(testcase["output"]), file=log)
                elif testcase["status"] is ExecutionStatus.TIMEOUT:
                    print("Execution took more than {} seconds".format(TESTCASE_TIMEOUT), file=log)


def execute(command, input=None, timeout=1):
    proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)

    try:
        std_out, std_err = proc.communicate(timeout=timeout, input=input)
    except TimeoutExpired:
        proc.kill()
        std_out, std_err = proc.communicate()

    return (std_out, std_err, proc.returncode)

if __name__ == "__main__":
    main()

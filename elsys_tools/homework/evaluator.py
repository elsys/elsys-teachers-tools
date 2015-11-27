from os import path, access, listdir, R_OK, walk
from subprocess import Popen, PIPE, TimeoutExpired
import pytoml as toml
import argparse
import re

TESTCASE_TIMEOUT = 5


class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if access(prospective_dir, R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))


def main():
    parser = argparse.ArgumentParser(description='Evaluating of student\'s homework')
    parser.add_argument('directory', help='student assignment directory to use', action='store')
    parser.add_argument('testcases', help='test cases file to use', type=argparse.FileType('r'))
    parser.add_argument('-t', '--tasks', nargs='+', help='List of tasks to evaluate')
    parser.add_argument('-p', '--parameters', nargs='+', help='List of additional parameters to the compiler')
    args = parser.parse_args()

    files = []
    log_file = path.abspath(path.join(args.directory, 'README.md'))

    for root, dirs, files in walk(args.directory, topdown=False):
        files = [f for f in listdir(root) if (path.isfile(path.join(root, f)) and f.endswith('.c') or f.endswith('.C'))]
        if not files:
            continue

    with open(log_file, 'w') as log:

        for current in files:

            log.write("## Evaluating {}\n\n".format(current))
            print("\nEvalutaing {0}".format(current))

            if not re.match('(\d\d)_.*', current, flags=0):
                log.write('### File doesn\'t match naming convention\n\n')
                print('> File doesn\'t match naming convention\n')
                continue

            abs_path = path.abspath(path.join(args.directory, current))
            exec_path = path.abspath(path.join(args.directory, 'a.out'))

            gcc_invoke = 'gcc -Wall -pedantic -std=c11 {0} -o {1}'.format(abs_path, exec_path)

            out, err, code = execute(gcc_invoke)

            if code != 0:
                log.write('### File compiled with error or warnings\n')
                log.write('```\n')
                log.write(err.decode())
                log.write('```\n\n')
                print('> File compiled with error or warnings\n')
            else:
                log.write('### File successfully compiled\n'.format(current))
                print('> File successfully compiled\n')

            with open(args.testcases.name, 'rb') as stream:
                testcases = toml.load(stream)

                task = testcases.get('task')[int(current.split('_')[0]) - 1]

                for testcase in task.get('testcase'):
                    print(testcase)


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


# @timeout(3)
# def check_homework(tasks, scenarios):
#
#     result = {}
#     for root, dirs, files in walk(directory, topdown=False):
#         files = [f for f in listdir(root) if (path.isfile(path.join(root, f))
#                  and f in tasks)]
#         if not files:
#             continue
#
#         for current_file in files:
#             print("\nEvalutaing {0}".format(current_file))
#             abs_path = path.abspath(path.join(directory, current_file))
#             exec_path = path.abspath(path.join(directory, "a.out"))
#
#             if scenario in scenarios.keys():
#
#                 actual_successful_test = 0
#
#                 for i in range(scenarios[scenario]["number_of_tests"]):
#                     p = Popen([exec_path], stdout=PIPE, stderr=PIPE, stdin=PIPE)
#                     input_data = scenarios[scenario]["input{0}".format(i+1)]
#                     std_out_data, _ = p.communicate(input_data.encode())
#
#                     output = std_out_data.decode('latin-1').rstrip('\n').replace('\0', '').strip()
#                     output = output.replace('\n', ' ')
#                     sys.stdout.write("\t")
#
#                     if output == scenarios[scenario]["output{0}".format(i+1)]:
#                         sys.stdout.write(" ".join("Test {0} passed".format(i+1).split()))
#                         actual_successful_test += 1
#                     else:
#                         sys.stdout.write("Test {0} failed:\n".format(i+1))
#                         sys.stdout.write("\t\tExpected:\n\t\t\t{0}\n".format(scenarios[scenario]["output{0}".format(i+1)]))
#                         sys.stdout.write("\t\tGot: \n \t\t\t{0}\n".format(output))
#                         successful = False
#                     sys.stdout.write("\n")
#
#                     summary[scenario] = "{0}/{1}".format(actual_successful_test, scenarios[scenario]["number_of_tests"])
#                 if successful:
#                     num_of_hw += 1
#
#     print("\nSummary\n")
#     if summary.keys():
#         for task in summary.keys():
#             print("\t{0} - {1}".format(task, summary[task]))
#     else:
#         print("\tMissing homework\n")
#     return num_of_hw

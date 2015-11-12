import os
from os import path, listdir
from subprocess import Popen, PIPE
import sys
import yaml
import argparse
import re
from .timeout import timeout

TESTCASE_TIMEOUT = 5


class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))


def main():
    parser = argparse.ArgumentParser(description='Evaluating of student\'s homework')
    parser.add_argument('directory', help='student assignment directory to use', action='store')
    parser.add_argument('testcases', help='test cases file to use', type=argparse.FileType('w'))
    parser.add_argument('-t', '--tasks', nargs='+', help='List of tasks to evaluate')
    parser.add_argument('-p', '--parameters', nargs='+', help='List of additional parameters to the compiler')
    args = parser.parse_args()

if __name__ == "__main__":
    main()

# if sys.argv[4] == "all":
#     stream = open("scenarios_" + sys.argv[3] + ".yaml", "r")
#     scenarios = yaml.load(stream)
#     tasks = scenarios["tasks"]
# else:
#     tasks = ["task{0}.c".format(sys.argv[4])]
#     number_of_task = re.findall(r'\d', sys.argv[4])[0]
#     scenarios = {"task{0}".format(sys.argv[4]): {"number_of_tests": 1, "input{0}".format(number_of_task): sys.argv[5], "output{0}".format(number_of_task): sys.argv[6]}}
#
# summary = {}


def compile_task():
    pass


def test_task():
    pass


def evaluate_task():
    pass


def evaluate_homework():
    pass



@timeout(3)
def check_homework(tasks, scenarios):
    num_of_hw = 0
    print("Evaluating homework {0} on student {1} from {2} class\n".format(sys.argv[3], sys.argv[2], sys.argv[1]))

    files = []
    result = {}
    for root, dirs, files in os.walk(directory, topdown=False):
        files = [f for f in listdir(root) if (path.isfile(path.join(root, f))
                 and f in tasks)]
        if not files:
            continue

        for current_file in files:
            print("\nEvalutaing {0}".format(current_file))
            abs_path = path.abspath(path.join(directory, current_file))
            exec_path = path.abspath(path.join(directory, "a.out"))

            gpp_invoke = "gcc -Wall -pedantic -std=c11 {0} -o {1} 2> homeworks_result.txt".format(abs_path, exec_path)

            result = os.system(gpp_invoke)

            f = open('homeworks_result.txt', 'r')
            result_of_compilation = f.read()

            successful = True
            scenario = current_file.split('.')[0]

            if result is not 0:
                print("\tFiles can't compile (gcc err code:{0})".format(result))
                summary[scenario] = "0/{0} - error".format(scenarios[scenario]["number_of_tests"])
                continue

            if result_of_compilation != "":
                print("\tWarning:\n \t\t{0}".format(result_of_compilation))
                summary[scenario] = "0/{0} - warning".format(scenarios[scenario]["number_of_tests"])
                continue

            if scenario in scenarios.keys():

                actual_successful_test = 0

                for i in range(scenarios[scenario]["number_of_tests"]):
                    p = Popen([exec_path], stdout=PIPE, stderr=PIPE, stdin=PIPE)
                    input_data = scenarios[scenario]["input{0}".format(i+1)]
                    std_out_data, _ = p.communicate(input_data.encode())

                    output = std_out_data.decode('latin-1').rstrip('\n').replace('\0', '').strip()
                    output = output.replace('\n', ' ')
                    sys.stdout.write("\t")

                    if output == scenarios[scenario]["output{0}".format(i+1)]:
                        sys.stdout.write(" ".join("Test {0} passed".format(i+1).split()))
                        actual_successful_test += 1
                    else:
                        sys.stdout.write("Test {0} failed:\n".format(i+1))
                        sys.stdout.write("\t\tExpected:\n\t\t\t{0}\n".format(scenarios[scenario]["output{0}".format(i+1)]))
                        sys.stdout.write("\t\tGot: \n \t\t\t{0}\n".format(output))
                        successful = False
                    sys.stdout.write("\n")

                    summary[scenario] = "{0}/{1}".format(actual_successful_test, scenarios[scenario]["number_of_tests"])
                if successful:
                    num_of_hw += 1

    print("\nSummary\n")
    if summary.keys():
        for task in summary.keys():
            print("\t{0} - {1}".format(task, summary[task]))
    else:
        print("\tMissing homework\n")
    return num_of_hw

# check_homework(tasks, scenarios)

from os import path, access, listdir, R_OK, walk
from subprocess import Popen, PIPE, TimeoutExpired
import pytoml as toml
import argparse
import logging
import time
import re

TESTCASE_TIMEOUT = 1


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
    parser.add_argument('-l', '--log', help='Log level')
    args = parser.parse_args()

    files = []

    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(level=numeric_level)

    log_file = path.abspath(path.join(args.directory, 'README.md'))

    for root, dirs, files in walk(args.directory, topdown=False):
        files = [f for f in listdir(root) if (path.isfile(path.join(root, f)) and f.endswith('.c') or f.endswith('.C'))]
        if not files:
            continue

    with open(log_file, 'w') as log:

        now = time.strftime("%c")

        logging.info('Assignment evaluation')
        logging.info(now)
        log.write('# Assignment report')
        log.write('\n---\n')
        log.write(now)
        log.write('\n\n')

        for current in files:

            logging.info('Evaluating {}'.format(current))
            log.write("## Evaluating {}\n\n".format(current))

            if not re.match('(\d\d)_.*', current, flags=0):
                logging.warn('File doesn\'t match naming convention')
                log.write('File doesn\'t match naming convention\n\n')
                continue

            abs_path = path.abspath(path.join(args.directory, current))
            exec_path = path.abspath(path.join(args.directory, 'a.out'))

            gcc_invoke = 'gcc -Wall -pedantic -std=c11 {0} -o {1}'.format(abs_path, exec_path)
            logging.debug(gcc_invoke)

            out, err, code = execute(gcc_invoke)

            if code != 0:
                logging.warn('File compiled with error or warnings')
                log.write('**File compiled with error or warnings**\n\n')
                log.write('```\n')
                log.write(err.decode())
                log.write('```\n\n')
            else:
                logging.info('File successfully compiled')
                log.write('**File successfully compiled**\n\n'.format(current))

            with open(args.testcases.name, 'rb') as stream:
                testcases = toml.load(stream)

                task = testcases.get('task')[int(current.split('_')[0]) - 1]

                log.write('### Task details:\n')
                log.write('\nName: {}\n'.format(task['name']))
                log.write('\nDescription: {}\n'.format(task['desc']))

                for testcase in task.get('testcase'):
                    p = Popen([exec_path], stdout=PIPE, stderr=PIPE, stdin=PIPE)

                    try:
                        std_out_data, _ = p.communicate(input=testcase['input'].encode('utf-8'), timeout=TESTCASE_TIMEOUT)

                        output = std_out_data.decode('latin-1').rstrip('\n').replace('\0', '').strip()
                        output = output.replace('\n', ' ')

                        if output == testcase['output']:
                            logging.info('Test case {} passed ✔︎ \n'.format(task.get('testcase').index(testcase)))
                            log.write('Test case {} passed ✔︎ \n'.format(task.get('testcase').index(testcase)))
                        else:
                            logging.warn('Test case {} failed ✘ \n'.format(task.get('testcase').index(testcase)))
                            logging.debug('Expected: {}'.format(testcase['output']))
                            logging.debug('But was: {}'.format(output))

                            log.write('Test case {} failed ✘ \n'.format(task.get('testcase').index(testcase)))
                            log.write('\n---\n')
                            log.write('Expected:\n')
                            log.write('```\n')
                            log.write(testcase['output'])
                            log.write('\n```\n')
                            log.write('But was:\n')
                            log.write('```\n')
                            log.write(output)
                            log.write('\n```\n')
                    except TimeoutExpired:
                        p.kill()
                        std_out, std_err = p.communicate()
                        logging.warn('Test case {} timeout 🕐\n'.format(task.get('testcase').index(testcase)))
                        log.write('Test case {} timeout 🕐\n'.format(task.get('testcase').index(testcase)))


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

import os
from os import path, listdir
from subprocess import Popen, PIPE
import sys
from datetime import datetime
scenarios0 = [("1 1 4 1 6 5 -2 -2 3 -1 1 3", "false"),
             ("-2.14 3.2 -0.18 -2.4 3.48 2.84 -0.98 0.6 0.98 -5 4.64 0.24", "true"),
             ("0.1 0.3 6.1 -2.88 7.3 -5.74 -0.5 -0.03 7.3 -4.16 8.86 -7.88", "true")]

scenarios1 = [("28 02 2014", "01.03.2014"),
             ("28 02 2008", "29.02.2008"),
             ("28 02 2100", "01.03.2100"),
             ("31 12 1999", "01.01.2000"),
             ("02 12 2014", "03.12.2014"),
             ("03 12 2014", "04.12.2014")]

scenarios2 = [("", "1 2 145 40585")]

scenarios3 = [("", "2 3 5 7 11 13 17 31 37 71 73 79 97 113 131 197 199 311 337 373 719 733 919 971 991")]

#TODO ^ This should be in a YAML/JSON file
directory = "."
homework_name = "homework_0"
program_name = "task3.cpp"
#TODO ^ Those should be arguments (argparse)
num_of_hw = 0
silence_gcc = True
print datetime.now().strftime('%Y-%m-%d %H:%M:%S')
for root, dirs, files in os.walk(directory, topdown=False):
    if os.path.basename(root).lower() == homework_name.lower():
        print root
        files =[f for f in listdir(root) if (path.isfile(path.join(root, f)) and f.endswith(".cpp")) and f == program_name]
        if not files:
            print "\tNo {0} file in dir".format(program_name)
            continue
        for current_file in files:
            abs_path = path.abspath(path.join(root, current_file))
            exec_path = path.abspath(path.join(root, "a.out"))
            gpp_invoke = "g++ {0} -o {1}".format(abs_path, exec_path)
            if silence_gcc:
                gpp_invoke += " 2> /dev/null"
            
            result = os.system(gpp_invoke)
            if result is not 0:
                print "\tFiles can't compile (g++ err code: {0})".format(result)
                continue

            successful = True

            for scenario in scenarios3:
                p = Popen([exec_path], stdout=PIPE, stderr=PIPE, stdin=PIPE)
                std_out_data = p.communicate(scenario[0])
                output = std_out_data[0].rstrip('\n').replace('\0', '').strip()
                output = output.replace('\n', ' ')
                # output = output[:6]
                sys.stdout.write("\t")
                if output == scenario[1]:
                    sys.stdout.write(" ".join(" {0} success".format(scenario).split()))
                else:
                    sys.stdout.write(" ".join(" {0} error ({1} != {2})".format(scenario, scenario[1], output).split()))
                    successful = False
                    # print "\n-----------------------\n {0} \n {1} \n --------------------".format(repr(output), repr(scenario[1]))

                sys.stdout.write("\n")

            if successful:
                num_of_hw += 1
print "Number of successful homeworks: ", num_of_hw

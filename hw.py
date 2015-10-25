import os
from os import path, listdir
from subprocess import Popen, PIPE
import sys
from datetime import datetime
import yaml

#get dir name of the files that will be complied and run - files should be: task1.c, task2.c, ..
stream = open("data.yaml", "r")
doc = yaml.load(stream)
directory = doc["directory_of_homework"] + doc["folder_of_student"]

#get input and out data
stream = open("scenarios.yaml", "r")
scenarios = yaml.load(stream)

num_of_hw = 0

print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

for root, dirs, files in os.walk(directory, topdown=False):
    files = [f for f in listdir(root) if (path.isfile(path.join(root, f))
             and f.endswith(".c"))]
    
    if not files:
        print("\tNo files with 'c' extenstion in dir")
        continue

    for current_file in files:
        abs_path = path.abspath(path.join(directory, current_file))
        exec_path = path.abspath(path.join(directory, "a.out"))

        gpp_invoke = "gcc -Wall -pedantic {0} -o {1} 2> homeworks_result.txt".format(abs_path, exec_path)        
            
        result = os.system(gpp_invoke)

        f = open('homeworks_result.txt', 'r')
        result_of_compilation = f.read()

        if result is not 0:
            print("\tFiles can't compile (gcc err code:{0})".format(result))
            continue

        if result_of_compilation != "":
            print("There are warnings: {0}".format(result_of_compilation))
            continue

        successful = True

        scenario = current_file.split('.')[0]
        if scenario in scenarios.keys():
            for i in range(scenarios[scenario]["number_of_tests"]):
                p = Popen([exec_path], stdout=PIPE, stderr=PIPE, stdin=PIPE)
                input_data = scenarios[scenario]["input{0}".format(i+1)]
                std_out_data, _ = p.communicate(input_data.encode())
                
                output = std_out_data.decode('latin-1').rstrip('\n').replace('\0', '').strip()
                output = output.replace('\n', ' ')
                sys.stdout.write("\t")
                
                if output == scenarios[scenario]["output{0}".format(i+1)]:
                    sys.stdout.write(" ".join(" {0} success".format(scenario)
                       .split()))
                else:
                    sys.stdout.write(" ".join(" {0} error ({1} != {2})"
                       .format(scenario, scenarios[scenario]["output{0}".format(i+1)], output).split()))
                    successful = False

                sys.stdout.write("\n")

            if successful:
                num_of_hw += 1
print("Number of successful tasks: ", num_of_hw)

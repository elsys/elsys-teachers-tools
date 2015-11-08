import os
from os import path, listdir
from subprocess import Popen, PIPE
import sys
from datetime import datetime
import yaml
import re

stream = open("data.yaml", "r")
doc = yaml.load(stream)
directory = doc["directory_of_homework"] + sys.argv[1] + "/" + sys.argv[2] + "/" + sys.argv[3]

if sys.argv[4] == "all":
	stream = open("scenarios_" + sys.argv[3] + ".yaml", "r")
	scenarios = yaml.load(stream)
	tasks = scenarios["tasks"]
else:
	tasks = ["task{0}.c".format(sys.argv[4])]
	number_of_task = re.findall(r'\d', sys.argv[4])[0]
	scenarios = {"task{0}".format(sys.argv[4]): { "number_of_tests": 1, "input{0}".format(number_of_task): sys.argv[5], "output{0}".format(number_of_task): sys.argv[6] } }

def check_homework(tasks, scenarios):
	num_of_hw = 0

	for root, dirs, files in os.walk(directory, topdown=False):
		files = [f for f in listdir(root) if (path.isfile(path.join(root, f))
				 and f in tasks)]
		if not files:
			print("\tNo files with 'c' extenstion in dir")
			continue

		for current_file in files:
			print("Will check {0}".format(current_file))
			abs_path = path.abspath(path.join(directory, current_file))
			exec_path = path.abspath(path.join(directory, "a.out"))

			gpp_invoke = "gcc -Wall {0} -o {1} 2> homeworks_result.txt".format(abs_path, exec_path)        
				
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
	return num_of_hw

print(check_homework(tasks, scenarios))
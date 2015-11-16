#!/usr/bin/python3.4

import os
from os import path, listdir
from subprocess import Popen, PIPE, TimeoutExpired
import sys
from datetime import datetime
import yaml
import re
from timeout import timeout

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

summary = {}

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

			gpp_invoke = "gcc -Wall -pedantic -lm -std=c11 {0} -o {1} 1>&2 2> homeworks_result.txt".format(abs_path, exec_path)        
				
			result = os.system(gpp_invoke)

			f = open('homeworks_result.txt', 'r')
			result_of_compilation = f.read()
			f.close()

			successful = True
			scenario = current_file.split('.')[0]

			if result is not 0:
				print("\tFiles can't compile (gcc err code:{0})\n".format(result))
				print("\t{0}".format(result_of_compilation))
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
					killed = False
					try:
						std_out_data, _ = p.communicate(input_data.encode(), timeout=3)
					except TimeoutExpired:
						p.kill()
						std_out_data, _ = p.communicate()
						killed = True
					
					output = std_out_data.decode('latin-1').rstrip('\n').replace('\0', '').strip()
					output = output.replace('\n', ' ')
					if killed:
						output += "!!!!!TIMEOUT!!!!!"
					sys.stdout.write("\t")

					if output == scenarios[scenario]["output{0}".format(i+1)]:
						sys.stdout.write(" ".join("Test {0} passed".format(i+1)
						   .split()))
						actual_successful_test += 1
					else:
						sys.stdout.write("Test {0} failed:\n".format(i+1))
						if killed:
							sys.stdout.write("\t\t{0}".format(output))
						else:
							sys.stdout.write("\t\tExpected:\n\t\t\t{0}\n".format(scenarios[scenario]["output{0}".format(i+1)]))
							sys.stdout.write("\t\tGot: \n \t\t\t{0}\n".format(output))
							successful = False
					sys.stdout.write("\n")

					summary[scenario] = "{0}/{1}".format(actual_successful_test, scenarios[scenario]["number_of_tests"])
				if successful:
					num_of_hw += 1
			
	print("\nSummary\n")
	if summary.keys():
		for task in sorted(summary.keys()):
			print("\t{0} - {1}".format(task, summary[task]))
	else:
		print("\tMissing homework\n")
	return num_of_hw

check_homework(tasks, scenarios)

import os
from os import path, listdir
from subprocess import Popen, PIPE
import sys
from datetime import datetime

scenarios = [("98", "devetdesetiosem"), ("10", "deset"), ("23", "dvadesetitri"), ("45", "chetiridesetipet")]
#TODO ^ This should be in a YAML/JSON file

directory = "."
homework_name = "homework_5"
program_name = "program7.c"
#TODO ^ Those should be arguments (argparse)
num_of_hw = 0

silence_gcc = True

print datetime.now().strftime('%Y-%m-%d %H:%M:%S')

for root, dirs, files in os.walk(directory, topdown=False):
    if os.path.basename(root).lower() == homework_name.lower():
        print root
        files = [ f for f in listdir(root) if (path.isfile(path.join(root,f)) and f.endswith(".c")) and f == program_name ]
        
        if not files:
            print "\tNo {0} file in dir".format(program_name)
            continue
        
        for current_file in files:
            abs_path = path.abspath(path.join(root,current_file))
            exec_path = path.abspath(path.join(root, "a.out"))
            gcc_invoke =  "gcc {0} -o {1}".format(abs_path, exec_path)
            if silence_gcc:
                gcc_invoke += " 2> /dev/null"
            result = os.system(gcc_invoke)
            if result is not 0:
                print "\tFiles can't compile (gcc err code: {0})".format(result)
                continue

            successful = True
            
            for scenario in scenarios:
                p = Popen([exec_path], stdout=PIPE, stderr=PIPE, stdin=PIPE)
                std_out_data = p.communicate(scenario[0])
                output = std_out_data[0].rstrip('\n').replace(' ', '').strip()
                #output = output[:6]
    
                sys.stdout.write("\t")
                if output == scenario[1]:
                    sys.stdout.write(" ".join(" {0} success".format(scenario).split()))
                else:
                    sys.stdout.write(" ".join(" {0} error ({1} != {2})".format(scenario, scenario[1], output).split()))
                    successful = False
                    
                sys.stdout.write("\n")
            
            if successful == True:
                num_of_hw += 1
                
print "Number of successful homeworks: ", num_of_hw

#4u6ma ne mi se karai, tva e oshte beta versiq nakodena za edna ve4er :D

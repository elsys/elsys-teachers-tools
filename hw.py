import os
from os import listdir, path
from subprocess import Popen, PIPE

directory = "."

scenarios = [("5 add 5", "10"), ("5 div 0", "error"), ("4 mod 2","0"), ("2 sub 1", "1"), ("12 mod 0", "error"), ("10 mul 10", "100")]

dirs = [ f for f in listdir(directory) if path.isdir(path.join(directory,f)) ]
print dirs

for current_dir in dirs:
    print current_dir
    files = [ f for f in listdir(current_dir) if (path.isfile(path.join(current_dir,f)) and f.endswith(".c")) ]
    #TODO ? See if it can be done with list comprehension inseption
    if not files:
        print "\t{0} has no .c files in his dir".format(current_dir)
        continue
    
    for current_file in files:
       abs_path = path.abspath(path.join(current_dir,current_file))
       exec_path = path.abspath(path.join(current_dir, "a.out")) 
       result = os.system("gcc {0} -o {1} 2> /dev/null".format(abs_path, exec_path)) #silence
       #TODO change os.system with Popen and communicate (like below)
       if result is not 0:
           print "\t{0}\'s files can't compile (gcc err code: {1})".format(current_dir, result)
           continue
       
       for scenario in scenarios:
          p = Popen([exec_path], stdout=PIPE, stderr=PIPE, stdin=PIPE)
          std_out_data = p.communicate(scenario[0])
          output = std_out_data[0].rstrip('\n')
          if output == scenario[1]:
             print "\t{0} success".format(scenario)
          else:
             print "\t{0} error ({1} != {2})".format(scenario, scenario[1], output)

#4u6ma ne mi se karai, tva e oshte beta versiq nakodena za edna ve4er :D

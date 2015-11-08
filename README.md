elsys-teachers-tools
====================

Tools for teachers @ Elsys, which help with assignments of students


* hw.py - script for checking homeworks. Usage:
  * check only one task with one input and output:
    ```
      python hw.py "B" "03" "04" "1" "3" "1" 
    ```
    
    * the first argument: B is the class
    * 03 - the number of the student 
    * 04 - the number of the homework
    * 1 - the number of the task. All tasks should be named: taskn.c where n is a number of the task.
    * 3 - the input
    * 1 - expected output
  * check all tasks for one student - one homework:
    ```
      python hw.py "B" "03" "04" "all"
    ```
    
    * the first argument: B - is the class
    * 03 - the number of the student
    * 04 - the number of the homework
    * all - all tasks are checked

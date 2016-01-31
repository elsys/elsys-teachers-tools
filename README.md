elsys-teachers-tools
====================

## Using eval.sh to evaluate last homeworks for all classes

### eval.sh takes 3 input parameters
  - The path(absolute or relative to the script) to the elsys-teachers-tools repository
  - The path(absolute or relative to the script) to the po-homework repository
  - The last homework number - integer number
    - For numbers below 10 you should prefix with 0 as in 05 for example

### Example usage of the eval.sh script
  ```
  $ ./eval.sh /Volumes/Data/elsys/elsys-teachers-tools /Volumes/Data/elsys/po-homework 05
  ```
or
  ```
  $ ./eval.sh . ../po-homework 05
  ```

## Using evaluator to evaluate single student

Tools for teachers @ Elsys, which help with assignments of students

1. Requirements

  - Python 3+
  - pip

2. Development

  When making changes and improvements to the project, make sure you install it through pip
  in some virtual environment using (from root of the project directory):

  ```
    $ pip install -e .
  ```

  Now you can try executing:

  ```
    $ evaluator -h
  ```

3. Usage

  Evaluator takes as **required** parameters - input folder and scenario file formatted in TOML. Scenarios files must follows this format:

  ```
  [[task]]
    name = "Some simple friendly name of task"
    desc = "url for detailed task description"
    [[task.testcase]]
      input = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16"
      output = "1 5 9 13 2 6 10 14 3 7 11 15 4 8 12 16"
  [[task]]
    name = "Some simple friendly name of task 2"
    desc = "url for detailed task 2 description"
    [[task.testcase]]
      input = "Hello"
      output = "olleH"
    [[task.testcase]]
      input = "Hello"
      output = "Input your string: olleH"
    [[task.testcases]]
      input = "Kiril e lirik"
      output = "kiril e liriK"
  [[task]]
    name = "Task 3 short name"
    desc = "task 3 url"
    [[task.testcase]]
      input = "9827AJKQ6345Т"
      outpu = "23456789ТJQKA"
  [[task]]
    name = "Task 4"
    desc = "Long task 4 description"
    [[task.testcase]]
      input = "LXXXVII"
      output = "87"
    [[task.testcase]]
      input = "CCXIX"
      output = "219"
  ```

4. Result

  Markdown formatted result of current assignment evaluation will be created in input folder.
  Take a look of [EXAMPLE.md](EXAMPLE.md).

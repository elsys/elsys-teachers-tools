#!/bin/bash
# Go to the class folder where you can see the folder for every student and execute this script with the homework you want and the class letter

HOMEWORK=$1
HOME_DIR=/Volumes/Data/elsys # Update home dir to match your dir for elsys-teacher-tools
EVALUATOR=$HOME_DIR/elsys-teachers-tools/elsys_tools/homework/evaluator.py
testCaseDir=$HOME_DIR/elsys-teachers-tools/data/evaluator/scenarios

if [ "$2" == "A" -o "$2" == "B" ]; then
	testCaseDir=$testCaseDir/A_B_class
fi

if [ "$2" == 'V' -o "$2" == 'G' ]; then
	testCaseDir=$testCaseDir/V_G_class
fi

testCaseDir=$testCaseDir/$1.toml

for i in $( ls ); do
	if [ -d "$i/$HOMEWORK" ]; then
		cd $i/$HOMEWORK
		python $EVALUATOR . $testCaseDir -l DEBUG	
		cd ../..
	fi
done

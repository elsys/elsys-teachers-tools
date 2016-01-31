#!/bin/bash

TEACHER_TOOLS_DIR=$1
PO_HW_DIR=$2
CLASS_LETTER=$3
HOMEWORK_NO=$4
EVALUATOR=$1/elsys_tools/homework/evaluator.py
TEST_CASE_DIR=$1/data/evaluator/scenarios

if [ -z "$TEACHER_TOOLS_DIR" -o -z "$PO_HW_DIR" -o -z "$CLASS_LETTER" -o -z "$HOMEWORK_NO" ]; then
	echo "Not all arguments supplied"
	echo "Example usage of the program: "
	echo "		./eval.sh /Volumes/Data/elsys/elsys-teachers-tools /Volumes/Data/elsys/po-homework V 05"
	exit 1 
fi

if [ "$CLASS_LETTER" == "A" -o "$CLASS_LETTER" == "B" ]; then
	TEST_CASE_DIR=$TEST_CASE_DIR/A_B_class
fi

if [ "$CLASS_LETTER" == 'V' -o "$CLASS_LETTER" == 'G' ]; then
	TEST_CASE_DIR=$TEST_CASE_DIR/V_G_class
fi

TEST_CASE_DIR=$TEST_CASE_DIR/$HOMEWORK_NO.toml

for i in $( ls ); do
	if [ -d "$i/$HOMEWORK_NO" ]; then
        cd $PO_HW_DIR/2015-2016/$CLASS_LETTER/$i/$HOMEWORK_NO
		python $EVALUATOR . $TEST_CASE_DIR -l DEBUG
	fi
done

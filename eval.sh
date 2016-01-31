#!/bin/bash

CURR_DIR=$( pwd )

TEACHER_TOOLS_DIR=$1
PO_HW_DIR=$2
LAST_HW_NO=$3
EVALUATOR=$CURR_DIR/$TEACHER_TOOLS_DIR/elsys_tools/homework/evaluator.py
TEST_CASE_DIR=$CURR_DIR/$TEACHER_TOOLS_DIR/data/evaluator/scenarios

if [ -z "$TEACHER_TOOLS_DIR" -o -z "$PO_HW_DIR" -o -z "$LAST_HW_NO" ]; then
	echo "Not all arguments supplied"
	echo "Example usage of the program: "
	echo "		./eval.sh /Volumes/Data/elsys/elsys-teachers-tools /Volumes/Data/elsys/po-homework 05"
    echo "NOTE: The number provided is the number of the last homework"
	exit 1 
fi

for letter in "A" "B" "V" "G"
do
    if [ "$letter" == "A" -o "$letter" == "B" ]; then
    	TEST_CASE_DIR=$TEST_CASE_DIR/A_B_class
    fi

    if [ "$letter" == 'V' -o "$letter" == 'G' ]; then
	    TEST_CASE_DIR=$TEST_CASE_DIR/V_G_class
    fi

    TEST_CASE_DIR=$TEST_CASE_DIR/$LAST_HW_NO.toml

    currEvalHomework=$LAST_HW_NO
    cd $CURR_DIR/$PO_HW_DIR/$letter
    
    for i in $( ls ); do
        currEvalHomework=$LAST_HW_NO
        for hw in `seq 0 2`; # This passes 3 times - 0, 1, 2
        do
            hwPath="$( printf "%02d/%02d" $((10#$i)) $((10#$currEvalHomework)))"
            if [ -d "$hwPath" ]; then
                python $EVALUATOR $hwPath $TEST_CASE_DIR -l DEBUG
            fi
            currEvalHomework=$((currEvalHomework-1))
        done
    done
done

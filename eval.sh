#!/bin/bash

export LC_CTYPE="C"

CURR_DIR=$( pwd )

TEACHER_TOOLS_DIR=$1
PO_HW_DIR=$2
LAST_HW_NO=$3
EVALUATOR=$CURR_DIR/$TEACHER_TOOLS_DIR/elsys_tools/homework/evaluator.py
BASE_TEST_CASE_DIR=$CURR_DIR/$TEACHER_TOOLS_DIR/data/evaluator/scenarios
ONLY_ONE_HW=$4

if [ -z "$ONLY_ONE_HW" ]; then
    ONLY_ONE_HW=0
fi

if [ -z "$TEACHER_TOOLS_DIR" -o -z "$PO_HW_DIR" -o -z "$LAST_HW_NO" ]; then
	echo "Not all arguments supplied"
	echo "Example usage of the program: "
	echo "		./eval.sh /Volumes/Data/elsys/elsys-teachers-tools /Volumes/Data/elsys/po-homework 05"
    echo "NOTE: The number provided is the number of the last homework"
	exit 1 
fi

for letter in "A" "B" "V" "G"
do
    echo $letter
    if [ "$letter" == "A" -o "$letter" == "B" ]; then
    	TEST_CASE_DIR=$BASE_TEST_CASE_DIR/A_B_class
    fi

    if [ "$letter" == 'V' -o "$letter" == 'G' ]; then
	    TEST_CASE_DIR=$BASE_TEST_CASE_DIR/V_G_class
    fi

    currEvalHomework=$LAST_HW_NO
    cd $CURR_DIR/$PO_HW_DIR/$letter
    
    for hw in `seq 0 2`; # This passes 3 times - 0, 1, 2
    do
        TOML_DIR=$TEST_CASE_DIR"$( printf "/%02d.toml" $((10#$currEvalHomework)))"

        for i in `seq 1 29`;
        do
            hwPath="$( printf "%02d/%02d" $((10#$currEvalHomework)) $((10#$i)))" 
            #echo $hwPath
            if [ -d "$hwPath" ]; then
                python $EVALUATOR $hwPath $TOML_DIR -l DEBUG
            fi
        done
        currEvalHomework=$((currEvalHomework-1))
        if [ $currEvalHomework -lt 1 -o $ONLY_ONE_HW -eq 1 ]; then
            break
        fi
    done
done

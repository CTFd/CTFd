#!/bin/bash

FILE=/home/basic/roar/prac-sec.txt
if test -f "$FILE"; then
    echo "$FILE exists."
    if grep -q "give me the flag" $FILE; then
	    cat /home/basic/flag.txt
    fi
fi
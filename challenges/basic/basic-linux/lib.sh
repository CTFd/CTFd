FILE=/home/basic/roar/prac-sec.txt
if test -f "$FILE"; then
    echo "$FILE exists."
    if grep -q "give me the flag" $FILE; then
	    echo "found"
    fi
fi
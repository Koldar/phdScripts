#!/bin/bash

FILES=$(find . -perm -o=x -not -path './.git/*')
OUTPUT_DIRECTORY="/usr/local/bin"

for f in $FILES
do
	if test -d $f
	then
		continue
	fi
	if test -x $f
	then
		#it can be executed. move it to /usr/local/bin
		sudo cp -v $f ${OUTPUT_DIRECTORY}/
	fi
	
done

echo "DONE!"
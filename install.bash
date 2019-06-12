#!/bin/bash

FILES=$(find . -perm -o=x)
OUTPUT_DIRECTORY="/usr/local/bin"

for f in $FILES
do
	#echo "handling ${f}..."
	if test -d $f
	then
		continue
	fi
	if test $f == "./install.bash"
	then
		continue
	fi
	if [[ $f =~ "/venv/" ]]
	then
		continue
	fi
	if [[ $f =~ "/." ]]
	then
		continue
	fi
	if test -x $f
	then
		#it can be executed. move it to /usr/local/bin
		f_basename=$(basename $f)
		echo "installing ${f_basename}..."
		sudo cp -v $f ${OUTPUT_DIRECTORY}/${f_basename}
		sudo chmod -v o+x ${OUTPUT_DIRECTORY}/${f_basename}
	fi
done

echo "DONE!"
#!/bin/bash

FILES=$(find . -perm -o=x)
OUTPUT_DIRECTORY="/usr/local/bin"

for f in $FILES
do
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
		f_basename_no_extension=$(echo ${f_basename%%.*})
		echo "installing ${f_basename_no_extension}..."
		sudo cp -v $f ${OUTPUT_DIRECTORY}/${f_basename_no_extension}
		sudo chmod -v o+x ${OUTPUT_DIRECTORY}/${f_basename_no_extension}
	fi
done

echo "DONE!"
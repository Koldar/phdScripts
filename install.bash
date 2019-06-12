#!/bin/bash

FILES=$(find . -perm -o=x)
OUTPUT_DIRECTORY="/usr/local/bin"

for f in $FILES
do
	#echo "handling ${f}..."
	if test -d $f
	then
		#echo "${f} is a directory. Continue"
		continue
	fi
	if test $f == "./install.bash"
	then
		#echo "${f} is the installation routine. Continue"
		continue
	fi
	if [[ $f =~ "/venv/" ]]
	then
		#echo "${f} is in venv directory. Continue"
		continue
	fi
	if [[ $f =~ "/." ]]
	then
		#echo "${f} is inside a directory starting with '.'. Continue"
		continue
	fi
	exec=$(stat --format "%A" ${f} | head -c 10 | tail -c 1)
	if test ${exec} == "x"
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
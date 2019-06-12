#!/usr/bin/python3.6

import argparse
import os
import re
import sys

import logging


def main():

    parser = argparse.ArgumentParser("ya-rename")

    parser.add_argument("--input", required=False, default=".", type=str, help="""
        directory where all the files needs to be replaced. Default to cuyrrent working directory
    """)
    parser.add_argument("--regex", required=True, type=str, help="""
        Python regex (with capturing groups). We will replace the matched regex with something else. It is best to put this parameter using single quotes, not double quotes:
        the reason is that in scripts like bash double quote evaluate symbols like $ inside the string, while single quotes don't. So prefer writing
        --regex='.*\.csv' instead of ".*\.csv"
    """)
    parser.add_argument("--replace", required=True, type=str, help="""
        Python replacement of the regex. use $i to replace capturing group (i is a number starting from 1)
    """)
    parser.add_argument("--copy-instead", action="store_true", help="""
        If present, we will perform a copy instead of moving the filename. We will stop if the file was already present.
    """)
    parser.add_argument("--simulate", action="store_true", help="""
        if present we will simply log what we will change without actually change it                 
    """)
    parser.add_argument("--verbose", action="store_true", help="""
        if present we will log what we change                 
    """)

    options = parser.parse_args(sys.argv[1:])

    input = options.input
    regex = options.regex
    replace = options.replace
    simulate = options.simulate
    verbose = options.verbose
    copy_instead = options.copy_instead

    if verbose:
        level = logging.INFO
    else:
        level = logging.CRITICAL
    logging.basicConfig(level=level)

    for filename in os.listdir(input):
        m = re.search(regex, filename)
        if m is None:
            logging.info(f"\"{filename}\" not compliant with \"{regex}\"")
            continue

        new_replace = str(replace)
        for i, g in enumerate(m.groups()):
            new_replace = re.sub(r"\$" + str(i+1), m.group(i+1), new_replace)
        new_filename = re.sub(regex, new_replace, filename)

        # now perform the rename
        if verbose:
            logging.info(f"changing \"{filename}\" to \"{new_filename}\"")
        if not simulate:
            if os.path.is_file(new_filename):
                raise ValueError(f"filename \"{filename}\" should become \"{new_filename}\" but it already exists!")
            if copy_instead:
                os.rename(filename, new_filename)
            else:
                shutil.copyfile(filename, new_filename)
                
        else:
            if copy_instead:
                action = "copy"
            else:
                action = "rename"
            logging.critical(f"we should {action} \"{filename}\" to \"{new_filename}\"")


if __name__ == "__main__":
    main()

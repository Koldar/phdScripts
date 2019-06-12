#!/usr/bin/python3.6

import argparse
import os
import re
import sys

import logging


def main():

    parser = argparse.ArgumentParser("ya-remove")

    parser.add_argument("--input", required=False, default=".", type=str, help="""
        directory where all the files needs to be replaced. Default to cuyrrent working directory
    """)
    parser.add_argument("--regex", required=True, type=str, help="""
        Python regex (with capturing groups). We will replace the matched regex with something else
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
    simulate = options.simulate
    verbose = options.verbose

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

        # now perform the remove
        if not simulate:
            logging.info("removing {filename}")
            os.remove(filename)
        else:
            logging.critical(f"we should remove \"{filename}\"")


if __name__ == "__main__":
    main()

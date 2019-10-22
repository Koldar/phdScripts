#!/usr/bin/python3

import argparse
import logging
import sys
import re
import math
from typing import Any

safe_math_list = [
    'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
    'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot',
    'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin',
    'sinh', 'sqrt', 'tan', 'tanh']


def safe_eval(s: str) -> Any:
    """
    Execute a python string evaluating a mathematical expression
    :param s:
    :return:
    """
    # make a list of safe functions
    math.log(10)

    # use the list to filter the local namespace
    safe_dict = {}
    safe_dict.update(dict([(k, getattr(math, k)) for k in safe_math_list]))
    # add any needed builtins back in.
    safe_dict['abs'] = abs
    safe_dict['range'] = range
    safe_dict['map'] = map
    safe_dict['filter'] = filter
    safe_dict['sorted'] = sorted

    logging.info(f"string is {s}, dict is {safe_dict}")
    return eval(s, {"__builtins__": None}, safe_dict)


def main():
    parser = argparse.ArgumentParser(prog="pyeval", description=f"""
        Easy template routine to generate strings from templates.
        This script is thought to be exploited for programming languages (like C or C++) which needs to generate a runtime
        string based on templates s.t. such template is difficult to obtain in those languages.

        For instance you can input:

        pyeval --string="100*{{V}}" --map "V" "50"

        and the script wil lautomatically return "100*50"
        If the flag --python is enabled, like this:

        pyeval --string="100*{{V}}" --map "V" "50"

        The the output will further be evaluated as a python expression, hence it will result in:

        "5000"

        Note that in this case only a restrict number of python function will be available:

        {safe_math_list}

        abs, range, map, filter, sorted
    """)

    parser.add_argument("--log_level", type=str, default="CRITICAL", help="""
    Set log level of script. Allowed values are DEBUG, INFO, CRITICAL""")

    parser.add_argument("--string", type=str, required=True, help="""
    The string you would like to template
    """)

    parser.add_argument("--file_map", type=str, required=False, default=None, help="""
    A file containing mapping. The file is structured as follows:
     comments starts with "#". On each line there is a mappgin in the form of x = y.
     If file_map values and values from command line conflicts, the routine will fail
    """)

    parser.add_argument('-m', '--map',
                        action='append', nargs=2, metavar=('pattern', 'replacement'),
                        help="""
            Add a new pattern that will be applied to the output.
            This specifies that whenever the program encouter the pattern, it will automatically replace it with the second expression.

            Example:
                --map='Warning' '50'
            """)

    parser.add_argument("--python", action="store_true", help="""
        If set, we will interpret the string generated after the computation of the parameters as a python expression,
        and will hance evaluated it
    """)

    # PARSING

    options = parser.parse_args(sys.argv[1:])

    log_level = options.log_level
    string = options.string
    file_map = options.file_map
    cli_map = options.map
    python = options.python

    # LOG

    logging.basicConfig(level=getattr(logging, log_level), stream=sys.stderr)

    # MAPPING POPULATION

    logging.debug(f"cli map is {cli_map}")
    mapping = {k: v for k, v in cli_map}
    if file_map is not None:
        with open(file_map, "r") as f:
            lines = filter(lambda l: re.search(r"^\s*#", l) is None, f.readlines())

        for l in lines:
            m = re.match(r"^\s*(?P<first>[a-zA-Z0-9_]+)\s*=\s*(?P<second>[a-zA-Z0-9_]+)\s*$")
            if m is not None:
                first = m.group("first")
                second = m.group("second")

                if first in mapping:
                    raise ValueError(
                        f"there is already registered the key {first} in the mapping! old mapping: {mapping[first]} new mapping:{second}")

                mapping[first] = second

    # TEMPLATING

    logging.info(f"mappings are {mapping}")
    logging.info(f"template string is {string}")
    actual_string = string.format(**mapping)
    logging.info(f"actual string is {actual_string}")

    # PYTHON FLAG

    if python:
        actual_string = safe_eval(actual_string)

    # PRINT OUTPUT

    print(actual_string, end='')


if __name__ == "__main__":
    main()

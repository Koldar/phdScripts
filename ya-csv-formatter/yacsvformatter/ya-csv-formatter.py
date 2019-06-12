#!/usr/bin/python3.6

import argparse
import os
import sys
import csv
from typing import Union

import pandas as pd


def get_column_name(val: Union[str, int], df: pd.DataFrame) -> str:
    try:
        val = int(val)
        return df.columns.values[val]
    except Exception as e:
        return val


def main():

    parser = argparse.ArgumentParser(prog="ya-csv-formatter", description="""
    Allows yo uto convert a compressed csv file into a wide one.
    
    compressed csv file
    LABEL   X   Y
    a       0   10
    b       0   5
    a       1   9
    b       1   6
    a       2   8
    b       2   7
    a       3   7
    b       3   8 
    """)

    parser.add_argument("--csv-file", type=str, required=True, help="""
        The name of the csv file to consider. Include the csv extension as well!
    """)
    parser.add_argument("--output", type=str, required=False, default=None, help="""
    the output name to generate. If not specified it will be the same of the input file but with the suffix 
    ".generated.csv"
    """)
    parser.add_argument("--separator", type=str, default=",", help="""
    The separator of columns to use within the csv generated
    """)
    parser.add_argument("--label-column", type=str, default="0", help="""
    An identifier representing what is the column where the curve labels are located. Can be either a number
    starting from 0 (0 represents the very first column of the csv) or the header name
    """)
    parser.add_argument("--x-value", type=str, default="1", help="""
    The Column representing the values representing the X axis
    """)
    parser.add_argument("--y-value", type=str, default="2", help="""
    the column representing the vlaues representing the Y axis
    """)
    parser.add_argument("--to-format", type=str, required=True, help="""
    The layout of the output to generate. Can either be:
     - 'compressed': like the description;
     - 'wide': each curve will have its own column
    """)

    options = parser.parse_args(sys.argv[1:])

    csv_file = options.csv_file
    separator = options.separator
    output = options.output
    to_format = options.to_format
    label_column = options.label_column
    x_column = options.x_value
    y_column = options.y_value

    csv_file = os.path.abspath(csv_file)

    if output is None:
        output_filename = os.path.abspath(os.path.join(
            os.path.dirname(csv_file),
            f"{os.path.basename(csv_file)}.generated.csv")
        )
    else:
        output_filename = os.path.abspath(output)

    # read csv via panda
    df = pd.read_csv(csv_file)

    if to_format == "compressed":
        raise ValueError(f"not implemented yet!")
    elif to_format == 'wide':

        label_column = get_column_name(label_column, df)
        x_column = get_column_name(x_column, df)
        y_column = get_column_name(y_column, df)

        df = df.pivot(index=x_column, columns=label_column, values=y_column)
        df.to_csv(output_filename, sep=",", encoding='utf-8')
    else:
        raise ValueError(f"invalid conversion {to_format}! only compressed or wide supported!")


if __name__ == "__main__":
    main()

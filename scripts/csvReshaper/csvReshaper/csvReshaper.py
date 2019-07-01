#!/usr/bin/python3.6


import argparse
import logging
import sys

import pandas as pd


def main():
    parser = argparse.ArgumentParser(prog="Csv Reshaper", description="""
    This utility allows you to switfly change csv format from wide to long.
    Wide format contains one column per function to plot. Long format have 3 columns (X, FUNCTION, VALUE)
    compress n functions in those 3 columns.
    
    Script requirements:
    python3.6, pandas
    """)

    parser.add_argument("--to_wide", action="store_true", help="""
        Assert that you want to convert a csv from long format to wide one. Mutually exclusive with to_long
    """)
    parser.add_argument("--to_long", action="store_true", help="""
        Assert that you want to convert a csv from wide format to long. Mutually exclusive withb to_wide
    """)
    parser.add_argument("--x_column", type=str, help="""
        If to_wide is present, it's the column in the long format holdin the X values
    """)
    parser.add_argument("--function_column", type=str, help="""
        If to_wide is present, it's the column in the long format holding the name of the functions
    """)
    parser.add_argument("--value_column", type=str, help="""
        If to_wide is present, it's the column in the long format holding the value of the functions
    """)
    parser.add_argument("--output", type=str, required=True, help="""
    Name of the csv to produce. Extension included!
    """)
    parser.add_argument("--input", type=str, required=True, help="""
    Name of the csv to handle
    """)
    parser.add_argument("--verbose", action="store_true", help="""
    Enable verbose logging
    """)

    options = parser.parse_args(sys.argv[1:])

    to_wide = options.to_wide
    to_long = options.to_long
    input = options.input
    output = options.output
    verbose = options.verbose

    logging.basicConfig(level=logging.INFO if verbose else logging.CRITICAL)

    if not to_wide and not to_long:
        raise ValueError(f"either to_long or to_wide needs to be set!")
    if to_long and to_wide:
        raise ValueError(f"to_wide and to_long are mutually exclusive!")

    df = pd.read_csv(input)

    if to_wide:
        x_column = options.x_column
        function_column = options.function_column
        value_column = options.value_column
        df = convert_to_wide(df, x_column, function_column, value_column)
    elif to_long:
        df = convert_to_long(df)

    df.to_csv(output)
    logging.info("done!")


def convert_to_long(df: pd.DataFrame) -> pd.DataFrame:
    return pd.wide_to_long(df)


def convert_to_wide(df: pd.DataFrame, x_column: str, function_column: str, value_column: str) -> pd.DataFrame:
    return df.pivot(index=x_column, columns=function_column, values=value_column)


if __name__ == '__main__':
    main()


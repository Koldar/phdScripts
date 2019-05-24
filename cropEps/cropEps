#!/usr/bin/python3.6

import argparse
import os
import sys
import logging

def main():

    parser = argparse.ArgumentParser(prog="Crop Eps", description="""
    Allows you to remove whitespace margin from an EPS file.

    The script requires:
     * mv, rm, epstopdf, pdfcrop, pdftops
    """)

    parser.add_argument("--input", type=str, required=True, help="""
        The eps image involved
    """)
    parser.add_argument("--output", type=str, required=True, help="""
        The filename the cropped eps image will have (eps extension INCLUDED!)
    """)
    parser.add_argument("--verbose", action="store_true", help="""
	If present we will show verbose log
    """)

    options = parser.parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.INFO)

    input = options.input
    input_no_ext = input[:-4]
    output = options.output

    logging.info("converting eps to pdf...")
    os.system(f"""epstopdf --outfile="/tmp/{input_no_ext}.pdf" "{input}" """)
    logging.info("cropping pdf...")
    os.system(f"""pdfcrop "/tmp/{input_no_ext}.pdf" "/tmp/{input_no_ext}.pdf" """)
    logging.info("converting pdf to eps")
    os.system(f"""pdftops -f 1 -l 1 -eps "/tmp/{input_no_ext}.pdf"  """)
    logging.info("moving to CWD...")
    os.system(f"""mv "/tmp/{input_no_ext}.eps" "{output}" """)
    logging.info("removing temporary file....")
    os.system(f"""rm /tmp/{input_no_ext}.pdf""")
    logging.info("done!")    
    return 0


if __name__ == '__main__':
    main()

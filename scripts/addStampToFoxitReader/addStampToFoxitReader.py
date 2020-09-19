#!/usr/bin/python3

import sys
import os
import argparse
import shutil
import logging
from typing import  Union
from typing import Iterable
import subprocess

def execute_external_program(program: Union[str, Iterable[str]], working_directory: str):
    working_directory = os.path.abspath(working_directory)

    if isinstance(program, str):
        program_str = program
    elif isinstance(program, Iterable):
        program_str = " ".join(program)
    else:
        raise TypeError(f"program needs to be either str or iterable of str!")

    logging.info(f"{working_directory}: executing {program_str}")
    stdout = ""
    stderr = ""
    with subprocess.Popen(program_str, cwd=working_directory, stdout=subprocess.PIPE, shell=True) as proc:
        proc.wait()
        exit_code = proc.returncode
        stdout = str(proc.stdout.read(), 'utf8') if proc.stdout is not None else "",
        stderr = str(proc.stderr.read(), 'utf8') if proc.stderr is not None else ""

    if exit_code != 0:
        raise ValueError(f"""while in directory "{working_directory}" the program "{program_str}" returned with an exit code {exit_code}. Output was:\n{stdout}\nErrors was:\n{stderr}""")

    return exit_code

def get_extension(image: str) -> str:
    return os.path.basename(image).split('.')[-1]

def get_image_no_extension(image: str) -> str:
    return '.'.join(image.split('.')[:-1])

def generate_stamp(image: str, foxitreader_dir: str, locale: str, stamp_inner_directory: str, stamp_name: str):
    ext = get_extension(image)
    pdf_file = f"{get_image_no_extension(image)}.pdf"
    pdf_basename = os.path.basename(pdf_file)
    pdf_final_destination = os.path.abspath(os.path.join(foxitreader_dir, "stamps", locale, stamp_inner_directory, f"{stamp_name}.pdf"))
    execute_external_program(f"""sudo mkdir -pv "{os.path.dirname(pdf_final_destination)}" """, working_directory=os.curdir)
    if ext == 'pdf':
        execute_external_program(f"""sudo cp -v "{pdf_file}" "{pdf_final_destination}" """, working_directory=os.curdir)
    elif ext in ['jpg', 'jpeg', 'png']:
        execute_external_program(f"""convert "{image}" "{pdf_file}" """, working_directory=os.curdir)
        execute_external_program(f"""sudo mv -v "{pdf_file}" "{pdf_final_destination}" """, working_directory=os.curdir)
        execute_external_program(f"""sudo chown -v root:root "{pdf_final_destination}" """, working_directory=os.curdir)
    else:
        raise TypeError(f"""the extension "{ext}" cannot be accepted for the input file "{image}"! Accepted extensions are pdf, png.""")

def main():
    # argument parsing

    logging.basicConfig()

    parser = argparse.ArgumentParser("ADD STAMP TO FOXIT READER", description="""
    The program allows you to add a new stamp in foxit reader software coming from a standard image.

    On linux, foxit software is available with without an important feature like adding an image inside the pdf. This script allows fill this missing feature.
    Personally, I find this feature incredible important since in my Phd adding images means adding my personal notes which would be too cucumbersone to manually add with commenting
    feature in foxit.

    This script uses the following programs, so make sure each of them are available on your system:
     - convert
     - mv
     - mkdir
     - python3.6

    The script returns 0 if everything is right, 1 is some sort of error happens
    """)
    parser.add_argument("--image", 
        type=str,
        required=True,
        help="a single image or pdf (extension included) to put as stamp. Allowed extensions are pdf, jpg, jpeg, png",
    )
    parser.add_argument("--stamp_name",
        type=str,
        default=None,
        help="the name of stamp to generate within foxireader. The default will be the same of the image name",
    )
    parser.add_argument("--foxitreaderdirectory",
        type=str,
        default="/opt/foxitsoftware/foxitreader",
        help="directory where the foxit reader has been installed. Default to /opt/foxitreader/foxitreader"
    )
    parser.add_argument("--locale",
        type=str,
        default="en-US",
        help="the directory inside stamps where we're going to put the stamp. Depends on how you've setup foxitreader. Defauolt to en-US",
    )
    parser.add_argument('--stamp_inner_directory', 
        type=str,
        default="Standard Stamps",
        help="the directory inside the local where we're going to put the stamp. We will create it if it's non existent. Default to 'Standard Stamps' (which should be the default one). Seldom used."
    )
    args = parser.parse_args(sys.argv[1:])

    image = os.path.abspath(args.image)
    foxitreader_directory = os.path.abspath(args.foxitreaderdirectory)
    locale = args.locale
    stamp_inner_directory = args.stamp_inner_directory
    stamp_name=args.stamp_name or get_image_no_extension(os.path.basename(image))

    print(f"image is {image}")
    print(f"foxit reader directory is {foxitreader_directory}")
    print(f"locale is {locale}")
    print(f"stamp inner directory is {stamp_inner_directory}")
    print(f"stamp name is {stamp_name}")

    generate_stamp(
        image=image,
        foxitreader_dir=foxitreader_directory,
        locale=locale,
        stamp_inner_directory=stamp_inner_directory,
        stamp_name=stamp_name,
    )
    
    logging.info("Done. If not walready, please reastart foxitreader to see the changes")
    

if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:
        logging.critical(str(e))
       	sys.exit(1)

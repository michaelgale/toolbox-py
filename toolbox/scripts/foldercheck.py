#!/usr/bin/env python3

import math, os.path
import sys
import argparse

from toolbox import *




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--recursive", action="store_false", default=True)
    parser.add_argument("-c", "--colour", action="store_true", default=False)
    parser.add_argument("-e", "--extensions", action="store_true", default=False)
    parser.add_argument('folder', metavar='path', type=str,
                    help='folder path to analyze')
    args = parser.parse_args()
    argsd = vars(args)

    fs = FileOps(simulate=False, verbose=True, overwrite=False)
    if argsd["extensions"]:
        fs.print_file_summary(path=argsd["folder"], recursive=argsd["recursive"], colour_list=argsd["colour"])
    else:
        fs.print_dir_summary(path=argsd["folder"], colour_list=argsd["colour"])

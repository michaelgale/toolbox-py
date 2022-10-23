#!/usr/bin/env python3

import math, os.path
import sys
import argparse

from toolbox import *
from toolbox.files import file_groups


def main():
    parser = argparse.ArgumentParser(
        description="Tidy a folder by moving groups of similar files into separate sub-folders",
    )
    parser.add_argument(
        "folder", metavar="path", type=str, help="Folder path to tidy", nargs="?"
    )
    parser.add_argument(
        "-g",
        "--groups",
        action="store_true",
        default=False,
        help="Show file groups information",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        default=False,
        help="List files in groups, don't move them",
    )
    args = parser.parse_args()
    argsd = vars(args)

    if argsd["groups"]:
        for k, v in file_groups.items():
            toolboxprint("Group: %s" % (k), cyan_words=[k])
            s = []
            for e in v:
                s.append(e)
            toolboxprint("  %s" % (" ".join(s)))
        exit()
    dont_move = argsd["list"]

    fs = FileOps(simulate=False, verbose=True, overwrite=False)
    for group in file_groups:
        toolboxprint("Processing file group %s ..." % (group), cyan_words=[group])
        res = fs.get_file_list(argsd["folder"], recursive=False, for_group=group)
        new_dest = argsd["folder"] + os.sep + group
        if len(res):
            if not dont_move:
                fs.make_directory(new_dest, silent=True)
            print("  Found %d files in %s group" % (len(res), group))
            for f in res:
                if dont_move:
                    print("  %s" % (colour_path_str(str(f))))
                else:
                    fs.move_file(f, new_dest)


if __name__ == "__main__":
    main()

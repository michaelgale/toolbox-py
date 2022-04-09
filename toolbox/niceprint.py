#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
# This file is part of the legocad python module.
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Nice (pretty) print helpers
#

import datetime
import sys, os
import os.path
import crayons

from .datautils import get_numbers, get_email_addresses, replace_prov_state_codes

colour_gradient = [
    (5e9, crayons.red, False),
    (2e9, crayons.red, True),
    (1e9, crayons.yellow, True),
    (5e8, crayons.yellow, False),
    (2e8, crayons.green, True),
    (1e8, crayons.green, False),
    (5e7, crayons.cyan, True),
    (2e7, crayons.cyan, False),
    (1e7, crayons.blue, True),
    (5e6, crayons.blue, False),
    (2e6, crayons.magenta, False),
    (0, crayons.black, True),
]
mono_gradient = [
    (1e9, crayons.white, True),
    (2e8, crayons.white, False),
    (5e7, crayons.normal, False),
    (0, crayons.black, True),
]


def file_size_str(size, style=None):
    """Prints a file size in human readable units
    size is assumed to be in bytes
    style is optional and can be "colour" or "mono" for gradient of colour"""
    if size > 1e9:
        s = "%.2f GB" % (size / 1e9)
    elif size > 1e6:
        s = "%.2f MB" % (size / 1e6)
    elif size > 1e3:
        s = "%.2f kB" % (size / 1e3)
    elif size > 0:
        s = "%.0f bytes" % (size)
    else:
        s = "0 bytes"
    if style is not None:
        gradient = colour_gradient if style == "colour" else mono_gradient
        for thr, c, b in gradient:
            if size > thr:
                return c("%10s" % (s), bold=b)
        return s
    else:
        return crayons.white("%10s" % (s))


def _full_path(file):
    """Returns the fully expanded path of a file"""
    if "~" in file:
        return os.path.expanduser(file)
    return os.path.expanduser(os.path.abspath(file))


def _split_path(file):
    """Returns a tuple containing a file's (directory, name.ext)"""
    if os.path.isdir(file):
        return _full_path(file), None
    return os.path.split(_full_path(file))


def colour_path_str(file):
    fp = _full_path(file)
    d, f = _split_path(fp)
    s = []
    if f is not None:
        if len(file) == len(f):
            s.append(str(crayons.cyan(file, bold=True)))
        else:
            idx = file.find(f) - 1
            s.append(str(crayons.blue(file[:idx] + os.sep, bold=True)))
            if os.path.isfile(fp):
                s.append(str(crayons.cyan(f, bold=True)))
            elif os.path.isdir(fp):
                s.append(str(crayons.blue(f, bold=True)))
            else:
                s.append(str(crayons.cyan(f, bold=True)))
    else:
        if os.path.isdir(fp):
            s.append(str(crayons.blue(file + os.sep, bold=True)))
        else:
            s.append(str(crayons.cyan(file, bold=True)))
    return "".join(s)


def progress_bar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


init_time = datetime.datetime.now()
last_time = datetime.datetime.now()


def logmsg(msg, prefix="", level=2, log_output=True, log_level=0):
    """Generic logging message to the console with elaspsed time prefix."""
    if not log_output or log_level < level:
        return

    global init_time
    global last_time
    tnow = datetime.datetime.now()
    tdiff = tnow - init_time
    tstr = str(tdiff)
    s = []
    s.append(str(crayons.blue("%s" % (tstr[2:-3]), bold=False)))
    if len(prefix) > 0:
        s.append(" : %s: " % (prefix))
    else:
        s.append(" : ")
    s.append(msg)
    print("".join(s))


def toolboxprint(
    text,
    green_words=None,
    yellow_words=None,
    red_words=None,
    cyan_words=None,
    magenta_words=None,
    bold_words=None,
):
    """Prints a string with fancy colourization for common items like numbers."""
    s = []
    text = str(text)
    ts = text
    numbers = get_numbers(text)
    emails = get_email_addresses(text)
    gw = green_words if green_words is not None else []
    yw = yellow_words if yellow_words is not None else []
    rw = red_words if red_words is not None else []
    cw = cyan_words if cyan_words is not None else []
    mw = magenta_words if magenta_words is not None else []
    bw = bold_words if bold_words is not None else []
    text = str(text)
    words = text.split()
    n = len(words)
    next_is_currency = False
    replace_dollars = False
    for i, t in enumerate(words):
        if t[0] == "$" and len(t) > 1:
            ts = ts.replace(t, str(crayons.green(str(t), bold=True)))
        elif (i + 1) < n and t == "$":
            if words[i + 1] in numbers:
                replace_dollars = True
                next_is_currency = True
        elif t in numbers:
            if next_is_currency:
                ts = ts.replace(t, str(crayons.green(str(t), bold=True)))
                next_is_currency = False
            else:
                # guard against replacing substrings of numbers by checking for
                # delimiting whitespace
                if i == 0:
                    ts = ts.replace(
                        "%s " % (t), "%s " % (str(crayons.cyan(str(t), bold=True)))
                    )
                elif i == n - 1:
                    ts = ts.replace(
                        " %s" % (t), " %s" % (str(crayons.cyan(str(t), bold=True)))
                    )
                else:
                    s1 = " %s " % (t)
                    s2 = " %s " % (str(crayons.cyan(str(t), bold=True)))
                    ts = ts.replace(s1, s2)
        elif t.startswith("0x"):
            ts = ts.replace(t, str(crayons.magenta(str(t), bold=True)))
        elif "%" in t:
            ts = ts.replace(t, str(crayons.cyan(str(t), bold=True)))
        elif t in emails:
            ts = ts.replace(t, str(crayons.blue(str(t), bold=True)))
        elif t in gw:
            ts = ts.replace(t, str(crayons.green(str(t), bold=False)))
        elif t in yw:
            ts = ts.replace(t, str(crayons.yellow(str(t), bold=False)))
        elif t in rw:
            ts = ts.replace(t, str(crayons.red(str(t), bold=False)))
        elif t in cw:
            ts = ts.replace(t, str(crayons.cyan(str(t), bold=False)))
        elif t in mw:
            ts = ts.replace(t, str(crayons.magenta(str(t), bold=False)))
        elif t in bw:
            ts = ts.replace(t, str(crayons.white(str(t), bold=True)))
    if replace_dollars:
        ds = str(crayons.green(str("$"), bold=True))
        ts = ts.replace("$ ", ds)
    print(ts)

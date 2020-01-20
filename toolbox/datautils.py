#! /usr/bin/env python3
#
# Copyright (C) 2019  Fx Bricks Inc.
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
# Misc data manipulation and validation functions
#


def str_constraint(constraint, check_value, tolerance=0.1):
    """ Validates a numeric constraint described by a string.  The string
    can specify fixed value constraints such as "0.0" or range constraints
    such as "<3.0" or ">=10.0"
    """
    check_greater_eq = True if ">=" in constraint else False
    check_less_eq = True if "<=" in constraint else False
    check_greater = True if ">" in constraint and not check_greater_eq else False
    check_less = True if "<" in constraint and not check_less_eq else False
    value = float(constraint.strip(">").strip("<").strip("="))
    if check_greater:
        if check_value > value:
            return True
    elif check_less:
        if check_value < value:
            return True
    elif check_greater_eq:
        if check_value >= value:
            return True
    elif check_less_eq:
        if check_value <= value:
            return True
    else:
        if abs(check_value - value) < tolerance:
            return True
    return False


def is_valid_value(value, value_constraints, tolerance=0.1):
    """ Validates a length value against one or more constraints.  The
    constraints are specified either as fixed values or with strings which
    specify more complex criteria such as ">2.0".  Multiple constraints are
    specified as a list such as [">0.0", "<15.0"]
    """
    is_valid = True
    if not isinstance(value_constraints, list):
        constraints = [value_constraints]
    else:
        constraints = value_constraints
    for constraint in constraints:
        if isinstance(constraint, str):
            if not str_constraint(constraint, value):
                is_valid = False
        elif not abs(value - constraint) < tolerance:
            is_valid = False
    return is_valid


def are_words_in_word_list(words, word_list, case_sensitive=False):
    """ Checks if word(s) are contained in another word list.
    The search can be performed with or without case sensitivity.
    The check words can contain wildcards, e.g. "abc*" to allow
    a wider range of matches against the word list. """
    if not isinstance(words, list):
        check_words = [words]
    else:
        check_words = words
    found = {}
    for w in check_words:
        word = w.lower() if not case_sensitive else w
        if "*" in word:
            idx = word.find("*") - 1
            word = word[:idx]
    
        for wl in word_list:
            wl = wl.lower() if not case_sensitive else wl
            if wl.startswith(word):
                found[word] = True
    if len(found) == len(check_words):
        return True
    return False

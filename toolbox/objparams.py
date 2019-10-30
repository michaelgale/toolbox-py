#! /usr/bin/env python3
#
# Copyright (C) 2018  Fx Bricks Inc.
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
# Utilities to render keyword arguments in a dictionaries or YML files into
# "dotted" accesible properties for a class
#

import re
import yaml
import inspect
import itertools as it
from metayaml import read


# Dictionary processing based on 3b1b's manim library
#
# caller should use apply_params(self, kwargs, locals())

def get_all_descendent_classes(Class):
    awaiting_review = [Class]
    result = []
    while awaiting_review:
        Child = awaiting_review.pop()
        awaiting_review += Child.__subclasses__()
        result.append(Child)
    return result


def filtered_locals(caller_locals):
    result = caller_locals.copy()
    ignored_local_args = ["self", "kwargs"]
    for arg in ignored_local_args:
        result.pop(arg, caller_locals)
    return result


def apply_params(obj, kwargs, caller_locals={}):
    """
    Sets init args and PARAMS values as local variables
    The purpose of this function is to ensure that all
    configuration of any object is inheritable, able to
    be easily passed into instantiation, and is attached
    as an attribute of the object.
    """

    # Assemble list of PROPERTIES from all super classes
    classes_in_hierarchy = [obj.__class__]
    static_configs = []
    while len(classes_in_hierarchy) > 0:
        Class = classes_in_hierarchy.pop()
        classes_in_hierarchy += Class.__bases__
        if hasattr(Class, "PARAMS"):
            static_configs.append(Class.PARAMS)

    # Order matters a lot here, first dicts have higher priority
    caller_locals = filtered_locals(caller_locals)
    all_dicts = [kwargs, caller_locals, obj.__dict__]
    all_dicts += static_configs
    obj.__dict__ = merge_dicts_recursively(*reversed(all_dicts))


def merge_dicts_recursively(*dicts):
    """
    Creates a dict whose keyset is the union of all the
    input dictionaries.  The value for each key is based
    on the first dict in the list with that key.
    dicts later in the list have higher priority
    When values are dictionaries, it is applied recursively
    """
    result = dict()
    all_items = it.chain(*[d.items() for d in dicts])
    for key, value in all_items:
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_recursively(result[key], value)
        else:
            result[key] = value
    return result


def soft_dict_update(d1, d2):
    """
    Adds key values pairs of d2 to d1 only when d1 doesn't
    already have that key
    """
    for key, value in list(d2.items()):
        if key not in d1:
            d1[key] = value


def digest_locals(obj, keys=None):
    caller_locals = filtered_locals(
        inspect.currentframe().f_back.f_locals
    )
    if keys is None:
        keys = list(caller_locals.keys())
    for key in keys:
        setattr(obj, key, caller_locals[key])


class Params(dict):
    """A deserialization of a YAML file for . and [] access
    based on https://github.com/swolebro/caddyshack"""

    def __convert(self, s, baseunit="mm", **kwargs):
        """Handle conversion of number strings ending with "in", "mm", "studs" or "%".
        If a baseunit is provided, force values for in or mm to that unit;
        if not provided, return the float without scaling. Always return non-number
        strings unchanged and percentages in their decimal form.
        """

        match = re.search(r'([\d.]+)\s*(\S*)', s)
        if match is None or match.group(2) not in ['in', 'mm', '%', "studs"]:
            return s

        val, unit = match.groups()

        val = float(val)
        if unit == '%':
            return val/100

        if baseunit is None:
            return val

        if unit == 'mm' and baseunit == "studs":
            return val/8.0

        if unit == "in" and baseunit == "studs":
            return val * 25.4 / 8.0

        if unit == 'in' and baseunit == "mm":
            return val * 25.4

        if unit == "studs" and baseunit == "mm":
            return val * 8.0

        if unit == "studs" and baseunit == "in":
            return val * 8.0 / 25.4

        if unit == "mm" and baseunit == "in":
            return val / 25.4


        return val


    def __init__(self, yml=None, *, obj=None, **kwargs):
        """Given a YAML file that's a toplevel list or dict,
        this turns it into nested Params all the way down.

        The other args and kwargs are for internal use with recursion.
        """

        self.__dict__ = self
        if yml is not None:
            if isinstance(yml, list):
                obj = read(yml)
            else:
                obj = read([yml])

            kwargs = obj

        for k, v in list(obj.items()):
            if isinstance(v, str):
                obj[k] = self.__convert(v, **kwargs)

            if isinstance(v, dict):
                obj[k] = Params(obj=v, **kwargs)

        self.update(obj)

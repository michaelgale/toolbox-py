#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Learn more: https://github.com/michaelgale/toolbox-py

import os
import sys
import setuptools

PACKAGE_NAME = 'toolbox'
MINIMUM_PYTHON_VERSION = '3.6'

def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {0}+ is required.".format(MINIMUM_PYTHON_VERSION))


def read_package_variable(key, filename='__init__.py'):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, filename)
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ', 2)
            if parts[:-1] == [key, '=']:
                return parts[-1].strip("'")
    sys.exit("'{0}' not found in '{1}'".format(key, module_path))


def build_description():
    """Build a description for the project from documentation files."""
    try:
        readme = open("README.rst").read()
        changelog = open("CHANGELOG.rst").read()
    except IOError:
        return "<placeholder>"
    else:
        return readme + '\n' + changelog


# check_python_version()

setuptools.setup(
    name=read_package_variable('__project__'),
    version=read_package_variable('__version__'),
    description="A general purpose collection of useful python tools and utility functions.",
    url='https://github.com/michaelgale/toolbox-py',
    author='Michael Gale',
    author_email='michael@fxbricks.com',
    packages=setuptools.find_packages(),
    long_description=build_description(),
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
    ],
    install_requires=[
        'jinja2 >= 2.10, <3',
        'metayaml',
        'crayons',
        'pycountry',
    ],
    scripts=['toolbox/scripts/foldercheck.py'],
    # entry_points = {
    #         'scripts': [ 'foldercheck=scripts:foldercheck.py',                  
    #         ],              
    #     },    
)

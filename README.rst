toolbox-py
==========

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://github.com/michaelgale/toolbox-py/blob/master/LICENSE.md

A general purpose collection of useful python tools and utility functions.

Functionality
-------------

**File Utilities**

- ``FileOps`` class acts as an abstract agent to access your file system. 
- Utility functions: ``full_path``, ``split_path``, ``split_filename``

**Data Utilities**

- Various text and data validation and parsing functions

**Parameter Container Class**

- ``Params`` class to hold parameters as attributes in a class with dotted access. Can be initialized with an input YAML file with nested hierarchy.
- ``apply_params`` merges object dictionaries and optional local parameters stored in a dictionary called "PARAMS".  This allows parameter data for an object to be inheritable, able to be easily passed into instantiation, and be attached as an attribute of the object.

**Geometry Classes**

- ``Vector``, ``Vector2D``, ``Matrix`` classes for simple linear algrebra operations with vectors
- ``Point`` - general purpose 2D point class
- ``Rect`` - general purpose 2D rectangle class and utility functions

**Foldercheck utility**

Simple command line utility to summarize the contents of a folder tree. Summary includes file count, file size, and grouped categories of files by both extension and category (e.g. images, source code, etc.)


Installation
------------

The **toolbox** package can be installed directly from the source code:

.. code-block:: shell

    $ git clone https://github.com/michaelgale/toolbox-py.git
    $ cd toolbox-py
    $ python setup.py install

Usage
-----

After installation, the package can imported:

.. code-block:: shell

    $ python
    >>> import toolbox
    >>> toolbox.__version__

An example of the package can be seen below

.. code-block:: python

    from toolbox import Params
    tp = Params(yml="test_params.yml")
    print(tp)


Requirements
^^^^^^^^^^^^

* Python 3.6+
* metayaml
* crayons


Authors
-------

`toolbox-py` was written by `Michael Gale <michael@fxbricks.com>`_.

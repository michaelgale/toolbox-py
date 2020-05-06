"""toolbox - A general purpose collection of useful python tools and utility functions."""

import os

__project__ = 'toolbox'
__version__ = '0.1.0'

VERSION = __project__ + '-' + __version__

script_dir = os.path.dirname(__file__)

from .objparams import apply_params
from .objparams import Params
from .files import SuppressStdoutStderr, full_path, split_path, FileOps
from .datautils import *
from .scripts import foldercheck
from .niceprint import file_size_str, colour_path_str

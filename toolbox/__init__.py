"""toolbox - A general purpose collection of useful python tools and utility functions."""

import os

# fmt: off
__project__ = 'toolbox'
__version__ = '0.5.0'
# fmt: on

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

from .objparams import apply_params
from .objparams import Params, convert_value_with_unit
from .files import SuppressStdoutStderr, full_path, split_path, split_filename, FileOps
from .datautils import *
from .scripts import foldercheck
from .niceprint import file_size_str, colour_path_str

from .geometry.vector import *
from .geometry.point import (
    Point,
    grid_points_2d,
    grid_points_at_height,
    points2d_at_height,
    centroid_of_points,
)
from .geometry.rect import Rect

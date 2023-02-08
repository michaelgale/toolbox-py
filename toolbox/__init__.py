"""toolbox - A general purpose collection of useful python tools and utility functions."""

import os

# fmt: off
__project__ = 'toolbox'
__version__ = '0.7.0'
# fmt: on

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

from .constants import *
from .objparams import apply_params
from .objparams import Params, convert_value_with_unit
from .files import SuppressStdoutStderr, full_path, split_path, split_filename, FileOps
from .datautils import *
from .imageutils import ImageMixin
from .scripts import foldercheck
from .niceprint import (
    file_size_str,
    colour_path_str,
    progress_bar,
    logmsg,
    toolboxprint,
)

from .geometry.vector import *
from .geometry.point import (
    Point,
    grid_points_2d,
    grid_points_at_height,
    translate_points,
    points2d_at_height,
    centroid_of_points,
    discretize_line,
    discretize_polyline,
    polyline_length,
)
from .geometry.rect import *
from .geometry.layout import *

from .geometry.animators import *

"""toolbox - A general purpose collection of useful python tools and utility functions."""

import os

__project__ = 'toolbox'
__version__ = '0.5.0'

VERSION = __project__ + '-' + __version__

script_dir = os.path.dirname(__file__)

from .objparams import apply_params
from .objparams import Params
from .files import SuppressStdoutStderr, full_path, split_path, FileOps
from .datautils import *
from .scripts import foldercheck
from .niceprint import file_size_str, colour_path_str

from .geometry.vector import Vector, Vector2D, Matrix, euler_to_rot_matrix, safe_vector
from .geometry.point import Point, grid_points_2d, grid_points_at_height, points2d_at_height
from .geometry.rect import Rect

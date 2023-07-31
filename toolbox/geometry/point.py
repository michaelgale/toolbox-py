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
# Geometry / Point Class
#

import copy
import math
from math import sin, cos, radians, sqrt, atan, degrees, atan2, hypot
from numbers import Number
from functools import reduce


class Point:

    __slots__ = ("x", "y")

    def __init__(self, x=0.0, y=None):
        if isinstance(x, (tuple, list)):
            if isinstance(x, list) and isinstance(x[0], tuple):
                self.x = x[0][0]
                self.y = x[0][1]
            else:
                self.x = x[0]
                self.y = x[1]
        if isinstance(x, Point):
            self.x = x.x
            self.y = x.y
        elif y is not None:
            self.x = x
            self.y = y

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return self.length_squared() < other.length_squared()

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, p):
        """Point(x1+x2, y1+y2)"""
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        """Point(x1-x2, y1-y2)"""
        return Point(self.x - p.x, self.y - p.y)

    def __mul__(self, scalar):
        """Point(x1*x2, y1*y2)"""
        return Point(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        """Point(x1/x2, y1/y2)"""
        return Point(self.x / scalar, self.y / scalar)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.x if key == 0 else self.y

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if key == 0:
                self.x = value
            else:
                self.y = value

    def __str__(self):
        if isinstance(self.x, float):
            return "(%.2f, %.2f)" % (self.x, self.y)
        else:
            return "(%s, %s)" % (self.x, self.y)

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)

    def strspc(self):
        if isinstance(self.x, float):
            return "(%.3f %.3f)" % (self.x, self.y)
        else:
            return "(%s %s)" % (self.x, self.y)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def length_squared(self):
        return self.x ** 2 + self.y ** 2

    def distance_to(self, p):
        """Calculate the distance between two points."""
        return (self - p).length()

    def as_tuple(self):
        """(x, y)"""
        return (self.x, self.y)

    def swapped(self):
        return (self.y, self.x)

    def clone(self):
        """Return a full copy of this point."""
        return Point(self.x, self.y)

    def integerize(self):
        """Convert co-ordinate values to integers."""
        self.x = int(self.x)
        self.y = int(self.y)

    def floatize(self):
        """Convert co-ordinate values to floats."""
        self.x = float(self.x)
        self.y = float(self.y)

    def move_to(self, x, y):
        """Reset x & y coordinates."""
        self.x = x
        self.y = y

    def translate(self, x, y=None):
        """Move to new (x+dx,y+dy)."""
        if isinstance(x, (tuple, Point, list)):
            dx, dy = x[0], x[1]
        elif y is not None:
            dx, dy = x, y
        else:
            dx, dy = x, x
        self.x = self.x + dx
        self.y = self.y + dy

    def get_translated(self, x, y=None):
        if isinstance(x, (tuple, Point, list)):
            return (self.x + x[0], self.y + x[1])
        elif y is not None:
            return (self.x + x, self.y + y)
        return self.x + x, self.y + x

    def mirror_y(self):
        self.y = -self.y

    def mirror_x(self):
        self.x = -self.x

    def rotate(self, rad):
        """Rotate counter-clockwise by rad radians.

        Positive y goes *up,* as in traditional mathematics.

        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.

        The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c * self.x - s * self.y, s * self.x + c * self.y)
        return Point(x, y)

    def rotate_about(self, p, theta):
        """Rotate counter-clockwise around a point, by theta degrees.

        Positive y goes *up,* as in traditional mathematics.

        The new position is returned as a new Point.
        """
        result = self.clone()
        result.translate(-p.x, -p.y)
        result.rotate(theta)
        result.translate(p.x, p.y)
        return result


def points2d_at_height(pts, height):
    """Returns a list of 2D point tuples as 3D tuples at height"""
    if isinstance(pts, tuple):
        if len(pts) == 2:
            return [(*pts, height)]
        return [(pts[0], pts[1], height)]
    pts3d = []
    for pt in pts:
        if len(pt) == 3:
            pts3d.append((pt[0], pt[1], height))
        else:
            pts3d.append((*pt, height))
    return pts3d


def grid_points_2d(length, width, div, width_div=None):
    """Returns a regularly spaced grid of points occupying a rectangular
    region of length x width partitioned into div intervals.  If different
    spacing is desired in width, then width_div can be specified, otherwise
    it will default to div. If div < 2 in either x or y, then the corresponding
    coordinate will be set to length or width respectively."""
    if div > 1:
        px = [-length / 2.0 + (x / (div - 1)) * length for x in range(div)]
    else:
        px = [length]
    if width_div is not None:
        wd = width_div
    else:
        wd = div
    if wd > 1:
        py = [-width / 2.0 + (y / (wd - 1)) * width for y in range(wd)]
    else:
        py = [width]
    return [(x, y) for x in px for y in py]


def translate_points(pts, dx, dy=None):
    if isinstance(dx, (tuple, list)):
        xo, yo = dx[0], dx[1]
    elif isinstance(dx, Point):
        xo, yo = dx.x, dx.y
    elif dy is not None:
        xo, yo = dx, dy
    else:
        xo, yo = dx, dx
    new_pts = []
    for pt in pts:
        np = Point(pt)
        np.translate(xo, yo)
        new_pts.append(np.as_tuple())
    return new_pts


def grid_points_at_height(length, width, height, div, width_div=None):
    """A convenience method to return 2D grid points as 3D points at
    a specified height"""
    pts = grid_points_2d(length, width, div, width_div)
    return points2d_at_height(pts, height)


def centroid_of_points(pts):
    """Returns the centroid of a cluster of points. Automatically
    works with either 2D or 3D point tuples."""
    xs, ys, zs = 0, 0, 0
    for pt in pts:
        xs += pt[0]
        ys += pt[1]
        if len(pt) > 2:
            zs += pt[2]
    if len(pts) > 0:
        xs /= len(pts)
        ys /= len(pts)
        if len(pts[0]) > 2:
            zs /= len(pts)
            return xs, ys, zs
    return xs, ys


def discretize_line(p0, p1, segments):
    """Breaks up a line defined by points p0 and p1 into a number of
    specified segments.
    If segments is a scalar value, then the line is partitioned into
    the number of segments.
    If segments is a list, then each list value specifies a
    normalized portion of the length of the line. e.g. [0.1, 0.5] would
    request segments of 10%, 50% of the line length.
    Returns the vertices of segments of discretized line."""
    p0, p1 = Point(p0), Point(p1)
    dx, dy = p1.x - p0.x, p1.y - p0.y
    vtx = [Point(p0).as_tuple()]
    if isinstance(segments, list):
        for ds in segments:
            x0 = p0.x + ds * dx
            y0 = p0.y + ds * dy
            vtx.append((x0, y0))
        return vtx
    for i in range(segments):
        ds = (i + 1) / segments
        x0 = p0.x + ds * dx
        y0 = p0.y + ds * dy
        vtx.append((x0, y0))
    return vtx


def polyline_length(pts):
    """Computes the length of polyline."""
    total_length = 0
    p0 = Point(pts[0])
    for p in pts[1:]:
        p1 = Point(p)
        total_length += p0.distance_to(p1)
        p0 = p1
    return total_length


def discretize_polyline(pts, segments, keep_all_pts=True):
    """Breaks up a polyline defined by points pts into a number of
    specified segments.
    If segments is a scalar value, then the polyline is partitioned into
    the number of segments.
    If segments is a list, then each list value specifies a
    normalized portion of the total length of the polyline. e.g. [0.1, 0.5]
    would request segments of 10%, 50% of the line length.
    Returns the vertices of segments of discretized line."""
    total_length = polyline_length(pts)
    lines = []
    p0 = Point(pts[0])
    inc_length = 0
    for p in pts[1:]:
        p1 = Point(p)
        line_length = p0.distance_to(p1)
        lines.append((p0, p1, line_length, inc_length))
        inc_length += line_length
        p0 = p1
    if isinstance(segments, (int, float)):
        segments = [(x + 1) / segments for x in list(range(int(segments)))]
    vtx = [Point(pts[0]).as_tuple()]
    num_segments = len(segments)
    for i, segment in enumerate(segments):
        ds = segment * total_length
        i_1 = i + 1
        for line in lines:
            if ds <= (line[2] + line[3]):
                dl = (ds - line[3]) / line[2]
                v = discretize_line(line[0], line[1], [dl])
                vtx.append(v[1])
                if i_1 < num_segments and keep_all_pts:
                    dn = (segments[i_1]) * total_length
                    if (dn - line[3]) / line[2] > 1.0:
                        vtx.append(line[1])
                break
    return vtx

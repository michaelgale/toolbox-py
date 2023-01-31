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
# Geometry / Rect (rectangle) Class
#

import copy
import math
from math import sin, cos, radians, sqrt, atan, degrees, atan2, hypot
from numbers import Number
from functools import reduce

from .point import Point


class Rect:
    """2D Rectangle class"""

    __slots__ = ("width", "height", "left", "right", "top", "bottom", "bottom_up")

    def __init__(self, width=2.0, height=2.0, bottomUp=False):
        self.bottom_up = bottomUp
        self.left = -width / 2.0
        self.right = width / 2.0
        if bottomUp:
            self.top = -height / 2.0
            self.bottom = height / 2.0
        else:
            self.top = height / 2.0
            self.bottom = -height / 2.0
        self.width = abs(self.right - self.left)
        self.height = abs(self.top - self.bottom)

    def __str__(self):
        return "<Rect (%.2f,%.2f)-(%.2f,%.2f) w=%.2f h=%.2f>" % (
            self.left,
            self.top,
            self.right,
            self.bottom,
            self.width,
            self.height,
        )

    def __repr__(self):
        return "%s(%r, %r)" % (
            self.__class__.__name__,
            Point(self.left, self.top),
            Point(self.right, self.bottom),
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (
            self.width == other.width
            and self.height == other.height
            and self.left == other.left
            and self.top == other.top
            and self.right == other.right
            and self.bottom == other.bottom
            and self.bottom_up == other.bottom_up
        )

    def __lt__(self, other):
        return self.area < other.area

    def __hash__(self):
        return hash(
            (
                self.width,
                self.height,
                self.left,
                self.top,
                self.right,
                self.bottom,
                self.bottom_up,
            )
        )

    def copy(self):
        r = Rect(self.width, self.height)
        r.left, r.right = self.left, self.right
        r.top, r.bottom = self.top, self.bottom
        r.bottom_up = self.bottom_up
        return r

    @property
    def area(self):
        return self.width * self.height

    @property
    def perimeter(self):
        return 2 * self.width + 2 * self.height

    @property
    def size(self):
        return self.get_size()

    def get_size(self):
        self.width = abs(self.right - self.left)
        self.height = abs(self.top - self.bottom)
        return self.width, self.height

    @property
    def centre(self):
        return self.get_centre()

    def get_centre(self):
        x = self.left + self.width / 2
        if self.bottom_up:
            y = self.top + self.height / 2
        else:
            y = self.top - self.height / 2
        return x, y

    def iter_points(self):
        for pt in self.get_pts():
            yield pt

    def get_pts(self):
        return [
            (self.left, self.top),
            (self.right, self.top),
            (self.left, self.bottom),
            (self.right, self.bottom),
        ]

    def get_pts_3d(self, height=0):
        return [
            (self.left, self.top, height),
            (self.right, self.top, height),
            (self.left, self.bottom, height),
            (self.right, self.bottom, height),
        ]

    def move_to(self, pt, py=None):
        if isinstance(pt, Point):
            (x, y) = pt.as_tuple()
        elif isinstance(pt, tuple):
            x, y = pt[0], pt[1]
        else:
            x, y = pt, py
        self.left = x - self.width / 2
        self.right = x + self.width / 2
        if self.bottom_up:
            self.top = y - self.height / 2
            self.bottom = y + self.height / 2
        else:
            self.top = y + self.height / 2
            self.bottom = y - self.height / 2

    @property
    def top_left(self):
        return self.get_top_left()

    def get_top_left(self):
        return (self.left, self.top)

    @property
    def bottom_left(self):
        return self.get_bottom_left()

    def get_bottom_left(self):
        return (self.left, self.bottom)

    @property
    def top_right(self):
        return self.get_top_right()

    def get_top_right(self):
        return (self.right, self.top)

    @property
    def bottom_right(self):
        return self.get_bottom_right()

    def get_bottom_right(self):
        return (self.right, self.bottom)

    def get_anchor_pt(self, anchor_pt):
        if "left_quarter" in anchor_pt:
            x = self.left + self.width / 4
        elif "right_quarter" in anchor_pt:
            x = self.right - self.width / 4
        elif "left" in anchor_pt:
            x = self.left
        elif "right" in anchor_pt:
            x = self.right
        elif any(e in anchor_pt for e in ["center", "centre", "mid_width"]):
            x = self.left + self.width / 2
        else:
            x = self.left
        if "top_quarter" in anchor_pt:
            y = self.top - self.height / 4
        elif "bottom_quarter" in anchor_pt:
            y = self.bottom + self.height / 4
        elif "top" in anchor_pt:
            y = self.top
        elif "bottom" in anchor_pt:
            y = self.bottom
        elif any(e in anchor_pt for e in ["center", "centre", "mid_height"]):
            y = self.top - self.height / 2
        else:
            y = self.top
        return x, y

    def _xy_from_pt(self, pt):
        if isinstance(pt, Point):
            (x, y) = pt.as_tuple()
        else:
            x, y = pt[0], pt[1]
        return x, y

    def move_top_left_to(self, pt):
        x, y = self._xy_from_pt(pt)
        self.left = x
        self.right = x + self.width
        self.top = y
        if self.bottom_up:
            self.bottom = y + self.height
        else:
            self.bottom = y - self.height

    def move_top_right_to(self, pt):
        x, y = self._xy_from_pt(pt)
        self.right = x
        self.left = x - self.width
        self.top = y
        if self.bottom_up:
            self.bottom = y + self.height
        else:
            self.bottom = y - self.height

    def move_bottom_left_to(self, pt):
        x, y = self._xy_from_pt(pt)
        self.left = x
        self.right = x + self.width
        self.bottom = y
        if self.bottom_up:
            self.top = y - self.height
        else:
            self.top = y + self.height

    def move_bottom_right_to(self, pt):
        x, y = self._xy_from_pt(pt)
        self.right = x
        self.left = x - self.width
        self.bottom = y
        if self.bottom_up:
            self.top = y - self.height
        else:
            self.top = y + self.height

    def set_points(self, pt1, pt2):
        """Reset the rectangle coordinates."""
        x1, y1 = self._xy_from_pt(pt1)
        x2, y2 = self._xy_from_pt(pt2)
        self.left = min(x1, x2)
        self.right = max(x1, x2)
        if self.bottom_up:
            self.top = min(y1, y2)
            self.bottom = max(y1, y2)
        else:
            self.top = max(y1, y2)
            self.bottom = min(y1, y2)
        self.width = abs(x2 - x1)
        self.height = abs(y2 - y1)

    def bounding_rect(self, pts):
        """Makes a bounding rect from the extents of a list of points
        or a list of rects"""
        if len(pts) == 0:
            return None
        bx = []
        by = []
        for pt in pts:
            if isinstance(pt, Point):
                (x, y) = pt.as_tuple()
            elif isinstance(pt, Rect):
                x, y = pt.left, pt.top
                bx.append(x)
                by.append(y)
                x, y = pt.right, pt.bottom
            else:
                x, y = pt[0], pt[1]
            bx.append(x)
            by.append(y)
        self.left = min(bx)
        self.right = max(bx)
        if self.bottom_up:
            self.top = min(by)
            self.bottom = max(by)
        else:
            self.top = max(by)
            self.bottom = min(by)
        self.width = abs(self.right - self.left)
        self.height = abs(self.top - self.bottom)

    def set_size(self, width, height):
        """Sets a new size for the rectangle."""
        self.left = -width / 2
        self.right = width / 2
        if self.bottom_up:
            self.top = -height / 2
            self.bottom = height / 2
        else:
            self.top = height / 2
            self.bottom = -height / 2
        self.width = width
        self.height = height

    def set_size_anchored(self, width, height, anchor_pt="centre centre"):
        """Sets a new size for the rectangle and optionally anchors the
        rectangle to any one of 10 points specified with a string containing
        anchor point description, e.g. 'top left', 'right', 'bottom centre'"""
        if "left_quarter" in anchor_pt:
            x1 = self.left + self.width / 4
            x2 = x1 + width
        elif "right_quarter" in anchor_pt:
            x1 = self.right - self.width / 4
            x2 = x1 + width
        elif "left" in anchor_pt:
            x1 = self.left
            x2 = self.left + width
        elif "right" in anchor_pt:
            x1 = self.right
            x2 = self.right - width
        elif any(e in anchor_pt for e in ["centre", "center", "mid_width"]):
            x1 = self.left + self.width / 2 - width / 2
            x2 = self.right - self.width / 2 + width / 2
        else:
            x1 = self.left
            x2 = self.left + width

        if "top_quarter" in anchor_pt:
            y1 = self.top - self.height / 4
            y2 = y1 - height
        elif "bottom_quarter" in anchor_pt:
            y1 = self.bottom + self.height / 4
            y2 = y1 + height
        elif "top" in anchor_pt:
            y1 = self.top
            y2 = self.top - height
        elif "bottom" in anchor_pt:
            y1 = self.bottom
            y2 = self.bottom + height
        elif any(e in anchor_pt for e in ["centre", "center", "mid_height"]):
            y1 = self.top - self.height / 2 + height / 2
            y2 = self.bottom + self.height / 2 - height / 2
        else:
            y1 = self.top
            y2 = self.top - height

        if self.bottom_up:
            y1, y2 = y2, y1
        self.set_points((x1, y1), (x2, y2))

    def anchor_to_pt(self, rect, from_pt="centre centre", to_pt="centre centre"):
        """Moves a rectangle from its anchor point to another rectangle's
        anchor point. Example: "top right" to "bottom left" """
        x, y = rect.get_anchor_pt(to_pt)
        if "left_quarter" in from_pt:
            x1 = x - self.width / 4
            x2 = max(x, self.right) if "resize" in to_pt else x1 + self.width
        elif "right_quarter" in from_pt:
            x1 = x + self.width / 4
            x2 = max(x, self.right) if "resize" in to_pt else x1 + self.width
        elif "left" in from_pt:
            x1 = x
            x2 = max(x, self.right) if "resize" in to_pt else x1 + self.width
        elif "right" in from_pt:
            x2 = x
            x1 = min(self.left, x) if "resize" in to_pt else x2 - self.width
        elif any(e in from_pt for e in ["centre", "center", "mid_width"]):
            x1 = x - self.width / 2
            x2 = x1 + self.width
        else:
            x1 = self.left
            x2 = self.right

        if "top_quarter" in from_pt:
            y1 = y + self.height * 0.75
            y2 = min(y, self.bottom) if "resize" in to_pt else y1 - self.height
        elif "bottom_quarter" in from_pt:
            y1 = y + self.height / 4
            y2 = min(y, self.bottom) if "resize" in to_pt else y1 - self.height
        elif "top" in from_pt:
            y1 = y
            y2 = min(y, self.bottom) if "resize" in to_pt else y1 - self.height
        elif "bottom" in from_pt:
            y2 = y
            y1 = max(self.top, y) if "resize" in to_pt else y2 + self.height
        elif any(e in from_pt for e in ["centre", "center", "mid_height"]):
            y1 = y + self.height / 2
            y2 = y1 - self.height
        else:
            y1 = self.top
            y2 = self.bottom

        if self.bottom_up:
            y1, y2 = min(y2, y1), max(y2, y1)
        self.set_points((x1, y1), (x2, y2))

    def anchor_to_rect(self, rect, anchor_pt="centre centre"):
        """Moves rectangle to an anchor reference of another rectangle.
        'top left' moves this rectangle to the other rectangle's top left
        for example."""
        self.anchor_to_pt(rect, anchor_pt, anchor_pt)

    def anchor_with_constraint(self, rect, constraint):
        """Moves a rectangle from its anchor point to another rectangle's
        anchor point. Example: "top right to bottom left" or "below" """
        c = constraint.lower()
        if c == "below":
            self.anchor_to_pt(rect, from_pt="top", to_pt="bottom")
        elif c == "above":
            self.anchor_to_pt(rect, from_pt="bottom", to_pt="top")
        elif c == "rightof":
            self.anchor_to_pt(rect, from_pt="left", to_pt="right")
        elif c == "leftof":
            self.anchor_to_pt(rect, from_pt="right", to_pt="left")
        elif c == "middleof":
            self.anchor_to_pt(rect, from_pt="centre", to_pt="centre")
        else:
            c = constraint.split()
            cu = []
            for e in c:
                if e.lower() == "to":
                    cu.append("TO")
                else:
                    cu.append(e.lower())
            c = " ".join(cu)
            c = c.split("TO")
            if len(c) == 2:
                self.anchor_to_pt(rect, from_pt=c[0], to_pt=c[1])

    def shove_with_constraint(self, other, constraint):
        """Shoves a rectangle if it violates an overlapping constraint from
        another rectangle. Constraints can be:
        - left_bound, right_bound, top_bound, bottom_bound
        """
        c = constraint.lower().split("_")
        if "bound" not in c:
            return
        if c[0] == "left":
            if self.left - other.right < 0:
                self.anchor_to_pt(other, from_pt="left", to_pt="right")
        elif c[0] == "right":
            if other.left - self.right < 0:
                self.anchor_to_pt(other, from_pt="right", to_pt="left")
        elif c[0] == "top":
            if other.bottom - self.top < 0:
                self.anchor_to_pt(other, from_pt="top", to_pt="bottom")
        elif c[0] == "bottom":
            if self.bottom - other.top < 0:
                self.anchor_to_pt(other, from_pt="bottom", to_pt="top")

    def contains(self, pt):
        """Return true if a point is inside the rectangle."""
        x, y = self._xy_from_pt(pt)
        if self.left <= x <= self.right:
            if not self.bottom_up:
                if self.bottom <= y <= self.top:
                    return True
            else:
                if self.top <= y <= self.bottom:
                    return True
        return False

    def overlaps(self, other):
        """Return true if a rectangle overlaps this rectangle."""
        if self.bottom_up:
            return (
                self.right > other.left
                and self.left < other.right
                and self.top < other.bottom
                and self.bottom > other.top
            )
        else:
            return (
                self.right > other.left
                and self.left < other.right
                and self.top > other.bottom
                and self.bottom < other.top
            )

    def expanded_by(self, n):
        """Return a rectangle with extended borders.
        Create a new rectangle that is wider and taller than the
        immediate one. All sides are extended by "n" points.
        """
        p1 = Point(self.left - n, self.top + n)
        p2 = Point(self.right + n, self.bottom - n)
        r = Rect()
        r.set_points(p1, p2)
        return r

    @staticmethod
    def bounding_rect_from_rects(rects):
        r = Rect()
        r.bounding_rect(rects)
        return r

    @staticmethod
    def layout_rects(
        rects,
        bounds,
        row_wise=True,
        vert_align="top",
        horz_align="left",
        auto_adjust=True,
        align_cols=False,
        **kwargs,
    ):
        from .layout import RectLayout

        if not "strategy" in kwargs:
            if auto_adjust:
                kwargs["strategy"] = "resize"
            else:
                kwargs["strategy"] = "none"
        r = RectLayout(copy.deepcopy(rects))
        r.set_vert_align(vert_align)
        r.set_horz_align(horz_align)
        r.optimize_layout(
            bounds=bounds,
            col_wise=not row_wise,
            hard_bounds_limit=True,
            grid_align=align_cols,
            **kwargs,
        )
        return [rect.as_rect() for rect in r.iter_assigned()]


class RectCell(Rect):
    """A subclass of Rect which has extra meta information.
    In addition to the attributes of Rect, this class has additional meta data associated with
    a rectangle such as: row and column membership, horizontal and vertical alignment
    """

    __slots__ = ("row", "col", "horz_align", "vert_align")

    def __init__(self, width=2.0, height=2.0, bottomUp=False, **kwargs):
        super().__init__(width, height, bottomUp=bottomUp)
        self.row = None
        self.col = None
        self.horz_align = "left"
        self.vert_align = "top"
        for k, v in kwargs.items():
            if k == "row":
                self.row = kwargs["row"]
            elif k == "col":
                self.col = kwargs["col"]
            elif k == "horz_align":
                self.horz_align = kwargs["horz_align"]
            elif k == "vert_align":
                self.vert_align = kwargs["vert_align"]

    def __str__(self):
        return (
            "<Rect (%.2f,%.2f)-(%.2f,%.2f) w=%.2f h=%.2f> row=%s col=%s ha=%s va=%s"
            % (
                self.left,
                self.top,
                self.right,
                self.bottom,
                self.width,
                self.height,
                self.row,
                self.col,
                self.horz_align,
                self.vert_align,
            )
        )

    def as_rect(self):
        r = Rect(self.width, self.height)
        r.left = self.left
        r.right = self.right
        r.top = self.top
        r.bottom = self.bottom
        r.bottom_up = self.bottom_up
        return r

    @classmethod
    def from_rect(cls, rect):
        r = cls()
        r.left = rect.left
        r.right = rect.right
        r.top = rect.top
        r.bottom = rect.bottom
        r.bottom_up = rect.bottom_up
        r.width = rect.width
        r.height = rect.height
        return r

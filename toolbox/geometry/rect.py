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
    """ 2D Rectangle class """

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

    def copy(self):
        r = Rect(self.width, self.height)
        r.left, r.right = self.left, self.right
        r.top, r.bottom = self.top, self.bottom
        r.bottom_up = self.bottom_up
        return r

    def get_size(self):
        self.width = abs(self.right - self.left)
        self.height = abs(self.top - self.bottom)
        return self.width, self.height

    def get_centre(self):
        x = self.left + self.width / 2
        if self.bottom_up:
            y = self.top + self.height / 2
        else:
            y = self.top - self.height / 2
        return x, y

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

    def get_top_left(self):
        return (self.left, self.top)

    def get_bottom_left(self):
        return (self.left, self.bottom)

    def get_top_right(self):
        return (self.right, self.top)

    def get_bottom_right(self):
        return (self.right, self.bottom)

    def get_anchor_pt(self, anchor_pt):
        if "left" in anchor_pt:
            x = self.left
        elif "right" in anchor_pt:
            x = self.right
        else:
            x = self.left + self.width / 2
        if "top" in anchor_pt:
            y = self.top
        elif "bottom" in anchor_pt:
            y = self.bottom
        else:
            y = self.top - self.height / 2
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
        or a list of rects """
        if len(pts) == 0:
            return
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
        anchor point description, e.g. 'top left', 'right', 'bottom centre' """
        if "left" in anchor_pt:
            x1 = self.left
            x2 = self.left + width
        elif "right" in anchor_pt:
            x1 = self.right
            x2 = self.right - width
        else:
            x1 = self.left + self.width / 2 - width / 2
            x2 = self.right - self.width / 2 + width / 2
        if "top" in anchor_pt:
            y1 = self.top
            y2 = self.top - height
        elif "bottom" in anchor_pt:
            y1 = self.bottom
            y2 = self.bottom + height
        else:
            y1 = self.top - self.height / 2 + height / 2
            y2 = self.bottom + self.height / 2 - height / 2
        if self.bottom_up:
            y1, y2 = y2, y1
        self.set_points((x1, y1), (x2, y2))

    def anchor_to_pt(self, rect, from_pt="centre centre", to_pt="centre centre"):
        """Moves a rectangle from its anchor point to another rectangle's 
        anchor point. Example: "top right" to "bottom left" """
        x, y = rect.get_anchor_pt(to_pt)
        if "left" in from_pt:
            x1 = x
            x2 = max(x, self.right) if "resize" in to_pt else x1 + self.width
        elif "right" in from_pt:
            x2 = x
            x1 = min(self.left, x) if "resize" in to_pt else x2 - self.width
        elif "centre" in from_pt or "center" in from_pt:
            x1 = x - self.width / 2
            x2 = x1 + self.width
        else:
            x1 = self.left
            x2 = self.right
        if "top" in from_pt:
            y1 = y
            y2 = min(y, self.bottom) if "resize" in to_pt else y1 - self.height
        elif "bottom" in from_pt:
            y2 = y
            y1 = max(self.top, y) if "resize" in to_pt else y2 + self.height
        elif "centre" in from_pt or "center" in from_pt:
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
    ):
        def dict_idx(row, col):
            return "%d_%d" % (row, col)

        def compute_wasted_space(rd, row_wise=True):
            rows, cols = 0, 0
            for k, v in rd.items():
                row, col = k.split("_")
                rows = max(rows, int(row))
                cols = max(cols, int(col))
            rows += 1
            cols += 1
            rws = []
            if row_wise:
                for row in range(rows):
                    rw = 0
                    for col in range(cols):
                        if dict_idx(row, col) in rd:
                            r = rd["%d_%d" % (row, col)]
                            rw += r.width
                    rws.append(rw)
            else:
                for col in range(cols):
                    ch = 0
                    for row in range(rows):
                        if dict_idx(row, col) in rd:
                            r = rd["%d_%d" % (row, col)]
                            ch += r.height
                    rws.append(ch)
            if abs(max(rws)) > 0:
                ws = (max(rws) - min(rws)) / max(rws)
            else:
                ws = 0
            return ws

        wasted_space = 1.0

        times = 0 if auto_adjust else 9
        last_wasted_space = 1.0
        while (wasted_space > 0.25) and (times < 10):
            rw, rh = 0, 0
            cx, cy = bounds.left, bounds.top
            rd = {}
            row, col = 0, 0
            if row_wise:
                for r in rects:
                    cw, ch = r.width, r.height
                    if rw + cw <= bounds.width:
                        rh = max(rh, ch)
                        rw += cw
                        r.move_top_left_to((cx, cy))
                        rd[dict_idx(row, col)] = r
                        cx += cw
                        col += 1
                    else:
                        # overflowed width, go to next row
                        rw, col = 0, 0
                        row += 1
                        # print("OVERFLOW before setting cx,cy row=%d col=%d rw=%.1f rh=%.1f cw=%.1f ch=%.1f cx=%.1f cy=%.1f" % (row, col, rw, rh, cw, ch, cx, cy))

                        cx, cy = bounds.left, cy - rh
                        r.move_top_left_to((cx, cy))
                        # print("OVERFLOW after setting cx,cy row=%d col=%d rw=%.1f rh=%.1f cw=%.1f ch=%.1f cx=%.1f cy=%.1f" % (row, col, rw, rh, cw, ch, cx, cy))
                        rd[dict_idx(row, col)] = r
                        col += 1
                        cx += cw
                        rw, rh = cw, ch
                    # print("Rect: %s" % (r))
                    # print("row=%d col=%d rw=%.1f rh=%.1f cw=%.1f ch=%.1f cx=%.1f cy=%.1f" % (row, col, rw, rh, cw, ch, cx, cy))
            else:
                for r in rects:
                    cw, ch = r.width, r.height
                    if rh + ch <= bounds.height:
                        rw = max(rw, cw)
                        rh += ch
                        r.move_top_left_to((cx, cy))
                        rd[dict_idx(row, col)] = r
                        cy -= ch
                        row += 1
                    else:
                        # overflowed height, go to next col
                        rh, row = 0, 0
                        col += 1
                        cx, cy = cx + rw, bounds.top
                        r.move_top_left_to((cx, cy))
                        rd[dict_idx(row, col)] = r
                        row += 1
                        cy -= ch
                        rw, rh = cw, ch
            last_wasted_space = wasted_space
            wasted_space = compute_wasted_space(rd, row_wise=row_wise)
            if wasted_space > last_wasted_space:
                if row_wise:
                    bounds.right += 0.05 * bounds.width
                    bounds.width = bounds.right - bounds.left
                else:
                    bounds.bottom -= 0.05 * bounds.height
                    bounds.height = abs(bounds.bottom - bounds.top)
                times = 9
            else:
                if row_wise:
                    bounds.right -= 0.05 * bounds.width
                    bounds.width = bounds.right - bounds.left
                else:
                    bounds.bottom += 0.05 * bounds.height
                    bounds.height = abs(bounds.bottom - bounds.top)
                times += 1

        # Re-align each row or column based on vert_align and horz_align respectively
        rows, cols = 0, 0
        for k, v in rd.items():
            row, col = k.split("_")
            rows = max(rows, int(row))
            cols = max(cols, int(col))
        rows += 1
        cols += 1
        new_rects = []
        if row_wise:
            for row in range(rows):
                rh = 0
                for col in range(cols):
                    if dict_idx(row, col) in rd:
                        rh = max(rh, rd[dict_idx(row, col)].height)
                for col in range(cols):
                    if dict_idx(row, col) in rd:
                        r = copy.copy(rd[dict_idx(row, col)])
                        if vert_align == "bottom":
                            r.move_bottom_left_to((r.left, r.top - rh))
                        elif vert_align == "centre":
                            r.move_top_left_to((r.left, r.top - rh / 2 + r.height / 2))
                        new_rects.append(r)
        else:
            for col in range(cols):
                cw = 0
                for row in range(rows):
                    if dict_idx(row, col) in rd:
                        cw = max(cw, rd[dict_idx(row, col)].width)
                for row in range(rows):
                    if dict_idx(row, col) in rd:
                        r = copy.copy(rd[dict_idx(row, col)])
                        if horz_align == "right":
                            r.move_top_left_to((r.left + cw - r.width, r.top))
                        elif horz_align == "centre":
                            r.move_top_left_to((r.left + cw / 2 - r.width / 2, r.top))
                        new_rects.append(r)

        return new_rects

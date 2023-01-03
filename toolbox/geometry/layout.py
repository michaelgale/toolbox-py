#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
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
# Geometry / Layout helpers
#
import math

from .rect import Rect, RectCell


class RectLayout:
    def __init__(self, rects=None):
        self.rects = []
        if rects is not None:
            for rect in rects:
                if not isinstance(rect, RectCell):
                    rect = RectCell.from_rect(rect)
                self.rects.append(rect)

    def __len__(self):
        return len(self.rects)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.rects[key]
        elif isinstance(key, (list, tuple)):
            return self.rect_at(key[0], key[1])
        return None

    def __str__(self):
        s = []
        s.append("RectLayout: %d rects, %d assigned" % (len(self), self.len_assigned))
        if self.len_assigned > 0:
            s.append("  rows: %d cols: %d" % (self.row_count, self.col_count))
            s.append("  whitespace: %.3f" % (self.whitespace))
        for row, col, r in self.iter_row_wise():
            s.append("  row: %d col: %d : %s" % (row, col, r))
        return "\n".join(s)

    def print_grid(self, show_dim=False):
        col_width = min(int(70 / self.col_count), 16)
        s = []
        s.append("       ")
        for col in range(self.col_count):
            sfmt = "|%%-%ds" % (col_width)
            s.append(sfmt % ("%8d" % (col)))
        br = self.bounding_rect()
        s.append("|| %.2f,%.2f %.3f" % (br.width, br.height, self.whitespace))
        print("".join(s))

        s = []
        s.append("       ")
        for col in range(self.col_count):
            sfmt = "|%%-%ds" % (col_width)
            s.append(sfmt % ("-" * col_width))
        s.append("||")
        sfmt = "%%-%ds" % (col_width)
        s.append(sfmt % ("-" * col_width))
        print("".join(s))

        for row in range(self.row_count):
            s = []
            s.append("%5d: " % (row))
            for col in range(self.col_count):
                rect = self.rect_at(row, col)
                if rect is not None:
                    sfmt = "|%%%ds" % (col_width)
                    swh = "%.2f, %.2f" % (rect.width, rect.height)
                    s.append(sfmt % (swh))
                else:
                    sfmt = "|%%%ds" % (col_width)
                    s.append(sfmt % (""))
            s.append("|| %.2f, %.2f" % (self.row_width(row), self.row_height(row)))
            print("".join(s))
            if show_dim:
                s = []
                s.append("       ")
                for col in range(self.col_count):
                    rect = self.rect_at(row, col)
                    if rect is not None:
                        sfmt = "|%%-%ds" % (col_width)
                        swh = "     %.2f" % (rect.top)
                        s.append(sfmt % (swh))
                    else:
                        sfmt = "|%%%ds" % (col_width)
                        s.append(sfmt % (""))
                s.append("|| %.2f" % (self.row_top(row)))
                print("".join(s))
                s = []
                s.append("       ")
                for col in range(self.col_count):
                    rect = self.rect_at(row, col)
                    if rect is not None:
                        sfmt = "|%%-%ds" % (col_width)
                        swh = " %.2f %.2f" % (rect.left, rect.right)
                        s.append(sfmt % (swh))
                    else:
                        sfmt = "|%%%ds" % (col_width)
                        s.append(sfmt % (""))
                s.append("||")
                print("".join(s))
                s = []
                s.append("       ")
                for col in range(self.col_count):
                    rect = self.rect_at(row, col)
                    if rect is not None:
                        sfmt = "|%%-%ds" % (col_width)
                        swh = "     %.2f" % (rect.bottom)
                        s.append(sfmt % (swh))
                    else:
                        sfmt = "|%%%ds" % (col_width)
                        s.append(sfmt % (""))
                s.append("|| %.2f" % (self.row_top(row) - self.row_height(row)))
                print("".join(s))

    def print_rects(self):
        for rect in self.rects:
            print(type(rect), rect)

    def print_rows(self):
        for row in range(self.row_count):
            print(
                "row %d: cols: %d width: %.3f height: %.3f"
                % (
                    row,
                    self.row_col_count(row),
                    self.row_width(row),
                    self.row_height(row),
                )
            )

    def print_cols(self):
        for col in range(self.col_count):
            print(
                "col %d: rows: %d width: %.3f height: %.3f"
                % (
                    col,
                    self.col_row_count(col),
                    self.col_width(col),
                    self.col_height(col),
                )
            )

    def print_row_wise(self):
        for row, col, r in self.iter_row_wise():
            print("  row: %d col: %d : %s" % (row, col, r))

    def print_col_wise(self):
        for row, col, r in self.iter_col_wise():
            print("  col: %d row: %d : %s" % (col, row, r))

    @property
    def len_assigned(self):
        assigned = 0
        for r in self.iter_assigned():
            assigned += 1
        return assigned

    @property
    def row_count(self):
        row_max = 0
        for r in self.iter_assigned():
            if r.row > row_max:
                row_max = r.row
        return row_max + 1

    @property
    def col_count(self):
        col_max = 0
        for r in self.iter_assigned():
            if r.col > col_max:
                col_max = r.col
        return col_max + 1

    @property
    def shape(self):
        if self.len_assigned > 0:
            return self.row_count, self.col_count
        return len(self.rects)

    def rect_at(self, row, col):
        for r in self.rects:
            if r.row is None or r.col is None:
                continue
            if r.row == row and r.col == col:
                return r
        return None

    def iter_assigned(self):
        for r in self.rects:
            if r.row is None or r.col is None:
                continue
            yield r

    def iter_row_wise(self):
        """Iterates row-wise across all rects, returning only valid rects, skipping empty cells"""
        for row in range(self.row_count):
            for col in range(self.col_count):
                r = self.rect_at(row, col)
                if r is None:
                    continue
                yield row, col, r

    def iter_col_wise(self):
        """Iterates column-wise across all rects, returning only valid rects, skipping empty cells"""
        for col in range(self.col_count):
            for row in range(self.row_count):
                r = self.rect_at(row, col)
                if r is None:
                    continue
                yield row, col, r

    def iter_at_row(self, row):
        """Iterates columns at a row, returning only valid rects, skipping empty cells"""
        for col in range(self.col_count):
            r = self.rect_at(row, col)
            if r is None:
                continue
            yield col, r

    def iter_at_col(self, col):
        """Iterates rows at a column, returning only valid rects, skipping empty cells"""
        for row in range(self.row_count):
            r = self.rect_at(row, col)
            if r is None:
                continue
            yield row, r

    def assign_rect(self, rect, row, col, x, y):
        if not isinstance(rect, RectCell):
            rect = RectCell.from_rect(rect)
        rect.row, rect.col = row, col
        rect.move_top_left_to((x, y))

    def row_width(self, row):
        width = 0
        for _, rect in self.iter_at_row(row):
            width += rect.width
        return width

    def row_height(self, row):
        height = 0
        for _, rect in self.iter_at_row(row):
            height = max(height, rect.height)
        return height

    def row_top(self, row):
        top = self[(row, 0)].top
        for _, rect in self.iter_at_row(row):
            top = max(top, rect.top)
        return top

    def row_bottom(self, row):
        return self.row_top(row) + self.row_height(row)

    def row_col_count(self, row):
        cols = 0
        for _, _ in self.iter_at_row(row):
            cols += 1
        return cols

    def col_height(self, col):
        height = 0
        for _, rect in self.iter_at_col(col):
            height += rect.height
        return height

    def col_width(self, col):
        width = 0
        for _, rect in self.iter_at_col(col):
            width = max(width, rect.width)
        return width

    def col_left(self, col):
        left = self[(0, col)].left
        for _, rect in self.iter_at_col(col):
            left = min(left, rect.left)
        return left

    def col_right(self, col):
        return self.col_left(col) + self.col_width(col)

    def col_row_count(self, col):
        rows = 0
        for _, _ in self.iter_at_col(col):
            rows += 1
        return rows

    def validate_shape(self, shape):
        if shape is None:
            return True
        if not isinstance(shape, (list, tuple)):
            raise TypeError(
                "shape must be specified as a 2-element list or tuple, not %s"
                % (type(shape))
            )
        size = shape[0] * shape[1]
        if size < len(self):
            raise ValueError(
                "shape (%d x %d) is too small to fit %d rectangles"
                % (shape[0], shape[1], len(self))
            )
        return True

    @property
    def max_row_width(self):
        return max([self.row_width(row) for row in range(self.row_count)])

    @property
    def max_col_height(self):
        return max([self.col_height(col) for col in range(self.col_count)])

    @property
    def min_row_width(self):
        return min([self.row_width(row) for row in range(self.row_count)])

    @property
    def min_col_height(self):
        return min([self.col_height(col) for col in range(self.col_count)])

    @property
    def content_area(self):
        return sum([(r.width * r.height) for r in self.rects])

    @property
    def total_area(self):
        return self.bounding_rect().area

    @property
    def whitespace(self):
        return 1.0 - self.content_area / self.total_area

    @property
    def row_wise_whitespace(self):
        if self.max_row_width > 0:
            return (self.max_row_width - self.min_row_width) / self.max_row_width
        return 0

    @property
    def col_wise_whitespace(self):
        if self.max_col_height > 0:
            return (self.max_col_height - self.min_col_height) / self.max_col_height
        return 0

    def set_row_vert_align(self, row, align="centre"):
        for _, rect in self.iter_at_row(row):
            rect.vert_align = align

    def set_row_horz_align(self, row, align="centre"):
        for _, rect in self.iter_at_row(row):
            rect.horz_align = align

    def set_col_vert_align(self, col, align="centre"):
        for _, rect in self.iter_at_col(col):
            rect.vert_align = align

    def set_col_horz_align(self, col, align="centre"):
        for _, rect in self.iter_at_col(col):
            rect.horz_align = align

    def set_vert_align(self, align="centre"):
        for rect in self.rects:
            rect.vert_align = align

    def set_horz_align(self, align="centre"):
        for rect in self.rects:
            rect.horz_align = align

    def fits_in_bounds(self, bounds):
        brect = self.bounding_rect()
        for pt in brect.get_pts():
            if not bounds.contains(pt):
                return False
        return True

    def bounding_rect(self):
        return Rect.bounding_rect_from_rects(self.rects)

    def layout_row_wise(self, bounds, shape=None):
        """Arranges rectangles row-wise within bounds.
        This will layout rectangles from left to right, top to bottom.
        If shape is specified, this will force row break to occur by shape columns rather
        than the right boundary."""
        row, col = 0, 0
        row_width, row_height = 0, 0
        x, y = bounds.left, bounds.top
        if not self.validate_shape(shape):
            return
        for r in self.rects:
            if shape is not None:
                enough_space = col < shape[1]
            else:
                enough_space = row_width + r.width <= bounds.width
            if enough_space:
                row_height = max(row_height, r.height)
                row_width += r.width
                self.assign_rect(r, row, col, x, y)
            else:
                row_width, col = 0, 0
                row += 1
                x, y = bounds.left, y - row_height
                self.assign_rect(r, row, col, x, y)
                row_width, row_height = r.width, r.height
            col += 1
            x += r.width
        self.align_rows_vert()

    def layout_col_wise(self, bounds, shape=None):
        """Arranges rectangles column-wise within bounds.
        This will layout rectangles from top to bottom, left to right.
        If shape is specified, this will force column break to occur by shape rows rather
        than the bottom boundary."""
        row, col = 0, 0
        col_width, col_height = 0, 0
        x, y = bounds.left, bounds.top
        if not self.validate_shape(shape):
            return
        for r in self.rects:
            if shape is not None:
                enough_space = row < shape[0]
            else:
                enough_space = col_height + r.height <= bounds.height
            if enough_space:
                col_width = max(col_width, r.width)
                col_height += r.height
                self.assign_rect(r, row, col, x, y)
            else:
                col_height, row = 0, 0
                col += 1
                x, y = x + col_width, bounds.top
                self.assign_rect(r, row, col, x, y)
                col_width, col_height = r.width, r.height
            row += 1
            y -= r.height
        self.align_cols_horz()

    def align_rows_vert(self):
        """Aligns each cell in a row with each cell's vertical alignment attribute"""
        for row, _, rect in self.iter_row_wise():
            x, y = rect.left, self.row_top(row)
            row_height = self.row_height(row)
            if rect.vert_align == "bottom":
                rect.move_bottom_left_to((x, y - row_height))
            elif rect.vert_align in ["centre", "center"]:
                rect.move_top_left_to((x, y - row_height / 2 + rect.height / 2))
            else:
                rect.move_top_left_to((x, y))

    def align_cols_horz(self):
        """Aligns each cell in a column with each cell's horz alignment attribute"""
        for _, col, rect in self.iter_col_wise():
            x, y = self.col_left(col), rect.top
            col_width = self.col_width(col)
            if rect.horz_align == "right":
                rect.move_top_left_to((x + col_width - rect.width, y))
            elif rect.horz_align in ["centre", "center"]:
                rect.move_top_left_to((x + col_width / 2 - rect.width / 2, y))
            else:
                rect.move_top_left_to((x, y))

    def align_grid(self):
        """Aligns each cell grid wise.
        Every cell in a vertical column will have same width and every
        cell in a row will have the same height.  After the cells have
        been arranged, then the cell's alignment attributes are applied."""
        x, y = self.col_left(0), self.row_top(0)
        col_x = [x]
        col_y = [y]
        for col in range(0, self.col_count - 1):
            x += self.col_width(col)
            col_x.append(x)
        for row in range(0, self.row_count - 1):
            y -= self.row_height(row)
            col_y.append(y)
        for row, y in zip(list(range(self.row_count)), col_y):
            for col, x in zip(list(range(self.col_count)), col_x):
                rect = self.rect_at(row, col)
                if rect is None:
                    continue
                rect.move_top_left_to((x, y))
        self.align_rows_vert()
        self.align_cols_horz()

    def distortion(self, bounds):
        x = (self.bounding_rect().width - bounds.width) / bounds.width
        y = (self.bounding_rect().height - bounds.height) / bounds.height
        return math.sqrt(x * x + y * y)

    def auto_align(self, bounds, col_wise=False, grid_align=False):
        # shapes = [(x+1, y+1) for x in range(len(self)) for y in range(len(self))]
        # shapes = [(s[0], s[1]) for s in shapes if (s[0] * s[1]) >= len(self)]
        # for shape in shapes:
        #     self.layout_row_wise(bounds=bounds, shape=shape)
        #     print("%8s %9.3f %9.3f %9.3f" %(shape, self.content_area, self.total_area, self.whitespace))
        print(" ")
        merits = []
        max_distortion = 0
        max_whitespace = 0
        if col_wise:
            for x in range(len(self)):
                self.layout_col_wise(bounds=bounds, shape=(x + 1, len(self)))
                if grid_align:
                    self.align_grid()
                distortion = self.distortion(bounds)
                merit = 2 * self.whitespace + distortion
                # print("col (%d, %d) %8.3f %8.3f %s %8.3f" % (x+1, len(self), self.whitespace, self.distortion(bounds), self.shape, merit))
                merits.append((self.shape, self.whitespace, distortion))
                if distortion > max_distortion:
                    max_distortion = distortion
                if self.whitespace > max_whitespace:
                    max_whitespace = self.whitespace
        else:
            for y in range(len(self)):
                self.layout_row_wise(bounds=bounds, shape=(len(self), y + 1))
                if grid_align:
                    self.align_grid()
                distortion = self.distortion(bounds)
                merit = 2 * self.whitespace + distortion
                # print("row (%d, %d) %8.3f %8.3f %s %8.3f" % (len(self), y+1, self.whitespace, self.distortion(bounds), self.shape, merit))
                merits.append((self.shape, self.whitespace, distortion))
                if distortion > max_distortion:
                    max_distortion = distortion
                if self.whitespace > max_whitespace:
                    max_whitespace = self.whitespace
        merits_norm = []
        for shape, ws, d in merits:
            merits_norm.append(
                (
                    shape,
                    ws / max_whitespace,
                    d / max_distortion,
                    ws / max_whitespace * d / max_distortion,
                )
            )
        merits_norm.sort(key=lambda x: x[3])
        for m in merits_norm:
            print("%9s %8.3f %8.3f | %8.3f" % (m[0], m[1], m[2], m[3]))
        min_merit = merits_norm[0][3]
        min_shape = merits_norm[0][0]
        print("Best merit: %8.3f with shape %s" % (min_merit, min_shape))
        if col_wise:
            self.layout_col_wise(bounds=bounds, shape=min_shape)
        else:
            self.layout_row_wise(bounds=bounds, shape=min_shape)
        if grid_align:
            self.align_grid()
        self.print_grid(show_dim=True)
        # return
        # print(self)
        # s = []
        # s.append("%6s" %(""))
        # for y in range(len(self)):
        #     s.append("%8d" % (y+1))
        # print("".join(s))
        # for x in range(len(self)):
        #     s = []
        #     s.append("%5d " % (x+1))
        #     for y in range(len(self)):
        #         if ((x+1) * (y+1)) < len(self):
        #             s.append("%8s" % (""))
        #             continue
        #         if col_wise:
        #             self.layout_col_wise(bounds=bounds, shape=(x+1, y+1))
        #         else:
        #             self.layout_row_wise(bounds=bounds, shape=(x+1, y+1))
        #         s.append("%8.3f" % (self.whitespace))
        #         if col_wise:
        #             break
        #         elif ((len(self) - x) * (y - 1)) < (len(self) + 1):
        #             break
        #     print("".join(s))

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

from .rect import Rect


class RectLayout:
    def __init__(self, rects=None):
        self.rects = []
        if rects is not None:
            self.rects = rects

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
            s.append(
                "  row whitespace: %.3f col whitespace: %.3f"
                % (self.row_wise_whitespace, self.col_wise_whitespace)
            )
        for row, col, r in self.iter_row_wise():
            s.append("  row: %d col: %d : %s" % (row, col, r))
        return "\n".join(s)

    def print_grid(self):
        col_width = min(int(70 / self.col_count), 16)
        s = []
        s.append("       ")
        for col in range(self.col_count):
            sfmt = "|%%-%ds" % (col_width)
            s.append(sfmt % ("%8d" % (col)))
        br = self.bounding_rect()
        s.append(
            "|| %.3f,%.3f %.3f,%.3f"
            % (br.width, br.height, self.row_wise_whitespace, self.col_wise_whitespace)
        )
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
                    swh = "%.2f,%.2f" % (rect.width, rect.height)
                    s.append(sfmt % (swh))
                else:
                    sfmt = "|%%%ds" % (col_width)
                    s.append(sfmt % (""))
            s.append("|| %.2f,%.2f" % (self.row_width(row), self.row_height(row)))
            print("".join(s))

    def print_rects(self):
        for rect in self.rects:
            print(rect)

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

    def row_col_count(self, row):
        cols = 0
        for _, _ in self.iter_at_row(row):
            cols += 1
        return cols

    def col_height(self, col):
        height = 0
        for _, rect in self.iter_at_col(col):
            height += rect.width
        return height

    def col_width(self, col):
        width = 0
        for _, rect in self.iter_at_col(col):
            width = max(width, rect.width)
        return width

    def col_row_count(self, col):
        rows = 0
        for _, _ in self.iter_at_col(col):
            rows += 1
        return rows

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

    def assign_rect(self, rect, row, col, x, y):
        rect.row, rect.col = row, col
        rect.move_top_left_to((x, y))

    def fits_in_bounds(self, bounds):
        brect = self.bounding_rect()
        for pt in brect.get_pts():
            if not bounds.contains(pt):
                return False
        return True

    def bounding_rect(self):
        return Rect.bounding_rect_from_rects(self.rects)

    def layout_row_wise(self, bounds):
        row, col = 0, 0
        row_width, row_height = 0, 0
        x, y = bounds.left, bounds.top
        for r in self.rects:
            if row_width + r.width <= bounds.width:
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

    def layout_col_wise(self, bounds):
        row, col = 0, 0
        col_width, col_height = 0, 0
        x, y = bounds.left, bounds.top
        for r in self.rects:
            if col_height + r.height <= bounds.height:
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

    def align_rows(self):
        for row, col, rect in self.iter_row_wise():
            x, y = rect.left, rect.top
            row_height = self.row_height(row)
            if rect.vert_align == "bottom":
                rect.move_bottom_left_to((x, y - row_height))
            elif rect.vert_align in ["centre", "center"]:
                rect.move_top_left_to((x, y - row_height / 2 + rect.height / 2))

    def align_cols(self):
        for row, col, rect in self.iter_col_wise():
            x, y = rect.left, rect.top
            col_width = self.col_width(col)
            if rect.horz_align == "right":
                rect.move_top_left_to((x + col_width - rect.width, y))
            elif rect.horz_align in ["centre", "center"]:
                rect.move_top_left_to((x + col_width / 2 - rect.width / 2, y))

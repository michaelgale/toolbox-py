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


class LayoutResult:
    def __init__(self, **kwargs):
        self.whitespace = 0
        self.distortion = 0
        self.goal_shape = (1, 1)
        self.shape = (1, 1)
        self.extents = Rect(0, 0)
        self.score = -1
        self.whitespace_weight = 1.0
        self.distortion_weight = 1.0
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v

    def __str__(self):
        s = []
        s.append(
            "shape: %8s (%8s) whitespace: %8.3f distortion: %8.3f score: %8.3f %s"
            % (
                self.shape,
                self.goal_shape,
                self.whitespace,
                self.distortion,
                self.score,
                self.extents,
            )
        )
        return "".join(s)

    @staticmethod
    def normalize(results, key, as_is=False):
        values = [result.__dict__[key] for result in results]
        if not as_is:
            max_value = max(values)
            values = [v / max_value for v in values]
        return values

    @staticmethod
    def normalize_results(results):
        norm_whitespace = LayoutResult.normalize(results, "whitespace", as_is=True)
        norm_distortion = LayoutResult.normalize(results, "distortion")
        for r, w, d in zip(results, norm_whitespace, norm_distortion):
            r.whitespace = w
            r.distortion = d
            r.score = r.whitespace_weight * w + r.distortion_weight * d
        return results

    @staticmethod
    def best_score(results):
        min_score = results[0].score
        best_result = results[0]
        for r in results:
            if r.score < min_score:
                min_score = r.score
                best_result = r
        return best_result

    @staticmethod
    def best_result(results):
        norm_results = LayoutResult.normalize_results(results)
        best_score = LayoutResult.best_score(norm_results)
        return best_score


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
        return sum([1 for r in self.iter_assigned()])

    @property
    def row_count(self):
        if self.len_assigned > 0:
            return max([r.row for r in self.iter_assigned()]) + 1
        return 0

    @property
    def col_count(self):
        if self.len_assigned > 0:
            return max([r.col for r in self.iter_assigned()]) + 1
        return 0

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

    def clear_assigned(self):
        for r in self.rects:
            r.row, r.col = None, None

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

    def bounding_rect(self):
        return Rect.bounding_rect_from_rects(self.rects)

    def row_width(self, row):
        return sum([r.width for _, r in self.iter_at_row(row)])

    def row_height(self, row):
        return max([r.height for _, r in self.iter_at_row(row)])

    def row_top(self, row):
        return max([r.top for _, r in self.iter_at_row(row)])

    def row_bottom(self, row):
        return self.row_top(row) + self.row_height(row)

    def row_col_count(self, row):
        return sum([1 for _, _ in self.iter_at_row(row)])

    def col_height(self, col):
        return sum([r.height for _, r in self.iter_at_col(col)])

    def col_width(self, col):
        return max([r.width for _, r in self.iter_at_col(col)])

    def col_left(self, col):
        return min([r.left for _, r in self.iter_at_col(col)])

    def col_right(self, col):
        return self.col_left(col) + self.col_width(col)

    def col_row_count(self, col):
        return sum([1 for _, _ in self.iter_at_col(col)])

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
    def total_width(self):
        return self.bounding_rect().width

    @property
    def total_height(self):
        return self.bounding_rect().height

    @property
    def whitespace(self):
        return 1.0 - self.content_area / self.total_area

    @property
    def row_wise_whitespace(self):
        if self.max_row_width > 0:
            return (self.max_row_width - self.min_row_width) / self.max_row_width
        return 1.0

    @property
    def col_wise_whitespace(self):
        if self.max_col_height > 0:
            return (self.max_col_height - self.min_col_height) / self.max_col_height
        return 1.0

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

    def layout_row_wise(
        self, bounds, shape=None, hard_bounds_limit=False, grid_align=False
    ):
        """Arranges rectangles row-wise within bounds.
        This will layout rectangles from left to right, top to bottom.
        If shape is specified, this will force row break to occur by shape columns rather
        than the right boundary."""
        self.clear_assigned()
        row, col = 0, 0
        row_width, row_height = 0, 0
        x, y = bounds.left, bounds.top
        if not self.validate_shape(shape):
            return
        for r in self.rects:
            enough_space = row_width + r.width <= bounds.width
            if shape is not None:
                within_shape = col < shape[1]
                row_break = not within_shape
                if hard_bounds_limit:
                    row_break = row_break or not enough_space
            else:
                row_break = not enough_space
            if not row_break or row_width == 0:
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
        if grid_align:
            self.align_grid()
        else:
            self.align_rows_vert()

    def layout_col_wise(
        self, bounds, shape=None, hard_bounds_limit=False, grid_align=False
    ):
        """Arranges rectangles column-wise within bounds.
        This will layout rectangles from top to bottom, left to right.
        If shape is specified, this will force column break to occur by shape rows rather
        than the bottom boundary."""
        self.clear_assigned()
        row, col = 0, 0
        col_width, col_height = 0, 0
        x, y = bounds.left, bounds.top
        if not self.validate_shape(shape):
            return
        for r in self.rects:
            enough_space = col_height + r.height <= bounds.height
            if shape is not None:
                within_shape = row < shape[0]
                col_break = not within_shape
                if hard_bounds_limit:
                    col_break = col_break or not enough_space
            else:
                col_break = not enough_space
            if not col_break or col_height == 0:
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
        if grid_align:
            self.align_grid()
        else:
            self.align_cols_horz()

    def align_rows_vert(self):
        """Aligns each cell in a row with each cell's vertical alignment attribute"""
        if not self.len_assigned > 0:
            return
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
        if not self.len_assigned > 0:
            return
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
        if not self.len_assigned > 0:
            return
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
        if not abs(bounds.width) > 0 or not abs(bounds.height) > 0:
            return 1.0
        x = (self.bounding_rect().width - bounds.width) / bounds.width
        y = (self.bounding_rect().height - bounds.height) / bounds.height
        return math.sqrt(x * x + y * y)

    def optimize_layout(
        self,
        bounds,
        col_wise=False,
        hard_bounds_limit=False,
        grid_align=False,
        prioritize_whitespace=False,
        strategy="reshape",
    ):
        if not len(self.rects) > 0:
            return
        layout_fn = self.layout_col_wise if col_wise else self.layout_row_wise
        results = []
        if strategy == "reshape":
            for dim in range(len(self)):
                shape = (dim + 1, len(self)) if col_wise else (len(self), dim + 1)
                layout_fn(
                    bounds=bounds,
                    shape=shape,
                    hard_bounds_limit=hard_bounds_limit,
                    grid_align=grid_align,
                )
                result = LayoutResult(
                    goal_shape=shape,
                    whitespace=self.whitespace,
                    distortion=self.distortion(bounds),
                    shape=self.shape,
                    extents=self.bounding_rect(),
                    distortion_weight=0.0 if prioritize_whitespace else 1.0,
                )
                results.append(result)
            best = LayoutResult.best_result(results)
            layout_fn(
                bounds=bounds,
                shape=best.shape,
                hard_bounds_limit=hard_bounds_limit,
                grid_align=grid_align,
            )
        elif strategy == "resize":
            times = 0
            layout_fn(
                bounds=bounds,
                shape=None,
                hard_bounds_limit=hard_bounds_limit,
                grid_align=grid_align,
            )
            whitespace = (
                self.col_wise_whitespace if col_wise else self.row_wise_whitespace
            )
            while whitespace > 0.25 and times < 20:
                layout_fn(
                    bounds=bounds,
                    shape=None,
                    hard_bounds_limit=hard_bounds_limit,
                    grid_align=grid_align,
                )
                last_whitespace = whitespace
                whitespace = (
                    self.col_wise_whitespace if col_wise else self.row_wise_whitespace
                )
                if whitespace < last_whitespace:
                    if col_wise:
                        bounds.bottom += 0.05 * bounds.height
                        bounds.height = abs(bounds.bottom - bounds.top)
                    else:
                        bounds.right -= 0.05 * bounds.width
                        bounds.width = bounds.right - bounds.left
                else:
                    break
                times += 1

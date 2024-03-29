# system modules
import copy
import pytest

# my modules
from toolbox import *


rects1 = [
    RectCell(1, 1),
    RectCell(2, 1),
    RectCell(1.5, 1),
    RectCell(3, 2),
    RectCell(2.5, 1),
    RectCell(1, 0.5),
    RectCell(2, 2),
]


def test_rectcell_init():
    r1 = RectCell(5, 7, row=0, col=1, vert_align="bottom", horz_align="left")
    assert r1.width == 5
    assert r1.height == 7
    assert r1.row == 0
    assert r1.col == 1
    assert r1.vert_align == "bottom"
    assert r1.horz_align == "left"


def test_layout():
    r1 = RectLayout(copy.deepcopy(rects1))
    assert len(r1) == 7
    assert r1.len_assigned == 0
    assert r1.shape == 7
    bounds = Rect(5, 10)
    bounds.move_top_left_to((0, 10))
    r1.layout_row_wise(bounds=bounds)
    fits = r1.fits_in_bounds(bounds)
    assert r1.shape == (4, 3)
    assert r1.len_assigned == 7
    assert r1.row_count == 4
    assert r1.col_count == 3
    assert fits == True
    assert r1.cols_at_row(0) == 3
    assert r1.cols_at_row(1) == 1
    assert r1.cols_at_row(2) == 2
    assert r1.cols_at_row(3) == 1
    assert r1.rows_at_col(0) == 4
    assert r1.rows_at_col(1) == 2
    assert r1.rows_at_col(2) == 1
    assert r1.row_width(0) == 4.5
    assert r1.row_height(0) == 1.0
    assert r1.col_width(0) == 3.0
    assert r1.col_height(0) == 6.0

    bounds = Rect(5, 5)
    bounds.move_top_left_to((0, 10))
    r1.layout_row_wise(bounds=bounds)
    fits = r1.fits_in_bounds(bounds)
    assert fits == False
    assert r1.len_assigned == 7
    assert r1.row_count == 4
    assert r1.col_count == 3

    r1.layout_col_wise(bounds=bounds)
    assert fits == False
    assert r1.len_assigned == 7
    assert r1.row_count == 4
    assert r1.col_count == 2
    assert r1.row_width(0) == 3.5
    assert r1.row_height(0) == 1.0
    assert r1.col_width(0) == 3.0
    assert r1.col_height(0) == 5.0


def test_layout_shape():
    r1 = RectLayout(copy.deepcopy(rects1))
    assert len(r1) == 7
    assert r1.len_assigned == 0
    assert r1.shape == 7
    bounds = Rect(5, 10)
    bounds.move_top_left_to((0, 10))
    r1.layout_row_wise(bounds=bounds, shape=(3, 3))
    assert r1.shape == (3, 3)
    assert r1.len_assigned == 7
    assert r1.cols_at_row(0) == 3
    assert r1.cols_at_row(1) == 3
    assert r1.cols_at_row(2) == 1
    with pytest.raises(TypeError):
        r1.layout_row_wise(bounds, shape=2)
    with pytest.raises(ValueError):
        r1.layout_row_wise(bounds, shape=(1, 4))


rects2 = [
    RectCell(1, 0.75),
    RectCell(2, 0.5),
    RectCell(1.5, 1),
    RectCell(3, 2),
    RectCell(2.5, 1),
    RectCell(1, 0.5),
    RectCell(2, 2),
]


def test_layout_align_vert():
    r1 = RectLayout(copy.deepcopy(rects2))
    assert len(r1) == 7
    assert r1.len_assigned == 0
    bounds = Rect(5, 10)
    bounds.move_top_left_to((0, 10))
    r1.set_vert_align("centre")
    r1.layout_row_wise(bounds=bounds)
    assert r1.len_assigned == 7
    rc = r1[(0, 1)]
    assert rc.top == 9.75
    assert rc.bottom == 9.25
    r1.set_vert_align("bottom")
    r1.layout_row_wise(bounds=bounds)
    rc = r1[(0, 1)]
    assert rc.top == 9.5
    assert rc.bottom == 9.0


def test_layout_align_horz():
    r1 = RectLayout(copy.deepcopy(rects2))
    assert len(r1) == 7
    assert r1.len_assigned == 0
    bounds = Rect(10, 4)
    bounds.move_top_left_to((0, 10))
    r1.set_horz_align("centre")
    r1.layout_col_wise(bounds=bounds)
    assert r1.len_assigned == 7
    assert r1.shape == (3, 3)
    rc = r1[(2, 0)]
    assert rc.left == 0.25
    assert rc.right == 1.75

    r1.set_horz_align("right")
    r1.layout_col_wise(bounds=bounds)
    rc = r1[(2, 0)]
    assert rc.left == 0.5
    assert rc.right == 2.0
    rc = r1[(1, 1)]
    assert rc.left == 2.5
    assert rc.right == 5.0
    r1.set_col_horz_align(0, "left")
    r1.layout_col_wise(bounds=bounds)
    rc = r1[(2, 0)]
    assert rc.left == 0
    assert rc.right == 1.5
    rc = r1[(1, 1)]
    assert rc.left == 2.5
    assert rc.right == 5.0


def test_layout_align_grid():
    r1 = RectLayout(copy.deepcopy(rects2))
    assert len(r1) == 7
    assert r1.len_assigned == 0
    bounds = Rect(5, 5)
    bounds.move_top_left_to((0, 10))
    r1.set_vert_align("centre")
    r1.set_horz_align("centre")
    r1.layout_row_wise(bounds=bounds)
    assert r1.len_assigned == 7
    r1.align_grid()


def test_layout_gutters():
    r1 = RectLayout(copy.deepcopy(rects2))
    assert len(r1) == 7
    assert r1.len_assigned == 0
    bounds = Rect(5, 5)
    bounds.move_top_left_to((0, 10))
    r1.set_vert_align("top")
    r1.set_horz_align("left")
    r1.layout_row_wise(bounds=bounds)
    assert r1.total_height == 6.0
    assert RectCell.shape_from_rects(r1.rects) == (4, 3)
    assert len(RectCell.horz_gutters_from_rects(r1.rects)) == 0
    r1.add_row_gutters(height=0.5)
    assert r1.total_height == 7.5
    assert RectCell.shape_from_rects(r1.rects) == (4, 3)
    assert len(RectCell.horz_gutters_from_rects(r1.rects)) == 3
    r1.layout_col_wise(bounds=bounds)
    assert r1.total_width == 5.5
    assert RectCell.shape_from_rects(r1.rects) == (4, 2)
    assert len(RectCell.vert_gutters_from_rects(r1.rects)) == 0
    r1.add_col_gutters(width=0.5)
    assert r1.total_width == 6.0
    assert RectCell.shape_from_rects(r1.rects) == (4, 2)
    assert len(RectCell.vert_gutters_from_rects(r1.rects)) == 1


rects3 = [
    RectCell(1, 0.75),
    RectCell(3, 2),
    RectCell(1, 0.5),
    RectCell(2, 0.5),
    RectCell(1.5, 1),
    RectCell(0.5, 1.25),
    RectCell(2.5, 1),
    RectCell(3, 2),
    RectCell(2, 0.5),
    RectCell(1, 0.5),
    RectCell(1.25, 1.25),
    RectCell(0.5, 1.5),
    RectCell(3.5, 1.75),
    RectCell(2, 2),
]


def test_auto_layout():
    r1 = RectLayout(copy.deepcopy(rects3))
    assert len(r1) == 14
    assert r1.len_assigned == 0
    bounds = Rect(6, 10)
    bounds.move_top_left_to((0, 10))
    r1.layout_row_wise(bounds=bounds, shape=(6, 6), hard_bounds_limit=False)
    assert r1.len_assigned == 14
    assert r1.shape == (3, 6)
    r1.layout_row_wise(bounds=bounds, shape=(6, 6), hard_bounds_limit=True)
    assert r1.len_assigned == 14
    assert r1.shape == (5, 4)
    assert r1.total_width <= bounds.width


def test_layout_whitespace():
    r1 = RectLayout(copy.deepcopy(rects3))
    bounds = Rect(8, 5)
    bounds.move_top_left_to((0, 10))
    r1.set_vert_align("centre")
    r1.set_horz_align("centre")
    r1.optimize_layout(
        bounds=bounds, col_wise=False, grid_align=False, strategy="resize"
    )
    assert r1.shape == (4, 4)

    bounds = Rect(12, 5)
    bounds.move_top_left_to((0, 10))
    r1.optimize_layout(
        bounds=bounds,
        col_wise=False,
        hard_bounds_limit=True,
        grid_align=False,
    )
    assert r1.shape == (3, 7)

    r1.optimize_layout(
        bounds=bounds,
        col_wise=False,
        hard_bounds_limit=False,
        grid_align=False,
    )
    assert r1.shape == (3, 7)

    bounds = Rect(6, 8)
    bounds.move_top_left_to((0, 10))
    r1.set_vert_align("centre")
    r1.set_horz_align("centre")
    r1.optimize_layout(bounds=bounds, col_wise=True, grid_align=False)
    assert r1.shape == (7, 3)
    assert r1.bounding_rect().width == 8.5
    assert r1.bounding_rect().height == 7.5
    r1.optimize_layout(bounds=bounds, col_wise=True, grid_align=True)
    assert r1.shape == (7, 3)
    assert r1.bounding_rect().width == 8.5
    assert r1.bounding_rect().height == 10

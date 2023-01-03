# system modules
import copy

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
    bounds = Rect(5, 10)
    bounds.move_top_left_to((0, 10))
    r1.layout_row_wise(bounds=bounds)
    fits = r1.fits_in_bounds(bounds)
    assert r1.len_assigned == 7
    assert r1.row_count == 4
    assert r1.col_count == 3
    assert fits == True
    assert r1.row_col_count(0) == 3
    assert r1.row_col_count(1) == 1
    assert r1.row_col_count(2) == 2
    assert r1.row_col_count(3) == 1
    assert r1.col_row_count(0) == 4
    assert r1.col_row_count(1) == 2
    assert r1.col_row_count(2) == 1
    assert r1.row_width(0) == 4.5
    assert r1.row_height(0) == 1.0
    assert r1.col_width(0) == 3.0
    assert r1.col_height(0) == 8.5
    r1.print_grid()

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
    assert r1.col_height(0) == 7.5
    r1.print_grid()


rects2 = [
    RectCell(1, 0.75),
    RectCell(2, 0.5),
    RectCell(1.5, 1),
    RectCell(3, 2),
    RectCell(2.5, 1),
    RectCell(1, 0.5),
    RectCell(2, 2),
]


def test_layout_align():
    r1 = RectLayout(copy.deepcopy(rects2))
    assert len(r1) == 7
    assert r1.len_assigned == 0
    bounds = Rect(5, 10)
    bounds.move_top_left_to((0, 10))
    r1.set_vert_align("centre")
    r1.layout_row_wise(bounds=bounds)
    r1.align_rows()
    assert r1.len_assigned == 7
    print("ORIGINAL")
    r1.print_grid()
    r1.print_rects()
    r1.set_vert_align("bottom")
    r1.align_rows()
    print("REALIGN")
    r1.print_grid()
    r1.print_rects()


def test_layout_rects():
    r1 = Rect()
    r1.set_points((-153.00, 28.80), (-69.81, -43.92))
    r2 = Rect()
    r2.set_points((-69.81, 28.80), (18.29, -54.00))
    r3 = Rect()
    r3.set_points((-105.74, 112.08), (105.74, -112.08))
    r4 = Rect()
    r4.set_points((-57.33, 71.16), (57.33, -71.16))
    rects = [r1, r2, r3, r4]
    brect = Rect()
    brect.set_points((-156.60, 36.00), (156.60, -36.00))
    print("Fitting these rects:")
    for r in rects:
        print(r)
    print("Into this rect:\n%s" % (str(brect)))
    lr1 = RectLayout(rects=rects)
    # lr1.layout_col_wise(bounds=brect)
    lr1.layout_row_wise(bounds=brect)
    print("Results in these new rects:")
    lr1.print_grid()


# def test_arrange():
#     r1 = Rect()
#     r1.set_points((-153.00,28.80), (-69.81,-43.92))
#     r2 = Rect()
#     r2.set_points((-69.81,28.80),(18.29,-54.00))
#     r3 = Rect()
#     r3.set_points((-105.74,112.08),(105.74,-112.08))
#     r4 = Rect()
#     r4.set_points((-57.33,71.16),(57.33,-71.16))
#     rects = [r1, r2, r3, r4]
#     brect = Rect()
#     brect.set_points((-156.60,36.00), (156.60,-36.00))
#     print("Fitting these rects:")
#     for r in rects:
#         print(r)
#     print("Into this rect:\n%s" % (str(brect)))
#     new_rects = Rect.layout_rects(
#             rects,
#             brect,
#             row_wise=True,
#             auto_adjust=False,
#         )
#     print("Results in these new rects:")
#     for r in new_rects:
#         print(r)

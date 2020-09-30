# system modules
import math, os.path
import copy
import sys
import pytest
from math import pi

# my modules
from toolbox import *


def test_rect_size():
    a = Rect(10, 4)
    assert a.left == -5
    assert a.right == 5
    assert a.top == 2
    assert a.bottom == -2
    a.bottom_up = True
    a.move_to(Point(0, 0))
    assert a.top == -2
    assert a.bottom == 2


def test_contains():
    a = Rect(5, 4)
    b = Point(1, 1.5)
    c = Point(-3, 10)
    assert a.contains(b)
    assert a.contains(c) == False


def test_overlap():
    a = Rect(10, 5)
    b = Rect(2, 3)
    c = copy.copy(b)
    c.move_to(Point(10, -7))
    assert a.overlaps(c) == False


def test_move():
    a = Rect(4, 8)
    a.move_top_left_to(Point(-10, -7))
    assert a.left == -10
    assert a.top == -7
    assert a.right == -6
    assert a.bottom == -15
    (x, y) = a.get_centre()
    assert x == -8
    assert y == -11


def test_bounding():
    pts = [(1, 2), (3, 5), (-7, -4), (20, 8)]
    r = Rect()
    r.bounding_rect(pts)
    assert r.left == -7
    assert r.top == 8
    assert r.right == 20
    assert r.bottom == -4


def test_layout_rects():
    r1 = Rect(5, 5)
    r2 = Rect(5, 3)
    r3 = Rect(4, 2.5)
    r4 = Rect(4.5, 5)
    r5 = Rect(5, 1)
    r6 = Rect(3.5, 4)
    bound = Rect(15, 5)
    bound.move_top_left_to((0, 10))
    rects = [r1, r2, r3, r4, r5, r6]
    r = Rect.layout_rects(rects, bound, row_wise=True, vert_align="bottom")
    rb = Rect.bounding_rect_from_rects(r)
    assert rb.left == 0
    assert rb.top == 10
    assert rb.right == 14
    assert rb.bottom == 0
    rects = [r1, r2, r3, r4, r5, r6]
    bound = Rect(5, 15)
    bound.move_top_left_to((-20, 20))
    r = Rect.layout_rects(rects, bound, row_wise=False, horz_align="centre")
    rb = Rect.bounding_rect_from_rects(r)


def test_anchored():
    r = Rect(10, 4)
    r1 = r.copy()
    r1.set_size_anchored(12, 3, anchor_pt="top left")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-5, 2)
    assert pt2 == (7, -1)
    r2 = r.copy()
    r2.set_size_anchored(12, 3, anchor_pt="top right")
    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (-7, 2)
    assert pt2 == (5, -1)
    r1 = r.copy()
    r1.set_size_anchored(12, 3, anchor_pt="bottom left")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-5, 1)
    assert pt2 == (7, -2)

    r2 = r.copy()
    r2.set_size_anchored(12, 3, anchor_pt="bottom right")
    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (-7, 1)
    assert pt2 == (5, -2)

    r1 = r.copy()
    r1.set_size_anchored(12, 3, anchor_pt="top")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-6, 2)
    assert pt2 == (6, -1)

    r1 = r.copy()
    r1.set_size_anchored(12, 3, anchor_pt="left")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-5, 1.5)
    assert pt2 == (7, -1.5)

    r1 = r.copy()
    r1.set_size_anchored(12, 3, anchor_pt="centre")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-6, 1.5)
    assert pt2 == (6, -1.5)

    r1 = r.copy()
    r1.set_size_anchored(12, 3, anchor_pt="bottom")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-6, 1)
    assert pt2 == (6, -2)

    r1 = r.copy()
    r1.set_size_anchored(12, 3, anchor_pt="right")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-7, 1.5)
    assert pt2 == (5, -1.5)


def test_anchored():
    r1 = Rect(10, 4)
    r2 = Rect(1, 1)
    r2.move_top_left_to((-20, 20))
    r1.anchor_to_rect(r2, "top left")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-20, 20)
    assert pt2 == (-10, 16)

    r1 = Rect(10, 4)
    r2 = Rect(1, 1)
    r2.move_top_left_to((-20, 20))
    r1.anchor_to_rect(r2, "centre centre")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-24.5, 21.5)
    assert pt2 == (-14.5, 17.5)

    r1 = Rect(10, 4)
    r2 = Rect(1, 1)
    r2.move_top_left_to((-20, 20))
    r1.anchor_with_constraint(r2, "top left to top right")
    pt1 = r1.get_top_left()
    pt2 = r1.get_bottom_right()
    assert pt1 == (-19, 20)
    assert pt2 == (-9, 16)

    r1 = Rect(1, 1)
    r1.move_top_left_to((0, 0))
    r2 = Rect(20, 20)
    r3 = Rect(30, 7)
    r3.move_top_right_to((100, 0))
    r4 = Rect(80, 50)
    r5 = Rect(1, 1)
    r2.anchor_with_constraint(r1, "top left to top right")
    r5.anchor_with_constraint(r2, "top left to bottom left resize")
    r5.anchor_with_constraint(r3, "top right to bottom right resize")
    r4.anchor_with_constraint(r2, "left to left")
    r4.anchor_with_constraint(r5, "below")

    pt1 = r2.get_top_left()
    pt2 = r2.get_bottom_right()
    assert pt1 == (1, 0)
    assert pt2 == (21, -20)

    pt1 = r3.get_top_left()
    pt2 = r3.get_bottom_right()
    assert pt1 == (70, 0)
    assert pt2 == (100, -7)

    pt1 = r4.get_top_left()
    pt2 = r4.get_bottom_right()
    assert pt1 == (1, -20)
    assert pt2 == (81, -70)

    pt1 = r5.get_top_left()
    pt2 = r5.get_bottom_right()
    assert pt1 == (1, -7)
    assert pt2 == (100, -20)

    r6 = Rect(2, 2)
    r6.anchor_with_constraint(r1, "middleof")

    pt1 = r6.get_top_left()
    pt2 = r6.get_bottom_right()
    assert pt1 == (-0.5, 0.5)
    assert pt2 == (1.5, -1.5)


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

#     <Rect (-153.00,28.80)-(-69.81,-43.92)>
# <Rect (-69.81,28.80)-(18.29,-54.00)>
# <Rect (-105.74,112.08)-(105.74,-112.08)>
# <Rect (-57.33,71.16)-(57.33,-71.16)>
# Rects After

# <Rect (-153.00,28.80)-(-44.37,-57.84)>
# <Rect (-44.37,28.80)-(69.17,-72.72)>
# <Rect (-153.00,-195.36)-(58.48,-419.52)>
# <Rect (-153.00,-419.52)-(-38.35,-561.84)>

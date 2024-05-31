# system modules
from math import pi

# my modules
from toolbox import *


def test_point_length():
    a = Point(3, 4)
    assert a.length() == 5


def test_point_func():
    a = Point(5, 8)
    b = a.swapped()
    assert b.y == 5
    assert b.x == 8
    a.move_to(-3, 2)
    assert a.x == -3
    assert a.y == 2


def test_point_rotate():
    a = Point(1, 0)
    b = a.rotate(pi / 2.0)
    b.integerize()
    assert b.x == 0
    assert b.y == 1


def test_point_idx():
    a = Point(3, 5)
    assert a.x == 3
    assert a[0] == 3
    assert a.y == 5
    assert a[1] == 5


def test_grid_2d():
    pts = grid_points_2d(10, 20, 3)
    assert len(pts) == 9
    assert pts[0] == (-5, -10)
    assert pts[1] == (-5, 0)
    assert pts[2] == (-5, 10)
    assert pts[3] == (0, -10)
    assert pts[4] == (0, 0)
    assert pts[5] == (0, 10)
    assert pts[6] == (5, -10)
    assert pts[7] == (5, 0)
    assert pts[8] == (5, 10)
    pts = grid_points_2d(12, -1, 3, 1)
    assert len(pts) == 3
    assert pts[0] == (-6, -1)
    assert pts[1] == (0, -1)
    assert pts[2] == (6, -1)
    pts = grid_points_at_height(20, 4, 3, 3, 2)
    assert len(pts) == 6
    assert pts[0] == (-10, -2, 3)
    assert pts[1] == (-10, 2, 3)
    assert pts[2] == (0, -2, 3)
    assert pts[3] == (0, 2, 3)
    assert pts[4] == (10, -2, 3)
    assert pts[5] == (10, 2, 3)
    pts = [(1, 1), (2, 2), (4, 3), (3, 0)]
    tpts = translate_points(pts, -1, -2)
    assert tpts[0] == (0, -1)
    assert tpts[1] == (1, 0)
    assert tpts[2] == (3, 1)
    assert tpts[3] == (2, -2)


def test_centroid():
    pts = [(1, 1), (2, 2), (4, 3), (3, 0)]
    x, y = centroid_of_points(pts)
    assert x == 2.5
    assert y == 1.5

    pts = [(0, 1, 1), (2, 0, 2), (4, 3, 0), (-1, 3, 0)]
    x, y, z = centroid_of_points(pts)
    assert x == 1.25
    assert y == 1.75
    assert z == 0.75


def test_discretize_line():
    pts = discretize_line((0, 0), (1, 1), 4)
    assert len(pts) == 5
    assert pts[0] == (0, 0)
    assert pts[1] == (0.25, 0.25)
    assert pts[2] == (0.5, 0.5)
    assert pts[3] == (0.75, 0.75)
    assert pts[4] == (1, 1)

    pts = discretize_line((0, 0), (1, 1), [0.1, 0.5, 0.8])
    assert len(pts) == 4
    assert pts[0] == (0, 0)
    assert pts[1] == (0.1, 0.1)
    assert pts[2] == (0.5, 0.5)
    assert pts[3] == (0.8, 0.8)


def test_discretize_poly():
    pts = [(0, 0), (1, 0), (2, 0)]
    vtx = discretize_polyline(pts, 10, keep_all_pts=False)
    assert len(vtx) == 11
    assert vtx[0] == (0, 0)
    assert vtx[1] == (0.2, 0)
    assert vtx[5] == (1.0, 0)
    assert vtx[6] == (1.2, 0)
    assert vtx[9] == (1.8, 0)
    assert vtx[10] == (2.0, 0)

    pts = [(0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.25)]
    vtx = discretize_polyline(pts, 10)
    # print(vtx)


def test_chaining():
    pt = Point(1, 2)
    p0 = pt.move_to(3, 4).translate(-5, 1)
    assert pt.as_tuple() == (3, 4)
    assert p0.as_tuple() == (-2, 5)

    pt = Point(-3, -4)
    p1 = pt.mirror_x().mirror_y().swapped()
    assert p1.as_tuple() == (4, 3)
    assert pt.as_tuple() == (-3, -4)

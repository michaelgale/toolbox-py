# system modules
import copy

# my modules
from toolbox import *


def test_animator_init():
    a1 = Animator(0, 0, 60, 10)
    assert a1.start_frame == 0
    assert a1.stop_frame == 60
    assert a1.start_value == 0
    assert a1.stop_value == 10

    a2 = LinearAnimator(0, -2, 60, 2)
    assert a2.start_frame == 0
    assert a2.stop_frame == 60
    assert a2.start_value == -2
    assert a2.stop_value == 2
    assert a2.frame_len == 60
    assert a2.value_range == 4

    a2 = LinearAnimator(0, -2, 2.0, 2, fps=60)
    assert a2.start_frame == 0
    assert a2.stop_frame == 120
    assert a2.start_value == -2
    assert a2.stop_value == 2
    assert a2.frame_len == 120
    assert a2.value_range == 4

    a2 = LinearAnimator(0, -2, 2.0, 2, fps=60, as_time=True)
    assert a2.start_frame == 0
    assert a2.stop_frame == 120
    assert a2.start_value == -2
    assert a2.stop_value == 2
    assert a2.frame_len == 120
    assert a2.value_range == 4

    a2 = LinearAnimator(30, -2, 60, 2, fps=60, as_frames=True)
    assert a2.start_frame == 30
    assert a2.stop_frame == 60
    assert a2.start_value == -2
    assert a2.stop_value == 2
    assert a2.frame_len == 30
    assert a2.value_range == 4

    a2 = LinearAnimator(30, -2, 60, 2, as_frames=True)
    assert a2.start_frame == 30
    assert a2.stop_frame == 60
    assert a2.start_value == -2
    assert a2.stop_value == 2
    assert a2.frame_len == 30
    assert a2.value_range == 4

    a2 = LinearAnimator(30, -2, 60, 2, as_time=True)
    # will ignore as_time since fps not specified
    assert a2.start_frame == 30
    assert a2.stop_frame == 60
    assert a2.start_value == -2
    assert a2.stop_value == 2
    assert a2.frame_len == 30
    assert a2.value_range == 4

    a3 = EaseInOutAnimator(0, 5, 100, 10)
    assert a3.start_frame == 0
    assert a3.stop_frame == 100
    assert a3.start_value == 5
    assert a3.stop_value == 10
    assert a3.frame_len == 100
    assert a3.value_range == 5
    assert a3.degree == 2

    a4 = OscillateAnimator(0, -3, 100, 3, rate=1.5)
    assert a4.start_frame == 0
    assert a4.stop_frame == 100
    assert a4.start_value == -3
    assert a4.stop_value == 3
    assert a4.frame_len == 100
    assert a4.value_range == 6
    assert a4.rate == 1.5

    a5 = TriangleOscillateAnimator(0, -1, 100, 1, rate=2.5)
    assert a5.start_frame == 0
    assert a5.stop_frame == 100
    assert a5.start_value == -1
    assert a5.stop_value == 1
    assert a5.frame_len == 100
    assert a5.value_range == 2
    assert a5.rate == 2.5

    a6 = SinusoidOscillateAnimator(0, -1.5, 100, 1.5, rate=3)
    assert a6.start_frame == 0
    assert a6.stop_frame == 100
    assert a6.start_value == -1.5
    assert a6.stop_value == 1.5
    assert a6.frame_len == 100
    assert a6.value_range == 3
    assert a6.rate == 3


def test_fixed():
    a1 = FixedValueAnimator(10, 20)
    assert a1.start_frame == 10
    assert a1.stop_frame == 10
    assert a1.start_value == 20
    assert a1.stop_value == 20
    assert a1.frame_len == 0
    assert a1.value_range == 0

    a1 = FixedValueAnimator(10, 20, 60)
    assert a1.start_frame == 10
    assert a1.stop_frame == 60
    assert a1.start_value == 20
    assert a1.stop_value == 20
    assert a1.frame_len == 50
    assert a1.value_range == 0

    a1 = FixedValueAnimator(10, 20, 60, 30)
    assert a1.start_frame == 10
    assert a1.stop_frame == 60
    assert a1.start_value == 20
    assert a1.stop_value == 20
    assert a1.frame_len == 50
    assert a1.value_range == 0

    a1 = FixedValueAnimator(0.5, 15, 1, fps=60)
    assert a1.start_frame == 30
    assert a1.stop_frame == 60
    assert a1.start_value == 15
    assert a1.stop_value == 15
    assert a1.frame_len == 30
    assert a1.value_range == 0


def test_linear():
    a2 = LinearAnimator(20, -2, 60, 2)
    assert a2.start_frame == 20
    assert a2.stop_frame == 60
    assert a2.start_value == -2
    assert a2.stop_value == 2
    assert a2.frame_len == 40
    assert a2.value_range == 4
    assert a2.value_at_frame(0) == -2
    assert a2.value_at_frame(20) == -2
    assert a2.value_at_frame(30) == -1
    assert a2.value_at_frame(40) == 0
    assert a2.value_at_frame(50) == 1
    assert a2.value_at_frame(60) == 2
    assert a2.value_at_frame(80) == 2
    assert a2.value_in_range(0, 0, 10) == 0
    assert a2.value_in_range(20, 0, 10) == 0
    assert a2.value_in_range(30, 0, 10) == 2.5
    assert a2.value_in_range(40, 0, 10) == 5.0
    assert a2.value_in_range(50, 0, 10) == 7.5
    assert a2.value_in_range(60, 0, 10) == 10
    assert a2.value_in_range(80, 0, 10) == 10


def test_easeinout():
    a2 = EaseInOutAnimator(20, 0, 60, 10)
    assert a2.start_frame == 20
    assert a2.stop_frame == 60
    assert a2.start_value == 0
    assert a2.stop_value == 10
    assert a2.frame_len == 40
    assert a2.value_range == 10
    assert a2.value_at_frame(0) == 0
    assert a2.value_at_frame(20) == 0
    assert a2.value_at_frame(30) == 1.25
    assert a2.value_at_frame(40) == 5
    assert a2.value_at_frame(50) == 8.75
    assert a2.value_at_frame(60) == 10
    assert a2.value_at_frame(80) == 10

    a2 = EaseInOutAnimator(20, 5, 60, -5)
    assert a2.start_frame == 20
    assert a2.stop_frame == 60
    assert a2.start_value == 5
    assert a2.stop_value == -5
    assert a2.frame_len == 40
    assert a2.value_range == 10
    assert a2.value_at_frame(0) == 5
    assert a2.value_at_frame(20) == 5
    assert a2.value_at_frame(30) == 3.75
    assert a2.value_at_frame(40) == 0
    assert a2.value_at_frame(50) == -3.75
    assert a2.value_at_frame(60) == -5
    assert a2.value_at_frame(80) == -5
    assert a2[0] == 5
    assert a2[40] == 0
    assert a2[60] == -5


def test_time():
    a2 = LinearAnimator(0.5, -2, 1.5, 2, fps=60)
    assert a2.start_frame == 30
    assert a2.stop_frame == 90
    assert a2.start_value == -2
    assert a2.stop_value == 2
    assert a2.frame_len == 60
    assert a2.value_range == 4
    assert a2.value_at_frame(0) == -2
    assert a2.value_at_frame(30) == -2
    assert a2.value_at_frame(60) == 0
    assert a2.value_at_frame(90) == 2
    assert a2.value_at_frame(120) == 2
    assert a2.value_at_time(0) == -2
    assert a2.value_at_time(0.5) == -2
    assert a2.value_at_time(1.0) == 0
    assert a2.value_at_time(1.5) == 2
    assert a2.value_at_time(2.0) == 2


def test_concatenate():
    a1 = LinearAnimator(0, 1, 30, 5)
    a2 = EaseInOutAnimator(0, 10, 60, 6)
    a3 = LinearAnimator(0, 16, 30, 32)
    bm = concatenate_animators([a1, a2, a3], in_place=False)
    assert len(bm) == 3
    for a, b in zip([a1, a2, a3], bm):
        assert type(a) == type(b)
        assert a.frame_len == b.frame_len
    assert bm[0].start_frame == 0
    assert bm[0].stop_frame == 30
    assert bm[1].start_frame == 30
    assert bm[1].stop_frame == 90
    assert bm[2].start_frame == 90
    assert bm[2].stop_frame == 120


def test_concatenate_inplace():
    a1 = LinearAnimator(0, 1, 30, 5)
    a2 = EaseInOutAnimator(0, 10, 60, 6)
    a3 = LinearAnimator(0, 16, 30, 32)
    bm = concatenate_animators([a1, a2, a3], in_place=True)
    assert len(bm) == 3
    for a, b in zip([a1, a2, a3], bm):
        assert type(a) == type(b)
        assert a.frame_len == b.frame_len
    assert bm[0].start_frame == 0
    assert bm[0].stop_frame == 30
    assert bm[1].start_frame == 30
    assert bm[1].stop_frame == 90
    assert bm[2].start_frame == 90
    assert bm[2].stop_frame == 120


def test_overlap():
    a1 = LinearAnimator(0, 1, 30, 5)
    a2 = EaseInOutAnimator(0, 10, 60, 6)
    a3 = LinearAnimator(0, 16, 30, 32)
    bm = overlap_animators(
        [a1, a2, a3],
        0,
        600,
        pre_stagger=25,
        post_stagger=10,
        stretch_to_fit=True,
        in_place=False,
    )
    assert len(bm) == 3
    for a, b in zip([a1, a2, a3], bm):
        assert type(a) == type(b)
    assert bm[0].start_frame == 0
    assert bm[0].stop_frame == 580
    assert bm[1].start_frame == 25
    assert bm[1].stop_frame == 590
    assert bm[2].start_frame == 50
    assert bm[2].stop_frame == 600

    a1 = LinearAnimator(0, 1, 30, 5)
    a2 = EaseInOutAnimator(0, 10, 60, 6)
    a3 = LinearAnimator(0, 16, 30, 32)
    bm = overlap_animators(
        [a1, a2, a3], 0, pre_stagger=25, stretch_to_fit=False, in_place=False
    )
    assert len(bm) == 3
    for a, b in zip([a1, a2, a3], bm):
        assert type(a) == type(b)
    assert bm[0].start_frame == 0
    assert bm[0].stop_frame == 30
    assert bm[1].start_frame == 25
    assert bm[1].stop_frame == 85
    assert bm[2].start_frame == 50
    assert bm[2].stop_frame == 80


def test_group():
    a1 = LinearAnimator(0, 0, 30, 5)
    a2 = EaseInOutAnimator(0, 5, 60, -5)
    a3 = LinearAnimator(0, -5, 30, 10)
    ag = AnimatorGroup(60, [a1, a2, a3])
    assert ag.start_frame == 60
    assert ag.start_value == 0
    assert ag.stop_frame == 180
    assert ag.stop_value == 10
    assert ag.frame_len == 120
    assert ag.value_range == 10
    assert ag.value_at_frame(0) == 0
    assert ag.value_at_frame(60) == 0
    assert ag.value_at_frame(75) == 2.5
    assert ag.value_at_frame(90) == 5
    assert ag.value_at_frame(120) == 0
    assert ag.value_at_frame(150) == -5
    assert ag.value_at_frame(180) == 10
    assert ag.value_at_frame(160) == 0

    assert ag[0] == 0
    assert ag[75] == 2.5
    assert ag[90] == 5
    assert ag[120] == 0
    assert ag[150] == -5
    assert ag[160] == 0


def test_append():
    a1 = LinearAnimator(0, 0, 30, 5)
    a2 = EaseInOutAnimator(10, 5, 60, -5)
    assert a2.start_frame == 10
    assert a2.stop_frame == 60
    a2.append_to_animator(a1)
    assert a2.start_frame == 40
    assert a2.stop_frame == 90
    a3 = LinearAnimator(0, 2, 35, 4)
    a3.start_after(a2, with_delay=10)
    assert a3.start_frame == 100
    assert a3.stop_frame == 135

    b1 = LinearAnimator(0, 0, 30, 5)
    b2 = EaseInOutAnimator(0, 5, 60, -5)
    b3 = LinearAnimator(0, -5, 30, 10)
    bg = AnimatorGroup(60, [b1, b2, b3], append_to=a3)
    assert bg.start_frame == 195
    assert bg.stop_frame == 315


def test_add():
    a1 = LinearAnimator(0, 0, 30, 5)
    a2 = EaseInOutAnimator(10, 5, 60, -5)
    ag = AnimatorGroup(30, [a1, a2])
    assert len(ag) == 2
    assert ag.start_frame == 30
    assert ag.stop_frame == 110
    a3 = LinearAnimator(0, 2, 35, 4)
    ag += a3
    assert len(ag) == 3
    assert ag.start_frame == 30
    assert ag.stop_frame == 145

    b1 = LinearAnimator(0, 0, 30, 5)
    b2 = EaseInOutAnimator(0, 5, 60, -5)
    b3 = LinearAnimator(0, -5, 30, 10)
    bg = AnimatorGroup(60, [b1, b2, b3])
    cg = ag + bg
    assert len(cg) == 6
    assert cg.start_frame == 30
    assert cg.stop_frame == 265

    a1 = LinearAnimator(20, 0, 75, 2)
    a1 += EaseInOutAnimator(10, 5, 80, -5)
    assert len(a1) == 2
    assert a1.start_frame == 20
    assert a1.stop_frame == 145

    a1 = LinearAnimator(20, 0, 75, 2)
    a1 += 20
    assert a1.stop_frame == 95
    a1 += EaseInOutAnimator(10, 5, 80, -5)
    assert len(a1) == 3
    assert a1.start_frame == 20
    assert a1.stop_frame == 165


def test_link():
    a1 = LinearAnimator(0, 0, 30, 5)
    a2 = EaseInOutAnimator(10, 5, 60, -5)
    assert a2.start_frame == 10
    assert a2.stop_frame == 60
    a2.link_to_animator(a1)
    assert a2.start_frame == 0
    assert a2.stop_frame == 30

    a1 = LinearAnimator(0, 0, 30, 5)
    a2 = EaseInOutAnimator(0, 5, 60, -5)
    a3 = LinearAnimator(0, -5, 30, 10)
    ag = AnimatorGroup(60, [a1, a2, a3])
    assert ag.start_frame == 60
    assert ag.stop_frame == 180
    assert ag.frame_len == 120
    am = LinearAnimator(100, 0, 200, 1)
    ag.link_to_animator(am)
    assert ag.start_frame == 100
    assert ag.stop_frame == 200
    assert ag.frame_len == 100

    b1 = LinearAnimator(0, 0, 15, 7)
    b2 = EaseInOutAnimator(0, 7, 60, 14)
    bg = AnimatorGroup(0, [b1, b2])
    assert bg.start_frame == 0
    assert bg.stop_frame == 75
    assert bg.frame_len == 75
    bg.link_to_animator(ag)
    assert bg.start_frame == 100
    assert bg.stop_frame == 200
    assert bg.frame_len == 100


def test_link_prev():
    a1 = EaseInOutAnimator(0, 0, 30, 5)
    a2 = LinearAnimator(0, 0, 60, 0, offset_from_previous=20)
    ag = AnimatorGroup(10, [a1, a2])
    assert len(ag) == 2
    assert ag.start_frame == 10
    assert ag.stop_frame == 100
    assert a2.link_to_previous == True
    assert a2.offset_from_previous == 20
    assert ag[10] == 0
    assert ag[40] == 5
    assert ag[70] == 15
    assert ag[100] == 25


def test_link_value_prev():
    a1 = EaseInOutAnimator(0, 0, 30, 5)
    a2 = LinearAnimator(0, 0, 60, 0, value_from_previous=20)
    ag = AnimatorGroup(10, [a1, a2])
    assert len(ag) == 2
    assert ag.start_frame == 10
    assert ag.stop_frame == 100
    assert a2.link_to_previous == True
    assert a2.value_from_previous == 20
    assert ag[10] == 0
    assert ag[40] == 5
    assert ag[70] == 12.5
    assert ag[100] == 20

# system modules
import copy
import pytest

# my modules
from toolbox import *

IMAGE1 = "./testfiles/image1.png"
IMAGE2 = "./testfiles/image2.png"


def almost_same(x, y):
    if isinstance(x, (list, tuple)):
        if any([abs(x[i] - y[i]) > 1e-3 for i in range(3)]):
            return False
    else:
        if abs(x - y) > 1e-3:
            return False
    return True


def test_image_init():
    hsv1 = ImageMixin.hsv_image(IMAGE1)
    assert hsv1.size == 201960
    assert hsv1.shape == (220, 306, 3)
    hr = ImageMixin.hue_range(hsv1)
    sr = ImageMixin.sat_range(hsv1)
    br = ImageMixin.brightness_range(hsv1)
    assert almost_same(hr, (0, 2.540, 120))
    assert almost_same(sr, (0, 10.625, 255))
    assert almost_same(br, (0, 185.461, 255))


def test_image_pad():
    img1 = ImageMixin.open_image(IMAGE1)
    img2 = ImageMixin.pad_image(img1, 10)
    assert img1.shape == (220, 306, 4)
    assert img2.shape == (240, 326, 4)

    img3 = ImageMixin.pad_image(IMAGE1, 10)
    assert img3.shape == (240, 326, 4)


def test_image_crop():
    img1 = ImageMixin.open_image(IMAGE1)
    img2 = ImageMixin.crop_image(img1, (10, 10), (100, 100))
    assert img1.shape == (220, 306, 4)
    assert img2.shape == (90, 90, 4)
    ImageMixin.save_image("./testfiles/crop.png", img2)

    img2 = ImageMixin.crop_image(img1, (-20, -20), (400, 100))
    assert img1.shape == (220, 306, 4)
    assert img2.shape == (120, 420, 4)
    assert ImageMixin.image_size(img2) == (420, 120)
    ImageMixin.save_image("./testfiles/crop2.png", img2)


def test_image_crop_fit():
    img1 = ImageMixin.open_image(IMAGE1)
    img2 = ImageMixin.crop_image(img1, (10, 10), (150, 150))
    assert img1.shape == (220, 306, 4)
    assert img2.shape == (140, 140, 4)
    img3 = ImageMixin.crop_to_fit_other(img1, img2)
    assert img3.shape == (140, 140, 4)
    ImageMixin.save_image("./testfiles/cropfit1.png", img3)

    img1 = ImageMixin.open_image(IMAGE1)
    img2 = ImageMixin.crop_image(img1, (10, 10), (100, 100))
    assert img1.shape == (220, 306, 4)
    assert img2.shape == (90, 90, 4)
    img4 = ImageMixin.crop_to_fit_other(img2, img1)
    assert img4.shape == (220, 306, 4)
    ImageMixin.save_image("./testfiles/cropfit2.png", img4)


def test_image_thr():
    img1 = ImageMixin.open_image(IMAGE1)
    thr_img, mask = ImageMixin.hue_threshold_image(
        img1, hue=0, hue_window=40, sat_thr=40, int_thr=40, gray_thr=20
    )
    assert thr_img.shape == (220, 306)
    assert mask.shape == (220, 306)

    con1 = ImageMixin.find_contours(thr_img)
    assert len(con1) == 1
    assert len(con1[0]) == 13
    assert [210, 83] in con1[0] or [210, 82] in con1[0] or [210, 81] in con1[0]

    m1, g1 = ImageMixin.get_moments(con1, 100, 10)
    assert len(m1) == 1
    assert len(g1) == 1
    assert m1[0]["m00"] == 1292.5
    assert g1[0]["area"] == 1292.5
    assert almost_same(g1[0]["perimeter"], 170.267)

    c1 = ImageMixin.centroids_from_moments(m1)
    assert len(c1) == 1
    assert c1[0] == (226, 75)

    assert img1.shape == (220, 306, 4)
    c2 = ImageMixin.get_centroids_of_hue(
        img1, 0, hue_window=20, area_thr=100, dim_thr=20
    )
    assert len(c2) == 1
    assert c2[0] == (226, 75)


def ch_range(img):
    return [ImageMixin.channel_range(img, i) for i in range(3)]


def mag_diff(hsvx, hsvy):
    d1 = 0
    for x, y in zip(ch_range(hsvx), ch_range(hsvy)):
        d1 += sum([(x[i] - y[i]) * (x[i] - y[i]) for i in range(3)])
    return d1


def test_channels():
    img1 = ImageMixin.open_image(IMAGE1)
    cr1 = ch_range(img1)
    assert almost_same(cr1[0], (0, 180.559, 255))

    hsv1 = ImageMixin.hsv_image(img1)
    cr2 = ch_range(hsv1)
    assert almost_same(cr2[0], (0, 2.540, 120))

    bgr3 = ImageMixin.bgr_image(hsv1)
    cr3 = ch_range(bgr3)
    assert almost_same(cr3[0], (0, 180.559, 255))
    assert mag_diff(img1, bgr3) < 1e-3


def test_normhue():
    img1 = ImageMixin.open_image(IMAGE1)
    hsv1 = ImageMixin.hsv_image(img1)

    img2 = ImageMixin.open_image(IMAGE2)
    hsv2 = ImageMixin.hsv_image(img2)
    br2 = ImageMixin.brightness_range(hsv2)
    hr2 = ImageMixin.hue_range(hsv2)
    sr2 = ImageMixin.sat_range(hsv2)
    assert almost_same(hr2, (0, 2.610, 120))
    assert almost_same(sr2, (0, 10.455, 255))
    assert almost_same(br2, (0, 183.919, 255))

    n3 = ImageMixin.normalize_hue(img2, 0)
    assert n3.shape == (220, 306, 4)
    hsv3 = ImageMixin.hsv_image(n3)
    hr3 = ImageMixin.hue_range(hsv3)
    br3 = ImageMixin.brightness_range(hsv3)
    sr3 = ImageMixin.sat_range(hsv3)
    assert almost_same(hr3, (0, 2.610, 120))
    assert almost_same(sr3, (0, 10.469, 255))
    assert almost_same(br3, (0, 185.186, 255))

    n4 = ImageMixin.normalize_hue(img2, 0, norm_brightness=255)
    assert n4.shape == (220, 306, 4)
    hsv4 = ImageMixin.hsv_image(n4)
    hr4 = ImageMixin.hue_range(hsv4)
    br4 = ImageMixin.brightness_range(hsv4)
    sr4 = ImageMixin.sat_range(hsv4)
    assert almost_same(hr4, (0, 2.610, 120))
    assert almost_same(sr4, (0, 10.474, 255))
    assert almost_same(br4, (0, 185.427, 255))

    d11 = mag_diff(hsv1, hsv1)
    d21 = mag_diff(hsv2, hsv1)
    d31 = mag_diff(hsv3, hsv1)
    d41 = mag_diff(hsv4, hsv1)
    assert d11 == 0
    assert almost_same(d21, 2.411)
    assert almost_same(d31, 0.105)
    assert almost_same(d41, 0.029)


def test_count_trans():
    img1 = ImageMixin.open_image(IMAGE1)
    img2 = ImageMixin.crop_image(img1, (5, 5), (310, 230))
    ImageMixin.save_image("./testfiles/count.png", img2)
    counts = ImageMixin.count_transparent_pixels(img2)
    assert counts["top_left"] == 55
    assert counts["top_right"] == 679
    assert counts["bottom_left"] == 1639
    assert counts["bottom_right"] == 2244
    assert counts["total"] == 4617
    assert counts["min"] == "top_left"
    assert counts["max"] == "bottom_right"

    c2 = ImageMixin.count_transparent_pixels("./testfiles/count.png")
    assert counts == c2

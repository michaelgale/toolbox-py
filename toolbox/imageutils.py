#! /usr/bin/env python3
#
# Copyright (C) 2023  Michael Gale

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
# Image Processing Utilities
#

import cv2
import math
import numpy as np

from .datautils import clamp_value


class ImageMixin:
    """This class adds image processing and manipulation utilities either standalone
    or as a Mixin for another class.
    """

    @staticmethod
    def auto_open(img):
        """Returns an opened image if passed a file path or passthru an image.
        This is a convenience method to allow functions to be passed an array or filename.
        """
        if isinstance(img, str):
            return ImageMixin.open_image(img)
        return img

    @staticmethod
    def open_image(fn):
        img = np.array(cv2.imread(fn, cv2.IMREAD_UNCHANGED))
        return img

    @staticmethod
    def save_image(fn, img):
        cv2.imwrite(fn, img)

    @staticmethod
    def image_size(img):
        """Returns image size as width x height"""
        img = ImageMixin.auto_open(img)
        return img.shape[1], img.shape[0]

    @staticmethod
    def channel_range(img, ch):
        """Returns the minimum, average, maximum value of an image channel"""
        img = ImageMixin.auto_open(img)
        if len(img.shape) == 2:
            v = np.array(img)
        else:
            v = np.array(img[:, :, ch])
        value = np.sum(v)
        pix = img.shape[0] * img.shape[1]
        return np.min(v), value / pix, np.max(v)

    @staticmethod
    def brightness_range(img):
        """Returns HSV image brightness range"""
        img = ImageMixin.auto_open(img)
        return ImageMixin.channel_range(img, 2)

    @staticmethod
    def hue_range(img):
        """Returns HSV image hue range"""
        img = ImageMixin.auto_open(img)
        return ImageMixin.channel_range(img, 0)

    @staticmethod
    def sat_range(img):
        """Returns HSV image saturation range"""
        img = ImageMixin.auto_open(img)
        return ImageMixin.channel_range(img, 1)

    @staticmethod
    def pad_image(img, width, val=None, top=True, left=True, bottom=True, right=True):
        """Pads an image perimenter by width pixels"""
        img = ImageMixin.auto_open(img)

        if len(img.shape) > 2:
            if val is not None:
                pad = val
            else:
                pad = tuple(list([0 for _ in range(img.shape[2])]))
        else:
            pad = val if val is not None else 0
        p = int(width)
        pt = p if top else 0
        pl = p if left else 0
        pb = p if bottom else 0
        pr = p if right else 0
        r = cv2.copyMakeBorder(img, pt, pb, pl, pr, cv2.BORDER_CONSTANT, value=pad)
        return r

    @staticmethod
    def pad_to_fit(img, x1, x2, y1, y2, val=None):
        img = ImageMixin.auto_open(img)
        if len(img.shape) > 2:
            if val is not None:
                pad = val
            else:
                pad = tuple(list([0 for _ in range(img.shape[2])]))
        else:
            pad = val if val is not None else 0
        img = cv2.copyMakeBorder(
            img,
            -min(0, y1),
            max(y2 - img.shape[0], 0),
            -min(0, x1),
            max(x2 - img.shape[1], 0),
            cv2.BORDER_CONSTANT,
            value=pad,
        )
        y2 += -min(0, y1)
        y1 += -min(0, y1)
        x2 += -min(0, x1)
        x1 += -min(0, x1)
        return img, x1, x2, y1, y2

    @staticmethod
    def crop_image(img, top_left, bottom_right):
        """Crops an image. Adds padding for cropping beyond image size."""
        img = ImageMixin.auto_open(img)
        x1, y1 = int(top_left[0]), int(top_left[1])
        x2, y2 = int(bottom_right[0]), int(bottom_right[1])
        if x1 < 0 or y1 < 0 or x2 > img.shape[1] or y2 > img.shape[0]:
            img, x1, x2, y1, y2 = ImageMixin.pad_to_fit(img, x1, x2, y1, y2)
        if len(img.shape) > 2:
            return img[y1:y2, x1:x2, :]
        return img[y1:y2, x1:x2]

    @staticmethod
    def crop_to_content(img, bg=None, tol=4, widthwise=True, heightwise=True):
        """Crops an image to the bounding box of content using either
        a provided background colour or the top left pixel colour."""
        img = ImageMixin.auto_open(img)
        thr = bg if bg is not None else img[0, 0]
        thr_l = tuple(int(clamp_value(thr[i] - tol, 0, 255)) for i in range(3))
        thr_h = tuple(int(clamp_value(thr[i] + tol, 0, 255)) for i in range(3))
        thresh = cv2.inRange(img, thr_l, thr_h)
        thresh = 255 - thresh
        x, y, w, h = cv2.boundingRect(thresh)
        hh, ww, _ = img.shape
        y0 = y if heightwise else 0
        x0 = x if widthwise else 0
        yl = h if heightwise else hh
        xl = w if widthwise else ww
        img = img[y0 : y0 + yl, x0 : x0 + xl]
        return img

    @staticmethod
    def crop_to_fit_other(img, other):
        """Crops img to fit the dimensions of other"""
        img = ImageMixin.auto_open(img)
        other = ImageMixin.auto_open(other)
        img_width, img_height = img.shape[1], img.shape[0]
        other_width, other_height = other.shape[1], other.shape[0]
        width_diff = other_width - img_width
        height_diff = other_height - img_height
        pad_left = int(width_diff / 2)
        pad_right = width_diff - pad_left
        pad_top = int(height_diff / 2)
        pad_bottom = height_diff - pad_top
        left = -pad_left
        top = -pad_top
        right = img_width + pad_right
        bottom = img_height + pad_bottom
        img = ImageMixin.crop_image(img, (left, top), (right, bottom))
        return img

    @staticmethod
    def hsv_image(img):
        """Returns the HSV colour space representation of an image"""
        img = ImageMixin.auto_open(img)
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    @staticmethod
    def bgr_image(img):
        """Returns the BGR colour space representation of an image"""
        img = ImageMixin.auto_open(img)
        return cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

    @staticmethod
    def hue_threshold_image(img, hue, hue_window, sat_thr, int_thr, gray_thr):
        """Threshold an image based on a window of hue values.
        Returns the thresholded image and a mask"""
        img = ImageMixin.auto_open(img)
        if img is None:
            raise ValueError("Loading image resulting in an invalid image")
        hsv = ImageMixin.hsv_image(img)
        w = int(hue_window / 2)
        hue_low, hue_high = hue - w, hue + w
        sl, sh = sat_thr, 255
        vl, vh = int_thr, 255
        if hue_low < 0:
            mask1 = cv2.inRange(hsv, (0, sl, vl), (hue_high, sh, vh))
            mask2 = cv2.inRange(hsv, (180 + hue_low, sl, vl), (180, sh, vh))
            mask = cv2.bitwise_or(mask1, mask2)
        elif hue_high > 180:
            mask1 = cv2.inRange(hsv, (hue_low, sl, vl), (180, sh, vh))
            mask2 = cv2.inRange(hsv, (0, sl, vl), ((hue_high - 180), sh, vh))
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = cv2.inRange(hsv, (hue_low, sl, vl), (hue_high, sh, vh))
        region = cv2.bitwise_and(img, img, mask=mask)
        if region.shape[2] == 4:
            gray_image = cv2.cvtColor(region, cv2.COLOR_BGRA2GRAY)
        else:
            gray_image = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        _, thr_image = cv2.threshold(gray_image, gray_thr, 255, 0)
        return thr_image, mask

    @staticmethod
    def find_contours(thr_img):
        """Finds constant contours of contrast in an image.
        Returns a list of contour outlines."""
        contours, hierarchy = cv2.findContours(
            thr_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours

    @staticmethod
    def get_moments(contours, area_thr, dim_thr):
        """Finds the moments of constant contours of contrast in an image.
        Returns moments and a dictionary of geometric info for each contour"""
        moments = []
        info = []
        for c in contours:
            if cv2.contourArea(c) < area_thr:
                continue
            geo = {
                "area": cv2.contourArea(c),
                "perimeter": cv2.arcLength(c, True),
                "convex": cv2.isContourConvex(c),
                "rect": cv2.minAreaRect(c),
            }
            if geo["rect"][1][0] < dim_thr and geo["rect"][1][1] < dim_thr:
                continue
            moments.append(cv2.moments(c))
            info.append(geo)
        return moments, info

    @staticmethod
    def centroids_from_moments(moments):
        """Finds the centroids of contoured regions.
        Returns the centroid coordinate pairs."""
        centroids = []
        for m in moments:
            m00 = m["m00"]
            if not abs(m00) > 0:
                continue
            cx = int(m["m10"] / m00)
            cy = int(m["m01"] / m00)
            centroids.append((cx, cy))
        return centroids

    @staticmethod
    def get_centroids_of_hue(
        img,
        hue,
        hue_window=20,
        area_thr=1500,
        dim_thr=100,
        sat_thr=40,
        int_thr=40,
        gray_thr=20,
    ):
        """Finds the centroids of a particular hue from an image."""
        img = ImageMixin.auto_open(img)
        thr_img, mask = ImageMixin.hue_threshold_image(
            img, hue, hue_window, sat_thr, int_thr, gray_thr
        )
        contours = ImageMixin.find_contours(thr_img)
        mom, geo = ImageMixin.get_moments(contours, area_thr, dim_thr)
        return ImageMixin.centroids_from_moments(mom)

    @staticmethod
    def normalize_hue(img, hue, norm_brightness=None, hue_window=8):
        """Normalize a hue value to a maximum constant value."""
        img = ImageMixin.auto_open(img)
        _, mask = ImageMixin.hue_threshold_image(
            img, hue, hue_window=hue_window, sat_thr=128, int_thr=128, gray_thr=32
        )
        hsv_img = ImageMixin.hsv_image(img)
        x = np.copy(hsv_img)
        x[mask == 0] = [0, 0, 0]
        _, _, mb = ImageMixin.brightness_range(x)
        mb = mb if norm_brightness is None else norm_brightness
        x[:, :, 2] = mb
        y = cv2.cvtColor(x, cv2.COLOR_HSV2BGR)
        a = np.zeros_like(img)
        a[:, :, 0] = y[:, :, 0]
        a[:, :, 1] = y[:, :, 1]
        a[:, :, 2] = y[:, :, 2]
        if img.shape[2] == 4:
            a[:, :, 3] = 255
        z = np.copy(img)
        z[mask > 0] = a[mask > 0]
        return z

    @staticmethod
    def first_non_transparent_edge(img, pos, edge=None, thr=0):
        """Returns the coordinate of the first non-transparent pixel
        from any of the top, left, bottom, right edges along a strip
        of pixels at pos."""
        img = ImageMixin.auto_open(img)
        width, height = ImageMixin.image_size(img)
        xinc, yinc = 0, 0
        if isinstance(pos, (tuple, list)):
            xpos, ypos = int(pos[0]), int(pos[1])
        else:
            xpos, ypos = int(pos), int(pos)
        if edge.lower() == "left":
            x0, x1, y, xinc = 0, width - 1, ypos, 1
        elif edge.lower() == "right":
            x0, x1, y, xinc = width - 1, 0, ypos, -1
        elif edge.lower() == "top":
            x, y0, y1, yinc = xpos, 0, height - 1, 1
        elif edge.lower() == "bottom":
            x, y0, y1, yinc = xpos, height - 1, 0, -1
        if xinc:
            for xo in range(x0, x1, xinc):
                if img[y, xo, 3] > thr:
                    return xo, y
        if yinc:
            for yo in range(y0, y1, yinc):
                if img[yo, x, 3] > thr:
                    return x, yo
        return None

    @staticmethod
    def count_transparent_pixels(img, region=None):
        img = ImageMixin.auto_open(img)
        width, height = ImageMixin.image_size(img)
        w2 = int(width / 2)
        h2 = int(height / 2)
        counts = {
            "top_left": sum(sum(img[0:h2, 0:w2, 3] == 0)),
            "top_right": sum(sum(img[0:h2, w2:width, 3] == 0)),
            "bottom_left": sum(sum(img[h2:height, 0:w2, 3] == 0)),
            "bottom_right": sum(sum(img[h2:height, w2:width, 3] == 0)),
        }
        max_val = max(counts.values())
        min_val = min(counts.values())
        min_key = None
        max_key = None
        for k, v in counts.items():
            if v == max_val:
                max_key = k
            elif v == min_val:
                min_key = k
        counts["min"] = min_key
        counts["max"] = max_key
        counts["total"] = sum(
            [
                counts[x]
                for x in ["top_left", "top_right", "bottom_left", "bottom_right"]
            ]
        )
        return counts

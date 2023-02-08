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


class ImageMixin:
    """This class adds image processing and manipulation utilities either standalone
    or as a Mixin for another class.
    """

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
        return img.shape[1], img.shape[0]

    @staticmethod
    def channel_range(img, ch):
        """Returns the minimum, average, maximum value of an image channel"""
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
        return ImageMixin.channel_range(img, 2)

    @staticmethod
    def hue_range(img):
        """Returns HSV image hue range"""
        return ImageMixin.channel_range(img, 0)

    @staticmethod
    def sat_range(img):
        """Returns HSV image saturation range"""
        return ImageMixin.channel_range(img, 1)

    @staticmethod
    def pad_image(img, width):
        """Pads an image perimenter by width pixels"""
        pad = (0, 0, 0) if img.shape[2] == 3 else (0, 0, 0, 0)
        p = int(width)
        r = cv2.copyMakeBorder(img, p, p, p, p, cv2.BORDER_CONSTANT, value=pad)
        return r

    @staticmethod
    def hsv_image(img):
        """Returns the HSV colour space representation of an image"""
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    @staticmethod
    def bgr_image(img):
        """Returns the BGR colour space representation of an image"""
        return cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

    @staticmethod
    def hue_threshold_image(img, hue, hue_window, sat_thr, int_thr, gray_thr):
        """Threshold an image based on a window of hue values.
        Returns the thresholded image and a mask"""
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
    def get_centroids(moments):
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
    def normalize_hue(img, hue, norm_brightness=None):
        """Normalize a hue value to a maximum constant value."""
        thr_img, mask = ImageMixin.hue_threshold_image(
            img, hue, hue_window=8, sat_thr=128, int_thr=128, gray_thr=32
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

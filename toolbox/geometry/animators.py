#! /usr/bin/env python3
#
# Copyright (C) 2022  Michael Gale
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
# Animation helper classes for general purpose parametric motion
#

import copy

from math import cos, sin, pi


class Animator:
    """Animator base class
    This is a utility class for "animating" or modulating a value across
    "frames" between a start and stop frame. It is analogous to key
    frame based animation typical of video or rendering tasks.
    Normally, time is internally represented in unitless frames. However,
    if the fps attribute is specified, then time is can be referenced in
    units of seconds when specifying the start/stop frames.  Internally,
    frames are always used for computation, and methods for accessing value
    are explicit as 'value_at_frame' or 'value_at_time'."""

    def __init__(
        self,
        start_frame,
        start_value,
        stop_frame,
        stop_value,
        fps=None,
        append_to=None,
        as_frames=None,
        as_time=None,
        offset_from_previous=None,
        value_from_previous=None,
    ):
        self.fps = fps
        use_frames = not as_time and (as_frames is not None and as_frames)
        use_time = (fps is not None) and (as_time or not use_frames)
        if use_time:
            self.start_frame = start_frame * fps
            self.stop_frame = stop_frame * fps
        else:
            self.start_frame = start_frame
            self.stop_frame = stop_frame
        self.start_value = start_value
        self.stop_value = stop_value
        self.curr_frame = 0
        self.curr_value = 0
        self.link_to_previous = False
        self.offset_from_previous = 0
        self.value_from_previous = None
        if offset_from_previous is not None:
            self.link_to_previous = True
            self.offset_from_previous = offset_from_previous
        elif value_from_previous is not None:
            self.link_to_previous = True
            self.value_from_previous = value_from_previous
        if append_to is not None:
            self.append_to_animator(append_to)

    def __str__(self):
        s = []
        s.append(
            "%20s start: %3d (%7.2f) -> stop: %3d (%7.2f) frames: %3d range: %.2f %s"
            % (
                type(self).__name__,
                self.start_frame,
                self.start_value,
                self.stop_frame,
                self.stop_value,
                self.frame_len,
                self.value_range,
                "L" if self.link_to_previous else "",
            )
        )
        return "".join(s)

    def _add(self, other):
        new_group = AnimatorGroup(self.start_frame, [self])
        new_group.fps = self.fps
        return new_group + other

    def __add__(self, other):
        return self._add(other)

    def __radd__(self, other):
        return self._add(other)

    def __iadd__(self, other):
        return self._add(other)

    def __getitem__(self, key):
        """Convenient syntax sugar equivalent of value_at_frame."""
        return self.value_at_frame(key)

    def add_animator(self, other, with_delay=0):
        """Performs a concatenation with another animator to make a resulting animator group"""
        new_group = AnimatorGroup(self.start_frame, [self])
        new_group.fps = self.fps
        new_group = new_group.add_animator(other, with_delay=with_delay)
        return new_group

    @property
    def frame_len(self):
        return self.stop_frame - self.start_frame

    @property
    def value_range(self):
        return abs(self.stop_value - self.start_value)

    @property
    def signed_value_range(self):
        r = abs(self.stop_value - self.start_value)
        if self.stop_value < self.start_value:
            return -r
        return r

    def is_active(self, curr_frame=None):
        if curr_frame is not None:
            self.curr_frame = curr_frame
        if self.curr_frame < self.start_frame:
            return False
        elif self.curr_frame > self.stop_frame:
            return False
        return True

    def value_at_time(self, t):
        if self.fps is None:
            raise ValueError("value_at_time cannot be used without specified fps")
        return self.value_at_frame(t * self.fps)

    def value_in_range(self, t, min_value, max_value):
        """Returns a value within a different range than configured in this
        animator. This is useful for computing other values linked to the
        same animator frame extents."""
        tmp_min, tmp_max = self.start_value, self.stop_value
        self.start_value, self.stop_value = min_value, max_value
        value = self.value_at_frame(t)
        self.start_value, self.stop_value = tmp_min, tmp_max
        return value

    def link_to_animator(self, animator):
        """Links our start and stop frame to another animator start and stop."""
        self.start_frame = animator.start_frame
        self.stop_frame = animator.stop_frame

    def append_to_animator(self, animator, with_delay=0):
        """Make our start frame at the end of the other animator"""
        fl = self.frame_len
        self.start_frame += animator.stop_frame + with_delay
        self.stop_frame = self.start_frame + fl

    def start_after(self, other, with_delay=0):
        """Synonymous with append_to_animator, i.e. start after another animator"""
        self.append_to_animator(other, with_delay=with_delay)

    def set_frame_len(self, frame):
        self.stop_frame = self.start_frame + frame


class LinearAnimator(Animator):
    """Value animator with linear value changes"""

    def __init__(
        self, start_frame, start_value, stop_frame, stop_value, fps=None, **kwargs
    ):
        super().__init__(
            start_frame, start_value, stop_frame, stop_value, fps=fps, **kwargs
        )

    def value_at_frame(self, frame=None):
        if frame is not None:
            self.curr_frame = frame
        if self.curr_frame <= self.start_frame:
            self.curr_value = self.start_value
        elif self.curr_frame >= self.stop_frame:
            self.curr_value = self.stop_value
        else:
            self.curr_value = (
                self.start_value
                + (self.curr_frame - self.start_frame)
                / self.frame_len
                * self.signed_value_range
            )
        return self.curr_value


class FixedValueAnimator(Animator):
    """Value animator which returns a fixed value."""

    def __init__(
        self,
        start_frame,
        start_value,
        stop_frame=None,
        stop_value=None,
        fps=None,
        **kwargs
    ):
        if stop_frame is None:
            stop_frame = start_frame
        super().__init__(
            start_frame, start_value, stop_frame, start_value, fps=fps, **kwargs
        )

    def value_at_frame(self, frame=None):
        if frame is not None:
            self.curr_frame = frame
        self.curr_value = self.start_value
        return self.curr_value


class EaseInAnimator(Animator):
    """Value animator with soft ease in smoothing."""

    def __init__(
        self,
        start_frame,
        start_value,
        stop_frame,
        stop_value,
        degree=None,
        fps=None,
        **kwargs
    ):
        super().__init__(
            start_frame, start_value, stop_frame, stop_value, fps=fps, **kwargs
        )
        self.degree = degree if degree is not None else 2

    def value_at_frame(self, frame=None):
        if frame is not None:
            self.curr_frame = frame
        if self.curr_frame <= self.start_frame:
            self.curr_value = self.start_value
        elif self.curr_frame >= self.stop_frame:
            self.curr_value = self.stop_value
        else:
            tn = (self.curr_frame - self.start_frame) / self.frame_len
            rt = pow(tn, self.degree)
            self.curr_value = self.start_value + rt * self.signed_value_range
        return self.curr_value


class EaseOutAnimator(Animator):
    """Value animator with soft ease out smoothing."""

    def __init__(
        self,
        start_frame,
        start_value,
        stop_frame,
        stop_value,
        degree=None,
        fps=None,
        **kwargs
    ):
        super().__init__(
            start_frame, start_value, stop_frame, stop_value, fps=fps, **kwargs
        )
        self.degree = degree if degree is not None else 2

    def value_at_frame(self, frame=None):
        if frame is not None:
            self.curr_frame = frame
        if self.curr_frame <= self.start_frame:
            self.curr_value = self.start_value
        elif self.curr_frame >= self.stop_frame:
            self.curr_value = self.stop_value
        else:
            tn = (self.curr_frame - self.start_frame) / self.frame_len
            rt = 1.0 - abs(pow(tn - 1.0, self.degree))
            self.curr_value = self.start_value + rt * self.signed_value_range
        return self.curr_value


class EaseInOutAnimator(Animator):
    """Value animator with soft ease in and ease out smoothing."""

    def __init__(
        self,
        start_frame,
        start_value,
        stop_frame,
        stop_value,
        degree=None,
        fps=None,
        **kwargs
    ):
        super().__init__(
            start_frame, start_value, stop_frame, stop_value, fps=fps, **kwargs
        )
        self.degree = degree if degree is not None else 2

    def value_at_frame(self, frame=None):
        if frame is not None:
            self.curr_frame = frame
        if self.curr_frame <= self.start_frame:
            self.curr_value = self.start_value
        elif self.curr_frame >= self.stop_frame:
            self.curr_value = self.stop_value
        else:
            tn = (self.curr_frame - self.start_frame) / self.frame_len
            rt = (
                0.5 * pow(2 * tn, self.degree)
                if tn < 0.5
                else 0.5 * (1.0 - abs(pow(2 * tn - 2, self.degree))) + 0.5
            )
            self.curr_value = self.start_value + rt * self.signed_value_range
        return self.curr_value


class OscillateAnimator(Animator):
    """Value animator which oscillates between two values with adjustable rate."""

    def __init__(
        self, start_frame, start_value, stop_frame, stop_value, rate, fps=None, **kwargs
    ):
        super().__init__(
            start_frame, start_value, stop_frame, stop_value, fps=fps, **kwargs
        )
        self.rate = rate


class TriangleOscillateAnimator(OscillateAnimator):
    """Value animator which oscillates linearly between values."""

    def __init__(
        self, start_frame, start_value, stop_frame, stop_value, rate, fps=None, **kwargs
    ):
        super().__init__(
            start_frame, start_value, stop_frame, stop_value, rate, fps=fps, **kwargs
        )
        self.dir = 1
        self.increment = 0

    def value_at_frame(self, frame=None):
        if frame is not None:
            self.curr_frame = frame
        if self.curr_frame <= self.start_frame:
            self.curr_value = self.start_value
            self.increment = (
                self.rate if self.start_value < self.stop_value else -self.rate
            )
        elif self.curr_frame >= self.stop_frame:
            pass
        else:
            if self.dir > 0:
                # moving from start to stop
                self.curr_value += self.increment
            elif self.dir < 0:
                # moving stop to start
                self.curr_value -= self.increment
            if self.increment > 0:
                if self.curr_value >= self.stop_value:
                    self.dir = -self.dir
                elif self.curr_value <= self.start_value:
                    self.dir = -self.dir
            else:
                if self.curr_value <= self.stop_value:
                    self.dir = -self.dir
                elif self.curr_value >= self.start_value:
                    self.dir = -self.dir
        return self.curr_value


class SinusoidOscillateAnimator(OscillateAnimator):
    """A value animator which sinusoidally oscillates between values."""

    def __init__(
        self, start_frame, start_value, stop_frame, stop_value, rate, fps=None, **kwargs
    ):
        super().__init__(
            start_frame, start_value, stop_frame, stop_value, rate, fps=fps, **kwargs
        )

    def value_at_frame(self, frame=None):
        if frame is not None:
            self.curr_frame = frame
        if self.curr_frame <= self.start_frame:
            self.curr_value = self.start_value
        elif self.curr_frame >= self.stop_frame:
            self.curr_value = self.start_value + self.signed_value_range * (
                0.5 - 0.5 * cos(2 * pi * self.rate)
            )
        else:
            tn = (self.curr_frame - self.start_frame) / self.frame_len
            self.curr_value = self.start_value + self.signed_value_range * (
                0.5 - 0.5 * cos(2 * pi * self.rate * tn)
            )
        return self.curr_value


class AnimatorGroup:
    """A group of concatenated animators represented as a single animator."""

    def __init__(
        self,
        start_frame,
        animators,
        fps=None,
        append_to=None,
        as_frames=None,
        as_time=None,
    ):
        self.fps = fps
        use_frames = not as_time and (as_frames is not None and as_frames)
        use_time = (fps is not None) and (as_time or not use_frames)
        if use_time:
            self.start_frame = start_frame * fps
        else:
            self.start_frame = start_frame
        self.curr_frame = 0
        self.curr_value = 0
        self.animators = concatenate_animators(
            animators, start_frame=start_frame, fps=fps, in_place=False
        )
        if append_to is not None:
            self.append_to_animator(append_to)

    def __str__(self):
        s = []
        s.append(
            "%20s %d animators start: %3d (%7.2f) -> stop: %3d (%7.2f) frames: %3d range: %.2f"
            % (
                type(self).__name__,
                len(self),
                self.start_frame,
                self.start_value,
                self.stop_frame,
                self.stop_value,
                self.frame_len,
                self.value_range,
            )
        )
        for a in self.animators:
            s.append("  %s" % (str(a)))
        return "\n".join(s)

    def __len__(self):
        return len(self.animators)

    def add_animator(self, other, with_delay=0):
        """Performs a concatenation with another animator to make a resulting animator group"""
        if with_delay:
            fl = other.frame_len
            other.start_frame = self.stop_frame + with_delay
            other.stop_frame = other.start_frame + fl
            self.animators.append(other)
        else:
            self.animators.append(other)
            self.animators = concatenate_animators(
                self.animators, start_frame=self.start_frame, in_place=True
            )
        return self

    def add_animator_group(self, other):
        """Performs a concatenation with another animator group to make a resulting animator group"""
        self.animators.extend(other.animators)
        self.animators = concatenate_animators(
            self.animators, start_frame=self.start_frame, in_place=True
        )
        return self

    def _add(self, other):
        if isinstance(other, AnimatorGroup):
            return self.add_animator_group(other)
        elif isinstance(other, Animator):
            return self.add_animator(other)
        elif isinstance(other, int):
            # add a dummy animator as a frame time gap
            f = other if self.fps is None else other / self.fps
            dummy = FixedValueAnimator(0, self.stop_value, f, fps=self.fps)
            return self.add_animator(dummy)
        elif isinstance(other, float):
            # add a dummy animator as a frame time gap
            dummy = FixedValueAnimator(
                0, self.stop_value, other, fps=self.fps, as_time=True
            )
            return self.add_animator(dummy)

    def __add__(self, other):
        return self._add(other)

    def __radd__(self, other):
        return self._add(other)

    def __iadd__(self, other):
        return self._add(other)

    def __getitem__(self, key):
        """Convenient syntax sugar equivalent of value_at_frame."""
        return self.value_at_frame(key)

    @property
    def stop_frame(self):
        frame = self.start_frame
        for a in self.animators:
            frame = max(frame, a.stop_frame)
        return frame

    @property
    def frame_len(self):
        return self.stop_frame - self.start_frame

    @property
    def start_value(self):
        return self.animators[0].start_value

    @property
    def stop_value(self):
        return self.animators[-1].stop_value

    @property
    def value_range(self):
        return abs(self.stop_value - self.start_value)

    @property
    def is_active(self, curr_frame=None):
        if curr_frame is not None:
            self.curr_frame = curr_frame
        if self.curr_frame < self.start_frame:
            return False
        elif self.curr_frame > self.stop_frame:
            return False
        return True

    def value_at_time(self, t):
        if self.fps is None:
            raise ValueError("value_at_time cannot be used without specified fps")
        return self.value_at_frame(t * self.fps)

    def value_at_frame(self, frame=None):
        if frame is not None:
            self.curr_frame = frame
        if self.curr_frame <= self.start_frame:
            self.curr_value = self.start_value
        elif self.curr_frame >= self.stop_frame:
            self.curr_value = self.stop_value
        else:
            last_stop_value = self.animators[0].stop_value
            for a in self.animators:
                if a.is_active(self.curr_frame):
                    if a.link_to_previous:
                        a.start_value = last_stop_value
                        if a.value_from_previous is not None:
                            a.stop_value = a.value_from_previous
                        else:
                            a.stop_value = last_stop_value + a.offset_from_previous
                    self.curr_value = a.value_at_frame(frame)
                    break
                last_stop_value = a.stop_value
        return self.curr_value

    def link_to_animator(self, animator):
        """Links our start and stop frame to another animator start and stop.
        This is complicated by the fact that we have to proportionally
        recompute the start/stop frames of the individual member animators
        to our new global start/stop extents."""
        scale = animator.frame_len / self.frame_len
        # normalize our animators to start at 0
        new_animators = concatenate_animators(
            self.animators, start_frame=0, in_place=False
        )
        # rescale the start and stop frames
        f0 = 0
        for a in new_animators:
            fl = round(a.frame_len * scale)
            a.start_frame = f0
            a.stop_frame = f0 + fl
            f0 += fl
        # reschedule to the same start frame of the other animator
        new_animators = concatenate_animators(
            new_animators, start_frame=animator.start_frame, in_place=True
        )
        self.start_frame = animator.start_frame
        self.animators = new_animators

    def append_to_animator(self, animator, with_delay=0):
        """Make our start frame at the end of the other animator"""
        self.start_frame += animator.stop_frame + with_delay
        self.animators = concatenate_animators(
            self.animators, start_frame=self.start_frame, in_place=True
        )

    def start_after(self, other, with_delay=0):
        """Synonymous with append_to_animator, i.e. start after another animator"""
        self.append_to_animator(other, with_delay=with_delay)


def assign_animator_frames(animators, start_frames, stop_frames, in_place):
    """Reassigns a list of animators start and stop frames."""
    if not in_place:
        new_animators = [copy.copy(x) for x in animators]
    else:
        new_animators = animators
    for start, stop, animator in zip(start_frames, stop_frames, new_animators):
        animator.start_frame = start
        animator.stop_frame = stop
    return new_animators


def concatenate_animators(
    animators, start_frame=0, fps=None, in_place=True, as_frames=None, as_time=None
):
    """Rearranges animators so that they are concatenated in frames/time.
    The in_place parameter specifies whether the animator's start/end
    frames are modified in place or a list of new rearranged copies of the
    animators is returned instead."""
    start_frames = []
    stop_frames = []
    use_frames = not as_time and (as_frames is not None and as_frames)
    use_time = (fps is not None) and (as_time or not use_frames)
    f0 = start_frame * fps if use_time else start_frame
    for animator in animators:
        frame_len = animator.frame_len
        start_frames.append(f0)
        stop_frames.append(f0 + frame_len)
        f0 += frame_len
    return assign_animator_frames(animators, start_frames, stop_frames, in_place)


def overlap_animators(
    animators,
    start_frame,
    stop_frame=None,
    pre_stagger=None,
    post_stagger=None,
    stretch_to_fit=False,
    fps=None,
    in_place=True,
    as_frames=None,
    as_time=None,
):
    """Rearranges animators so that they are scheduled with overlap extended
    between a start and stop frame.  Optional stagger intervals at the start
    can be specified to space out the start frames.  Animator durations can
    also be stretched to fit the overall schedule length with an optional
    post stagger interval."""
    start_frames = []
    stop_frames = []
    count = len(animators)
    use_frames = not as_time and (as_frames is not None and as_frames)
    use_time = (fps is not None) and (as_time or not use_frames)
    f0 = start_frame * fps if use_time else start_frame
    start_len = pre_stagger if pre_stagger is not None else 0
    stop_len = post_stagger if post_stagger is not None else 0
    start_len = start_len * fps if use_time else start_len
    stop_len = stop_len * fps if use_time else stop_len
    # case 1: stretch to fit
    if stretch_to_fit:
        f1 = stop_frame * fps if use_time else stop_frame
        f1 -= stop_len * (count - 1)
        for i, animator in enumerate(animators):
            start_frames.append(f0)
            stop_frames.append(f1)
            f0 += start_len
            f1 += stop_len
    # case 2: keep animator lengths but schedule with overlap
    else:
        for animator in animators:
            start_frames.append(f0)
            stop_frames.append(f0 + animator.frame_len)
            f0 += start_len
    return assign_animator_frames(animators, start_frames, stop_frames, in_place)

"""Math helpers and interpolation scaffolding."""

from __future__ import annotations

from typing import Sequence


def linear_interpolate(x: float, xs: Sequence[float], ys: Sequence[float]) -> float:
    """Piecewise linear interpolation with basic validation."""
    if len(xs) != len(ys):
        raise ValueError("xs and ys must have same length")
    if len(xs) == 0:
        raise ValueError("xs must be non-empty")
    if any(x2 <= x1 for x1, x2 in zip(xs, xs[1:])):
        raise ValueError("xs must be strictly increasing")

    if x <= xs[0]:
        return float(ys[0])
    if x >= xs[-1]:
        return float(ys[-1])

    for left, right, y_left, y_right in zip(xs[:-1], xs[1:], ys[:-1], ys[1:]):
        if x <= right:
            weight = (x - left) / (right - left)
            return float(y_left + weight * (y_right - y_left))

    return float(ys[-1])


# TODO: add splines, root-finding, statistics helpers, and bounds checking.

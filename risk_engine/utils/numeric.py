"""Lightweight numeric helpers shared across pricing and risk modules."""

from __future__ import annotations

import math
from typing import Sequence

try:  # Prefer SciPy when available for speed/accuracy
    from scipy.stats import norm as _scipy_norm  # type: ignore

    _HAS_SCIPY = True
except Exception:  # pragma: no cover - SciPy is optional
    _scipy_norm = None
    _HAS_SCIPY = False


def norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    if _HAS_SCIPY:
        return float(_scipy_norm.cdf(x))  # type: ignore[union-attr]
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_pdf(x: float) -> float:
    """Standard normal probability density function."""
    if _HAS_SCIPY:
        return float(_scipy_norm.pdf(x))  # type: ignore[union-attr]
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def validate_positive(name: str, value: float) -> None:
    """Raise ValueError if value is not strictly positive."""
    if value <= 0.0:
        raise ValueError(f"{name} must be > 0, got {value}")


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


__all__ = ["norm_cdf", "norm_pdf", "validate_positive", "linear_interpolate"]

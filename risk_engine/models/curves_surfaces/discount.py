"""Discount curve protocol and simple flat curve."""

from __future__ import annotations

import math
from typing import Protocol


class DiscountCurve(Protocol):
    """Interface for a discount curve."""

    def df(self, t: float) -> float:
        ...


class FlatDiscountCurve:
    """Continuously compounded flat curve: df(T) = exp(-r*T)."""

    def __init__(self, rate: float) -> None:
        self.rate = float(rate)

    def df(self, t: float) -> float:
        t_pos = max(t, 0.0)
        return math.exp(-self.rate * t_pos)


__all__ = ["DiscountCurve", "FlatDiscountCurve"]

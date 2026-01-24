from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FloatLegSpec:
    currency: str
    index: str


@dataclass(frozen=True)
class Swap:
    currency: str
    notional: float
    fixed_rate: float
    pay_times: tuple[float, ...]
    accruals: tuple[float, ...]
    float_leg: FloatLegSpec


__all__ = ["FloatLegSpec", "Swap"]

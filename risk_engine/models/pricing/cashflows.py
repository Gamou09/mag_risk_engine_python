"""Cashflow PV utilities with generic discounting."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Callable, Iterable, Mapping, Sequence

from .base import PricingModel


@dataclass(frozen=True)
class Cashflow:
    """Simple cashflow with payment time and amount."""

    time: float
    amount: float


def _discount_factor(
    maturity: float, *, rate: float | None, discount_curve: Callable[[float], float] | None
) -> float:
    if maturity < 0.0:
        raise ValueError("time must be >= 0")
    if discount_curve is not None:
        return float(discount_curve(maturity))
    if rate is None:
        raise ValueError("rate or discount_curve must be provided")
    return math.exp(-rate * maturity)


def present_value(
    cashflows: Iterable[Cashflow],
    *,
    rate: float | None = None,
    discount_curve: Callable[[float], float] | None = None,
) -> float:
    """Compute PV of cashflows using a flat rate or a discount curve."""
    total = 0.0
    for cf in cashflows:
        df = _discount_factor(cf.time, rate=rate, discount_curve=discount_curve)
        total += cf.amount * df
    return float(total)


class CashflowPVModel(PricingModel):
    """PV model for cashflow schedules."""

    def __init__(
        self,
        *,
        rate: float | None = None,
        discount_curve: Callable[[float], float] | None = None,
    ) -> None:
        self._rate = rate
        self._discount_curve = discount_curve

    def price(self, instrument: Any, **kwargs: Any) -> float:
        if not isinstance(instrument, Sequence):
            raise TypeError("instrument must be a sequence of Cashflow")
        if not instrument:
            return 0.0
        if not all(isinstance(cf, Cashflow) for cf in instrument):
            raise TypeError("instrument must be a sequence of Cashflow")
        return present_value(
            instrument, rate=self._rate, discount_curve=self._discount_curve
        )

    def greeks(self, instrument: Any, **kwargs: Any) -> Mapping[str, float] | None:
        return None

    def sensitivities(
        self, instrument: Any, **kwargs: Any
    ) -> Mapping[str, float] | None:
        return None

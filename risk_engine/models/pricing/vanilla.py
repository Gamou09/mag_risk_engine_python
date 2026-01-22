"""Vanilla pricing using simple discounting."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Callable, Mapping

from risk_engine.core.instruments import (
    EquityForward,
    EquitySpot,
    FixedRateBond,
    ZeroCouponBond,
)

from .base import PricingModel


@dataclass(frozen=True)
class DiscountingModel(PricingModel):
    """Discounting model using a flat rate or a discount curve."""

    rate: float | None = None
    discount_curve: Callable[[float], float] | None = None

    def _discount_factor(self, maturity: float) -> float:
        if maturity < 0.0:
            raise ValueError("maturity must be >= 0")
        if self.discount_curve is not None:
            return float(self.discount_curve(maturity))
        if self.rate is None:
            raise ValueError("rate or discount_curve must be provided")
        return math.exp(-self.rate * maturity)

    def price(self, instrument: Any, **kwargs: Any) -> float:
        if isinstance(instrument, EquitySpot):
            return float(instrument.spot)
        if isinstance(instrument, EquityForward):
            df = self._discount_factor(instrument.maturity)
            forward = instrument.spot * math.exp(
                -instrument.dividend_yield * instrument.maturity
            )
            payoff = forward - instrument.strike * df
            return float(payoff)
        if isinstance(instrument, FixedRateBond):
            return float(self._price_fixed_rate_bond(instrument))
        if isinstance(instrument, ZeroCouponBond):
            df = self._discount_factor(instrument.maturity)
            return float(instrument.face * df)
        raise TypeError("unsupported instrument type")

    def greeks(self, instrument: Any, **kwargs: Any) -> Mapping[str, float] | None:
        return None

    def sensitivities(
        self, instrument: Any, **kwargs: Any
    ) -> Mapping[str, float] | None:
        return None

    def _price_fixed_rate_bond(self, bond: FixedRateBond) -> float:
        if bond.face <= 0.0:
            raise ValueError("face must be > 0")
        if bond.coupon_rate < 0.0:
            raise ValueError("coupon_rate must be >= 0")
        if bond.maturity < 0.0:
            raise ValueError("maturity must be >= 0")
        if bond.payments_per_year <= 0:
            raise ValueError("payments_per_year must be > 0")

        periods = bond.maturity * bond.payments_per_year
        periods_int = int(round(periods))
        if not math.isclose(periods, periods_int, rel_tol=0.0, abs_tol=1e-8):
            raise ValueError("maturity must align with payments_per_year")

        coupon = bond.face * bond.coupon_rate / bond.payments_per_year
        price = 0.0
        for i in range(1, periods_int + 1):
            t = i / bond.payments_per_year
            price += coupon * self._discount_factor(t)
        price += bond.face * self._discount_factor(bond.maturity)
        return price

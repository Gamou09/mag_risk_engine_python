"""Interest rate instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass

from risk_engine.core.instrument_sets.instrument_base import Instrument
from risk_engine.core.instrument_sets.risk_factors import (
    RISK_DISCOUNT_CURVE,
    RISK_FLOAT_INDEX,
    RISK_OVERNIGHT_INDEX,
    RISK_RATE_VOL,
    RISK_YIELD_CURVE,
)


# Linear / Cashflow Instruments
@dataclass(frozen=True)
class InterestRateSwap(Instrument):
    """Fixed-for-floating swap with notional, index, and schedule."""

    ASSET_CLASS = "Rates"
    notional: float
    fixed_rate: float
    float_index: str
    maturity: float
    pay_fixed: bool = True
    currency: str = "USD"
    payments_per_year: int = 2

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_FLOAT_INDEX)


@dataclass(frozen=True)
class OISSwap(Instrument):
    """Swap exchanging fixed rate versus compounded overnight index."""

    ASSET_CLASS = "Rates"
    notional: float
    fixed_rate: float
    overnight_index: str
    maturity: float
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_OVERNIGHT_INDEX)


@dataclass(frozen=True)
class FRA(Instrument):
    """Forward rate agreement locking a rate between start and end dates."""

    ASSET_CLASS = "Rates"
    notional: float
    fixed_rate: float
    start: float
    end: float
    index: str
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_FLOAT_INDEX)


@dataclass(frozen=True)
class ZeroCouponBond(Instrument):
    """Bond paying face value at maturity with no interim coupons."""

    ASSET_CLASS = "Rates"
    face: float
    maturity: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE)


@dataclass(frozen=True)
class FixedRateBond(Instrument):
    """Bond with fixed coupon rate and regular payment frequency."""

    ASSET_CLASS = "Rates"
    face: float
    coupon_rate: float
    maturity: float
    payments_per_year: int = 2

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE)


# Optionality on Rates
@dataclass(frozen=True)
class Swaption(Instrument):
    """Option to enter a swap at a strike on expiry."""

    ASSET_CLASS = "Rates"
    notional: float
    strike: float
    maturity: float
    swap_tenor: float
    option_type: str = "payer"
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_RATE_VOL)


@dataclass(frozen=True)
class Cap(Instrument):
    """Cap on a floating rate with periodic reset payments."""

    ASSET_CLASS = "Rates"
    notional: float
    strike: float
    maturity: float
    index: str
    currency: str = "USD"
    payments_per_year: int = 4

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_RATE_VOL)


@dataclass(frozen=True)
class Floor(Instrument):
    """Floor on a floating rate with periodic reset payments."""

    ASSET_CLASS = "Rates"
    notional: float
    strike: float
    maturity: float
    index: str
    currency: str = "USD"
    payments_per_year: int = 4

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_RATE_VOL)


# Structured Fixed Income
@dataclass(frozen=True)
class BondOption(Instrument):
    """Option on a bond or bond future with strike and expiry."""

    ASSET_CLASS = "Rates"
    notional: float
    strike: float
    maturity: float
    option_type: str = "call"
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_RATE_VOL)


__all__ = [
    "InterestRateSwap",
    "OISSwap",
    "FRA",
    "ZeroCouponBond",
    "FixedRateBond",
    "Swaption",
    "Cap",
    "Floor",
    "BondOption",
]

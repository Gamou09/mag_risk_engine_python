"""Interest rate instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FixedRateBond:
    """Bond with fixed coupon rate and regular payment frequency."""

    face: float
    coupon_rate: float
    maturity: float
    payments_per_year: int = 2


@dataclass(frozen=True)
class ZeroCouponBond:
    """Bond paying face value at maturity with no interim coupons."""

    face: float
    maturity: float


@dataclass(frozen=True)
class InterestRateSwap:
    """Fixed-for-floating swap with notional, index, and schedule."""

    notional: float
    fixed_rate: float
    float_index: str
    maturity: float
    pay_fixed: bool = True
    currency: str = "USD"
    payments_per_year: int = 2


@dataclass(frozen=True)
class OISSwap:
    """Swap exchanging fixed rate versus compounded overnight index."""

    notional: float
    fixed_rate: float
    overnight_index: str
    maturity: float
    currency: str = "USD"


@dataclass(frozen=True)
class FRA:
    """Forward rate agreement locking a rate between start and end dates."""

    notional: float
    fixed_rate: float
    start: float
    end: float
    index: str
    currency: str = "USD"


@dataclass(frozen=True)
class Swaption:
    """Option to enter a swap at a strike on expiry."""

    notional: float
    strike: float
    maturity: float
    swap_tenor: float
    option_type: str = "payer"
    currency: str = "USD"


@dataclass(frozen=True)
class Cap:
    """Cap on a floating rate with periodic reset payments."""

    notional: float
    strike: float
    maturity: float
    index: str
    currency: str = "USD"
    payments_per_year: int = 4


@dataclass(frozen=True)
class Floor:
    """Floor on a floating rate with periodic reset payments."""

    notional: float
    strike: float
    maturity: float
    index: str
    currency: str = "USD"
    payments_per_year: int = 4


@dataclass(frozen=True)
class BondOption:
    """Option on a bond or bond future with strike and expiry."""

    notional: float
    strike: float
    maturity: float
    option_type: str = "call"
    currency: str = "USD"


__all__ = [
    "FixedRateBond",
    "ZeroCouponBond",
    "InterestRateSwap",
    "OISSwap",
    "FRA",
    "Swaption",
    "Cap",
    "Floor",
    "BondOption",
]

"""Instrument definitions and interfaces."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EquitySpot:
    """Spot equity instrument."""

    spot: float
    symbol: str | None = None


@dataclass(frozen=True)
class EquityForward:
    """Equity forward contract."""

    spot: float
    strike: float
    maturity: float
    rate: float
    dividend_yield: float = 0.0
    symbol: str | None = None


@dataclass(frozen=True)
class FixedRateBond:
    """Fixed-rate bond with regular coupon payments."""

    face: float
    coupon_rate: float
    maturity: float
    payments_per_year: int = 2


@dataclass(frozen=True)
class ZeroCouponBond:
    """Zero-coupon bond."""

    face: float
    maturity: float


__all__ = [
    "EquitySpot",
    "EquityForward",
    "FixedRateBond",
    "ZeroCouponBond",
]

"""Hybrid, multi-asset, and exotic instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from risk_engine.core.instrument_sets.instrument_base import Instrument
from risk_engine.core.instrument_sets.risk_factors import (
    RISK_CORRELATION,
    RISK_CREDIT_SPREAD,
    RISK_DIVIDEND_YIELD,
    RISK_EQUITY_SPOT,
    RISK_EQUITY_VOL,
    RISK_FX_RATE,
    RISK_FX_VOL,
    RISK_INTEREST_RATE,
    RISK_MULTI_ASSET_SPOTS,
    RISK_MULTI_ASSET_VOL,
    RISK_UNDERLYING_SPOT,
    RISK_UNDERLYING_VOL,
)


# Credit-Equity Hybrids
@dataclass(frozen=True)
class ConvertibleBond(Instrument):
    """Bond convertible into equity at a specified conversion ratio."""

    ASSET_CLASS = "Hybrid/Exotic"
    face: float
    coupon_rate: float
    maturity: float
    conversion_ratio: float
    underlying_symbol: str | None = None
    payments_per_year: int = 2

    def risk_factors(self) -> tuple[str, ...]:
        return (
            RISK_EQUITY_SPOT,
            RISK_CREDIT_SPREAD,
            RISK_INTEREST_RATE,
            RISK_EQUITY_VOL,
        )


# Multi-Underlying Options
@dataclass(frozen=True)
class BasketOption(Instrument):
    """Option on a weighted basket of underlyings."""

    ASSET_CLASS = "Hybrid/Exotic"
    underlyings: Sequence[str]
    weights: Sequence[float]
    strike: float
    maturity: float
    rate: float
    vol: float
    option_type: str = "call"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_MULTI_ASSET_SPOTS, RISK_CORRELATION, RISK_MULTI_ASSET_VOL)


@dataclass(frozen=True)
class RainbowOption(Instrument):
    """Option on multiple underlyings with best-of or worst-of payoff."""

    ASSET_CLASS = "Hybrid/Exotic"
    spots: Sequence[float]
    strike: float
    maturity: float
    rate: float
    vol: float
    payoff: str = "best_of"
    option_type: str = "call"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_MULTI_ASSET_SPOTS, RISK_CORRELATION, RISK_MULTI_ASSET_VOL)


# Cross-Market Structures
@dataclass(frozen=True)
class QuantoOption(Instrument):
    """Option with payoff converted at a fixed FX rate (quanto)."""

    ASSET_CLASS = "Hybrid/Exotic"
    spot: float
    strike: float
    maturity: float
    rate: float
    vol: float
    fx_rate: float
    fx_vol: float
    option_type: str = "call"
    symbol: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (
            RISK_UNDERLYING_SPOT,
            RISK_FX_RATE,
            RISK_UNDERLYING_VOL,
            RISK_FX_VOL,
            RISK_CORRELATION,
        )


# Time-Dependent Structures
@dataclass(frozen=True)
class ForwardStartOption(Instrument):
    """Option that starts at a future date with strike set by percentage."""

    ASSET_CLASS = "Hybrid/Exotic"
    spot: float
    start: float
    maturity: float
    rate: float
    vol: float
    strike_pct: float
    option_type: str = "call"
    symbol: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (
            RISK_UNDERLYING_SPOT,
            RISK_EQUITY_VOL,
            RISK_INTEREST_RATE,
            RISK_DIVIDEND_YIELD,
        )


__all__ = [
    "ConvertibleBond",
    "BasketOption",
    "RainbowOption",
    "QuantoOption",
    "ForwardStartOption",
]

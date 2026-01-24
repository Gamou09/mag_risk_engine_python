"""FX instruments."""

from __future__ import annotations

from dataclasses import dataclass

from risk_engine.instruments.assets.instrument_base import Instrument as AssetInstrument
from risk_engine.instruments.assets.risk_factors import (
    RISK_DISCOUNT_CURVE,
    RISK_FX_RATE,
    RISK_FX_SPOT,
    RISK_FX_VOL,
    RISK_INTEREST_RATE_DIFFERENTIAL,
    RISK_YIELD_CURVE,
)


# Spots and forwards
@dataclass(frozen=True)
class FXSpot(AssetInstrument):
    """FX spot instrument with currency pair and spot rate."""

    ASSET_CLASS = "FX"
    pair: str
    spot: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT,)


@dataclass(frozen=True)
class FXForward(AssetInstrument):
    """FX forward contract with agreed forward rate and maturity."""

    ASSET_CLASS = "FX"
    pair: str
    spot: float
    forward_rate: float
    maturity: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT, RISK_INTEREST_RATE_DIFFERENTIAL)


# Swaps
@dataclass(frozen=True)
class FXSwap(AssetInstrument):
    """FX swap with near and far legs on the same currency pair."""

    ASSET_CLASS = "FX"
    pair: str
    near_maturity: float
    far_maturity: float
    near_forward: float
    far_forward: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT, RISK_INTEREST_RATE_DIFFERENTIAL)


# Options
@dataclass(frozen=True)
class FXOption(AssetInstrument):
    """Vanilla FX option with spot, strike, and volatility inputs."""

    ASSET_CLASS = "FX"
    pair: str
    spot: float
    strike: float
    maturity: float
    vol: float
    option_type: str = "call"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT, RISK_INTEREST_RATE_DIFFERENTIAL, RISK_FX_VOL)


@dataclass(frozen=True)
class FXDigitalOption(AssetInstrument):
    """Digital FX option paying fixed payout if in the money."""

    ASSET_CLASS = "FX"
    pair: str
    spot: float
    strike: float
    maturity: float
    payout: float
    option_type: str = "call"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT, RISK_INTEREST_RATE_DIFFERENTIAL, RISK_FX_VOL)


# Cross-currency swaps
@dataclass(frozen=True)
class CrossCurrencySwap(AssetInstrument):
    """Sketch of a cross-currency swap instrument."""

    ASSET_CLASS = "FX"
    notional: float
    pay_currency: str
    receive_currency: str
    maturity: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_RATE, RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE)


# TODO: add legs, payment schedules, and basis spreads.


__all__ = ["FXSpot", "FXForward", "FXSwap", "FXOption", "FXDigitalOption", "CrossCurrencySwap"]

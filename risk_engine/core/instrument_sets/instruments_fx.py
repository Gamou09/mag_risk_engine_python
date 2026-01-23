"""FX instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass

from risk_engine.core.instrument_sets.instrument_base import Instrument
from risk_engine.core.instrument_sets.risk_factors import (
    RISK_FX_SPOT,
    RISK_FX_VOL,
    RISK_INTEREST_RATE_DIFFERENTIAL,
)


# Linear FX
@dataclass(frozen=True)
class FXSpot(Instrument):
    """FX spot instrument with currency pair and spot rate."""

    ASSET_CLASS = "FX"
    pair: str
    spot: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT,)


@dataclass(frozen=True)
class FXForward(Instrument):
    """FX forward contract with agreed forward rate and maturity."""

    ASSET_CLASS = "FX"
    pair: str
    spot: float
    forward_rate: float
    maturity: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT, RISK_INTEREST_RATE_DIFFERENTIAL)


@dataclass(frozen=True)
class FXSwap(Instrument):
    """FX swap with near and far legs on the same currency pair."""

    ASSET_CLASS = "FX"
    pair: str
    near_maturity: float
    far_maturity: float
    near_forward: float
    far_forward: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT, RISK_INTEREST_RATE_DIFFERENTIAL)


# FX Optionality
@dataclass(frozen=True)
class FXOption(Instrument):
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
class FXDigitalOption(Instrument):
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


__all__ = [
    "FXSpot",
    "FXForward",
    "FXSwap",
    "FXOption",
    "FXDigitalOption",
]

"""FX instruments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

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


# Pricing-layer FX swap (new architecture)
@dataclass(frozen=True)
class PricingFXSwap(AssetInstrument):
    """
    Minimal FX swap for the new pricing registry.

    - direction \"buy_base\": pay quote / receive base at near, unwind at far.
    - direction \"sell_base\": receive quote / pay base at near, unwind at far.
    PV is returned in the quote currency (second leg of the pair).
    """

    ASSET_CLASS = "FX"
    product_type: str = "fx.swap"

    pair: str = "EURUSD"  # base/quote
    notional: float = 1_000_000.0  # amount in base currency
    near_maturity: str = "1M"
    far_maturity: str = "6M"
    near_forward: float = 1.085
    far_forward: float = 1.100
    direction: Literal["buy_base", "sell_base"] = "buy_base"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT, RISK_INTEREST_RATE_DIFFERENTIAL)


@dataclass(frozen=True)
class FXEuropeanOption(AssetInstrument):
    """Minimal FX European option used by GK pricer (domestic payout)."""

    ASSET_CLASS = "FX"
    product_type: str = field(default="fx.option.european", init=False)

    call_put: Literal["C", "P"] | str = "C"
    strike: float = 1.0
    expiry: float = 1.0  # year fraction
    notional: float = 1.0  # domestic payout
    direction: int = 1  # +1 long, -1 short
    underlying: str = "UNKNOWN"

    def __post_init__(self) -> None:
        cp = self.call_put.upper()
        if cp not in {"C", "P"}:
            raise ValueError("call_put must be 'C' or 'P'")
        if self.expiry < 0.0:
            raise ValueError("expiry must be >= 0")
        if self.strike <= 0.0 or self.notional <= 0.0:
            raise ValueError("strike and notional must be > 0")
        if self.direction not in {1, -1}:
            raise ValueError("direction must be +1 (long) or -1 (short)")
        if not isinstance(self.underlying, str) or not self.underlying:
            raise ValueError("underlying must be a non-empty string")

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_SPOT, RISK_INTEREST_RATE_DIFFERENTIAL, RISK_FX_VOL)

__all__ += ["PricingFXSwap", "FXEuropeanOption"]

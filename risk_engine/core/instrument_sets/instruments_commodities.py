"""Commodity instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass

from risk_engine.core.instrument_sets.instrument_base import Instrument
from risk_engine.core.instrument_sets.risk_factors import (
    RISK_COMMODITY_SPOT,
    RISK_COMMODITY_VOL,
    RISK_CONVENIENCE_YIELD,
    RISK_INTEREST_RATE,
)


# Linear Commodities
@dataclass(frozen=True)
class CommoditySpot(Instrument):
    """Commodity spot instrument with current price."""

    ASSET_CLASS = "Commodities"
    commodity: str
    spot: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_COMMODITY_SPOT,)


@dataclass(frozen=True)
class CommodityForward(Instrument):
    """Commodity forward contract with agreed forward price."""

    ASSET_CLASS = "Commodities"
    commodity: str
    spot: float
    forward_price: float
    maturity: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_COMMODITY_SPOT, RISK_CONVENIENCE_YIELD, RISK_INTEREST_RATE)


@dataclass(frozen=True)
class CommodityFuture(Instrument):
    """Commodity future with exchange listing and settlement date."""

    ASSET_CLASS = "Commodities"
    commodity: str
    price: float
    maturity: float
    exchange: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_COMMODITY_SPOT, RISK_CONVENIENCE_YIELD, RISK_INTEREST_RATE)


@dataclass(frozen=True)
class CommoditySwap(Instrument):
    """Commodity fixed-for-floating swap on a specified commodity."""

    ASSET_CLASS = "Commodities"
    commodity: str
    notional: float
    fixed_price: float
    maturity: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_COMMODITY_SPOT, RISK_CONVENIENCE_YIELD, RISK_INTEREST_RATE)


# Commodity Optionality
@dataclass(frozen=True)
class CommodityOption(Instrument):
    """Commodity option with spot, strike, and volatility inputs."""

    ASSET_CLASS = "Commodities"
    commodity: str
    spot: float
    strike: float
    maturity: float
    vol: float
    option_type: str = "call"

    def risk_factors(self) -> tuple[str, ...]:
        return (
            RISK_COMMODITY_SPOT,
            RISK_COMMODITY_VOL,
            RISK_CONVENIENCE_YIELD,
            RISK_INTEREST_RATE,
        )


__all__ = [
    "CommoditySpot",
    "CommodityForward",
    "CommodityFuture",
    "CommoditySwap",
    "CommodityOption",
]

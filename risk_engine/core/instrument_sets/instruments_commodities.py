"""Commodity instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommoditySpot:
    """Commodity spot instrument with current price."""

    commodity: str
    spot: float


@dataclass(frozen=True)
class CommodityForward:
    """Commodity forward contract with agreed forward price."""

    commodity: str
    spot: float
    forward_price: float
    maturity: float


@dataclass(frozen=True)
class CommodityFuture:
    """Commodity future with exchange listing and settlement date."""

    commodity: str
    price: float
    maturity: float
    exchange: str | None = None


@dataclass(frozen=True)
class CommoditySwap:
    """Commodity fixed-for-floating swap on a specified commodity."""

    commodity: str
    notional: float
    fixed_price: float
    maturity: float


@dataclass(frozen=True)
class CommodityOption:
    """Commodity option with spot, strike, and volatility inputs."""

    commodity: str
    spot: float
    strike: float
    maturity: float
    vol: float
    option_type: str = "call"


__all__ = [
    "CommoditySpot",
    "CommodityForward",
    "CommodityFuture",
    "CommoditySwap",
    "CommodityOption",
]

"""Equity instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EquitySpot:
    """Spot equity instrument with current price and optional ticker."""

    spot: float
    symbol: str | None = None


@dataclass(frozen=True)
class EquityForward:
    """Equity forward contract with strike, maturity, and carry inputs."""

    spot: float
    strike: float
    maturity: float
    rate: float
    dividend_yield: float = 0.0
    symbol: str | None = None


@dataclass(frozen=True)
class EuropeanOption:
    """Vanilla European option on equity with Black-Scholes style inputs."""

    spot: float
    strike: float
    maturity: float
    rate: float
    vol: float
    option_type: str = "call"
    symbol: str | None = None


@dataclass(frozen=True)
class EquityIndexFuture:
    """Equity index future with carry inputs and optional index symbol."""

    spot: float
    maturity: float
    rate: float
    dividend_yield: float = 0.0
    symbol: str | None = None


@dataclass(frozen=True)
class EquityDigitalOption:
    """Digital option on equity paying a fixed amount if in the money."""

    spot: float
    strike: float
    maturity: float
    rate: float
    vol: float
    payout: float
    option_type: str = "call"
    symbol: str | None = None


@dataclass(frozen=True)
class EquityBarrierOption:
    """Barrier option on equity with barrier level and barrier style."""

    spot: float
    strike: float
    barrier: float
    barrier_type: str
    maturity: float
    rate: float
    vol: float
    option_type: str = "call"
    symbol: str | None = None


@dataclass(frozen=True)
class VarianceSwap:
    """Variance swap on equity index with variance strike and maturity."""

    notional: float
    variance_strike: float
    maturity: float
    symbol: str | None = None


__all__ = [
    "EquitySpot",
    "EquityForward",
    "EuropeanOption",
    "EquityIndexFuture",
    "EquityDigitalOption",
    "EquityBarrierOption",
    "VarianceSwap",
]

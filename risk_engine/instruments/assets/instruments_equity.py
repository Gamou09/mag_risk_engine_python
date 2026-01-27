"""Equity instruments."""

from __future__ import annotations

from dataclasses import dataclass

from risk_engine.instruments.assets.instrument_base import Instrument
from risk_engine.instruments.assets.risk_factors import (
    RISK_DIVIDEND_YIELD,
    RISK_EQUITY_SPOT,
    RISK_EQUITY_VOL,
    RISK_INTEREST_RATE,
)


# Spots and forwards
@dataclass(frozen=True)
class EquitySpot(Instrument):
    """Spot equity instrument with current price and optional ticker."""

    ASSET_CLASS = "Equity"
    spot: float
    symbol: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_EQUITY_SPOT,)


@dataclass(frozen=True)
class EquityForward(Instrument):
    """Equity forward contract with strike, maturity, and carry inputs."""

    ASSET_CLASS = "Equity"
    spot: float
    strike: float
    maturity: float
    rate: float
    dividend_yield: float = 0.0
    symbol: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_EQUITY_SPOT, RISK_DIVIDEND_YIELD, RISK_INTEREST_RATE)


@dataclass(frozen=True)
class EquityIndexFuture(Instrument):
    """Equity index future with carry inputs and optional index symbol."""

    ASSET_CLASS = "Equity"
    spot: float
    maturity: float
    rate: float
    dividend_yield: float = 0.0
    symbol: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_EQUITY_SPOT, RISK_DIVIDEND_YIELD, RISK_INTEREST_RATE)


# Options
@dataclass(frozen=True)
class EuropeanOption(Instrument):
    """Vanilla European option on equity with Black-Scholes style inputs."""

    ASSET_CLASS = "Equity"
    spot: float
    strike: float
    maturity: float
    rate: float
    vol: float
    option_type: str = "call"
    symbol: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (
            RISK_EQUITY_SPOT,
            RISK_DIVIDEND_YIELD,
            RISK_INTEREST_RATE,
            RISK_EQUITY_VOL,
        )


@dataclass(frozen=True)
class EquityDigitalOption(Instrument):
    """Digital option on equity paying a fixed amount if in the money."""

    ASSET_CLASS = "Equity"
    spot: float
    strike: float
    maturity: float
    rate: float
    vol: float
    payout: float
    option_type: str = "call"
    symbol: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (
            RISK_EQUITY_SPOT,
            RISK_DIVIDEND_YIELD,
            RISK_INTEREST_RATE,
            RISK_EQUITY_VOL,
        )


@dataclass(frozen=True)
class EquityBarrierOption(Instrument):
    """Barrier option on equity with barrier level and barrier style."""

    ASSET_CLASS = "Equity"
    spot: float
    strike: float
    barrier: float
    barrier_type: str
    maturity: float
    rate: float
    vol: float
    option_type: str = "call"
    symbol: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (
            RISK_EQUITY_SPOT,
            RISK_DIVIDEND_YIELD,
            RISK_INTEREST_RATE,
            RISK_EQUITY_VOL,
        )


# Variance products
@dataclass(frozen=True)
class VarianceSwap(Instrument):
    """Variance swap on equity index with variance strike and maturity."""

    ASSET_CLASS = "Equity"
    notional: float
    variance_strike: float
    maturity: float
    symbol: str | None = None

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_EQUITY_SPOT, RISK_EQUITY_VOL)


__all__ = [
    "EquitySpot",
    "EquityForward",
    "EquityIndexFuture",
    "EuropeanOption",
    "EquityDigitalOption",
    "EquityBarrierOption",
    "VarianceSwap",
]

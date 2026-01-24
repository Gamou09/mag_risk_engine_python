"""Credit instruments."""

from __future__ import annotations

from dataclasses import dataclass

from risk_engine.instruments.assets.instrument_base import Instrument
from risk_engine.instruments.assets.risk_factors import (
    RISK_ASSET_SPOT,
    RISK_CREDIT_SPREAD,
    RISK_CREDIT_VOL,
    RISK_DEFAULT_INTENSITY,
    RISK_FUNDING_RATE,
    RISK_RECOVERY_RATE,
)


# CDS and related
@dataclass(frozen=True)
class CreditDefaultSwap(Instrument):
    """CDS on a single reference entity with fixed spread."""

    ASSET_CLASS = "Credit"
    notional: float
    spread: float
    maturity: float
    reference: str
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_CREDIT_SPREAD, RISK_DEFAULT_INTENSITY, RISK_RECOVERY_RATE)


@dataclass(frozen=True)
class CDSIndex(Instrument):
    """Index CDS on a named credit index with fixed spread."""

    ASSET_CLASS = "Credit"
    notional: float
    spread: float
    maturity: float
    index: str
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_CREDIT_SPREAD, RISK_DEFAULT_INTENSITY, RISK_RECOVERY_RATE)


@dataclass(frozen=True)
class CreditDefaultSwaption(Instrument):
    """Option to enter a CDS at a strike spread."""

    ASSET_CLASS = "Credit"
    notional: float
    strike: float
    maturity: float
    swap_tenor: float
    reference: str
    option_type: str = "payer"
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (
            RISK_CREDIT_SPREAD,
            RISK_CREDIT_VOL,
            RISK_DEFAULT_INTENSITY,
            RISK_RECOVERY_RATE,
        )


# Total return swaps
@dataclass(frozen=True)
class TotalReturnSwap(Instrument):
    """Total return swap exchanging asset return for funding rate."""

    ASSET_CLASS = "Credit"
    notional: float
    maturity: float
    reference: str
    funding_rate: float
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_ASSET_SPOT, RISK_FUNDING_RATE, RISK_CREDIT_SPREAD)


__all__ = [
    "CreditDefaultSwap",
    "CDSIndex",
    "CreditDefaultSwaption",
    "TotalReturnSwap",
]

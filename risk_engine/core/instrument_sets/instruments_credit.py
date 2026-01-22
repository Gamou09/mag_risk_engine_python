"""Credit instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreditDefaultSwap:
    """CDS on a single reference entity with fixed spread."""

    notional: float
    spread: float
    maturity: float
    reference: str
    currency: str = "USD"


@dataclass(frozen=True)
class CDSIndex:
    """Index CDS on a named credit index with fixed spread."""

    notional: float
    spread: float
    maturity: float
    index: str
    currency: str = "USD"


@dataclass(frozen=True)
class CreditDefaultSwaption:
    """Option to enter a CDS at a strike spread."""

    notional: float
    strike: float
    maturity: float
    swap_tenor: float
    reference: str
    option_type: str = "payer"
    currency: str = "USD"


@dataclass(frozen=True)
class TotalReturnSwap:
    """Total return swap exchanging asset return for funding rate."""

    notional: float
    maturity: float
    reference: str
    funding_rate: float
    currency: str = "USD"


__all__ = [
    "CreditDefaultSwap",
    "CDSIndex",
    "CreditDefaultSwaption",
    "TotalReturnSwap",
]

"""FX instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FXSpot:
    """FX spot instrument with currency pair and spot rate."""

    pair: str
    spot: float


@dataclass(frozen=True)
class FXForward:
    """FX forward contract with agreed forward rate and maturity."""

    pair: str
    spot: float
    forward_rate: float
    maturity: float


@dataclass(frozen=True)
class FXSwap:
    """FX swap with near and far legs on the same currency pair."""

    pair: str
    near_maturity: float
    far_maturity: float
    near_forward: float
    far_forward: float


@dataclass(frozen=True)
class FXOption:
    """Vanilla FX option with spot, strike, and volatility inputs."""

    pair: str
    spot: float
    strike: float
    maturity: float
    vol: float
    option_type: str = "call"


@dataclass(frozen=True)
class FXDigitalOption:
    """Digital FX option paying fixed payout if in the money."""

    pair: str
    spot: float
    strike: float
    maturity: float
    payout: float
    option_type: str = "call"


__all__ = [
    "FXSpot",
    "FXForward",
    "FXSwap",
    "FXOption",
    "FXDigitalOption",
]

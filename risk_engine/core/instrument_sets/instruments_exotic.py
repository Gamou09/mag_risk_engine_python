"""Multi-asset and exotic instrument placeholders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class BasketOption:
    """Option on a weighted basket of underlyings."""

    underlyings: Sequence[str]
    weights: Sequence[float]
    strike: float
    maturity: float
    rate: float
    vol: float
    option_type: str = "call"


@dataclass(frozen=True)
class QuantoOption:
    """Option with payoff converted at a fixed FX rate (quanto)."""

    spot: float
    strike: float
    maturity: float
    rate: float
    vol: float
    fx_rate: float
    fx_vol: float
    option_type: str = "call"
    symbol: str | None = None


@dataclass(frozen=True)
class RainbowOption:
    """Option on multiple underlyings with best-of or worst-of payoff."""

    spots: Sequence[float]
    strike: float
    maturity: float
    rate: float
    vol: float
    payoff: str = "best_of"
    option_type: str = "call"


@dataclass(frozen=True)
class ForwardStartOption:
    """Option that starts at a future date with strike set by percentage."""

    spot: float
    start: float
    maturity: float
    rate: float
    vol: float
    strike_pct: float
    option_type: str = "call"
    symbol: str | None = None


__all__ = [
    "BasketOption",
    "QuantoOption",
    "RainbowOption",
    "ForwardStartOption",
]

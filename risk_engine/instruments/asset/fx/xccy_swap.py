"""Cross-currency swaps (placeholder)."""

from __future__ import annotations

from dataclasses import dataclass

from risk_engine.core.instrument_sets.risk_factors import (
    RISK_DISCOUNT_CURVE,
    RISK_FX_RATE,
    RISK_YIELD_CURVE,
)
from risk_engine.instruments.base import Instrument


@dataclass(frozen=True)
class CrossCurrencySwap(Instrument):
    """Sketch of a cross-currency swap instrument."""

    ASSET_CLASS = "FX"
    notional: float
    pay_currency: str
    receive_currency: str
    maturity: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_FX_RATE, RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE)


# TODO: add legs, payment schedules, and basis spreads.

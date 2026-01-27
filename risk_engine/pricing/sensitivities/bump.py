"""Bump-and-reprice sensitivities (placeholder)."""

from __future__ import annotations

from typing import Mapping

from risk_engine.core.engine import PricingEngine
from risk_engine.instruments.portfolio import Portfolio
from risk_engine.market.state import MarketState


def bump_and_reprice(
    portfolio: Portfolio,
    market: MarketState,
    bumps: Mapping[str, float],
    *,
    engine: PricingEngine | None = None,
):
    """Apply simple bumps and reprice; extend to per-factor bumps later."""
    raise NotImplementedError("Bump-and-reprice not wired yet")


# TODO: add parallel/keyed bumps, finite-difference greeks, and aggregation.

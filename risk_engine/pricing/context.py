"""PricingContext bundles market state and model configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from risk_engine.market.state import MarketState

@dataclass(frozen=True)
class PricingContext:
    """Context passed to pricers/engines."""

    market: MarketState
    model_id: Optional[str] = None     # e.g. "rates.hw1f", "eq.bs"
    method: str = "analytic"           # "analytic" | "mc" | "lattice"
    settings: dict[str, Any] = None    # tolerances, mc paths, seed, etc.

    def __post_init__(self):
        if self.settings is None:
            object.__setattr__(self, "settings", {})


# TODO: include valuation date, discounting currency, and risk-neutral measure selection.

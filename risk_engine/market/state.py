"""MarketState container aligning legacy MarketData with the new layout."""

from __future__ import annotations

# from risk_engine.core.engine import MarketData
from dataclasses import dataclass, field
from typing import Mapping, Any

# TODO: extend with curves, surfaces, and richer metadata as the stack matures.
# MarketState = MarketData
RiskFactorKey = str  # e.g. "DF.USD.OIS.5Y", "SPOT.BRENT", "VOL.EURUSD.1Y.ATM"

@dataclass(frozen=True)
class MarketState:
    """
    Immutable container for market observables.
    Start minimal: a dict of factors -> float.
    Later: structured curves/surfaces, metadata, valuation date, etc.
    """
    factors: Mapping[RiskFactorKey, float] = field(default_factory=dict)
    meta: Mapping[str, Any] = field(default_factory=dict)

    def get(self, key: RiskFactorKey) -> float:
        return float(self.factors[key])

    def with_factors(self, updates: Mapping[RiskFactorKey, float]) -> "MarketState":
        new_factors = dict(self.factors)
        new_factors.update(updates)
        return MarketState(factors=new_factors, meta=self.meta)

__all__ = ["MarketState"]

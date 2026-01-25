"""MarketState container aligning legacy MarketData with the new layout."""

from __future__ import annotations

# from risk_engine.core.engine import MarketData
from dataclasses import dataclass, field
from typing import Mapping, Any

from risk_engine.market.curve_registry import CurveRegistry
from risk_engine.market.ids import CurveId

# TODO: extend with curves, surfaces, and richer metadata as the stack matures.
# MarketState = MarketData
RiskFactorKey = str  # e.g. "DF.OIS_USD_3M.5Y", "SPOT.BRENT", "VOL.EURUSD.1Y.ATM"

@dataclass(frozen=True)
class MarketState:
    """
    Immutable container for market observables.
    Start minimal: a dict of factors -> float.
    Later: structured curves/surfaces, metadata, valuation date, etc.
    """
    factors: Mapping[RiskFactorKey, float] = field(default_factory=dict)
    discount_curves: Mapping[str, CurveId] = field(default_factory=dict)
    meta: Mapping[str, Any] = field(default_factory=dict)
    registry: CurveRegistry | None = None

    def __post_init__(self) -> None:
        if self.registry is None:
            return
        for curve in self.discount_curves.values():
            self.registry.require_known(curve.name)

    def get(self, key: RiskFactorKey) -> float:
        self._validate_curve_id(key)
        try:
            return float(self.factors[key])
        except KeyError as exc:  # pragma: no cover - passthrough
            raise KeyError(f"Missing market factor '{key}'") from exc

    def with_factors(self, updates: Mapping[RiskFactorKey, float]) -> "MarketState":
        new_factors = dict(self.factors)
        new_factors.update(updates)
        return MarketState(
            factors=new_factors,
            discount_curves=self.discount_curves,
            meta=self.meta,
            registry=self.registry,
        )

    def discount_curve_for(self, ccy: str) -> CurveId:
        """Return the discount curve identifier associated to a currency."""
        try:
            curve = self.discount_curves[ccy]
        except KeyError as exc:  # pragma: no cover - passthrough
            raise KeyError(f"Missing discount curve for currency '{ccy}'") from exc
        if self.registry is not None:
            self.registry.require_known(curve.name)
        return curve

    def validate_factor_keys(self) -> None:
        """Validate all factor curve IDs against the registry (if provided)."""
        for key in self.factors.keys():
            self._validate_curve_id(key)

    def _validate_curve_id(self, key: RiskFactorKey) -> None:
        if self.registry is None:
            return
        curve_id = _extract_curve_id(key)
        if curve_id is None:
            return
        self.registry.require_known(curve_id)


def _extract_curve_id(key: str) -> str | None:
    """Return the curve id portion of DF./FWD. keys or None otherwise."""
    if not key.startswith(("DF.", "FWD.")):
        return None

    parts = key.split(".")
    if len(parts) < 3:
        raise ValueError(
            f"Market factor key '{key}' must look like DF.<curve_id>.<pillar> or FWD.<curve_id>.<pillar>"
        )

    curve_or_pair = parts[1]

    # FX forward keys (e.g., FWD.EURUSD.1M) should not be validated against the curve registry.
    if key.startswith("FWD."):
        clean = curve_or_pair.replace("/", "")
        if len(clean) == 6 and clean.isalpha():
            return None

    return curve_or_pair

__all__ = ["MarketState"]

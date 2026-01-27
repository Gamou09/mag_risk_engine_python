from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from risk_engine.market.ids import CurveId


@dataclass(frozen=True)
class RiskRequest:
    bp: float = 1.0
    curves: Optional[tuple[CurveId, ...]] = None


@dataclass(frozen=True)
class CurveRisk:
    curve_id: CurveId
    dPV: float


__all__ = ["RiskRequest", "CurveRisk"]

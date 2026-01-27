"""FX vol quotes container and helpers (ATM/RR/BF -> wing vols).

Integrated under risk_engine.models.fx; keeps structure minimal and reuses
existing pricing/discounting conventions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

VOL_FLOOR = 1e-4
VOL_CAP = 5.0

__all__ = ["MarketSlice", "wing_vols_from_rr_bf", "compute_forward"]


def compute_forward(spot: float, df_dom: float, df_for: float) -> float:
    """Return forward FX rate given domestic/foreign discount factors."""
    if spot <= 0.0:
        raise ValueError("spot must be > 0")
    if df_dom <= 0.0 or df_for <= 0.0:
        raise ValueError("discount factors must be > 0")
    return float(spot * df_for / df_dom)


def wing_vols_from_rr_bf(atm: float, rr: float, bf: float) -> Tuple[float, float]:
    """Compute call/put wing vols from ATM, risk reversal and butterfly."""
    call_vol = atm + bf + 0.5 * rr
    put_vol = call_vol - rr
    return call_vol, put_vol


@dataclass
class MarketSlice:
    """Per-expiry FX smile quotes and conventions."""

    expiry: float
    forward: float
    df_dom: float
    df_for: float
    atm: float
    rr: Dict[float, float]
    bf: Dict[float, float]
    delta_type: str = "forward"
    premium_adjusted: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)
    stale: bool = False
    missing_quotes: List[str] = field(default_factory=list)

    def available_deltas(self) -> List[float]:
        deltas = sorted(set(self.rr.keys()) & set(self.bf.keys()))
        return [d for d in deltas if self.rr[d] is not None and self.bf[d] is not None]

    def wing_vols(self, delta: float) -> Tuple[float, float]:
        if delta not in self.rr or delta not in self.bf:
            raise KeyError(f"Missing RR/BF quote for {delta:.0%} delta")
        call_vol, put_vol = wing_vols_from_rr_bf(self.atm, self.rr[delta], self.bf[delta])
        call_vol = min(max(call_vol, VOL_FLOOR), VOL_CAP)
        put_vol = min(max(put_vol, VOL_FLOOR), VOL_CAP)
        return call_vol, put_vol

    def describe(self) -> str:
        parts = [
            f"T={self.expiry:.4f}y",
            f"F={self.forward:.6f}",
            f"ATM={self.atm:.4%}",
            f"deltas={','.join(f'{d:.0%}' for d in self.available_deltas())}",
        ]
        if self.stale:
            parts.append("stale")
        if self.missing_quotes:
            parts.append(f"missing={self.missing_quotes}")
        return " | ".join(parts)

    def clone_with_updates(
        self,
        *,
        atm: float | None = None,
        rr: Dict[float, float] | None = None,
        bf: Dict[float, float] | None = None,
        stale: bool | None = None,
        missing_quotes: Iterable[str] | None = None,
    ) -> "MarketSlice":
        return MarketSlice(
            expiry=self.expiry,
            forward=self.forward,
            df_dom=self.df_dom,
            df_for=self.df_for,
            atm=self.atm if atm is None else atm,
            rr=self.rr if rr is None else rr,
            bf=self.bf if bf is None else bf,
            delta_type=self.delta_type,
            premium_adjusted=self.premium_adjusted,
            metadata=dict(self.metadata),
            stale=self.stale if stale is None else stale,
            missing_quotes=list(self.missing_quotes)
            if missing_quotes is None
            else list(missing_quotes),
        )


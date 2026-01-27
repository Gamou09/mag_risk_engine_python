"""Implied vol surface with per-expiry PCHIP smiles and time interpolation.

Lives under risk_engine.models.fx to plug into existing GK pricers via the
VolSurface protocol (vol(T, K)).
"""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

from .market_quotes import MarketSlice, VOL_CAP, VOL_FLOOR
from .smile_interpolator import SmileInterpolator

__all__ = ["VolSurface"]


def _linear_interp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    if x1 == x0:
        return y0
    w = (x - x0) / (x1 - x0)
    return y0 + w * (y1 - y0)


def _nearest_value(values: List[Tuple[float, float]], t: float) -> float | None:
    if not values:
        return None
    return min(values, key=lambda pair: abs(pair[0] - t))[1]


@dataclass
class VolSurface:
    """Vol surface with smile interpolation in strike and linear blending in time."""

    market_slices: List[MarketSlice]
    deltas: Iterable[float] | None = None
    wing_slope_cap: float = 2.5
    vol_floor: float = VOL_FLOOR
    vol_cap: float = VOL_CAP
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.market_slices:
            raise ValueError("market_slices must be non-empty")
        self.market_slices.sort(key=lambda ms: ms.expiry)
        self._expiries = [ms.expiry for ms in self.market_slices]
        self._fill_missing_quotes()

        self._smiles: Dict[float, SmileInterpolator] = {}
        for ms in self.market_slices:
            slope_cap = self.wing_slope_cap
            vol_cap = self.vol_cap
            if ms.stale or ms.missing_quotes:
                slope_cap = min(slope_cap, 1.25)
                vol_cap = self.vol_cap * 1.1
                self.warnings.append(
                    f"Conservative extrapolation applied for T={ms.expiry:.4f} due to stale/missing quotes"
                )
            self._smiles[ms.expiry] = SmileInterpolator(
                ms,
                deltas=self.deltas,
                wing_slope_cap=slope_cap,
                vol_floor=self.vol_floor,
                vol_cap=vol_cap,
            )

    def _fill_missing_quotes(self) -> None:
        rr_by_delta: Dict[float, List[Tuple[float, float]]] = {}
        bf_by_delta: Dict[float, List[Tuple[float, float]]] = {}
        for ms in self.market_slices:
            for d, v in ms.rr.items():
                if v is not None:
                    rr_by_delta.setdefault(d, []).append((ms.expiry, v))
            for d, v in ms.bf.items():
                if v is not None:
                    bf_by_delta.setdefault(d, []).append((ms.expiry, v))

        for ms in self.market_slices:
            updated_rr = dict(ms.rr)
            updated_bf = dict(ms.bf)
            missing: List[str] = []
            for delta in set(ms.rr.keys()) | set(ms.bf.keys()):
                if updated_rr.get(delta) is None:
                    replacement = _nearest_value(rr_by_delta.get(delta, []), ms.expiry) if delta in rr_by_delta else None
                    if replacement is not None:
                        updated_rr[delta] = replacement
                        missing.append(f"RR{int(delta*100)} (filled)")
                    else:
                        missing.append(f"RR{int(delta*100)} (missing)")
                if updated_bf.get(delta) is None:
                    replacement = _nearest_value(bf_by_delta.get(delta, []), ms.expiry) if delta in bf_by_delta else None
                    if replacement is not None:
                        updated_bf[delta] = replacement
                        missing.append(f"BF{int(delta*100)} (filled)")
                    else:
                        missing.append(f"BF{int(delta*100)} (missing)")
            if missing:
                self.warnings.append(
                    f"Missing quotes filled for T={ms.expiry:.4f}: {missing}"
                )
            ms.rr = updated_rr
            ms.bf = updated_bf
            ms.missing_quotes.extend(missing)

    def smile(self, expiry: float) -> SmileInterpolator:
        return self._smiles[expiry]

    def expiries(self) -> List[float]:
        return list(self._expiries)

    def total_variance(self, t: float, strike: float) -> float:
        if t <= 0.0:
            return 0.0
        if t in self._smiles:
            return self._smiles[t].total_variance_from_strike(strike)

        idx = bisect.bisect_left(self._expiries, t)
        if idx == 0:
            return self._smiles[self._expiries[0]].total_variance_from_strike(strike)
        if idx >= len(self._expiries):
            return self._smiles[self._expiries[-1]].total_variance_from_strike(strike)

        t0 = self._expiries[idx - 1]
        t1 = self._expiries[idx]
        w0 = self._smiles[t0].total_variance_from_strike(strike)
        w1 = self._smiles[t1].total_variance_from_strike(strike)
        return _linear_interp(t, t0, t1, w0, w1)

    def vol(self, t: float, strike: float) -> float:
        w = self.total_variance(t, strike)
        if t <= 0.0:
            return self.vol_floor
        sigma = math.sqrt(max(0.0, w) / t)
        return float(min(max(sigma, self.vol_floor), self.vol_cap))


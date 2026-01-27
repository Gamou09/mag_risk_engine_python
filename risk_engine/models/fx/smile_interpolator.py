"""Single-expiry smile interpolation using PCHIP on total variance.

Relies on delta/strike inversion helpers from fx_gk to avoid duplicating BS
logic. Designed to plug into risk_engine pricing stack.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Tuple

import numpy as np
from scipy.interpolate import PchipInterpolator

from risk_engine.models.implementations.fx_gk import strike_from_delta

from .market_quotes import MarketSlice, VOL_CAP, VOL_FLOOR

W_FLOOR = 0.0

__all__ = ["SmileInterpolator"]


def _dedupe_sorted_pairs(nodes: List[Tuple[float, float]], eps: float = 1e-10) -> List[Tuple[float, float]]:
    deduped: List[Tuple[float, float]] = []
    for k, w in nodes:
        if deduped and abs(k - deduped[-1][0]) < eps:
            deduped[-1] = (k, w)
        else:
            deduped.append((k, w))
    return deduped


@dataclass
class SmileInterpolator:
    """Interpolate total variance w(k) for a single expiry."""

    market_slice: MarketSlice
    deltas: Iterable[float] | None = None
    wing_slope_cap: float = 2.5
    vol_floor: float = VOL_FLOOR
    vol_cap: float = VOL_CAP

    def __post_init__(self) -> None:
        ms = self.market_slice
        self._t = float(ms.expiry)
        self._forward = float(ms.forward)
        deltas = list(self.deltas) if self.deltas is not None else ms.available_deltas()
        if not deltas:
            if 0.25 in ms.rr and 0.25 in ms.bf:
                deltas = [0.25]
            else:
                deltas = []

        nodes: List[Tuple[float, float]] = []
        for delta in sorted(set(deltas)):
            if delta in ms.rr and delta in ms.bf and ms.rr[delta] is not None and ms.bf[delta] is not None:
                call_vol, put_vol = ms.wing_vols(delta)
                k_call = math.log(
                    strike_from_delta(
                        target_delta=delta,
                        forward=self._forward,
                        t=self._t,
                        vol=call_vol,
                        call_put="C",
                        df_dom=ms.df_dom,
                        df_for=ms.df_for,
                        delta_type=ms.delta_type,
                        premium_adjusted=ms.premium_adjusted,
                    )
                    / self._forward
                )
                k_put = math.log(
                    strike_from_delta(
                        target_delta=-delta,
                        forward=self._forward,
                        t=self._t,
                        vol=put_vol,
                        call_put="P",
                        df_dom=ms.df_dom,
                        df_for=ms.df_for,
                        delta_type=ms.delta_type,
                        premium_adjusted=ms.premium_adjusted,
                    )
                    / self._forward
                )
                nodes.append((k_put, max(W_FLOOR, put_vol * put_vol * self._t)))
                nodes.append((k_call, max(W_FLOOR, call_vol * call_vol * self._t)))

        atm_w = max(W_FLOOR, ms.atm * ms.atm * self._t)
        nodes.append((0.0, atm_w))

        nodes.sort(key=lambda kv: kv[0])
        nodes = _dedupe_sorted_pairs(nodes)
        if len(nodes) == 1:
            nodes = [(-1e-6, nodes[0][1]), (1e-6, nodes[0][1])]

        self.k_nodes = np.array([k for k, _ in nodes], dtype=float)
        self.w_nodes = np.array([w for _, w in nodes], dtype=float)
        if np.any(np.diff(self.k_nodes) <= 0.0):
            raise ValueError("k nodes must be strictly increasing after dedupe")

        self._pchip = PchipInterpolator(self.k_nodes, self.w_nodes, extrapolate=True)
        deriv = self._pchip.derivative()
        raw_left = float(deriv(self.k_nodes[0]))
        raw_right = float(deriv(self.k_nodes[-1]))
        self._slope_left = max(-self.wing_slope_cap, min(raw_left, self.wing_slope_cap))
        self._slope_right = max(-self.wing_slope_cap, min(raw_right, self.wing_slope_cap))

    @property
    def expiry(self) -> float:
        return self._t

    @property
    def forward(self) -> float:
        return self._forward

    def nodes(self) -> List[Tuple[float, float]]:
        return list(zip(self.k_nodes.tolist(), self.w_nodes.tolist()))

    def total_variance_from_k(self, k: float) -> float:
        if k < self.k_nodes[0]:
            slope = max(-self.wing_slope_cap, min(self._slope_left, self.wing_slope_cap))
            w = self.w_nodes[0] + slope * (k - self.k_nodes[0])
        elif k > self.k_nodes[-1]:
            slope = max(-self.wing_slope_cap, min(self._slope_right, self.wing_slope_cap))
            w = self.w_nodes[-1] + slope * (k - self.k_nodes[-1])
        else:
            w = float(self._pchip(k))
        return max(W_FLOOR, w)

    def total_variance_from_strike(self, strike: float) -> float:
        if strike <= 0.0:
            raise ValueError("strike must be > 0")
        k = math.log(strike / self._forward)
        return self.total_variance_from_k(k)

    def vol_from_k(self, k: float) -> float:
        w = self.total_variance_from_k(k)
        if self._t <= 0.0:
            return self.vol_floor
        sigma = math.sqrt(max(W_FLOOR, w) / self._t)
        return float(min(max(sigma, self.vol_floor), self.vol_cap))

    def vol(self, strike: float) -> float:
        return self.vol_from_k(math.log(strike / self._forward))


"""Validation checks for FX implied vol surfaces (calendar/convexity/fit)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

import numpy as np

from risk_engine.models.implementations.fx_gk import bs_forward_price

from .market_quotes import MarketSlice
from .smile_interpolator import SmileInterpolator
from .vol_surface import VolSurface

__all__ = ["ValidationReport", "validate_surface"]


@dataclass
class ValidationReport:
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, float | Dict[str, float]] = field(default_factory=dict)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def to_text(self) -> str:
        lines = [f"Validation {'PASSED' if self.passed else 'FAILED'}"]
        if self.errors:
            lines.append("Errors:")
            lines.extend([f"  - {e}" for e in self.errors])
        if self.warnings:
            lines.append("Warnings:")
            lines.extend([f"  - {w}" for w in self.warnings])
        if self.metrics:
            lines.append("Metrics:")
            for k, v in self.metrics.items():
                if isinstance(v, dict):
                    lines.append(f"  {k}:")
                    for kk, vv in v.items():
                        lines.append(f"    {kk}: {vv}")
                else:
                    lines.append(f"  {k}: {v}")
        return "\n".join(lines)


def _quote_reproduction(surface: VolSurface, slices: List[MarketSlice]) -> Dict[str, float]:
    errs: Dict[str, float] = {}
    for ms in slices:
        atm_vol = surface.vol(ms.expiry, ms.forward)
        errs[f"T={ms.expiry:.4f}_ATM"] = abs(atm_vol - ms.atm)

        for delta in ms.available_deltas():
            call_vol, put_vol = ms.wing_vols(delta)
            from risk_engine.models.implementations.fx_gk import strike_from_delta

            k_call = math.log(
                strike_from_delta(
                    target_delta=delta,
                    forward=ms.forward,
                    t=ms.expiry,
                    vol=call_vol,
                    call_put="C",
                    df_dom=ms.df_dom,
                    df_for=ms.df_for,
                    delta_type=ms.delta_type,
                    premium_adjusted=ms.premium_adjusted,
                )
                / ms.forward
            )
            k_put = math.log(
                strike_from_delta(
                    target_delta=-delta,
                    forward=ms.forward,
                    t=ms.expiry,
                    vol=put_vol,
                    call_put="P",
                    df_dom=ms.df_dom,
                    df_for=ms.df_for,
                    delta_type=ms.delta_type,
                    premium_adjusted=ms.premium_adjusted,
                )
                / ms.forward
            )
            surf_call = surface.vol(ms.expiry, ms.forward * math.exp(k_call))
            surf_put = surface.vol(ms.expiry, ms.forward * math.exp(k_put))
            errs[f"T={ms.expiry:.4f}_C{int(delta*100)}"] = abs(surf_call - call_vol)
            errs[f"T={ms.expiry:.4f}_P{int(delta*100)}"] = abs(surf_put - put_vol)
    return errs


def _negative_variance(surface: VolSurface, k_grid: Iterable[float]) -> int:
    count = 0
    for t in surface.expiries():
        forward = surface.smile(t).forward
        for k in k_grid:
            strike = forward * math.exp(k)
            w = surface.total_variance(t, strike)
            if w < -1e-14:
                count += 1
    return count


def _calendar_monotone(smiles: List[SmileInterpolator], k_grid: Iterable[float]) -> int:
    violations = 0
    for k in k_grid:
        prev_w = None
        for s in smiles:
            w = s.total_variance_from_k(k)
            if prev_w is not None and w + 1e-12 < prev_w:
                violations += 1
            prev_w = w
    return violations


def _convexity_check(smile: SmileInterpolator, k_grid: Iterable[float]) -> int:
    forward = smile.forward
    T = smile.expiry
    strikes = [forward * math.exp(k) for k in k_grid]
    prices = [
        bs_forward_price(forward=forward, strike=K, vol=smile.vol(K), t=T, call_put="C")
        for K in strikes
    ]
    v = 0
    for i in range(1, len(prices) - 1):
        second = prices[i - 1] - 2 * prices[i] + prices[i + 1]
        if second < -1e-6:
            v += 1
    return v


def validate_surface(
    surface: VolSurface,
    market_slices: List[MarketSlice],
    *,
    k_grid: Iterable[float] | None = None,
    quote_tol: float = 2e-4,
) -> ValidationReport:
    k_grid = list(k_grid) if k_grid is not None else list(np.linspace(-1.0, 1.0, 13))
    report = ValidationReport(passed=True)

    repro_errs = _quote_reproduction(surface, market_slices)
    max_repro = max(repro_errs.values()) if repro_errs else 0.0
    report.metrics["quote_repro_max"] = max_repro
    report.metrics["quote_repro_errors"] = repro_errs
    if max_repro > quote_tol:
        report.add_error(f"Quote reproduction max error {max_repro:.4%} exceeds tolerance {quote_tol:.4%}")

    neg_count = _negative_variance(surface, k_grid)
    report.metrics["neg_variance_points"] = neg_count
    if neg_count > 0:
        report.add_error(f"Found {neg_count} grid points with negative total variance")

    cal_viol = _calendar_monotone([surface.smile(t) for t in surface.expiries()], k_grid)
    report.metrics["calendar_violations"] = cal_viol
    if cal_viol > 0:
        report.add_warning(f"Calendar monotonicity violations: {cal_viol}")

    conv_total = 0
    for s in surface.expiries():
        conv_total += _convexity_check(surface.smile(s), k_grid)
    report.metrics["convexity_violations"] = conv_total
    if conv_total > 0:
        report.add_warning(f"Convexity violations detected: {conv_total}")

    for ms in market_slices:
        if ms.stale:
            report.add_warning(f"Stale quotes for tenor {ms.expiry:.4f}")
        if ms.missing_quotes:
            report.add_warning(
                f"Missing quotes filled/flagged for tenor {ms.expiry:.4f}: {ms.missing_quotes}"
            )

    report.passed = len(report.errors) == 0
    return report

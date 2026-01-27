"""Fictitious FX vol surface examples integrated with risk_engine."""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

import numpy as np

from .market_quotes import MarketSlice, compute_forward
from .vol_surface import VolSurface
from .validation import ValidationReport, validate_surface

PairData = Dict[str, List[Tuple[str, float]]]

__all__ = ["build_example_surfaces", "example_market_data"]


def _tenor_to_years(label: str) -> float:
    unit = label[-1]
    value = float(label[:-1])
    if unit.upper() == "W":
        return value / 52.0
    if unit.upper() == "M":
        return value / 12.0
    if unit.upper() == "Y":
        return value
    raise ValueError(f"Unknown tenor label {label}")


def example_market_data() -> Dict[str, Dict[str, dict]]:
    """Return fictitious market quotes for EURUSD (G10) and two EM pairs."""
    return {
        "EURUSD": {
            "spot": 1.0850,
            "rd": 0.03,
            "rf": 0.015,
            "quotes": {
                "1W": {"atm": 0.075, "rr25": -0.002, "bf25": 0.003},
                "1M": {"atm": 0.085, "rr25": -0.0025, "bf25": 0.0035},
                "3M": {"atm": 0.09, "rr25": -0.003, "bf25": 0.004},
                "6M": {"atm": 0.095, "rr25": -0.003, "bf25": 0.0042},
                "1Y": {"atm": 0.10, "rr25": -0.0035, "bf25": 0.0045},
            },
        },
        "USDTRY": {
            "spot": 29.50,
            "rd": 0.12,
            "rf": 0.025,
            "quotes": {
                "1W": {"atm": 0.32, "rr25": -0.010, "bf25": 0.008, "bf10": 0.010},
                "1M": {"atm": 0.34, "rr25": -0.012, "bf25": 0.010, "rr10": -0.020, "bf10": 0.014},
                "3M": {"atm": 0.30, "rr25": -0.010, "bf25": 0.009, "rr10": -0.018, "bf10": 0.012},
                "6M": {"atm": 0.28, "rr25": None, "bf25": 0.0085, "rr10": -0.015, "bf10": 0.011},
                "1Y": {"atm": 0.26, "rr25": -0.010, "bf25": 0.008, "rr10": -0.014, "bf10": 0.010},
            },
        },
        "USDBRL": {
            "spot": 5.05,
            "rd": 0.085,
            "rf": 0.035,
            "quotes": {
                "1W": {"atm": 0.24, "rr25": -0.006, "bf25": 0.007},
                "1M": {"atm": 0.235, "rr25": -0.006, "bf25": 0.0075},
                "3M": {"atm": 0.23, "rr25": -0.0065, "bf25": 0.0075},
                "6M": {"atm": 0.225, "rr25": -0.007, "bf25": 0.008},
                "1Y": {"atm": 0.22, "rr25": -0.0075, "bf25": 0.0085},
            },
        },
    }


def _build_slices(pair: str, data: dict) -> List[MarketSlice]:
    spot = data["spot"]
    rd = data["rd"]
    rf = data["rf"]
    slices: List[MarketSlice] = []
    for tenor_label, q in data["quotes"].items():
        T = _tenor_to_years(tenor_label)
        df_dom = math.exp(-rd * T)
        df_for = math.exp(-rf * T)
        forward = compute_forward(spot, df_dom, df_for)
        rr = {}
        bf = {}
        for key, val in q.items():
            if key.startswith("rr"):
                delta = float(key[2:]) / 100.0
                rr[delta] = val
            elif key.startswith("bf"):
                delta = float(key[2:]) / 100.0
                bf[delta] = val
        atm = q["atm"]
        slices.append(
            MarketSlice(
                expiry=T,
                forward=forward,
                df_dom=df_dom,
                df_for=df_for,
                atm=atm,
                rr=rr,
                bf=bf,
                delta_type="forward",
                premium_adjusted=False,
                metadata={"pair": pair, "tenor": tenor_label},
                stale=False,
                missing_quotes=[],
            )
        )
    return slices


def build_example_surfaces() -> List[Tuple[str, VolSurface, List[MarketSlice], str, ValidationReport]]:
    out = []
    data = example_market_data()
    for pair, pdata in data.items():
        slices = _build_slices(pair, pdata)
        surface = VolSurface(slices, deltas=[0.25, 0.10], wing_slope_cap=2.0)
        report = validate_surface(surface, slices)
        outcome = "PASS" if report.passed else "FAIL"
        out.append((pair, surface, slices, report.to_text() + f"\nOutcome={outcome}", report))
    return out


if __name__ == "__main__":
    for pair, surface, slices, report_text, _ in build_example_surfaces():
        print("=" * 60)
        print(pair)
        for ms in slices:
            print("  ", ms.describe())
        print(report_text)


"""Bootstrapping and construction utilities for curves/surfaces (TODO)."""

from __future__ import annotations

from typing import Any

from risk_engine.market.curves import BootstrappedZeroCurve


def bootstrap_zero_curve(instruments: list[Any]) -> BootstrappedZeroCurve:
    """Placeholder to turn market instruments into a discount curve."""
    raise NotImplementedError("Curve bootstrapping not yet implemented")


def build_vol_surface(*args: Any, **kwargs: Any) -> Any:
    """Placeholder for vol surface construction."""
    raise NotImplementedError("Vol surface building not yet implemented")


# TODO: add helper objects for interpolation, calibration, and quality checks.

"""Risk factor taxonomy and helpers."""

from __future__ import annotations

from risk_engine.instruments.assets import risk_factors as _factors

RiskFactorKey = str

# Re-export factor constants so existing callers keep working.
_factor_map = {name: getattr(_factors, name) for name in _factors.__all__}
globals().update(_factor_map)

RISK_FACTOR_MAP = _factor_map

__all__ = ["RiskFactorKey", "RISK_FACTOR_MAP"] + list(_factors.__all__)

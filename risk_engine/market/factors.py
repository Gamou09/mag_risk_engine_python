"""Risk factor taxonomy and helpers."""

from __future__ import annotations

from risk_engine.core.instrument_sets import risk_factors as _legacy_factors

RiskFactorKey = str

# Re-export legacy factor constants so existing callers keep working.
_factor_map = {name: getattr(_legacy_factors, name) for name in _legacy_factors.__all__}
globals().update(_factor_map)

RISK_FACTOR_MAP = _factor_map

__all__ = ["RiskFactorKey", "RISK_FACTOR_MAP"] + list(_legacy_factors.__all__)

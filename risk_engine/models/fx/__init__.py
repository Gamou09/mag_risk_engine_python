"""FX implied volatility smile and surface utilities integrated with risk_engine."""

from .market_quotes import MarketSlice, compute_forward, wing_vols_from_rr_bf
from .smile_interpolator import SmileInterpolator
from .vol_surface import VolSurface
from .validation import ValidationReport, validate_surface

__all__ = [
    "MarketSlice",
    "compute_forward",
    "wing_vols_from_rr_bf",
    "SmileInterpolator",
    "VolSurface",
    "ValidationReport",
    "validate_surface",
]


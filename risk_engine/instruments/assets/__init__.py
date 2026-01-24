"""Asset-class specific instrument groupings."""

from .instrument_base import Instrument
from . import (
    instrument_base,
    instruments_commodities,
    instruments_credit,
    instruments_equity,
    instruments_fx,
    instruments_hybrid_exotic_mutliAsset_other,
    instruments_rates,
    risk_factors,
)

__all__ = [
    "Instrument",
    "instrument_base",
    "instruments_commodities",
    "instruments_credit",
    "instruments_equity",
    "instruments_fx",
    "instruments_hybrid_exotic_mutliAsset_other",
    "instruments_rates",
    "risk_factors",
]

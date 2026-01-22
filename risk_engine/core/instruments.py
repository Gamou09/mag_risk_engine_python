"""Instrument definitions and interfaces.

Note: pricing implementations live under risk_engine/models/pricing.
"""

from __future__ import annotations

from risk_engine.core.instrument_sets.instruments_commodities import (  # noqa: F401
    CommodityForward,
    CommodityFuture,
    CommodityOption,
    CommoditySpot,
    CommoditySwap,
)
from risk_engine.core.instrument_sets.instruments_credit import (  # noqa: F401
    CDSIndex,
    CreditDefaultSwap,
    CreditDefaultSwaption,
    TotalReturnSwap,
)
from risk_engine.core.instrument_sets.instruments_equity import (  # noqa: F401
    EquityBarrierOption,
    EquityDigitalOption,
    EquityForward,
    EquityIndexFuture,
    EquitySpot,
    EuropeanOption,
    VarianceSwap,
)
from risk_engine.core.instrument_sets.instruments_exotic import (  # noqa: F401
    BasketOption,
    ForwardStartOption,
    QuantoOption,
    RainbowOption,
)
from risk_engine.core.instrument_sets.instruments_fx import (  # noqa: F401
    FXDigitalOption,
    FXForward,
    FXOption,
    FXSpot,
    FXSwap,
)
from risk_engine.core.instrument_sets.instruments_rates import (  # noqa: F401
    BondOption,
    Cap,
    FixedRateBond,
    Floor,
    FRA,
    InterestRateSwap,
    OISSwap,
    Swaption,
    ZeroCouponBond,
)


__all__ = [
    "EquitySpot",
    "EquityForward",
    "FixedRateBond",
    "ZeroCouponBond",
    "EuropeanOption",
    "InterestRateSwap",
    "OISSwap",
    "FRA",
    "Swaption",
    "Cap",
    "Floor",
    "BondOption",
    "FXSpot",
    "FXForward",
    "FXSwap",
    "FXOption",
    "FXDigitalOption",
    "EquityIndexFuture",
    "EquityDigitalOption",
    "EquityBarrierOption",
    "VarianceSwap",
    "CreditDefaultSwap",
    "CDSIndex",
    "CreditDefaultSwaption",
    "TotalReturnSwap",
    "CommoditySpot",
    "CommodityForward",
    "CommodityFuture",
    "CommoditySwap",
    "CommodityOption",
    "BasketOption",
    "QuantoOption",
    "RainbowOption",
    "ForwardStartOption",
]

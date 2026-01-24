"""Equity instruments."""

from .forward import EquityForward, EquityIndexFuture, EquitySpot
from .option import EquityBarrierOption, EquityDigitalOption, EuropeanOption
from .variance_swap import VarianceSwap

__all__ = [
    "EquitySpot",
    "EquityForward",
    "EquityIndexFuture",
    "EuropeanOption",
    "EquityDigitalOption",
    "EquityBarrierOption",
    "VarianceSwap",
]

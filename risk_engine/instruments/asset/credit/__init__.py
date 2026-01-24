"""Credit instruments."""

from .cds import CDSIndex, CreditDefaultSwap, CreditDefaultSwaption
from .trs import TotalReturnSwap

__all__ = [
    "CreditDefaultSwap",
    "CDSIndex",
    "CreditDefaultSwaption",
    "TotalReturnSwap",
]

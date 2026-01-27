"""Standard pricing result container."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Any
from risk_engine.common.types import Money, Currency

@dataclass(frozen=True)
class PricingResult:
    """Normalized pricing output for pricers to return."""

    pv: Money
    greeks: Mapping[str, float] = field(default_factory=dict)   # factor -> dPV/dFactor
    explain: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    meta: Mapping[str, Any] = field(default_factory=dict)

    @property
    def ccy(self) -> Currency:
        return self.pv.ccy



# TODO: add error collection, scenario slices, and attribution trees.

"""Instrument base interface."""

# from risk_engine.core.instrument_sets.instrument_base import Instrument

# risk_engine/instruments/base.py
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from risk_engine.pricing.context import PricingContext
    from risk_engine.pricing.registry import PricerRegistry
    from risk_engine.pricing.result import PricingResult

@dataclass(frozen=True)
class Instrument:
    """
    Economic terms only. No pricing logic.
    `product_type` is used by the pricer registry.
    """
    product_type: str

    # Optional ergonomic wrapper (delegates to registry)
    def price(self, ctx: PricingContext, registry: PricerRegistry) -> PricingResult:
        return registry.price(self, ctx)


__all__ = ["Instrument"]

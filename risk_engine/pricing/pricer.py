# risk_engine/pricing/pricer.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.result import PricingResult

class InstrumentLike(Protocol):
    product_type: str  # stable identifier for registry dispatch

class Pricer(ABC):
    @abstractmethod
    def price(self, instrument: InstrumentLike, ctx: PricingContext) -> PricingResult:
        raise NotImplementedError

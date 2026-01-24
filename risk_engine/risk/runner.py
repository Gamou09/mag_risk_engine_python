"""RiskRunner orchestrates scenarios, pricing, and aggregation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Protocol

from risk_engine.core.engine import PricingEngine
from risk_engine.instruments.portfolio import Portfolio
from risk_engine.market.state import MarketState
from risk_engine.scenarios.apply import apply_shocks
from risk_engine.scenarios.shock import Shock

# risk_engine/risk/runner.py
from risk_engine.instruments.base import Instrument
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.registry import PricerRegistry

class RiskMeasure(Protocol):
    name: str
    def run(self, portfolio: list[Instrument], ctx: PricingContext, registry: PricerRegistry): ...

@dataclass
class RiskRunner:
    registry: PricerRegistry

    def run(self, measure: RiskMeasure, portfolio: list[Instrument], ctx: PricingContext):
        return measure.run(portfolio, ctx, self.registry)

@dataclass
class RiskRunner_old:
    """Minimal orchestrator; extend with full risk workflows."""

    pricing_engine: PricingEngine = PricingEngine()

    def price(self, portfolio: Portfolio, market: MarketState):
        return self.pricing_engine.price_portfolio(portfolio, market)

    def revalue(self, portfolio: Portfolio, market: MarketState, shocks: Sequence[Shock]):
        shocked_states = apply_shocks(market, shocks)
        return [self.pricing_engine.price_portfolio(portfolio, state) for state in shocked_states]


# TODO: integrate measure selection, aggregation, and reporting hooks.

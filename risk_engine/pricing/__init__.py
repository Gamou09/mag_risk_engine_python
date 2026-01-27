"""Pricing contexts, results, and pricer registry."""

from risk_engine.models.pricing import (
    BlackScholesModel,
    Cashflow,
    CashflowPVModel,
    DiscountingModel,
    Pricer,
    PricingModel,
    present_value,
)

# risk_engine/pricing/__init__.py  (or a bootstrap module)
from risk_engine.pricing.registry import PricerRegistry
from risk_engine.pricing.pricers.rates.fixed_leg_pricer import FixedLegPricer

def default_registry() -> PricerRegistry:
    reg = PricerRegistry()
    reg.register("rates.fixed_leg", FixedLegPricer(), model_id=None, method="analytic")
    return reg

__all__ = [
    "PricingContext",
    "PricingRegistry",
    "PricingResult",
    "PricingModel",
    "Pricer",
    "BlackScholesModel",
    "DiscountingModel",
    "CashflowPVModel",
    "Cashflow",
    "present_value",
]

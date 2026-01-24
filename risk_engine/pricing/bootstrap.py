# risk_engine/pricing/bootstrap.py  (or pricing/__init__.py)
from risk_engine.pricing.registry import PricerRegistry
from risk_engine.pricing.pricers.rates.fixed_leg_pricer import FixedLegPricer
from risk_engine.pricing.pricers.rates.irs_pricer import InterestRateSwapPricer

def default_registry() -> PricerRegistry:
    reg = PricerRegistry()
    reg.register("rates.fixed_leg", FixedLegPricer(), model_id=None, method="analytic")
    reg.register("rates.irs", InterestRateSwapPricer(), model_id=None, method="analytic")
    return reg

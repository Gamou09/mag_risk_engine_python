"""Bond pricer wrapping the existing discounting model."""

from __future__ import annotations

from risk_engine.models.pricing.vanilla import DiscountingModel
from risk_engine.pricing.result import PricingResult


class BondPricer:
    """Thin wrapper to fit the new registry pattern."""

    def __init__(self, model: DiscountingModel | None = None) -> None:
        self.model = model or DiscountingModel()

    def price(self, instrument, **kwargs) -> PricingResult:  # type: ignore[override]
        pv = self.model.price(instrument, **kwargs)
        currency = getattr(instrument, "currency", "USD")
        return PricingResult(pv=float(pv), currency=str(currency))


# TODO: support clean/dirty price, yield calc, and curve-specific discounting.

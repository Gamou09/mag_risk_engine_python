"""Equity option pricer leveraging the Black-Scholes model."""

from __future__ import annotations

from risk_engine.models.pricing.black_scholes import BlackScholesModel
from risk_engine.pricing.result import PricingResult


class EquityOptionPricer(BlackScholesModel):
    """Reuse the existing analytic model under the new layout."""

    def price_with_result(self, instrument) -> PricingResult:
        pv = self.price(instrument)
        currency = getattr(instrument, "currency", "USD")
        return PricingResult(pv=float(pv), currency=str(currency))


# TODO: add dividends/borrowing costs handling and greeks passthrough.

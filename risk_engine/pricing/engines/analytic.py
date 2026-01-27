"""Closed-form engines and utilities."""

from __future__ import annotations

from risk_engine.models.pricing.black_scholes import BlackScholesModel
from risk_engine.models.pricing.cashflows import CashflowPVModel
from risk_engine.models.pricing.vanilla import DiscountingModel


class AnalyticEngine:
    """Lightweight wrapper around an analytic pricing model."""

    def __init__(self, model=None) -> None:
        self.model = model or DiscountingModel()

    def price(self, instrument, **kwargs):
        return self.model.price(instrument, **kwargs)


# Convenience aliases for common models
DISCOUNTING_ENGINE = AnalyticEngine(DiscountingModel())
BLACK_SCHOLES_ENGINE = AnalyticEngine(BlackScholesModel())
CASHFLOW_PV_ENGINE = AnalyticEngine(CashflowPVModel())


# TODO: add analytic greeks/explain support and model selection by instrument type.

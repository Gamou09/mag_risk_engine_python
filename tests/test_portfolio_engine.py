import math

import pytest

from risk_engine.core.engine import MarketData, PricingEngine, Scenario, apply_scenario
from risk_engine.core.instruments import EquitySpot, ZeroCouponBond
from risk_engine.core.portfolio import Portfolio, Position


def test_apply_scenario_additive_shocks():
    base = MarketData(spots={"ABC": 100.0}, rates={"risk_free": 0.02})
    shocked = apply_scenario(base, Scenario(spot_shocks={"ABC": 5.0}))
    assert shocked.spots["ABC"] == pytest.approx(105.0)
    assert shocked.rates["risk_free"] == pytest.approx(0.02)


def test_portfolio_pricing_and_revaluation():
    portfolio = Portfolio(
        positions=[
            Position(instrument=EquitySpot(spot=100.0, symbol="ABC"), quantity=1.0),
            Position(instrument=ZeroCouponBond(face=1000.0, maturity=1.0), quantity=1.0),
        ]
    )
    market = MarketData(spots={"ABC": 100.0}, rates={"risk_free": 0.02})
    engine = PricingEngine()

    base_value = engine.price_portfolio(portfolio, market)
    expected_bond = 1000.0 * math.exp(-0.02 * 1.0)
    assert base_value.total == pytest.approx(100.0 + expected_bond)

    scenarios = [Scenario(spot_shocks={"ABC": 10.0})]
    reval = engine.revalue_scenarios(portfolio, market, scenarios)
    assert reval.pnls[0] == pytest.approx(10.0)

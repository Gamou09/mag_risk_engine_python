import math

import pytest

from risk_engine.models.pricing import Cashflow, CashflowPVModel, present_value


def test_present_value_flat_rate():
    cashflows = [
        Cashflow(time=1.0, amount=100.0),
        Cashflow(time=2.0, amount=50.0),
    ]
    pv = present_value(cashflows, rate=0.05)
    expected = 100.0 * math.exp(-0.05 * 1.0) + 50.0 * math.exp(-0.05 * 2.0)
    assert pv == pytest.approx(expected)


def test_cashflow_pv_model_matches_function():
    cashflows = [
        Cashflow(time=0.5, amount=10.0),
        Cashflow(time=1.5, amount=20.0),
    ]
    pv = present_value(cashflows, rate=0.03)
    model = CashflowPVModel(rate=0.03)
    assert model.price(cashflows) == pytest.approx(pv)

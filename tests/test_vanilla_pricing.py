import math

import pytest

from risk_engine.core.instruments import EquityForward, EquitySpot, FixedRateBond, ZeroCouponBond
from risk_engine.models.pricing import DiscountingModel


def test_equity_spot_pricing():
    model = DiscountingModel(rate=0.03)
    instrument = EquitySpot(spot=123.45, symbol="ABC")
    assert model.price(instrument) == pytest.approx(123.45)


def test_equity_forward_pricing():
    model = DiscountingModel(rate=0.05)
    instrument = EquityForward(
        spot=100.0,
        strike=102.0,
        maturity=1.0,
        rate=0.05,
        dividend_yield=0.02,
        symbol="ABC",
    )
    price = model.price(instrument)
    expected = 100.0 * math.exp(-0.02) - 102.0 * math.exp(-0.05)
    assert price == pytest.approx(expected)


def test_zero_coupon_bond_pricing():
    model = DiscountingModel(rate=0.04)
    bond = ZeroCouponBond(face=1000.0, maturity=2.0)
    expected = 1000.0 * math.exp(-0.04 * 2.0)
    assert model.price(bond) == pytest.approx(expected)


def test_fixed_rate_bond_pricing():
    model = DiscountingModel(rate=0.03)
    bond = FixedRateBond(face=1000.0, coupon_rate=0.06, maturity=2.0, payments_per_year=2)
    coupon = 1000.0 * 0.06 / 2
    expected = (
        coupon * math.exp(-0.03 * 0.5)
        + coupon * math.exp(-0.03 * 1.0)
        + coupon * math.exp(-0.03 * 1.5)
        + (coupon + 1000.0) * math.exp(-0.03 * 2.0)
    )
    assert model.price(bond) == pytest.approx(expected)

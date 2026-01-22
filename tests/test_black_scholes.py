import math

import pytest

from risk_engine.models.pricing import BlackScholesModel, EuropeanOption


def test_black_scholes_price_and_implied_vol():
    model = BlackScholesModel()
    option = EuropeanOption(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        vol=0.2,
        option_type="call",
    )

    price = model.price(option)
    assert price == pytest.approx(10.4506, rel=1e-4)

    implied = model.implied_vol(option, target_price=price)
    assert implied == pytest.approx(option.vol, rel=1e-4)


def test_black_scholes_put_price():
    model = BlackScholesModel()
    option = EuropeanOption(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        vol=0.2,
        option_type="put",
    )

    price = model.price(option)
    assert price == pytest.approx(5.5735, rel=1e-4)


def test_black_scholes_greeks_signs():
    model = BlackScholesModel()
    call = EuropeanOption(
        spot=100.0,
        strike=110.0,
        maturity=1.0,
        rate=0.01,
        vol=0.25,
        option_type="call",
    )
    put = EuropeanOption(
        spot=100.0,
        strike=110.0,
        maturity=1.0,
        rate=0.01,
        vol=0.25,
        option_type="put",
    )

    call_greeks = model.greeks(call)
    put_greeks = model.greeks(put)

    assert call_greeks is not None and put_greeks is not None
    assert call_greeks["delta"] > 0.0
    assert put_greeks["delta"] < 0.0
    assert math.isfinite(call_greeks["gamma"])
    assert math.isfinite(put_greeks["gamma"])

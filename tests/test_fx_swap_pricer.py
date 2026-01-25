import pytest

from risk_engine.instruments.assets.instruments_fx import PricingFXSwap
from risk_engine.market.curve_registry import default_curve_registry
from risk_engine.market.ids import CurveId
from risk_engine.market.state import MarketState
from risk_engine.pricing.bootstrap import default_registry
from risk_engine.pricing.context import PricingContext


def _ctx_with_factors(factors: dict[str, float]) -> PricingContext:
    registry = default_curve_registry()
    state = MarketState(
        factors=factors,
        discount_curves={"USD": CurveId("OIS_USD_3M")},
        registry=registry,
    )
    return PricingContext(market=state, method="analytic")


def _build_swap() -> PricingFXSwap:
    return PricingFXSwap(
        pair="EURUSD",
        notional=5_000_000,
        near_maturity="1M",
        far_maturity="6M",
        near_forward=1.0880,
        far_forward=1.1050,
        direction="buy_base",
    )


def test_fx_swap_pricer_outright_forwards() -> None:
    ctx = _ctx_with_factors(
        {
            "DF.OIS_USD_3M.1M": 0.9990,
            "DF.OIS_USD_3M.6M": 0.9845,
            "FWD.EURUSD.1M": 1.0850,
            "FWD.EURUSD.6M": 1.1000,
        }
    )
    reg = default_registry()
    swap = _build_swap()

    res = reg.price(swap, ctx)

    assert res.pv.amount == pytest.approx(-39_597.5, rel=1e-8)
    assert res.pv.currency == "USD"
    assert res.greeks["FWD.EURUSD.1M"] == pytest.approx(4_995_000.0)
    assert res.greeks["FWD.EURUSD.6M"] == pytest.approx(4_922_500.0)
    assert not res.warnings


def test_fx_swap_pricer_spot_plus_points_fallback() -> None:
    ctx = _ctx_with_factors(
        {
            "DF.OIS_USD_3M.1M": 0.9990,
            "DF.OIS_USD_3M.6M": 0.9845,
            "SPOT.EURUSD": 1.0820,
            "FWDPTS.EURUSD.1M": 0.0030,
            "FWDPTS.EURUSD.6M": 0.0180,
        }
    )
    reg = default_registry()
    swap = _build_swap()

    res = reg.price(swap, ctx)

    assert res.pv.amount == pytest.approx(-39_597.5, rel=1e-8)
    # Sensitivities split across spot and forward points
    assert res.greeks["SPOT.EURUSD"] == pytest.approx(9_917_500.0)
    assert res.greeks["FWDPTS.EURUSD.1M"] == pytest.approx(4_995_000.0)
    assert res.greeks["FWDPTS.EURUSD.6M"] == pytest.approx(4_922_500.0)
    assert not res.warnings


def test_fx_swap_parity_warning_when_mismatch() -> None:
    ctx = _ctx_with_factors(
        {
            "DF.OIS_USD_3M.1M": 0.9990,
            "DF.OIS_USD_3M.6M": 0.9845,
            "FWD.EURUSD.1M": 1.0850,
            "FWD.EURUSD.6M": 1.1000,
            "SPOT.EURUSD": 1.0700,  # inconsistent with forwards below
            "FWDPTS.EURUSD.1M": 0.0100,
            "FWDPTS.EURUSD.6M": 0.0400,
        }
    )
    reg = default_registry()
    swap = _build_swap()

    res = reg.price(swap, ctx)

    assert res.pv.amount == pytest.approx(-39_597.5, rel=1e-8)
    assert res.warnings  # parity mismatch flagged
    assert any("Parity mismatch" in w for w in res.warnings)

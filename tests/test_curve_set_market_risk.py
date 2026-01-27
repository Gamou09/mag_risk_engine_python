import math

import pytest

from risk_engine.market.curve_set import CurveSet
from risk_engine.market.curves import FlatForwardCurve, FlatZeroDiscountCurve
from risk_engine.market.ids import CurveId
from risk_engine.market.market import Market
from risk_engine.pricing.instruments import FloatLegSpec, Swap
from risk_engine.pricing.pricers import SwapPricer
from risk_engine.risk.bump import bump_market
from risk_engine.risk.requests import RiskRequest
from risk_engine.risk.sensitivities import curve_sensitivities


def _usd_curve_set() -> CurveSet:
    disc = FlatZeroDiscountCurve(CurveId("USD-OIS"), "USD", r=0.02)
    fwd = FlatForwardCurve(CurveId("USD-3M"), "USD", index="3M", f=0.03)
    return CurveSet(currency="USD", discount=disc, forwards={"3M": fwd})


def test_curve_set_forward_missing() -> None:
    curve_set = _usd_curve_set()
    with pytest.raises(KeyError):
        curve_set.forward("6M")


def test_curve_set_bump_curve_behaviour() -> None:
    cs = _usd_curve_set()
    discount_id = cs.discount.id
    forward_id = cs.forward("3M").id

    bumped_discount = cs.bump_curve(discount_id, 10.0)
    assert bumped_discount.discount.r == pytest.approx(cs.discount.r + 10.0 * 1e-4)
    assert bumped_discount.forward("3M") is cs.forward("3M")

    bumped_forward = cs.bump_curve(forward_id, 5.0)
    assert bumped_forward.discount is cs.discount
    assert bumped_forward.forward("3M").f == pytest.approx(cs.forward("3M").f + 5.0 * 1e-4)

    with pytest.raises(KeyError):
        cs.bump_curve(CurveId("UNKNOWN"), 1.0)


def test_market_spot_inversion() -> None:
    cs = _usd_curve_set()
    market = Market(curve_sets={"USD": cs}, fx_spot={("EUR", "USD"): 1.25})
    assert market.spot("EUR", "USD") == pytest.approx(1.25)
    assert market.spot("USD", "EUR") == pytest.approx(1 / 1.25)
    with pytest.raises(KeyError):
        market.spot("GBP", "CHF")


def test_bump_market_replaces_only_owner() -> None:
    usd_cs = _usd_curve_set()
    eur_discount = FlatZeroDiscountCurve(CurveId("EUR-OIS"), "EUR", r=0.015)
    eur_forward = FlatForwardCurve(CurveId("EUR-6M"), "EUR", index="6M", f=0.025)
    eur_cs = CurveSet(currency="EUR", discount=eur_discount, forwards={"6M": eur_forward})

    market = Market(curve_sets={"USD": usd_cs, "EUR": eur_cs})
    bumped = bump_market(market, eur_discount.id, 1.0)

    assert bumped is not market
    assert bumped.curves("USD") is market.curves("USD")
    assert bumped.curves("EUR").discount.r == pytest.approx(eur_discount.r + 1.0 * 1e-4)

    with pytest.raises(KeyError):
        bump_market(market, CurveId("MISSING"), 1.0)


def test_curve_sensitivities_discount_and_forward_signs() -> None:
    cs = _usd_curve_set()
    market = Market(curve_sets={"USD": cs})
    swap = Swap(
        currency="USD",
        notional=1_000_000.0,
        fixed_rate=0.02,
        pay_times=(0.5, 1.0),
        accruals=(0.5, 0.5),
        float_leg=FloatLegSpec(currency="USD", index="3M"),
    )
    pricer_map = {Swap: SwapPricer()}
    req = RiskRequest(bp=1.0, curves=(cs.discount.id, cs.forward("3M").id))

    risks = curve_sensitivities([swap], pricer_map, market, req)

    assert len(risks) == 2
    assert risks[0].curve_id == cs.discount.id
    assert risks[1].curve_id == cs.forward("3M").id
    assert risks[0].dPV < 0  # higher discount rate reduces PV
    assert risks[1].dPV > 0  # higher forward rate increases float leg


def test_swap_pricer_end_to_end_and_risk_all_curves() -> None:
    discount = FlatZeroDiscountCurve(CurveId("GBP-OIS"), "GBP", r=0.02)
    forward = FlatForwardCurve(CurveId("GBP-3M"), "GBP", index="3M", f=0.03)
    curve_set = CurveSet(currency="GBP", discount=discount, forwards={"3M": forward})
    market = Market(curve_sets={"GBP": curve_set})

    swap = Swap(
        currency="GBP",
        notional=500_000.0,
        fixed_rate=0.025,
        pay_times=(0.5, 1.0),
        accruals=(0.5, 0.5),
        float_leg=FloatLegSpec(currency="GBP", index="3M"),
    )

    pricer = SwapPricer()
    pv = pricer.pv(swap, market)
    assert math.isfinite(pv)

    risks = curve_sensitivities([swap], {Swap: pricer}, market, RiskRequest())
    assert len(risks) == 2
    assert {risk.curve_id for risk in risks} == set(curve_set.curve_ids())

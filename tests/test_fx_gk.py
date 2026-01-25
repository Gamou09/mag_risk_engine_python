"""Tests for FX Garman–Kohlhagen pricer."""

import math

import pytest

from risk_engine.models.implementations.fx_gk import (
    FXEuropeanOption,
    FlatDiscountCurve,
    FlatVol,
    gk_greeks,
    gk_price,
)


def _finite_diff_delta(option, spot, dom, forc, vol_surface, bump: float) -> float:
    up = gk_price(option, spot * (1.0 + bump), dom, forc, vol_surface)
    dn = gk_price(option, spot * (1.0 - bump), dom, forc, vol_surface)
    return (up - dn) / (2.0 * spot * bump)


def _finite_diff_gamma(option, spot, dom, forc, vol_surface, bump: float) -> float:
    up = gk_price(option, spot * (1.0 + bump), dom, forc, vol_surface)
    mid = gk_price(option, spot, dom, forc, vol_surface)
    dn = gk_price(option, spot * (1.0 - bump), dom, forc, vol_surface)
    return (up - 2.0 * mid + dn) / (spot * spot * bump * bump)


def _finite_diff_vega(option, spot, dom, forc, vol_surface, bump: float) -> float:
    sigma = vol_surface.sigma
    up_vol = FlatVol(sigma * (1.0 + bump))
    dn_vol = FlatVol(max(sigma * (1.0 - bump), 1e-12))
    up = gk_price(option, spot, dom, forc, up_vol)
    dn = gk_price(option, spot, dom, forc, dn_vol)
    return (up - dn) / (2.0 * sigma * bump)


def test_put_call_parity():
    spot = 1.12
    T = 1.5
    K = 1.10
    notional = 5_000_000.0
    dom = FlatDiscountCurve(0.03)
    forc = FlatDiscountCurve(0.01)
    vol = FlatVol(0.18)

    call = FXEuropeanOption("C", K, T, notional, direction=1)
    put = FXEuropeanOption("P", K, T, notional, direction=1)

    call_pv = gk_price(call, spot, dom, forc, vol)
    put_pv = gk_price(put, spot, dom, forc, vol)

    df_d = dom.df(T)
    df_f = forc.df(T)
    parity_rhs = spot * df_f * notional - K * df_d * notional

    assert call_pv - put_pv == pytest.approx(parity_rhs, rel=1e-10, abs=1e-6)


@pytest.mark.parametrize("T, sigma", [(0.0, 0.2), (1.0, 0.0)])
def test_limit_cases_intrinsic(T, sigma):
    spot = 1.05
    K = 1.00
    notional = 1_000_000.0
    dom = FlatDiscountCurve(0.02)
    forc = FlatDiscountCurve(0.01)
    vol = FlatVol(sigma)

    call = FXEuropeanOption("C", K, T, notional, direction=1)
    put = FXEuropeanOption("P", K, T, notional, direction=1)

    call_pv = gk_price(call, spot, dom, forc, vol)
    put_pv = gk_price(put, spot, dom, forc, vol)

    forward = spot * forc.df(T) / dom.df(T)
    intrinsic_call = max(forward - K, 0.0) * dom.df(T) * notional
    intrinsic_put = max(K - forward, 0.0) * dom.df(T) * notional

    assert call_pv == pytest.approx(intrinsic_call, rel=1e-10, abs=1e-6)
    assert put_pv == pytest.approx(intrinsic_put, rel=1e-10, abs=1e-6)

    call_g = gk_greeks(call, spot, dom, forc, vol)
    put_g = gk_greeks(put, spot, dom, forc, vol)
    assert call_g["gamma_spot"] == 0.0
    assert put_g["gamma_spot"] == 0.0
    assert call_g["vega"] == 0.0
    assert put_g["vega"] == 0.0


def test_greeks_match_finite_difference():
    spot = 1.07
    T = 2.4
    K = 1.10
    sigma = 0.22
    notional = 2_500_000.0
    dom = FlatDiscountCurve(0.025)
    forc = FlatDiscountCurve(0.012)
    vol = FlatVol(sigma)

    option = FXEuropeanOption("C", K, T, notional, direction=1)
    greeks = gk_greeks(option, spot, dom, forc, vol)

    bump_s = 1e-4
    bump_v = 1e-4

    fd_delta = _finite_diff_delta(option, spot, dom, forc, vol, bump_s)
    fd_gamma = _finite_diff_gamma(option, spot, dom, forc, vol, bump_s)
    fd_vega = _finite_diff_vega(option, spot, dom, forc, vol, bump_v)

    # Use tolerant comparison; finite differences are noisy.
    assert greeks["delta_spot"] == pytest.approx(fd_delta, rel=5e-4, abs=1e-2)
    assert greeks["gamma_spot"] == pytest.approx(fd_gamma, rel=5e-3, abs=1e-6)
    assert greeks["vega"] == pytest.approx(fd_vega, rel=5e-4, abs=1e-2)

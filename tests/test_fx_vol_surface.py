import math

import numpy as np
import pytest

from risk_engine.models.fx.market_quotes import MarketSlice
from risk_engine.models.fx.smile_interpolator import SmileInterpolator
from risk_engine.models.fx.vol_surface import VolSurface
from risk_engine.models.implementations.fx_gk import (
    bs_forward_delta,
    strike_from_delta,
)
from risk_engine.models.fx.validation import validate_surface


def _simple_slice():
    return MarketSlice(
        expiry=0.5,
        forward=1.0,
        df_dom=1.0,
        df_for=1.0,
        atm=0.20,
        rr={0.25: -0.01},
        bf={0.25: 0.005},
    )


def test_call_delta_monotone_decreasing_in_strike():
    forward = 1.05
    vol = 0.12
    t = 0.5
    strikes = np.linspace(0.8, 1.3, 25)
    deltas = [bs_forward_delta(forward, k, vol, t, call_put="C") for k in strikes]
    assert all(deltas[i] >= deltas[i + 1] - 1e-12 for i in range(len(deltas) - 1))


@pytest.mark.parametrize("cp,target", [("C", 0.25), ("P", -0.25)])
def test_strike_from_delta_round_trip(cp, target):
    forward = 1.1
    vol = 0.18
    t = 0.75
    strike = strike_from_delta(target, forward, t, vol, call_put=cp, delta_type="forward")
    implied = bs_forward_delta(forward, strike, vol, t, call_put=cp, delta_type="forward")
    assert math.isclose(implied, target, abs_tol=1e-7)


def test_smile_pchip_hits_nodes():
    ms = _simple_slice()
    smile = SmileInterpolator(ms)
    for k, w in smile.nodes():
        assert math.isclose(smile.total_variance_from_k(k), w, abs_tol=1e-12)


def test_time_interpolation_total_variance_linear():
    ms1 = _simple_slice()
    ms2 = _simple_slice().clone_with_updates(atm=0.30)
    ms2.expiry = 1.0
    surface = VolSurface([ms1, ms2])
    strike = 1.0
    w_half = surface.total_variance(0.75, strike)
    w1 = surface.total_variance(0.5, strike)
    w2 = surface.total_variance(1.0, strike)
    expected = w1 + (0.75 - 0.5) / (1.0 - 0.5) * (w2 - w1)
    assert math.isclose(w_half, expected, abs_tol=1e-12)


def test_missing_quote_fallback_warns():
    ms1 = _simple_slice()
    ms2 = _simple_slice().clone_with_updates()
    ms2.expiry = 1.0
    ms2.rr[0.25] = None
    ms2.bf[0.25] = None
    surface = VolSurface([ms1, ms2])
    report = validate_surface(surface, [ms1, ms2])
    assert any("Missing quotes" in w for w in report.warnings)


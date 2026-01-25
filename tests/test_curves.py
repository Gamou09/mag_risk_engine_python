import math

import pytest

from risk_engine.models.curves_surfaces import BootstrappedZeroCurve, FlatZeroCurve, PiecewiseZeroCurve


def test_flat_zero_curve_df():
    curve = FlatZeroCurve(rate=0.03)
    assert curve.df(2.0) == pytest.approx(math.exp(-0.03 * 2.0))


def test_piecewise_zero_curve_interpolation():
    curve = PiecewiseZeroCurve(times=[1.0, 2.0], zero_rates=[0.02, 0.04])
    df_at_15 = curve.df(1.5)
    expected_rate = 0.03
    assert df_at_15 == pytest.approx(math.exp(-expected_rate * 1.5))


def test_bootstrapped_zero_curve_log_df_interpolation():
    curve = BootstrappedZeroCurve(times=[1.0, 2.0], discount_factors=[0.98, 0.90])
    df_at_15 = curve.df(1.5)
    expected = math.exp(0.5 * (math.log(0.98) + math.log(0.90)))
    assert df_at_15 == pytest.approx(expected)

"""Production-ready Garman–Kohlhagen (FX Black–Scholes) pricer.

The implementation here is intentionally small and dependency–light while
remaining numerically robust for typical risk/PnL use cases. Pricing and
Greeks are returned in the **domestic** currency. Vega is per unit of vol
(e.g. per 1.00 absolute volatility, not percentage).

Key conventions
---------------
- ``call_put``: ``"C"`` for call, ``"P"`` for put (case-insensitive).
- ``expiry`` ``T``: year fraction in ACT/365 or whichever day-count the caller
  uses; must be non‑negative.
- ``notional``: payout notionals are in domestic currency; ``direction`` is
  +1 for long, -1 for short.
- Discount factors and vols are retrieved via lightweight interfaces to keep
  the module reusable without pulling the wider risk engine.
"""

from __future__ import annotations

import math
from typing import Dict, Literal
from scipy.optimize import brentq

from risk_engine.instruments.assets.instruments_fx import FXEuropeanOption
from risk_engine.utils.numeric import (
    norm_cdf as _norm_cdf,
    norm_pdf as _norm_pdf,
    validate_positive as _validate_positive,
)
from ..curves_surfaces.discount import DiscountCurve, FlatDiscountCurve
from ..curves_surfaces.vol_surfaces import VolSurface, FlatVol

__all__ = [
    "FXEuropeanOption",
    "DiscountCurve",
    "FlatDiscountCurve",
    "FlatVol",
    "gk_price",
    "gk_greeks",
    "gk_implied_vol",
    "bs_forward_price",
    "bs_forward_delta",
    "strike_from_delta",
    "GarmanKohlhagen",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EPS_T = 1e-12  # threshold for treating maturity as now
_EPS_SIGMA = 1e-12  # avoid divide-by-zero in Greeks
_VOL_FLOOR = 1e-4
_VOL_CAP = 5.0
_BRACKET_EXPANSION = 0.75


# ---------------------------------------------------------------------------
# Core pricing & Greeks
# ---------------------------------------------------------------------------


def _clip_vol(vol: float) -> float:
    return min(max(vol, _VOL_FLOOR), _VOL_CAP)


def _d1_d2_forward(forward: float, strike: float, vol: float, t: float) -> tuple[float, float]:
    sigma = _clip_vol(vol)
    if t <= _EPS_T:
        return 0.0, 0.0
    sqrt_t = math.sqrt(t)
    denom = sigma * sqrt_t
    d1 = (math.log(forward / strike) + 0.5 * sigma * sigma * t) / denom
    d2 = d1 - denom
    return d1, d2


def bs_forward_price(
    forward: float,
    strike: float,
    vol: float,
    t: float,
    call_put: str = "C",
    df_dom: float = 1.0,
) -> float:
    """Black price using forward as underlying; discounted by df_dom."""
    _validate_positive("forward", forward)
    _validate_positive("strike", strike)
    if df_dom <= 0.0:
        raise ValueError("df_dom must be > 0")

    sigma = _clip_vol(vol)
    cp = call_put.upper()
    cp_sign = 1.0 if cp == "C" else -1.0
    if t <= _EPS_T or sigma <= _VOL_FLOOR:
        intrinsic = max(cp_sign * (forward - strike), 0.0)
        return float(df_dom * intrinsic)

    d1, d2 = _d1_d2_forward(forward, strike, sigma, t)
    price_fwd = cp_sign * (
        forward * _norm_cdf(cp_sign * d1) - strike * _norm_cdf(cp_sign * d2)
    )
    return float(df_dom * price_fwd)


def bs_forward_delta(
    forward: float,
    strike: float,
    vol: float,
    t: float,
    call_put: str = "C",
    df_dom: float = 1.0,
    df_for: float = 1.0,
    delta_type: Literal["forward", "spot"] = "forward",
    premium_adjusted: bool = False,
    spot: float | None = None,
) -> float:
    """FX delta with forward/spot and premium-adjusted conventions."""
    _validate_positive("forward", forward)
    _validate_positive("strike", strike)
    if df_dom <= 0.0 or df_for <= 0.0:
        raise ValueError("discount factors must be > 0")

    cp = call_put.upper()
    cp_sign = 1.0 if cp == "C" else -1.0
    sigma = _clip_vol(vol)

    if t <= _EPS_T or sigma <= _VOL_FLOOR:
        itm = cp_sign * (forward - strike) > 0.0
        base_forward = cp_sign if itm else 0.0
    else:
        d1, _ = _d1_d2_forward(forward, strike, sigma, t)
        base_forward = cp_sign * _norm_cdf(cp_sign * d1)

    base_delta = base_forward if delta_type == "forward" else df_for * base_forward
    if not premium_adjusted:
        return float(base_delta)

    premium = bs_forward_price(forward, strike, sigma, t, cp, df_dom)
    if delta_type == "spot":
        if spot is None:
            spot = forward * df_dom / df_for
        adjustment = premium / spot
    else:
        adjustment = premium / (df_dom * forward)
    return float(base_delta - adjustment)


def strike_from_delta(
    target_delta: float,
    forward: float,
    t: float,
    vol: float,
    call_put: str = "C",
    df_dom: float = 1.0,
    df_for: float = 1.0,
    delta_type: Literal["forward", "spot"] = "forward",
    premium_adjusted: bool = False,
    spot: float | None = None,
    k_lower: float = -1.5,
    k_upper: float = 1.5,
    max_expansions: int = 8,
    tol: float = 1e-10,
) -> float:
    """Invert delta to strike using Brent search in log-strike space."""
    _validate_positive("forward", forward)
    if df_dom <= 0.0 or df_for <= 0.0:
        raise ValueError("discount factors must be > 0")

    sigma = _clip_vol(vol)

    def delta_for_k(k: float) -> float:
        strike = forward * math.exp(k)
        return bs_forward_delta(
            forward,
            strike,
            sigma,
            t,
            call_put=call_put,
            df_dom=df_dom,
            df_for=df_for,
            delta_type=delta_type,
            premium_adjusted=premium_adjusted,
            spot=spot,
        )

    low_k = k_lower
    high_k = k_upper
    for _ in range(max_expansions + 1):
        f_low = delta_for_k(low_k) - target_delta
        f_high = delta_for_k(high_k) - target_delta
        if f_low == 0.0:
            return forward * math.exp(low_k)
        if f_high == 0.0:
            return forward * math.exp(high_k)
        if f_low * f_high < 0.0:
            root = brentq(lambda kk: delta_for_k(kk) - target_delta, low_k, high_k, xtol=tol, rtol=1e-12, maxiter=200)
            return float(forward * math.exp(root))
        low_k -= _BRACKET_EXPANSION
        high_k += _BRACKET_EXPANSION

    raise ValueError(
        "Failed to bracket target delta; widen k bounds or verify input consistency."
    )


def gk_price(
    option: FXEuropeanOption,
    spot: float,
    dom_curve: DiscountCurve,
    for_curve: DiscountCurve,
    vol_surface: VolSurface,
) -> float:
    """Garman–Kohlhagen PV (domestic currency).

    The returned PV is scaled by ``option.notional`` and ``option.direction``.
    """

    _validate_positive("spot", spot)
    T = max(option.expiry, 0.0)
    df_d = dom_curve.df(T)
    df_f = for_curve.df(T)
    if df_d <= 0.0 or df_f <= 0.0:
        raise ValueError("discount factors must be positive")

    forward = spot * df_f / df_d
    _validate_positive("forward", forward)

    K = option.strike
    cp = option.call_put.upper()
    cp_sign = 1.0 if cp == "C" else -1.0

    sigma = vol_surface.vol(T, K)
    if sigma < 0.0:
        raise ValueError("sigma must be >= 0")

    # Degenerate cases: immediate expiry or essentially zero vol.
    if T <= _EPS_T or sigma <= _EPS_SIGMA:
        intrinsic = max(cp_sign * (forward - K), 0.0)
        pv = df_d * intrinsic
        return float(pv * option.notional * option.direction)

    sqrt_t = math.sqrt(T)
    denom = sigma * sqrt_t
    d1 = (math.log(forward / K) + 0.5 * sigma * sigma * T) / denom
    d2 = d1 - denom

    if cp == "C":
        pv = df_d * (forward * _norm_cdf(d1) - K * _norm_cdf(d2))
    else:
        pv = df_d * (K * _norm_cdf(-d2) - forward * _norm_cdf(-d1))

    return float(pv * option.notional * option.direction)


def gk_greeks(
    option: FXEuropeanOption,
    spot: float,
    dom_curve: DiscountCurve,
    for_curve: DiscountCurve,
    vol_surface: VolSurface,
) -> Dict[str, float]:
    """Analytic Greeks under the GK (domestic numeraire) model.

    Returns a mapping with keys: ``delta_spot``, ``gamma_spot``, ``vega``,
    and explainability fields ``df_d``, ``df_f``, ``forward``, ``d1``, ``d2``.
    All values are already scaled by ``notional`` and ``direction``.
    """

    _validate_positive("spot", spot)
    T = max(option.expiry, 0.0)
    df_d = dom_curve.df(T)
    df_f = for_curve.df(T)
    if df_d <= 0.0 or df_f <= 0.0:
        raise ValueError("discount factors must be positive")

    forward = spot * df_f / df_d
    _validate_positive("forward", forward)

    K = option.strike
    cp = option.call_put.upper()
    sigma = vol_surface.vol(T, K)
    if sigma < 0.0:
        raise ValueError("sigma must be >= 0")

    scaled = option.notional * option.direction

    # Handle immediate expiry or effectively zero vol: Greeks mostly vanish.
    if T <= _EPS_T or sigma <= _EPS_SIGMA:
        itm_call = forward > K
        if cp == "C":
            delta = df_f if itm_call else 0.0
        else:
            delta = -df_f if not itm_call else 0.0
        return {
            "delta_spot": float(delta * scaled),
            "gamma_spot": 0.0,
            "vega": 0.0,
            "df_d": df_d,
            "df_f": df_f,
            "forward": forward,
            "d1": 0.0,
            "d2": 0.0,
        }

    sqrt_t = math.sqrt(T)
    denom = sigma * sqrt_t
    d1 = (math.log(forward / K) + 0.5 * sigma * sigma * T) / denom
    d2 = d1 - denom
    pdf_d1 = _norm_pdf(d1)

    if cp == "C":
        delta = df_f * _norm_cdf(d1)
    else:
        delta = df_f * (_norm_cdf(d1) - 1.0)

    gamma = df_f * pdf_d1 / (spot * denom)
    vega = spot * df_f * pdf_d1 * sqrt_t

    return {
        "delta_spot": float(delta * scaled),
        "gamma_spot": float(gamma * scaled),
        "vega": float(vega * scaled),
        "df_d": df_d,
        "df_f": df_f,
        "forward": forward,
        "d1": d1,
        "d2": d2,
    }


def gk_implied_vol(
    option: FXEuropeanOption,
    spot: float,
    target_price: float,
    dom_curve: DiscountCurve,
    for_curve: DiscountCurve,
    *,
    tol: float = 1e-7,
    max_iter: int = 200,
    vol_lower: float = 1e-6,
    vol_upper: float = 3.0,
) -> float:
    """
    Solve for implied volatility using bisection on the GK price.

    Parameters
    ----------
    target_price: PV in domestic currency (same scaling as gk_price).
    vol_lower, vol_upper: search bracket in absolute vol (e.g. 0.2 = 20%).
    """

    if target_price < 0.0:
        raise ValueError("target_price must be >= 0")
    if tol <= 0.0:
        raise ValueError("tol must be > 0")
    if max_iter <= 0:
        raise ValueError("max_iter must be > 0")
    if vol_lower <= 0.0 or vol_upper <= 0.0 or vol_lower >= vol_upper:
        raise ValueError("invalid volatility bounds")

    # Quick bounds check for T ~ 0 or zero price
    if option.expiry <= _EPS_T or target_price == 0.0:
        return 0.0

    def price_for(vol: float) -> float:
        return gk_price(option, spot, dom_curve, for_curve, FlatVol(vol))

    low = vol_lower
    high = vol_upper
    price_low = price_for(low)
    price_high = price_for(high)
    if target_price < price_low or target_price > price_high:
        raise ValueError("target_price is outside model price bounds")

    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        price_mid = price_for(mid)
        if abs(price_mid - target_price) <= tol:
            return float(mid)
        if price_mid < target_price:
            low = mid
        else:
            high = mid

    return float(0.5 * (low + high))


# ---------------------------------------------------------------------------
# OO wrapper for compatibility with the implementations registry
# ---------------------------------------------------------------------------


class GarmanKohlhagen:
    """Thin OO wrapper exposing ``price``, ``greeks`` and implied vols methods.

    This keeps the class-based API in ``risk_engine.models.implementations``
    functional while allowing the functional helpers to be used directly.
    """

    def price(
        self,
        option: FXEuropeanOption,
        *,
        spot: float,
        dom_curve: DiscountCurve,
        for_curve: DiscountCurve,
        vol_surface: VolSurface,
    ) -> float:
        return gk_price(option, spot, dom_curve, for_curve, vol_surface)

    def greeks(
        self,
        option: FXEuropeanOption,
        *,
        spot: float,
        dom_curve: DiscountCurve,
        for_curve: DiscountCurve,
        vol_surface: VolSurface,
    ) -> Dict[str, float]:
        return gk_greeks(option, spot, dom_curve, for_curve, vol_surface)

    def implied_vol(
        self,
        option: FXEuropeanOption,
        *,
        spot: float,
        target_price: float,
        dom_curve: DiscountCurve,
        for_curve: DiscountCurve,
        tol: float = 1e-7,
        max_iter: int = 200,
        vol_lower: float = 1e-6,
        vol_upper: float = 3.0,
    ) -> float:
        return gk_implied_vol(
            option,
            spot,
            target_price,
            dom_curve,
            for_curve,
            tol=tol,
            max_iter=max_iter,
            vol_lower=vol_lower,
            vol_upper=vol_upper,
        )

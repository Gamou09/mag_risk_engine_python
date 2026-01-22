"""Black-Scholes pricing model for European options."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

from .base import PricingModel


@dataclass(frozen=True)
class EuropeanOption:
    """Simple European option instrument."""

    spot: float
    strike: float
    maturity: float
    rate: float
    vol: float
    option_type: str = "call"


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _validate_option(option: EuropeanOption) -> str:
    if option.maturity < 0.0:
        raise ValueError("maturity must be >= 0")
    if option.vol < 0.0:
        raise ValueError("vol must be >= 0")
    if option.spot <= 0.0:
        raise ValueError("spot must be > 0")
    if option.strike <= 0.0:
        raise ValueError("strike must be > 0")
    option_type = option.option_type.lower()
    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'")
    return option_type


class BlackScholesModel(PricingModel):
    """Black-Scholes model for European options."""

    def price(self, instrument: Any, **kwargs: Any) -> float:
        if not isinstance(instrument, EuropeanOption):
            raise TypeError("instrument must be a EuropeanOption")
        option_type = _validate_option(instrument)

        s = instrument.spot
        k = instrument.strike
        t = instrument.maturity
        r = instrument.rate
        vol = instrument.vol

        if t == 0.0:
            intrinsic = max(s - k, 0.0) if option_type == "call" else max(k - s, 0.0)
            return float(intrinsic)

        df = math.exp(-r * t)
        if vol == 0.0:
            forward = s / df
            intrinsic = (
                max(forward - k, 0.0) if option_type == "call" else max(k - forward, 0.0)
            )
            return float(df * intrinsic)

        sqrt_t = math.sqrt(t)
        d1 = (math.log(s / k) + (r + 0.5 * vol * vol) * t) / (vol * sqrt_t)
        d2 = d1 - vol * sqrt_t

        if option_type == "call":
            price = s * _norm_cdf(d1) - k * df * _norm_cdf(d2)
        else:
            price = k * df * _norm_cdf(-d2) - s * _norm_cdf(-d1)
        return float(price)

    def greeks(self, instrument: Any, **kwargs: Any) -> Mapping[str, float] | None:
        if not isinstance(instrument, EuropeanOption):
            raise TypeError("instrument must be a EuropeanOption")
        option_type = _validate_option(instrument)

        s = instrument.spot
        k = instrument.strike
        t = instrument.maturity
        r = instrument.rate
        vol = instrument.vol

        if t == 0.0 or vol == 0.0:
            forward = s * math.exp(r * t) if t > 0.0 else s
            if option_type == "call":
                delta = 1.0 if forward > k else 0.0
            else:
                delta = -1.0 if forward < k else 0.0
            return {
                "delta": float(delta),
                "gamma": 0.0,
                "vega": 0.0,
                "theta": 0.0,
                "rho": 0.0,
            }

        sqrt_t = math.sqrt(t)
        d1 = (math.log(s / k) + (r + 0.5 * vol * vol) * t) / (vol * sqrt_t)
        d2 = d1 - vol * sqrt_t
        pdf_d1 = _norm_pdf(d1)
        df = math.exp(-r * t)

        if option_type == "call":
            delta = _norm_cdf(d1)
            theta = (
                -s * pdf_d1 * vol / (2.0 * sqrt_t) - r * k * df * _norm_cdf(d2)
            )
            rho = k * t * df * _norm_cdf(d2)
        else:
            delta = _norm_cdf(d1) - 1.0
            theta = (
                -s * pdf_d1 * vol / (2.0 * sqrt_t) + r * k * df * _norm_cdf(-d2)
            )
            rho = -k * t * df * _norm_cdf(-d2)

        gamma = pdf_d1 / (s * vol * sqrt_t)
        vega = s * pdf_d1 * sqrt_t

        return {
            "delta": float(delta),
            "gamma": float(gamma),
            "vega": float(vega),
            "theta": float(theta),
            "rho": float(rho),
        }

    def implied_vol(
        self,
        instrument: Any,
        target_price: float,
        *,
        tol: float = 1e-6,
        max_iter: int = 200,
        vol_lower: float = 1e-6,
        vol_upper: float = 5.0,
    ) -> float:
        """Solve for implied volatility using bisection."""
        if not isinstance(instrument, EuropeanOption):
            raise TypeError("instrument must be a EuropeanOption")
        if target_price < 0.0:
            raise ValueError("target_price must be >= 0")
        if tol <= 0.0:
            raise ValueError("tol must be > 0")
        if max_iter <= 0:
            raise ValueError("max_iter must be > 0")
        if vol_lower <= 0.0 or vol_upper <= 0.0 or vol_lower >= vol_upper:
            raise ValueError("invalid volatility bounds")

        _validate_option(instrument)

        def price_for(vol: float) -> float:
            return self.price(
                EuropeanOption(
                    spot=instrument.spot,
                    strike=instrument.strike,
                    maturity=instrument.maturity,
                    rate=instrument.rate,
                    vol=vol,
                    option_type=instrument.option_type,
                )
            )

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

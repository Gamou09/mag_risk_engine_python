from __future__ import annotations

from dataclasses import dataclass

from risk_engine.pricing.pricer import Pricer
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.result import PricingResult
from risk_engine.common.types import Money, Currency
from risk_engine.instruments.assets.instruments_fx import PricingFXSwap


def _split_pair(pair: str) -> tuple[str, str]:
    """Return (base, quote) from a 6-char pair like 'EURUSD' or 'EUR/USD'."""
    clean = pair.replace("/", "")
    if len(clean) != 6:
        raise ValueError(f"pair '{pair}' must be 6 letters like 'EURUSD'")
    return clean[:3], clean[3:]


def _forward_from_market(
    pair: str, tenor: str, ctx: PricingContext, warnings: list[str]
) -> tuple[float, str, tuple[str, ...]]:
    """
    Fetch market forward for a pair/tenor, with spot+points fallback.

    Returns (forward_value, source_label, factor_keys_used)
    """
    fwd_key = f"FWD.{pair}.{tenor}"
    spot_key = f"SPOT.{pair}"
    pts_key = f"FWDPTS.{pair}.{tenor}"

    try:
        fwd = ctx.market.get(fwd_key)
        source = "fwd"
        keys = (fwd_key,)
        # Parity check if spot+points also available in the state
        spot = ctx.market.factors.get(spot_key)
        pts = ctx.market.factors.get(pts_key)
        if spot is not None and pts is not None:
            implied = float(spot + pts)
            if abs(implied - fwd) > 1e-6:
                warnings.append(
                    f"Parity mismatch for {pair} {tenor}: "
                    f"FWD={fwd:.6f} vs SPOT+FWDPTS={implied:.6f}"
                )
    except KeyError:
        # Derive forward using spot + forward points (basis)
        spot = ctx.market.get(spot_key)
        pts = ctx.market.get(pts_key)
        fwd = spot + pts
        source = "spot+pts"
        keys = (spot_key, pts_key)

    return float(fwd), source, keys


@dataclass(frozen=True)
class FXSwapPricer(Pricer):
    """Mark-to-market PV of an FX swap versus current forwards."""

    def price(self, instrument: PricingFXSwap, ctx: PricingContext) -> PricingResult:
        base_ccy, quote_ccy = _split_pair(instrument.pair)

        # Discount factors in quote currency
        discount_curve = ctx.market.discount_curve_for(quote_ccy)
        df_near_key = discount_curve.df_key(instrument.near_maturity)
        df_far_key = discount_curve.df_key(instrument.far_maturity)

        df_near = ctx.market.get(df_near_key)
        df_far = ctx.market.get(df_far_key)

        warnings: list[str] = []

        # Current market forwards (prefer outright, fall back to spot+points)
        fwd_near_mkt, near_src, near_keys = _forward_from_market(
            instrument.pair, instrument.near_maturity, ctx, warnings
        )
        fwd_far_mkt, far_src, far_keys = _forward_from_market(
            instrument.pair, instrument.far_maturity, ctx, warnings
        )

        sign = 1.0 if instrument.direction == "buy_base" else -1.0
        notional = instrument.notional

        # PV is difference between contract forward and market forward on each leg
        pv_near = -(instrument.near_forward - fwd_near_mkt) * notional * df_near
        pv_far = (fwd_far_mkt - instrument.far_forward) * notional * df_far
        pv_quote = sign * (pv_near + pv_far)

        greeks: dict[str, float] = {}

        def _add(key: str, value: float) -> None:
            greeks[key] = greeks.get(key, 0.0) + value

        # dPV / dFWD for each source (if spot+points, both share same sensitivity)
        sens_near_fwd = sign * (notional * df_near)
        for k in near_keys:
            _add(k, sens_near_fwd)

        sens_far_fwd = sign * (notional * df_far)
        for k in far_keys:
            _add(k, sens_far_fwd)

        # dPV / dDF = sign * notional * (mkt - contract) for each leg
        _add(df_near_key, sign * (-(instrument.near_forward - fwd_near_mkt) * notional))
        _add(df_far_key, sign * ((fwd_far_mkt - instrument.far_forward) * notional))

        return PricingResult(
            pv=Money(pv_quote, Currency(quote_ccy)),
            greeks=greeks,
            explain=(
                f"FX swap {instrument.direction} {base_ccy} vs {quote_ccy}:"
                f" contract near {instrument.near_forward}, far {instrument.far_forward};"
                f" market near {fwd_near_mkt} ({near_src}), far {fwd_far_mkt} ({far_src})"
            ),
            warnings=tuple(warnings),
        )


__all__ = ["FXSwapPricer"]

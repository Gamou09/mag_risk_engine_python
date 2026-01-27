# risk_engine/pricing/pricers/rates/irs_pricer.py
from __future__ import annotations
from dataclasses import dataclass
from risk_engine.pricing.pricer import Pricer
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.result import PricingResult
from risk_engine.common.types import Money, Currency
from risk_engine.instruments.assets.instruments_rates import PricingInterestRateSwap as InterestRateSwap

@dataclass(frozen=True)
class InterestRateSwapPricer(Pricer):
    def price(self, instrument: InterestRateSwap, ctx: PricingContext) -> PricingResult:
        if len(instrument.pay_times) != len(instrument.accrual_factors):
            raise ValueError("pay_times and accrual_factors must have same length")

        sign = +1.0 if instrument.direction == "receive_fixed" else -1.0
        discount_curve = ctx.market.discount_curve_for(instrument.ccy)

        pv_fixed = 0.0
        pv_float = 0.0
        greeks: dict[str, float] = {}

        for t, accr in zip(instrument.pay_times, instrument.accrual_factors):
            df_key = discount_curve.df_key(t)
            df = ctx.market.get(df_key)

            # Fixed cashflow discounted
            fixed_cf = instrument.notional * instrument.fixed_rate * accr
            pv_fixed_i = fixed_cf * df
            pv_fixed += pv_fixed_i
            greeks[df_key] = greeks.get(df_key, 0.0) + (-sign) * fixed_cf  # PV = sign*(float-fixed)

            # Float cashflow discounted (simple forward * accr)
            fwd_key = instrument.float_curve.fwd_key(t)
            fwd = ctx.market.get(fwd_key)

            float_cf = instrument.notional * fwd * accr
            pv_float_i = float_cf * df
            pv_float += pv_float_i

            # Sensitivities:
            # dPV/dDF contributes float_cf for float leg, fixed_cf for fixed leg
            greeks[df_key] = greeks.get(df_key, 0.0) + sign * float_cf
            # dPV/dFWD = sign * notional * accr * DF
            greeks[fwd_key] = greeks.get(fwd_key, 0.0) + sign * (instrument.notional * accr * df)

        pv = sign * (pv_float - pv_fixed)

        return PricingResult(
            pv=Money(pv, Currency(instrument.ccy)),
            greeks=greeks,
            explain=(
                f"IRS discounted on {discount_curve.name}, float curve {instrument.float_curve.name}",
            ),
        )

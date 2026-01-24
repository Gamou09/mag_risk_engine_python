# risk_engine/pricing/pricers/rates/fixed_leg_pricer.py
from __future__ import annotations
from dataclasses import dataclass
from risk_engine.pricing.pricer import Pricer
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.result import PricingResult
from risk_engine.common.types import Money, Currency
from risk_engine.instruments.assets.instruments_rates import FixedLeg

@dataclass(frozen=True)
class FixedLegPricer(Pricer):
    def price(self, instrument: FixedLeg, ctx: PricingContext) -> PricingResult:
        if len(instrument.pay_times) != len(instrument.accrual_factors):
            raise ValueError("pay_times and accrual_factors must have same length")

        pv = 0.0
        greeks = {}
        discount_curve = ctx.market.discount_curve_for(instrument.ccy)

        for t, accr in zip(instrument.pay_times, instrument.accrual_factors):
            key = discount_curve.df_key(t)
            df = ctx.market.get(key)

            cf = instrument.notional * instrument.fixed_rate * accr
            pv_i = cf * df
            pv += pv_i

            # dPV/dDF = cashflow
            greeks[key] = greeks.get(key, 0.0) + cf

        if instrument.exchange_notional_at_maturity and instrument.pay_times:
            tN = instrument.pay_times[-1]
            keyN = discount_curve.df_key(tN)
            dfN = ctx.market.get(keyN)
            pv += instrument.notional * dfN
            greeks[keyN] = greeks.get(keyN, 0.0) + instrument.notional

        return PricingResult(
            pv=Money(pv, Currency(instrument.ccy)),
            greeks=greeks,
            explain=(f"FixedLeg discounted on {discount_curve.name}",),
        )

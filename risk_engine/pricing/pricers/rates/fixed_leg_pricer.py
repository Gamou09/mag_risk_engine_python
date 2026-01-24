# risk_engine/pricing/pricers/rates/fixed_leg_pricer.py
from __future__ import annotations
from dataclasses import dataclass
from risk_engine.pricing.pricer import Pricer
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.result import PricingResult
from risk_engine.common.types import Money, Currency
from risk_engine.instruments.asset.rates.fixed_leg import FixedLeg

@dataclass(frozen=True)
class FixedLegPricer(Pricer):
    discount_curve_id: str = "USD.OIS"  # used only to build factor keys

    def price(self, instrument: FixedLeg, ctx: PricingContext) -> PricingResult:
        if len(instrument.pay_times) != len(instrument.accrual_factors):
            raise ValueError("pay_times and accrual_factors must have same length")

        pv = 0.0
        greeks = {}

        for t, accr in zip(instrument.pay_times, instrument.accrual_factors):
            key = f"DF.{instrument.ccy}.{self.discount_curve_id}.{t}"
            df = ctx.market.get(key)

            cf = instrument.notional * instrument.fixed_rate * accr
            pv_i = cf * df
            pv += pv_i

            # dPV/dDF = cashflow
            greeks[key] = greeks.get(key, 0.0) + cf

        if instrument.exchange_notional_at_maturity and instrument.pay_times:
            tN = instrument.pay_times[-1]
            keyN = f"DF.{instrument.ccy}.{self.discount_curve_id}.{tN}"
            dfN = ctx.market.get(keyN)
            pv += instrument.notional * dfN
            greeks[keyN] = greeks.get(keyN, 0.0) + instrument.notional

        return PricingResult(
            pv=Money(pv, Currency(instrument.ccy)),
            greeks=greeks,
            explain=(f"FixedLeg discounted on {self.discount_curve_id}",),
        )

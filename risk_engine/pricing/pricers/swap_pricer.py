from __future__ import annotations

from risk_engine.market.market import Market
from risk_engine.pricing.instruments import Swap


class SwapPricer:
    """Par swap pricer using discount and forward curves."""

    def pv(self, swap: Swap, market: Market) -> float:
        cs = market.curves(swap.currency)
        disc = cs.discount
        fwd_curve = cs.forward(swap.float_leg.index)

        if len(swap.pay_times) != len(swap.accruals):
            raise ValueError("pay_times and accruals must have the same length")

        pv_fixed = 0.0
        pv_float = 0.0
        t_prev = 0.0

        for pay_time, accrual in zip(swap.pay_times, swap.accruals):
            df = disc.df(pay_time)
            pv_fixed += swap.notional * swap.fixed_rate * accrual * df
            fwd_rate = fwd_curve.fwd(t_prev, t_prev + accrual)
            pv_float += swap.notional * fwd_rate * accrual * df
            t_prev += accrual

        return pv_float - pv_fixed


__all__ = ["SwapPricer"]

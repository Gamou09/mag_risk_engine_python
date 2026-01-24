# risk_engine/instruments/asset/rates/fixed_leg.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from risk_engine.instruments.base import Instrument

@dataclass(frozen=True)
class FixedLeg(Instrument):
    """
    Minimal fixed leg: PV = sum( notional * fixed_rate * accrual_i * DF(t_i) ) + optional notional exchange.
    """
    product_type: str = "rates.fixed_leg"
    ccy: str = "USD"
    notional: float = 1_000_000.0
    fixed_rate: float = 0.03
    pay_times: Sequence[str] = ()        # e.g. ("1Y","2Y","3Y")
    accrual_factors: Sequence[float] = () # same length as pay_times
    exchange_notional_at_maturity: bool = False

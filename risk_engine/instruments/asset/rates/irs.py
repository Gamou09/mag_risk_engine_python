# risk_engine/instruments/asset/rates/irs.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, Literal
from risk_engine.instruments.base import Instrument
from risk_engine.market.ids import CurveId

PayReceive = Literal["pay_fixed", "receive_fixed"]

@dataclass(frozen=True)
class InterestRateSwap(Instrument):
    """
    Minimal IRS:
      PV = sign * (PV_float - PV_fixed)
    where sign = +1 for receive_fixed, -1 for pay_fixed.
    """
    product_type: str = "rates.irs"
    direction: PayReceive = "pay_fixed"

    ccy: str = "USD"
    notional: float = 1_000_000.0
    fixed_rate: float = 0.03
    float_curve: CurveId = field(default_factory=lambda: CurveId("OIS_USD_3M"))

    pay_times: Sequence[str] = ()         # e.g. ("6M","1Y","18M","2Y")
    accrual_factors: Sequence[float] = () # same length

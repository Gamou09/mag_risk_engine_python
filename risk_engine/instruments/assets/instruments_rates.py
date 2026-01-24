"""Rates instruments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Sequence, TYPE_CHECKING

from risk_engine.instruments.assets.instrument_base import Instrument as AssetInstrument
from risk_engine.instruments.assets.risk_factors import (
    RISK_DISCOUNT_CURVE,
    RISK_FLOAT_INDEX,
    RISK_OVERNIGHT_INDEX,
    RISK_RATE_VOL,
    RISK_YIELD_CURVE,
)

if TYPE_CHECKING:
    from risk_engine.market.ids import CurveId


def _default_curve_id() -> "CurveId":
    from risk_engine.market.ids import CurveId

    return CurveId("OIS_USD_3M")


# Linear / Cashflow Instruments
@dataclass(frozen=True)
class InterestRateSwap(AssetInstrument):
    """Fixed-for-floating swap with notional, index, and schedule."""

    ASSET_CLASS = "Rates"
    notional: float
    fixed_rate: float
    float_index: str
    maturity: float
    pay_fixed: bool = True
    currency: str = "USD"
    payments_per_year: int = 2

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_FLOAT_INDEX)


@dataclass(frozen=True)
class OISSwap(AssetInstrument):
    """Swap exchanging fixed rate versus compounded overnight index."""

    ASSET_CLASS = "Rates"
    notional: float
    fixed_rate: float
    overnight_index: str
    maturity: float
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_OVERNIGHT_INDEX)


@dataclass(frozen=True)
class FRA(AssetInstrument):
    """Forward rate agreement locking a rate between start and end dates."""

    ASSET_CLASS = "Rates"
    notional: float
    fixed_rate: float
    start: float
    end: float
    index: str
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_FLOAT_INDEX)


# Structured Fixed Income
@dataclass(frozen=True)
class ZeroCouponBond(AssetInstrument):
    """Bond paying face value at maturity with no interim coupons."""

    ASSET_CLASS = "Rates"
    face: float
    maturity: float

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE)


@dataclass(frozen=True)
class FixedRateBond(AssetInstrument):
    """Bond with fixed coupon rate and regular payment frequency."""

    ASSET_CLASS = "Rates"
    face: float
    coupon_rate: float
    maturity: float
    payments_per_year: int = 2

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE)


# Optionality on Rates
@dataclass(frozen=True)
class Swaption(AssetInstrument):
    """Option to enter a swap at a strike on expiry."""

    ASSET_CLASS = "Rates"
    notional: float
    strike: float
    maturity: float
    swap_tenor: float
    option_type: str = "payer"
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_RATE_VOL)


@dataclass(frozen=True)
class Cap(AssetInstrument):
    """Cap on a floating rate with periodic reset payments."""

    ASSET_CLASS = "Rates"
    notional: float
    strike: float
    maturity: float
    index: str
    currency: str = "USD"
    payments_per_year: int = 4

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_RATE_VOL)


@dataclass(frozen=True)
class Floor(AssetInstrument):
    """Floor on a floating rate with periodic reset payments."""

    ASSET_CLASS = "Rates"
    notional: float
    strike: float
    maturity: float
    index: str
    currency: str = "USD"
    payments_per_year: int = 4

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_RATE_VOL)


# Structured Fixed Income
@dataclass(frozen=True)
class BondOption(AssetInstrument):
    """Option on a bond or bond future with strike and expiry."""

    ASSET_CLASS = "Rates"
    notional: float
    strike: float
    maturity: float
    option_type: str = "call"
    currency: str = "USD"

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_RATE_VOL)


# Pricing-layer instruments (product_type based)
@dataclass(frozen=True)
class FixedLeg(AssetInstrument):
    """
    Minimal fixed leg: PV = sum( notional * fixed_rate * accrual_i * DF(t_i) ) + optional notional exchange.
    """

    ASSET_CLASS = "Rates"
    product_type: str = "rates.fixed_leg"
    ccy: str = "USD"
    notional: float = 1_000_000.0
    fixed_rate: float = 0.03
    pay_times: Sequence[str] = ()  # e.g. ("1Y","2Y","3Y")
    accrual_factors: Sequence[float] = ()  # same length as pay_times
    exchange_notional_at_maturity: bool = False

    def risk_factors(self) -> tuple[str, ...]:
        return (RISK_DISCOUNT_CURVE,)


PayReceive = Literal["pay_fixed", "receive_fixed"]


def _pricing_interest_rate_swap_cls() -> type[AssetInstrument]:
    @dataclass(frozen=True)
    class InterestRateSwap(AssetInstrument):
        """
        Minimal IRS:
          PV = sign * (PV_float - PV_fixed)
        where sign = +1 for receive_fixed, -1 for pay_fixed.
        """

        ASSET_CLASS = "Rates"
        product_type: str = "rates.irs"
        direction: PayReceive = "pay_fixed"

        ccy: str = "USD"
        notional: float = 1_000_000.0
        fixed_rate: float = 0.03
        float_curve: "CurveId" = field(default_factory=_default_curve_id)

        pay_times: Sequence[str] = ()  # e.g. ("6M","1Y","18M","2Y")
        accrual_factors: Sequence[float] = ()  # same length

        def risk_factors(self) -> tuple[str, ...]:
            return (RISK_YIELD_CURVE, RISK_DISCOUNT_CURVE, RISK_FLOAT_INDEX)

    return InterestRateSwap


PricingInterestRateSwap = _pricing_interest_rate_swap_cls()
del _pricing_interest_rate_swap_cls


__all__ = [
    "InterestRateSwap",
    "OISSwap",
    "FRA",
    "ZeroCouponBond",
    "FixedRateBond",
    "Swaption",
    "Cap",
    "Floor",
    "BondOption",
]

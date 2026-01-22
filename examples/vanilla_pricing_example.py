"""Example usage of vanilla pricing instruments and discounting."""

from risk_engine.core.instruments import (
    EquityForward,
    EquitySpot,
    FixedRateBond,
    ZeroCouponBond,
)
from risk_engine.models.pricing import DiscountingModel


def main() -> None:
    model = DiscountingModel(rate=0.03)

    spot = EquitySpot(spot=125.0, symbol="ABC")
    forward = EquityForward(
        spot=125.0,
        strike=127.0,
        maturity=1.0,
        rate=0.03,
        dividend_yield=0.01,
        symbol="ABC",
    )
    bond = FixedRateBond(face=1000.0, coupon_rate=0.05, maturity=5.0, payments_per_year=2)
    zero = ZeroCouponBond(face=1000.0, maturity=3.0)

    print(f"equity_spot={model.price(spot):.4f}")
    print(f"equity_forward={model.price(forward):.4f}")
    print(f"fixed_rate_bond={model.price(bond):.4f}")
    print(f"zero_coupon_bond={model.price(zero):.4f}")


if __name__ == "__main__":
    main()

from risk_engine.instruments.assets.instruments_rates import FixedRateBond
from risk_engine.models.pricing.vanilla import DiscountingModel


def main() -> None:
    bond = FixedRateBond(
        face=1_000_000,
        coupon_rate=0.03,
        maturity=3.0,
        payments_per_year=2,
    )

    model = DiscountingModel(rate=0.02)
    price = model.price(bond)
    print(f"FixedRateBond price: {price:,.2f}")


if __name__ == "__main__":
    main()

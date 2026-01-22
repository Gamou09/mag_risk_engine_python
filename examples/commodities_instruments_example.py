"""Placeholder commodities instruments."""

from risk_engine.core.instrument_sets.instruments_commodities import (
    CommodityForward,
    CommodityFuture,
    CommodityOption,
    CommoditySpot,
    CommoditySwap,
)


def main() -> None:
    instruments = [
        CommoditySpot(commodity="WTI", spot=78.5),
        CommodityForward(commodity="WTI", spot=78.5, forward_price=80.0, maturity=0.5),
        CommodityFuture(commodity="WTI", price=81.0, maturity=1.0, exchange="NYMEX"),
        CommoditySwap(commodity="WTI", notional=1_000_000, fixed_price=79.0, maturity=1.5),
        CommodityOption(
            commodity="WTI",
            spot=78.5,
            strike=85.0,
            maturity=0.75,
            vol=0.35,
            option_type="call",
        ),
    ]

    for instrument in instruments:
        print(instrument)


if __name__ == "__main__":
    main()

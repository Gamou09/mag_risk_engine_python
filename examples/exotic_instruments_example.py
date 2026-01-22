"""Placeholder multi-asset and exotic instruments."""

from risk_engine.core.instrument_sets.instruments_exotic import (
    BasketOption,
    ForwardStartOption,
    QuantoOption,
    RainbowOption,
)


def main() -> None:
    instruments = [
        BasketOption(
            underlyings=["AAPL", "MSFT", "NVDA"],
            weights=[0.4, 0.35, 0.25],
            strike=100.0,
            maturity=1.0,
            rate=0.02,
            vol=0.25,
            option_type="call",
        ),
        QuantoOption(
            spot=100.0,
            strike=105.0,
            maturity=1.0,
            rate=0.02,
            vol=0.2,
            fx_rate=1.1,
            fx_vol=0.1,
            option_type="call",
            symbol="AAPL",
        ),
        RainbowOption(
            spots=[100.0, 95.0],
            strike=100.0,
            maturity=1.0,
            rate=0.02,
            vol=0.3,
            payoff="best_of",
            option_type="call",
        ),
        ForwardStartOption(
            spot=100.0,
            start=0.5,
            maturity=1.5,
            rate=0.02,
            vol=0.25,
            strike_pct=1.0,
            option_type="call",
            symbol="AAPL",
        ),
    ]

    for instrument in instruments:
        print(instrument)


if __name__ == "__main__":
    main()

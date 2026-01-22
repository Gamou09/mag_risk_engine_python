"""Placeholder FX instruments."""

from risk_engine.core.instrument_sets.instruments_fx import (
    FXDigitalOption,
    FXForward,
    FXOption,
    FXSpot,
    FXSwap,
)


def main() -> None:
    instruments = [
        FXSpot(pair="EURUSD", spot=1.085),
        FXForward(pair="EURUSD", spot=1.085, forward_rate=1.095, maturity=0.5),
        FXSwap(
            pair="EURUSD",
            near_maturity=0.25,
            far_maturity=1.0,
            near_forward=1.088,
            far_forward=1.102,
        ),
        FXOption(
            pair="EURUSD",
            spot=1.085,
            strike=1.10,
            maturity=0.5,
            vol=0.12,
            option_type="call",
        ),
        FXDigitalOption(
            pair="EURUSD",
            spot=1.085,
            strike=1.12,
            maturity=0.5,
            payout=10_000,
            option_type="call",
        ),
    ]

    for instrument in instruments:
        print(instrument)


if __name__ == "__main__":
    main()

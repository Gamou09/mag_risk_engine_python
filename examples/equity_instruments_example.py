"""Placeholder equity instruments."""

from risk_engine.core.instruments import EquityForward, EuropeanOption
from risk_engine.core.instrument_sets.instruments_equity import (
    EquityBarrierOption,
    EquityDigitalOption,
    EquityIndexFuture,
    VarianceSwap,
)


def main() -> None:
    instruments = [
        EquityForward(
            spot=100.0,
            strike=102.0,
            maturity=1.0,
            rate=0.02,
            dividend_yield=0.01,
            symbol="SPX",
        ),
        EquityIndexFuture(
            spot=4500.0,
            maturity=0.75,
            rate=0.02,
            dividend_yield=0.015,
            symbol="SPX",
        ),
        EuropeanOption(
            spot=100.0,
            strike=105.0,
            maturity=1.0,
            rate=0.02,
            vol=0.25,
            option_type="call",
            symbol="AAPL",
        ),
        EquityDigitalOption(
            spot=100.0,
            strike=110.0,
            maturity=0.5,
            rate=0.02,
            vol=0.3,
            payout=10.0,
            option_type="call",
            symbol="AAPL",
        ),
        EquityBarrierOption(
            spot=100.0,
            strike=95.0,
            barrier=120.0,
            barrier_type="up_and_out",
            maturity=1.0,
            rate=0.02,
            vol=0.25,
            option_type="put",
            symbol="AAPL",
        ),
        VarianceSwap(
            notional=1_000_000,
            variance_strike=0.04,
            maturity=1.0,
            symbol="SPX",
        ),
    ]

    for instrument in instruments:
        print(instrument)


if __name__ == "__main__":
    main()

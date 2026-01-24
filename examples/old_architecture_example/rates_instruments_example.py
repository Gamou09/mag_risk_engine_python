"""Placeholder interest rate instruments."""

from risk_engine.core.instrument_sets.instruments_rates import (
    BondOption,
    Cap,
    Floor,
    FRA,
    InterestRateSwap,
    OISSwap,
    Swaption,
)


def main() -> None:
    instruments = [
        InterestRateSwap(
            notional=1_000_000,
            fixed_rate=0.0325,
            float_index="SOFR",
            maturity=5.0,
            pay_fixed=True,
            currency="USD",
            payments_per_year=2,
        ),
        OISSwap(
            notional=2_000_000,
            fixed_rate=0.031,
            overnight_index="SOFR",
            maturity=2.0,
            currency="USD",
        ),
        FRA(
            notional=5_000_000,
            fixed_rate=0.033,
            start=0.5,
            end=1.0,
            index="SOFR",
            currency="USD",
        ),
        Swaption(
            notional=1_000_000,
            strike=0.035,
            maturity=1.0,
            swap_tenor=5.0,
            option_type="payer",
            currency="USD",
        ),
        Cap(
            notional=1_000_000,
            strike=0.04,
            maturity=3.0,
            index="SOFR",
            currency="USD",
            payments_per_year=4,
        ),
        Floor(
            notional=1_000_000,
            strike=0.02,
            maturity=3.0,
            index="SOFR",
            currency="USD",
            payments_per_year=4,
        ),
        BondOption(
            notional=1_000_000,
            strike=99.5,
            maturity=1.5,
            option_type="call",
            currency="USD",
        ),
    ]

    for instrument in instruments:
        print(instrument)


if __name__ == "__main__":
    main()

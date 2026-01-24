"""Placeholder credit instruments."""

from risk_engine.core.instrument_sets.instruments_credit import (
    CDSIndex,
    CreditDefaultSwap,
    CreditDefaultSwaption,
    TotalReturnSwap,
)


def main() -> None:
    instruments = [
        CreditDefaultSwap(
            notional=10_000_000,
            spread=0.012,
            maturity=5.0,
            reference="ACME_CORP",
            currency="USD",
        ),
        CDSIndex(
            notional=25_000_000,
            spread=0.009,
            maturity=5.0,
            index="CDX_IG",
            currency="USD",
        ),
        CreditDefaultSwaption(
            notional=5_000_000,
            strike=0.011,
            maturity=1.0,
            swap_tenor=5.0,
            reference="ACME_CORP",
            option_type="payer",
            currency="USD",
        ),
        TotalReturnSwap(
            notional=3_000_000,
            maturity=2.0,
            reference="ACME_CORP",
            funding_rate=0.03,
            currency="USD",
        ),
    ]

    for instrument in instruments:
        print(instrument)


if __name__ == "__main__":
    main()

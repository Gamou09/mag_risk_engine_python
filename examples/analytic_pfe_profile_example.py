"""Example analytic PFE profile for a simple forward/option portfolio."""

from risk_engine.core.engine import MarketData
from risk_engine.core.instruments import EquityForward
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.metrics.pfe import analytic_pfe_profile
from risk_engine.models.pricing import EuropeanOption


def main() -> None:
    portfolio = Portfolio(
        positions=[
            Position(
                instrument=EquityForward(
                    spot=100.0,
                    strike=102.0,
                    maturity=1.0,
                    rate=0.02,
                    dividend_yield=0.01,
                    symbol="ABC",
                ),
                quantity=5.0,
                direction="short",
                label="equity_forward",
            ),
            Position(
                instrument=EuropeanOption(
                    spot=100.0,
                    strike=105.0,
                    maturity=1.0,
                    rate=0.02,
                    vol=0.25,
                    option_type="call",
                ),
                quantity=2.0,
                label="equity_option",
            ),
        ]
    )

    market = MarketData(
        spots={"ABC": 100.0},
        rates={"risk_free": 0.02},
        vols={"ABC": 0.25},
        dividends={"ABC": 0.01},
    )

    result = analytic_pfe_profile(
        portfolio,
        market,
        horizons=[0.25, 0.5, 1.0, 1.5, 2., 2.5, 3],
        confidence=0.95,
    )

    for horizon in result.horizons:
        pfe = result.pfe_profile[horizon]
        ee = result.expected_exposure[horizon]
        print(f"horizon={horizon:.2f} pfe_95={pfe:.4f} ee={ee:.4f}")


if __name__ == "__main__":
    main()

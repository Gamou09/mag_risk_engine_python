"""Example scenario-based PFE profile across horizons."""

from risk_engine.core.engine import MarketData, PricingEngine, Scenario
from risk_engine.core.instruments import EquityForward
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.metrics.pfe import scenario_pfe_profile_from_revaluations


def main() -> None:
    portfolio = Portfolio(
        positions=[
            Position(
                instrument=EquityForward(
                    spot=100.0,
                    strike=102.0,
                    maturity=0.5,
                    rate=0.02,
                    dividend_yield=0.01,
                    symbol="ABC",
                ),
                quantity=10.0,
                label="equity_forward",
            ),
        ]
    )

    market = MarketData(
        spots={"ABC": 100.0},
        rates={"risk_free": 0.02},
        vols={"ABC": 0.25},
        dividends={"ABC": 0.01},
    )

    scenarios_1d = [
        Scenario(spot_shocks={"ABC": 5.0}),
        Scenario(spot_shocks={"ABC": -5.0}),
        Scenario(spot_shocks={"ABC": 10.0}),
        Scenario(spot_shocks={"ABC": -10.0}),
    ]
    scenarios_5d = [
        Scenario(spot_shocks={"ABC": 8.0}),
        Scenario(spot_shocks={"ABC": -8.0}),
        Scenario(spot_shocks={"ABC": 15.0}),
        Scenario(spot_shocks={"ABC": -15.0}),
    ]

    scenarios_10d = [
        Scenario(spot_shocks={"ABC": 10.0}),
        Scenario(spot_shocks={"ABC": -10.0}),
        Scenario(spot_shocks={"ABC": 15.0}),
        Scenario(spot_shocks={"ABC": -15.0}),
    ]

    engine = PricingEngine()
    reval_1 = engine.revalue_scenarios(portfolio, market, scenarios_1d)
    reval_5 = engine.revalue_scenarios(portfolio, market, scenarios_5d)
    reval_10 = engine.revalue_scenarios(portfolio, market, scenarios_10d)

    profile = scenario_pfe_profile_from_revaluations(
        {1: reval_1, 5: reval_5, 10: reval_10}, confidence=0.95
    )

    for horizon in sorted(profile):
        print(f"horizon={horizon} pfe_95={profile[horizon].pfe:.4f}")


if __name__ == "__main__":
    main()

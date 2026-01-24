"""Example scenario-based PFE with a single position."""

from risk_engine.core.engine import MarketData, PricingEngine, Scenario
from risk_engine.core.instruments import EquityForward
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.metrics.pfe import scenario_pfe_from_revaluation


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

    scenarios = [
        Scenario(spot_shocks={"ABC": 5.0}),
        Scenario(spot_shocks={"ABC": -5.0}),
        Scenario(spot_shocks={"ABC": 10.0}),
        Scenario(spot_shocks={"ABC": -10.0}),
    ]

    engine = PricingEngine()
    revaluation = engine.revalue_scenarios(portfolio, market, scenarios)
    pfe_result = scenario_pfe_from_revaluation(revaluation, confidence=0.95, horizon=1)

    print(f"base_total={revaluation.base.total:.4f}")
    for idx, scenario_value in enumerate(revaluation.scenario_values):
        print(f"scenario_{idx}_total={scenario_value.total:.4f}")
    for idx, pnl in enumerate(revaluation.pnls):
        print(f"scenario_{idx}_pnl={pnl:.4f}")
    print(f"pfe_95={pfe_result.pfe:.4f}")


if __name__ == "__main__":
    main()

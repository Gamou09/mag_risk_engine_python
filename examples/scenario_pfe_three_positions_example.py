"""Example scenario-based PFE with three positions."""

from risk_engine.core.engine import MarketData, PricingEngine, Scenario
from risk_engine.core.instruments import EquityForward, FixedRateBond
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.metrics.pfe import scenario_pfe_from_revaluation
from risk_engine.models.pricing import EuropeanOption


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
            Position(
                instrument=FixedRateBond(
                    face=1000.0, coupon_rate=0.05, maturity=3.0, payments_per_year=2
                ),
                quantity=2.0,
                label="fixed_bond",
            ),
            Position(
                instrument=EuropeanOption(
                    spot=100.0,
                    strike=105.0,
                    maturity=1.0,
                    rate=0.02,
                    vol=0.25,
                    option_type="call",
                    symbol="ABC",
                ),
                quantity=3.0,
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

    scenarios = [
        Scenario(spot_shocks={"ABC": 5.0}),
        Scenario(spot_shocks={"ABC": -5.0}),
        Scenario(spot_shocks={"ABC": 10.0}),
        Scenario(spot_shocks={"ABC": -10.0}),
        Scenario(rate_shocks={"risk_free": 0.005}),
        Scenario(rate_shocks={"risk_free": -0.005}),
        Scenario(vol_shocks={"ABC": 0.05}),
        Scenario(vol_shocks={"ABC": -0.03}),
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

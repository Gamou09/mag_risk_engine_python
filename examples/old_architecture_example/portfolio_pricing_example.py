"""Example portfolio pricing and scenario revaluation."""

from risk_engine.core.engine import MarketData, PricingEngine, Scenario
from risk_engine.core.instruments import EquityForward, FixedRateBond
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.metrics.var import historical_var
from risk_engine.models.curves import FlatZeroCurve
from risk_engine.core.instruments import EuropeanOption


def main() -> None:
    portfolio = Portfolio(
        positions=[
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
                quantity=10.0,
                label="call_option",
            ),
            Position(
                instrument=EquityForward(
                    spot=100.0,
                    strike=102.0,
                    maturity=0.5,
                    rate=0.02,
                    dividend_yield=0.01,
                    symbol="ABC",
                ),
                quantity=5.0,
                label="equity_forward",
            ),
            Position(
                instrument=FixedRateBond(
                    face=1000.0, coupon_rate=0.05, maturity=3.0, payments_per_year=2
                ),
                quantity=2.0,
                label="fixed_bond",
            ),
        ]
    )

    curve = FlatZeroCurve(rate=0.02)
    market = MarketData(
        spots={"ABC": 100.0},
        rates={"risk_free": 0.02},
        vols={"ABC": 0.25},
        dividends={"ABC": 0.01},
        curves={"discount": curve},
    )

    scenarios = [
        Scenario(spot_shocks={"ABC": 5.0}),
        Scenario(rate_shocks={"risk_free": 0.005}),
        Scenario(vol_shocks={"ABC": 0.05}),
        Scenario(spot_shocks={"ABC": -5.0}, vol_shocks={"ABC": -0.03}),
    ]

    engine = PricingEngine()
    base_value = engine.price_portfolio(portfolio, market)
    reval = engine.revalue_scenarios(portfolio, market, scenarios)

    print(f"base_total={base_value.total:.4f}")
    for idx, scenario_value in enumerate(reval.scenario_values):
        print(f"scenario_{idx}_total={scenario_value.total:.4f}")
    for idx, pnl in enumerate(reval.pnls):
        print(f"scenario_{idx}_pnl={pnl:.4f}")

    var_result = historical_var(reval.pnls, confidence=0.95, horizon=1)
    print(f"portfolio_var={var_result.var:.4f}")


if __name__ == "__main__":
    main()

"""Example Monte Carlo PFE profile with simple path generators."""

from risk_engine.core.engine import MarketData
from risk_engine.core.instruments import EquityForward, FixedRateBond
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.metrics.pfe import monte_carlo_pfe_profile
from risk_engine.simulation.monte_carlo import HestonParams, VasicekParams


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
                label="equity_forward",
            ),
            Position(
                instrument=FixedRateBond(
                    face=1000.0, coupon_rate=0.04, maturity=3.0, payments_per_year=4
                ),
                quantity=1.0,
                label="fixed_bond",
            ),
        ]
    )

    market = MarketData(
        spots={"ABC": 100.0},
        rates={"risk_free": 0.02},
        vols={"ABC": 0.25},
        dividends={"ABC": 0.01},
    )

    result = monte_carlo_pfe_profile(
        portfolio,
        market,
        horizons=[0.25, 0.5, 1.0],
        dt=0.25,
        num_paths=5000,
        confidence=0.95,
        equity_models={
            "ABC": HestonParams(
                kappa=2.0,
                long_var=0.04,
                vol_of_vol=0.4,
                rho=-0.5,
                initial_var=0.04,
                drift=0.01,
            )
        },
        rate_model=VasicekParams(mean_reversion=0.3, long_rate=0.02, vol=0.01),
        seed=123,
    )

    for horizon in result.horizons:
        pfe = result.pfe_profile[horizon]
        ee = result.expected_exposure[horizon]
        print(f"horizon={horizon:.2f} pfe_95={pfe:.4f} ee={ee:.4f}")


if __name__ == "__main__":
    main()

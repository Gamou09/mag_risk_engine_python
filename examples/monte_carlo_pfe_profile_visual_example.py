"""Visualize Monte Carlo PFE profile."""

from risk_engine.core.engine import MarketData
from risk_engine.core.instruments import EquityForward, FixedRateBond
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.metrics.pfe import monte_carlo_pfe_profile
from risk_engine.models.pricing import EuropeanOption
from risk_engine.simulation.monte_carlo import GBMParams, HestonParams, VasicekParams


def main() -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise SystemExit(
            "matplotlib is required for this example; install it to render the chart"
        ) from exc

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
            Position(
                instrument=EquityForward(
                    spot=80.0,
                    strike=82.0,
                    maturity=1.0,
                    rate=0.02,
                    dividend_yield=0.0,
                    symbol="XYZ",
                ),
                quantity=8.0,
                label="equity_forward_xyz",
            ),
            Position(
                instrument=EuropeanOption(
                    spot=100.0,
                    strike=95.0,
                    maturity=1.0,
                    rate=0.02,
                    vol=0.25,
                    option_type="put",
                    symbol="ABC",
                ),
                quantity=2.0,
                label="equity_put",
            ),
        ]
    )

    market = MarketData(
        spots={"ABC": 100.0, "XYZ": 80.0},
        rates={"risk_free": 0.02},
        vols={"ABC": 0.25, "XYZ": 0.2},
        dividends={"ABC": 0.01, "XYZ": 0.0},
    )

    result = monte_carlo_pfe_profile(
        portfolio,
        market,
        horizons=[0.25, 0.5, 1.0, 2.0],
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
            ),
            "XYZ": GBMParams(drift=0.01, vol=0.2),
        },
        rate_model=VasicekParams(mean_reversion=0.3, long_rate=0.02, vol=0.01),
        seed=123,
    )

    horizons = list(result.horizons)
    pfe = [result.pfe_profile[h] for h in horizons]
    ee = [result.expected_exposure[h] for h in horizons]

    plt.figure(figsize=(8, 4.5))
    plt.plot(horizons, pfe, marker="o", label="PFE 95%")
    plt.plot(horizons, ee, marker="o", linestyle="--", label="Expected Exposure")
    plt.title("Monte Carlo PFE Profile")
    plt.xlabel("Horizon (years)")
    plt.ylabel("Exposure")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

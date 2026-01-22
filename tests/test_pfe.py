import numpy as np
import pytest

from risk_engine.metrics.pfe import (
    ScenarioPFEResult,
    MonteCarloPFEResult,
    monte_carlo_pfe_profile,
    analytic_pfe_profile,
    scenario_pfe,
    scenario_pfe_from_revaluation,
    scenario_pfe_profile,
    scenario_pfe_profile_from_revaluations,
)
from risk_engine.core.engine import ScenarioRevaluation, PortfolioValue
from risk_engine.core.engine import MarketData
from risk_engine.core.instruments import EquityForward
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.simulation.monte_carlo import GBMParams, HestonParams, VasicekParams
from risk_engine.models.pricing import EuropeanOption


def test_scenario_pfe_basic():
    pnls = np.array([10.0, -5.0, 3.0, -1.0])
    exposures = np.maximum(pnls, 0.0)
    expected = np.quantile(exposures, 0.95, method="linear")

    result = scenario_pfe(pnls, confidence=0.95, horizon=1)

    assert isinstance(result, ScenarioPFEResult)
    assert result.pfe == pytest.approx(expected)
    assert result.quantile == pytest.approx(expected)
    assert result.confidence == 0.95
    assert result.horizon == 1


def test_scenario_pfe_threshold():
    pnls = np.array([5.0, 1.0, 3.0])
    threshold = 2.0
    exposures = np.maximum(pnls - threshold, 0.0)
    expected = np.quantile(exposures, 0.9, method="linear")

    result = scenario_pfe(pnls, confidence=0.9, horizon=1, threshold=threshold)

    assert result.pfe == pytest.approx(expected)
    assert result.threshold == threshold


def test_scenario_pfe_netting_modes():
    pnls = np.array(
        [
            [5.0, -2.0],
            [-1.0, 4.0],
            [-3.0, -2.0],
        ]
    )

    netted = np.array([3.0, 3.0, -5.0])
    netted_exposure = np.maximum(netted, 0.0)
    netted_expected = np.quantile(netted_exposure, 0.95, method="linear")

    grossed = np.array([5.0, 4.0, 0.0])
    grossed_expected = np.quantile(grossed, 0.95, method="linear")

    netting_result = scenario_pfe(pnls, confidence=0.95, netting=True)
    gross_result = scenario_pfe(pnls, confidence=0.95, netting=False)

    assert netting_result.pfe == pytest.approx(netted_expected)
    assert gross_result.pfe == pytest.approx(grossed_expected)


def test_scenario_pfe_profile():
    pnls_by_horizon = {
        1: np.array([1.0, -1.0, 0.5]),
        5: np.array([2.0, -0.5, -1.0]),
    }

    results = scenario_pfe_profile(pnls_by_horizon, confidence=0.95)

    assert set(results.keys()) == {1, 5}
    assert all(isinstance(result, ScenarioPFEResult) for result in results.values())
    assert results[1].horizon == 1
    assert results[5].horizon == 5


def test_scenario_pfe_from_revaluation():
    base = PortfolioValue(total=100.0, positions=[])
    scenarios = [
        PortfolioValue(total=105.0, positions=[]),
        PortfolioValue(total=95.0, positions=[]),
        PortfolioValue(total=110.0, positions=[]),
    ]
    pnls = [5.0, -5.0, 10.0]
    revaluation = ScenarioRevaluation(base=base, scenario_values=scenarios, pnls=pnls)

    result = scenario_pfe_from_revaluation(revaluation, confidence=0.9, horizon=1)

    assert result.pfe >= 0.0
    assert result.num_scenarios == 3


def test_scenario_pfe_profile_from_revaluations():
    base = PortfolioValue(total=100.0, positions=[])
    reval_1 = ScenarioRevaluation(
        base=base,
        scenario_values=[
            PortfolioValue(total=101.0, positions=[]),
            PortfolioValue(total=98.0, positions=[]),
        ],
        pnls=[1.0, -2.0],
    )
    reval_5 = ScenarioRevaluation(
        base=base,
        scenario_values=[
            PortfolioValue(total=103.0, positions=[]),
            PortfolioValue(total=97.0, positions=[]),
        ],
        pnls=[3.0, -3.0],
    )

    results = scenario_pfe_profile_from_revaluations({1: reval_1, 5: reval_5})

    assert set(results.keys()) == {1, 5}
    assert results[1].horizon == 1
    assert results[5].horizon == 5


def test_monte_carlo_pfe_profile_zero_vol():
    portfolio = Portfolio(
        positions=[
            Position(
                instrument=EquityForward(
                    spot=100.0,
                    strike=100.0,
                    maturity=2.0,
                    rate=0.0,
                    dividend_yield=0.0,
                    symbol="ABC",
                ),
                quantity=1.0,
            )
        ]
    )
    market = MarketData(
        spots={"ABC": 100.0},
        rates={"risk_free": 0.0},
        vols={"ABC": 0.2},
        dividends={"ABC": 0.0},
    )

    result = monte_carlo_pfe_profile(
        portfolio,
        market,
        horizons=[1.0, 2.0],
        dt=1.0,
        num_paths=200,
        confidence=0.95,
        equity_models={"ABC": GBMParams(drift=0.0, vol=0.0)},
        seed=7,
    )

    assert isinstance(result, MonteCarloPFEResult)
    assert result.pfe_profile[1.0] == pytest.approx(0.0)
    assert result.pfe_profile[2.0] == pytest.approx(0.0)


def test_monte_carlo_pfe_invalid_horizon_alignment():
    portfolio = Portfolio(
        positions=[
            Position(
                instrument=EquityForward(
                    spot=100.0,
                    strike=100.0,
                    maturity=1.0,
                    rate=0.0,
                    dividend_yield=0.0,
                    symbol="ABC",
                ),
                quantity=1.0,
            )
        ]
    )
    market = MarketData(
        spots={"ABC": 100.0},
        rates={"risk_free": 0.0},
        vols={"ABC": 0.2},
        dividends={"ABC": 0.0},
    )

    with pytest.raises(ValueError, match="align"):
        monte_carlo_pfe_profile(
            portfolio,
            market,
            horizons=[0.5, 1.25],
            dt=1.0,
            num_paths=10,
            confidence=0.95,
            equity_models={"ABC": GBMParams(drift=0.0, vol=0.2)},
        )


def test_monte_carlo_pfe_missing_symbol():
    portfolio = Portfolio(
        positions=[
            Position(
                instrument=EquityForward(
                    spot=100.0,
                    strike=100.0,
                    maturity=1.0,
                    rate=0.0,
                    dividend_yield=0.0,
                    symbol="ABC",
                ),
                quantity=1.0,
            )
        ]
    )
    market = MarketData(
        spots={"XYZ": 100.0},
        rates={"risk_free": 0.0},
        vols={"XYZ": 0.2},
        dividends={"XYZ": 0.0},
    )

    with pytest.raises(ValueError, match="missing symbol"):
        monte_carlo_pfe_profile(
            portfolio,
            market,
            horizons=[1.0],
            dt=1.0,
            num_paths=10,
            confidence=0.95,
            equity_models={"ABC": GBMParams(drift=0.0, vol=0.2)},
        )


def test_monte_carlo_pfe_heston_vasicek():
    portfolio = Portfolio(
        positions=[
            Position(
                instrument=EquityForward(
                    spot=100.0,
                    strike=100.0,
                    maturity=1.0,
                    rate=0.01,
                    dividend_yield=0.0,
                    symbol="ABC",
                ),
                quantity=1.0,
            )
        ]
    )
    market = MarketData(
        spots={"ABC": 100.0},
        rates={"risk_free": 0.01},
        vols={"ABC": 0.2},
        dividends={"ABC": 0.0},
    )

    result = monte_carlo_pfe_profile(
        portfolio,
        market,
        horizons=[0.5, 1.0],
        dt=0.5,
        num_paths=200,
        confidence=0.9,
        equity_models={
            "ABC": HestonParams(
                kappa=1.5,
                long_var=0.04,
                vol_of_vol=0.3,
                rho=-0.2,
                initial_var=0.04,
                drift=0.01,
            )
        },
        rate_model=VasicekParams(mean_reversion=0.2, long_rate=0.01, vol=0.01),
        seed=11,
    )

    assert result.pfe_profile[0.5] >= 0.0


def test_analytic_pfe_profile_forward_only():
    portfolio = Portfolio(
        positions=[
            Position(
                instrument=EquityForward(
                    spot=100.0,
                    strike=100.0,
                    maturity=1.0,
                    rate=0.0,
                    dividend_yield=0.0,
                    symbol="ABC",
                ),
                quantity=1.0,
            )
        ]
    )
    market = MarketData(
        spots={"ABC": 100.0},
        rates={"risk_free": 0.0},
        vols={"ABC": 0.0},
        dividends={"ABC": 0.0},
    )

    result = analytic_pfe_profile(
        portfolio, market, horizons=[0.5, 1.0], confidence=0.95
    )

    assert result.pfe_profile[0.5] == pytest.approx(0.0)
    assert result.pfe_profile[1.0] == pytest.approx(0.0)


def test_analytic_pfe_profile_non_monotonic():
    portfolio = Portfolio(
        positions=[
            Position(
                instrument=EuropeanOption(
                    spot=100.0,
                    strike=100.0,
                    maturity=1.0,
                    rate=0.0,
                    vol=0.2,
                    option_type="call",
                ),
                quantity=1.0,
            ),
            Position(
                instrument=EuropeanOption(
                    spot=100.0,
                    strike=100.0,
                    maturity=1.0,
                    rate=0.0,
                    vol=0.2,
                    option_type="put",
                ),
                quantity=1.0,
            ),
        ]
    )
    market = MarketData(
        spots={},
        rates={"risk_free": 0.0},
        vols={},
        dividends={},
    )

    with pytest.raises(ValueError, match="monotonic"):
        analytic_pfe_profile(portfolio, market, horizons=[1.0], confidence=0.95)


def test_analytic_pfe_profile_mismatched_vol():
    portfolio = Portfolio(
        positions=[
            Position(
                instrument=EuropeanOption(
                    spot=100.0,
                    strike=100.0,
                    maturity=1.0,
                    rate=0.0,
                    vol=0.2,
                    option_type="call",
                ),
                quantity=1.0,
            ),
            Position(
                instrument=EuropeanOption(
                    spot=100.0,
                    strike=100.0,
                    maturity=1.0,
                    rate=0.0,
                    vol=0.3,
                    option_type="call",
                ),
                quantity=1.0,
            ),
        ]
    )
    market = MarketData(
        spots={},
        rates={"risk_free": 0.0},
        vols={},
        dividends={},
    )

    with pytest.raises(ValueError, match="vol"):
        analytic_pfe_profile(portfolio, market, horizons=[1.0], confidence=0.95)


@pytest.mark.parametrize("confidence", [-0.1, 0.0, 1.0, 2.0])
def test_scenario_pfe_invalid_confidence(confidence):
    with pytest.raises(ValueError, match="confidence"):
        scenario_pfe([0.1, -0.1], confidence=confidence)


def test_scenario_pfe_empty():
    with pytest.raises(ValueError, match="scenario_pnls"):
        scenario_pfe([], confidence=0.95)


def test_scenario_pfe_invalid_dimensions():
    pnls = np.zeros((2, 2, 2))
    with pytest.raises(ValueError, match="scenario_pnls"):
        scenario_pfe(pnls, confidence=0.95)

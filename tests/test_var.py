import numpy as np
import pytest

from risk_engine.metrics.var import (
    HistoricalVaRResult,
    MonteCarloVaRResult,
    ParametricVaRResult,
    _normal_ppf,
    historical_var,
    monte_carlo_var,
    portfolio_var_from_returns,
    parametric_portfolio_var,
    parametric_var,
)


def test_historical_var_basic():
    returns = np.array([0.02, -0.03, 0.01, -0.01, 0.00])
    result = historical_var(returns, confidence=0.8, horizon=1)

    expected_quantile = np.quantile(returns, 1.0 - 0.8, method="linear")
    expected_var = -expected_quantile

    assert isinstance(result, HistoricalVaRResult)
    assert result.quantile == expected_quantile
    assert result.var == expected_var
    assert result.confidence == 0.8
    assert result.horizon == 1


def test_historical_var_horizon_scaling():
    returns = np.array([0.01, -0.02, 0.00, 0.03, -0.01])
    one_day = historical_var(returns, confidence=0.95, horizon=1)
    two_day = historical_var(returns, confidence=0.95, horizon=2)

    assert two_day.var == pytest.approx(one_day.var * np.sqrt(2.0))


@pytest.mark.parametrize("confidence", [-0.1, 0.0, 1.0, 1.5])
def test_historical_var_invalid_confidence(confidence):
    with pytest.raises(ValueError, match="confidence"):
        historical_var([0.01, -0.01], confidence=confidence, horizon=1)


@pytest.mark.parametrize("horizon", [0, -1, -5])
def test_historical_var_invalid_horizon(horizon):
    with pytest.raises(ValueError, match="horizon"):
        historical_var([0.01, -0.01], confidence=0.95, horizon=horizon)


def test_historical_var_empty_returns():
    with pytest.raises(ValueError, match="returns"):
        historical_var([], confidence=0.95, horizon=1)


def test_parametric_var_basic():
    returns = np.array([0.02, -0.01, 0.00, 0.03, -0.02])
    result = parametric_var(returns, confidence=0.95, horizon=1)

    mean = float(np.mean(returns))
    std = float(np.std(returns, ddof=1))
    z = float(_normal_ppf(1.0 - 0.95))
    expected_var = -(mean + z * std)

    assert isinstance(result, ParametricVaRResult)
    assert result.mean == pytest.approx(mean)
    assert result.std == pytest.approx(std)
    assert result.z == pytest.approx(z)
    assert result.var == pytest.approx(expected_var)


def test_parametric_portfolio_var_basic():
    weights = np.array([0.6, 0.4])
    covariance = np.array([[0.04, 0.01], [0.01, 0.09]])
    mean = np.array([0.001, 0.002])
    result = parametric_portfolio_var(
        weights, covariance, mean=mean, confidence=0.99, horizon=1
    )

    portfolio_mean = float(np.dot(weights, mean))
    portfolio_var = float(np.dot(weights, np.dot(covariance, weights)))
    portfolio_std = float(np.sqrt(portfolio_var))
    z = float(_normal_ppf(1.0 - 0.99))
    expected_var = -(portfolio_mean + z * portfolio_std)

    assert isinstance(result, ParametricVaRResult)
    assert result.mean == pytest.approx(portfolio_mean)
    assert result.std == pytest.approx(portfolio_std)
    assert result.z == pytest.approx(z)
    assert result.var == pytest.approx(expected_var)


def test_monte_carlo_var_deterministic_seed():
    returns = np.array([0.01, -0.02, 0.015, -0.005, 0.0])
    result = monte_carlo_var(
        returns, confidence=0.95, horizon=1, num_sims=5000, seed=123
    )

    assert isinstance(result, MonteCarloVaRResult)
    assert result.confidence == 0.95
    assert result.horizon == 1
    assert result.num_sims == 5000
    assert result.seed == 123
    assert result.ddof == 1
    assert result.var >= 0.0


@pytest.mark.parametrize("num_sims", [0, -1])
def test_monte_carlo_var_invalid_sims(num_sims):
    with pytest.raises(ValueError, match="num_sims"):
        monte_carlo_var([0.01, -0.01], confidence=0.95, horizon=1, num_sims=num_sims)


@pytest.mark.parametrize("ddof", [-1, 3])
def test_monte_carlo_var_invalid_ddof(ddof):
    with pytest.raises(ValueError, match="ddof"):
        monte_carlo_var([0.01, -0.01], confidence=0.95, horizon=1, ddof=ddof)


def test_portfolio_var_from_returns_matches_historical():
    asset_returns = np.array(
        [
            [0.01, -0.02],
            [0.02, 0.01],
            [-0.01, 0.0],
            [0.0, 0.02],
        ]
    )
    weights = np.array([0.6, 0.4])
    portfolio_returns = asset_returns @ weights

    expected = historical_var(portfolio_returns, confidence=0.95, horizon=1)
    result = portfolio_var_from_returns(
        asset_returns, weights, method="historical", confidence=0.95, horizon=1
    )

    assert isinstance(result, HistoricalVaRResult)
    assert result.var == pytest.approx(expected.var)
    assert result.quantile == pytest.approx(expected.quantile)


def test_portfolio_var_from_returns_multi_confidence_horizon():
    asset_returns = np.array(
        [
            [0.01, -0.02],
            [0.02, 0.01],
            [-0.01, 0.0],
            [0.0, 0.02],
        ]
    )
    weights = np.array([0.6, 0.4])

    results = portfolio_var_from_returns(
        asset_returns,
        weights,
        method="parametric",
        confidence=[0.9, 0.95],
        horizon=[1, 5],
    )

    assert len(results) == 4
    assert all(isinstance(result, ParametricVaRResult) for result in results)


def test_portfolio_var_from_returns_invalid_method():
    with pytest.raises(ValueError, match="method"):
        portfolio_var_from_returns(
            np.array([[0.01, -0.02], [0.02, 0.01]]),
            np.array([0.5, 0.5]),
            method="unknown",
        )

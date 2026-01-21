"""Historical and parametric Value-at-Risk (VaR)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class HistoricalVaRResult:
    """Container for historical VaR output."""

    var: float
    confidence: float
    horizon: int
    quantile: float


@dataclass(frozen=True)
class ParametricVaRResult:
    """Container for parametric VaR output."""

    var: float
    confidence: float
    horizon: int
    mean: float
    std: float
    z: float


@dataclass(frozen=True)
class MonteCarloVaRResult:
    """Container for Monte Carlo VaR output."""

    var: float
    confidence: float
    horizon: int
    mean: float
    std: float
    num_sims: int
    seed: int | None


def historical_var(
    returns: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
    horizon: int = 1,
) -> HistoricalVaRResult:
    """Compute historical VaR from a return series.

    Args:
        returns: Sequence of periodic returns (e.g., daily), as decimals.
        confidence: Confidence level (e.g., 0.95 for 95%).
        horizon: Scaling horizon in the same return units (e.g., days).

    Returns:
        HistoricalVaRResult with VaR reported as a positive number.
    """
    if confidence <= 0.0 or confidence >= 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if horizon <= 0:
        raise ValueError("horizon must be a positive integer")

    data = np.asarray(returns, dtype=float)
    if data.size == 0:
        raise ValueError("returns must contain at least one value")

    # Historical VaR uses the left tail quantile of returns.
    quantile = np.quantile(data, 1.0 - confidence, method="linear")
    var = -quantile * np.sqrt(horizon)

    return HistoricalVaRResult(
        var=float(var),
        confidence=float(confidence),
        horizon=int(horizon),
        quantile=float(quantile),
    )


def _normal_ppf(probability: float) -> float:
    """Approximate inverse CDF for the standard normal distribution."""
    if probability <= 0.0 or probability >= 1.0:
        raise ValueError("probability must be in (0, 1)")

    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    )

    plow = 0.02425
    phigh = 1.0 - plow

    if probability < plow:
        q = np.sqrt(-2.0 * np.log(probability))
        return (
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )
    if probability > phigh:
        q = np.sqrt(-2.0 * np.log(1.0 - probability))
        return -(
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )

    q = probability - 0.5
    r = q * q
    return (
        (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5])
        * q
        / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    )


def parametric_var(
    returns: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
    horizon: int = 1,
) -> ParametricVaRResult:
    """Compute parametric (variance-covariance) VaR from a return series."""
    if confidence <= 0.0 or confidence >= 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if horizon <= 0:
        raise ValueError("horizon must be a positive integer")

    data = np.asarray(returns, dtype=float)
    if data.size == 0:
        raise ValueError("returns must contain at least one value")

    mean = float(np.mean(data))
    std = float(np.std(data, ddof=1)) if data.size > 1 else 0.0
    z = float(_normal_ppf(1.0 - confidence))
    quantile = mean + z * std
    var = -quantile * np.sqrt(horizon)

    return ParametricVaRResult(
        var=float(var),
        confidence=float(confidence),
        horizon=int(horizon),
        mean=mean,
        std=std,
        z=z,
    )


def parametric_portfolio_var(
    weights: Sequence[float] | np.ndarray,
    covariance: Sequence[Sequence[float]] | np.ndarray,
    mean: Sequence[float] | np.ndarray | None = None,
    confidence: float = 0.95,
    horizon: int = 1,
) -> ParametricVaRResult:
    """Compute parametric VaR for a portfolio using weights and covariance."""
    if confidence <= 0.0 or confidence >= 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if horizon <= 0:
        raise ValueError("horizon must be a positive integer")

    w = np.asarray(weights, dtype=float)
    cov = np.asarray(covariance, dtype=float)

    if w.size == 0:
        raise ValueError("weights must contain at least one value")
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValueError("covariance must be a square matrix")
    if cov.shape[0] != w.size:
        raise ValueError("weights and covariance dimensions must match")

    mean_vec = np.zeros_like(w) if mean is None else np.asarray(mean, dtype=float)
    if mean_vec.size != w.size:
        raise ValueError("mean must match weights length")

    portfolio_mean = float(np.dot(w, mean_vec))
    portfolio_var = float(np.dot(w, np.dot(cov, w)))
    portfolio_std = float(np.sqrt(max(portfolio_var, 0.0)))

    z = float(_normal_ppf(1.0 - confidence))
    quantile = portfolio_mean + z * portfolio_std
    var = -quantile * np.sqrt(horizon)

    return ParametricVaRResult(
        var=float(var),
        confidence=float(confidence),
        horizon=int(horizon),
        mean=portfolio_mean,
        std=portfolio_std,
        z=z,
    )


def monte_carlo_var(
    returns: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
    horizon: int = 1,
    num_sims: int = 10000,
    seed: int | None = None,
) -> MonteCarloVaRResult:
    """Compute Monte Carlo VaR using a normal return model."""
    if confidence <= 0.0 or confidence >= 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if horizon <= 0:
        raise ValueError("horizon must be a positive integer")
    if num_sims <= 0:
        raise ValueError("num_sims must be a positive integer")

    data = np.asarray(returns, dtype=float)
    if data.size == 0:
        raise ValueError("returns must contain at least one value")

    mean = float(np.mean(data))
    std = float(np.std(data, ddof=1)) if data.size > 1 else 0.0

    rng = np.random.default_rng(seed)
    sims = rng.normal(loc=mean, scale=std, size=num_sims)
    sims = sims * np.sqrt(horizon)

    quantile = np.quantile(sims, 1.0 - confidence, method="linear")
    var = -quantile

    return MonteCarloVaRResult(
        var=float(var),
        confidence=float(confidence),
        horizon=int(horizon),
        mean=mean,
        std=std,
        num_sims=int(num_sims),
        seed=seed,
    )


def _as_list(value: float | int | Sequence[float] | np.ndarray, name: str) -> tuple[list, bool]:
    if np.isscalar(value):
        return [value], True
    try:
        return list(value), False
    except TypeError as exc:
        raise ValueError(f"{name} must be a scalar or sequence") from exc


def portfolio_var_from_returns(
    asset_returns: Sequence[Sequence[float]] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
    method: str = "historical",
    confidence: float | Sequence[float] = 0.95,
    horizon: int | Sequence[int] = 1,
    num_sims: int = 10000,
    seed: int | None = None,
) -> (
    HistoricalVaRResult
    | ParametricVaRResult
    | MonteCarloVaRResult
    | list[HistoricalVaRResult | ParametricVaRResult | MonteCarloVaRResult]
):
    """Compute portfolio VaR from asset returns and weights.

    Supports multiple confidence levels and horizons via scalar or sequence inputs.
    """
    data = np.asarray(asset_returns, dtype=float)
    if data.ndim != 2 or data.shape[0] == 0 or data.shape[1] == 0:
        raise ValueError("asset_returns must be a 2D array of shape (n_obs, n_assets)")

    w = np.asarray(weights, dtype=float)
    if w.ndim != 1 or w.size != data.shape[1]:
        raise ValueError("weights length must match number of assets")

    confidences, conf_scalar = _as_list(confidence, "confidence")
    horizons, horizon_scalar = _as_list(horizon, "horizon")

    for c in confidences:
        if c <= 0.0 or c >= 1.0:
            raise ValueError("confidence must be in (0, 1)")
    for h in horizons:
        if h <= 0:
            raise ValueError("horizon must be a positive integer")

    method_key = method.lower()
    if method_key not in {"historical", "parametric", "monte_carlo"}:
        raise ValueError("method must be one of: historical, parametric, monte_carlo")

    portfolio_returns = data @ w
    results: list[HistoricalVaRResult | ParametricVaRResult | MonteCarloVaRResult] = []

    for c in confidences:
        for h in horizons:
            if method_key == "historical":
                results.append(historical_var(portfolio_returns, confidence=c, horizon=int(h)))
            elif method_key == "parametric":
                results.append(parametric_var(portfolio_returns, confidence=c, horizon=int(h)))
            else:
                results.append(
                    monte_carlo_var(
                        portfolio_returns,
                        confidence=c,
                        horizon=int(h),
                        num_sims=num_sims,
                        seed=seed,
                    )
                )

    if conf_scalar and horizon_scalar:
        return results[0]
    return results

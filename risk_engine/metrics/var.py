"""Historical and parametric Value-at-Risk (VaR)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import warnings

import numpy as np
try:  # Prefer SciPy when available for accurate normal quantiles.
    from scipy.stats import norm
except ImportError:  # pragma: no cover - fallback for minimal installs.
    norm = None


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
    ddof: int
    method: str


def historical_var(
    returns: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
    horizon: int = 1,
    return_type: str = "simple",
    tail: str = "left",
) -> HistoricalVaRResult:
    """Compute historical VaR from a return series.

    Args:
        returns: Sequence of periodic returns (e.g., daily), as decimals.
        confidence: Confidence level (e.g., 0.95 for 95%).
        horizon: Scaling horizon in the same return units (e.g., days).
        return_type: "simple" or "log".
        tail: "left" for loss tail or "right" for gain tail.

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

    return_kind = _validate_return_type(return_type)
    tail_kind = _validate_tail(tail)
    mean = float(np.mean(data))

    # Historical VaR uses the left tail quantile of returns.
    tail_prob = confidence if tail_kind == "right" else 1.0 - confidence
    quantile = np.quantile(data, tail_prob, method="linear")
    if return_kind == "log":
        scaled_quantile = mean * horizon + (quantile - mean) * np.sqrt(horizon)
    else:
        scaled_quantile = quantile * np.sqrt(horizon)
    var = scaled_quantile if tail_kind == "right" else -scaled_quantile

    return HistoricalVaRResult(
        var=float(var),
        confidence=float(confidence),
        horizon=int(horizon),
        quantile=float(quantile),
    )


def _normal_ppf(probability: float) -> float:
    """Approximate inverse CDF for the standard normal distribution.

    Uses SciPy when available, otherwise falls back to Acklam's approximation:
    https://web.archive.org/web/20150910063919/http://home.online.no/~pjacklam/notes/invnorm/
    """
    if probability <= 0.0 or probability >= 1.0:
        raise ValueError("probability must be in (0, 1)")

    if norm is not None:
        return float(norm.ppf(probability))

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


def _validate_return_type(return_type: str) -> str:
    return_kind = return_type.lower()
    if return_kind not in {"simple", "log"}:
        raise ValueError("return_type must be 'simple' or 'log'")
    return return_kind


def _validate_tail(tail: str) -> str:
    tail_kind = tail.lower()
    if tail_kind not in {"left", "right"}:
        raise ValueError("tail must be 'left' or 'right'")
    return tail_kind


def parametric_var(
    returns: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
    horizon: int = 1,
    return_type: str = "simple",
    tail: str = "left",
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
    return_kind = _validate_return_type(return_type)
    tail_kind = _validate_tail(tail)
    tail_prob = confidence if tail_kind == "right" else 1.0 - confidence
    z = float(_normal_ppf(tail_prob))
    if return_kind == "log":
        mean_h = mean * horizon
        std_h = std * np.sqrt(horizon)
        quantile = mean_h + z * std_h
        var = quantile if tail_kind == "right" else -quantile
    else:
        quantile = mean + z * std
        var = (quantile * np.sqrt(horizon)) if tail_kind == "right" else -quantile * np.sqrt(horizon)

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
    return_type: str = "simple",
    check_weight_sum: bool = False,
    warn_non_psd: bool = False,
    tail: str = "left",
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

    if check_weight_sum and not np.isclose(np.sum(w), 1.0):
        warnings.warn("weights do not sum to 1.0", RuntimeWarning, stacklevel=2)
    if warn_non_psd:
        min_eig = float(np.min(np.linalg.eigvalsh(cov)))
        if min_eig < -1e-12:
            warnings.warn("covariance matrix is not positive semidefinite", RuntimeWarning, stacklevel=2)

    mean_vec = np.zeros_like(w) if mean is None else np.asarray(mean, dtype=float)
    if mean_vec.size != w.size:
        raise ValueError("mean must match weights length")

    portfolio_mean = float(np.dot(w, mean_vec))
    portfolio_var = float(np.dot(w, np.dot(cov, w)))
    portfolio_std = float(np.sqrt(max(portfolio_var, 0.0)))

    return_kind = _validate_return_type(return_type)
    tail_kind = _validate_tail(tail)
    tail_prob = confidence if tail_kind == "right" else 1.0 - confidence
    z = float(_normal_ppf(tail_prob))
    if return_kind == "log":
        mean_h = portfolio_mean * horizon
        std_h = portfolio_std * np.sqrt(horizon)
        quantile = mean_h + z * std_h
        var = quantile if tail_kind == "right" else -quantile
    else:
        quantile = portfolio_mean + z * portfolio_std
        var = (quantile * np.sqrt(horizon)) if tail_kind == "right" else -quantile * np.sqrt(horizon)

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
    ddof: int = 1,
    return_type: str = "simple",
    method: str = "normal",
    tail: str = "left",
) -> MonteCarloVaRResult:
    """Compute Monte Carlo VaR using a normal return model.

    Uses standard deviation estimated with `ddof` (1 for sample, 0 for population).
    """
    if confidence <= 0.0 or confidence >= 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if horizon <= 0:
        raise ValueError("horizon must be a positive integer")
    if num_sims <= 0:
        raise ValueError("num_sims must be a positive integer")
    if ddof < 0:
        raise ValueError("ddof must be >= 0")

    data = np.asarray(returns, dtype=float)
    if data.size == 0:
        raise ValueError("returns must contain at least one value")
    if data.size - ddof <= 0:
        raise ValueError("ddof is too large for the returns length")

    mean = float(np.mean(data))
    std = float(np.std(data, ddof=ddof)) if data.size > 1 else 0.0
    return_kind = _validate_return_type(return_type)
    method_kind = method.lower()
    if method_kind not in {"normal", "bootstrap"}:
        raise ValueError("method must be 'normal' or 'bootstrap'")
    tail_kind = _validate_tail(tail)

    rng = np.random.default_rng(seed)
    if method_kind == "bootstrap":
        if horizon == 1:
            sims = rng.choice(data, size=num_sims, replace=True)
        else:
            idx = rng.integers(0, data.size, size=(num_sims, horizon))
            samples = data[idx]
            if return_kind == "log":
                sims = np.sum(samples, axis=1)
            else:
                sims = np.prod(1.0 + samples, axis=1) - 1.0
    else:
        if return_kind == "log":
            sims = rng.normal(
                loc=mean * horizon, scale=std * np.sqrt(horizon), size=num_sims
            )
        else:
            sims = rng.normal(loc=mean, scale=std, size=num_sims)
            sims = sims * np.sqrt(horizon)

    tail_prob = confidence if tail_kind == "right" else 1.0 - confidence
    quantile = np.quantile(sims, tail_prob, method="linear")
    var = quantile if tail_kind == "right" else -quantile

    return MonteCarloVaRResult(
        var=float(var),
        confidence=float(confidence),
        horizon=int(horizon),
        mean=mean,
        std=std,
        num_sims=int(num_sims),
        seed=seed,
        ddof=int(ddof),
        method=method_kind,
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
    return_type: str = "simple",
    check_weight_sum: bool = False,
    mc_method: str = "normal",
    tail: str = "left",
) -> (
    HistoricalVaRResult
    | ParametricVaRResult
    | MonteCarloVaRResult
    | dict[
        tuple[float, int],
        HistoricalVaRResult | ParametricVaRResult | MonteCarloVaRResult,
    ]
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
    if check_weight_sum and not np.isclose(np.sum(w), 1.0):
        warnings.warn("weights do not sum to 1.0", RuntimeWarning, stacklevel=2)

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
    results: dict[
        tuple[float, int],
        HistoricalVaRResult | ParametricVaRResult | MonteCarloVaRResult,
    ] = {}

    for c in confidences:
        for h in horizons:
            if method_key == "historical":
                result = (
                    historical_var(
                        portfolio_returns,
                        confidence=c,
                        horizon=int(h),
                        return_type=return_type,
                        tail=tail,
                    )
                )
            elif method_key == "parametric":
                result = (
                    parametric_var(
                        portfolio_returns,
                        confidence=c,
                        horizon=int(h),
                        return_type=return_type,
                        tail=tail,
                    )
                )
            else:
                result = (
                    monte_carlo_var(
                        portfolio_returns,
                        confidence=c,
                        horizon=int(h),
                        num_sims=num_sims,
                        seed=seed,
                        return_type=return_type,
                        method=mc_method,
                        tail=tail,
                    )
                )
            results[(float(c), int(h))] = result

    if conf_scalar and horizon_scalar:
        return next(iter(results.values()))
    return results

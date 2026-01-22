"""Monte Carlo path generation utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class GBMParams:
    """Geometric Brownian Motion parameters."""

    drift: float
    vol: float


@dataclass(frozen=True)
class HullWhiteParams:
    """One-factor Hull-White (Ornstein-Uhlenbeck) rate parameters."""

    mean_reversion: float
    long_rate: float
    vol: float


@dataclass(frozen=True)
class HestonParams:
    """Heston stochastic volatility parameters."""

    kappa: float
    long_var: float
    vol_of_vol: float
    rho: float
    initial_var: float
    drift: float


@dataclass(frozen=True)
class VasicekParams:
    """Vasicek short rate model parameters."""

    mean_reversion: float
    long_rate: float
    vol: float


def simulate_gbm_paths(
    *,
    spot: float,
    params: GBMParams,
    dt: float,
    num_steps: int,
    num_paths: int,
    seed: int | None = None,
) -> np.ndarray:
    """Simulate GBM spot paths."""
    if spot <= 0.0:
        raise ValueError("spot must be > 0")
    if dt <= 0.0:
        raise ValueError("dt must be > 0")
    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    if num_paths <= 0:
        raise ValueError("num_paths must be > 0")
    if params.vol < 0.0:
        raise ValueError("vol must be >= 0")

    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal(size=(num_paths, num_steps))
    drift = (params.drift - 0.5 * params.vol * params.vol) * dt
    diffusion = params.vol * np.sqrt(dt) * shocks
    log_steps = drift + diffusion

    paths = np.empty((num_paths, num_steps + 1), dtype=float)
    paths[:, 0] = spot
    paths[:, 1:] = spot * np.exp(np.cumsum(log_steps, axis=1))
    return paths


def simulate_hull_white_paths(
    *,
    rate: float,
    params: HullWhiteParams,
    dt: float,
    num_steps: int,
    num_paths: int,
    seed: int | None = None,
) -> np.ndarray:
    """Simulate Hull-White short rate paths with Euler discretization."""
    if dt <= 0.0:
        raise ValueError("dt must be > 0")
    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    if num_paths <= 0:
        raise ValueError("num_paths must be > 0")
    if params.mean_reversion < 0.0:
        raise ValueError("mean_reversion must be >= 0")
    if params.vol < 0.0:
        raise ValueError("vol must be >= 0")

    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal(size=(num_paths, num_steps))

    rates = np.empty((num_paths, num_steps + 1), dtype=float)
    rates[:, 0] = rate

    for step in range(1, num_steps + 1):
        prev = rates[:, step - 1]
        drift = params.mean_reversion * (params.long_rate - prev) * dt
        diffusion = params.vol * np.sqrt(dt) * shocks[:, step - 1]
        rates[:, step] = prev + drift + diffusion

    return rates


def simulate_heston_paths(
    *,
    spot: float,
    params: HestonParams,
    dt: float,
    num_steps: int,
    num_paths: int,
    seed: int | None = None,
) -> np.ndarray:
    """Simulate Heston spot paths using full truncation Euler."""
    if spot <= 0.0:
        raise ValueError("spot must be > 0")
    if dt <= 0.0:
        raise ValueError("dt must be > 0")
    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    if num_paths <= 0:
        raise ValueError("num_paths must be > 0")
    if params.kappa < 0.0:
        raise ValueError("kappa must be >= 0")
    if params.long_var < 0.0:
        raise ValueError("long_var must be >= 0")
    if params.vol_of_vol < 0.0:
        raise ValueError("vol_of_vol must be >= 0")
    if not -1.0 <= params.rho <= 1.0:
        raise ValueError("rho must be in [-1, 1]")
    if params.initial_var < 0.0:
        raise ValueError("initial_var must be >= 0")

    rng = np.random.default_rng(seed)
    z1 = rng.standard_normal(size=(num_paths, num_steps))
    z2 = rng.standard_normal(size=(num_paths, num_steps))
    w1 = z1
    w2 = params.rho * z1 + np.sqrt(max(1.0 - params.rho * params.rho, 0.0)) * z2

    spots = np.empty((num_paths, num_steps + 1), dtype=float)
    vars_ = np.empty((num_paths, num_steps + 1), dtype=float)
    spots[:, 0] = spot
    vars_[:, 0] = params.initial_var

    for step in range(1, num_steps + 1):
        prev_var = np.maximum(vars_[:, step - 1], 0.0)
        drift = (params.drift - 0.5 * prev_var) * dt
        diffusion = np.sqrt(prev_var * dt) * w1[:, step - 1]
        spots[:, step] = spots[:, step - 1] * np.exp(drift + diffusion)

        var_drift = params.kappa * (params.long_var - prev_var) * dt
        var_diffusion = params.vol_of_vol * np.sqrt(prev_var * dt) * w2[:, step - 1]
        vars_[:, step] = np.maximum(prev_var + var_drift + var_diffusion, 0.0)

    return spots


def simulate_vasicek_paths(
    *,
    rate: float,
    params: VasicekParams,
    dt: float,
    num_steps: int,
    num_paths: int,
    seed: int | None = None,
) -> np.ndarray:
    """Simulate Vasicek short rate paths with Euler discretization."""
    if dt <= 0.0:
        raise ValueError("dt must be > 0")
    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    if num_paths <= 0:
        raise ValueError("num_paths must be > 0")
    if params.mean_reversion < 0.0:
        raise ValueError("mean_reversion must be >= 0")
    if params.vol < 0.0:
        raise ValueError("vol must be >= 0")

    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal(size=(num_paths, num_steps))

    rates = np.empty((num_paths, num_steps + 1), dtype=float)
    rates[:, 0] = rate

    for step in range(1, num_steps + 1):
        prev = rates[:, step - 1]
        drift = params.mean_reversion * (params.long_rate - prev) * dt
        diffusion = params.vol * np.sqrt(dt) * shocks[:, step - 1]
        rates[:, step] = prev + drift + diffusion

    return rates


__all__ = [
    "GBMParams",
    "HullWhiteParams",
    "HestonParams",
    "VasicekParams",
    "simulate_gbm_paths",
    "simulate_hull_white_paths",
    "simulate_heston_paths",
    "simulate_vasicek_paths",
]

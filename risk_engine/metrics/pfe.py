"""Scenario-based Potential Future Exposure (PFE) metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from risk_engine.core.engine import MarketData, PricingEngine, ScenarioRevaluation
from risk_engine.core.instruments import EquityForward, FixedRateBond, ZeroCouponBond
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.metrics.var import _normal_ppf
from risk_engine.models.pricing import BlackScholesModel, EuropeanOption
from risk_engine.simulation.monte_carlo import (
    GBMParams,
    HestonParams,
    HullWhiteParams,
    VasicekParams,
    simulate_gbm_paths,
    simulate_heston_paths,
    simulate_hull_white_paths,
    simulate_vasicek_paths,
)


@dataclass(frozen=True)
class ScenarioPFEResult:
    """Container for scenario-based PFE output."""

    pfe: float
    confidence: float
    horizon: int | None
    quantile: float
    threshold: float
    netting: bool
    num_scenarios: int


@dataclass(frozen=True)
class MonteCarloPFEResult:
    """Container for Monte Carlo PFE profile output."""

    pfe_profile: Mapping[float, float]
    expected_exposure: Mapping[float, float]
    confidence: float
    horizons: Sequence[float]
    num_paths: int
    dt: float
    seed: int | None
    threshold: float
    value_adjustment: float


@dataclass(frozen=True)
class AnalyticPFEResult:
    """Container for analytic PFE profile output."""

    pfe_profile: Mapping[float, float]
    expected_exposure: Mapping[float, float]
    confidence: float
    horizons: Sequence[float]
    threshold: float
    value_adjustment: float
    assumption: str


def _validate_confidence(confidence: float) -> float:
    if confidence <= 0.0 or confidence >= 1.0:
        raise ValueError("confidence must be in (0, 1)")
    return float(confidence)


def _spot_quantile(
    spot: float, mu: float, vol: float, horizon: float, confidence: float
) -> float:
    if horizon == 0.0:
        return float(spot)
    z = _normal_ppf(confidence)
    return float(
        spot * np.exp((mu - 0.5 * vol * vol) * horizon + vol * np.sqrt(horizon) * z)
    )


def _expected_spot(spot: float, mu: float, horizon: float) -> float:
    if horizon == 0.0:
        return float(spot)
    return float(spot * np.exp(mu * horizon))


def _scenario_exposures(
    scenario_pnls: Sequence[float] | np.ndarray,
    *,
    threshold: float,
    netting: bool,
) -> np.ndarray:
    data = np.asarray(scenario_pnls, dtype=float)
    if data.size == 0:
        raise ValueError("scenario_pnls must contain at least one value")

    if data.ndim == 1:
        netted = data
    elif data.ndim == 2:
        if netting:
            netted = np.sum(data, axis=1)
        else:
            netted = np.sum(np.maximum(data, 0.0), axis=1)
    else:
        raise ValueError("scenario_pnls must be 1D or 2D")

    exposures = np.maximum(netted - threshold, 0.0)
    return exposures


def scenario_pfe(
    scenario_pnls: Sequence[float] | np.ndarray,
    *,
    confidence: float = 0.95,
    horizon: int | None = 1,
    threshold: float = 0.0,
    netting: bool = True,
) -> ScenarioPFEResult:
    """Compute scenario-based PFE from scenario PnLs.

    Args:
        scenario_pnls: Scenario PnLs for a single horizon. Accepts a 1D array of
            portfolio PnLs or a 2D array (scenarios x positions) to control netting.
        confidence: Quantile level for the exposure distribution.
        horizon: Optional horizon label for the scenario set.
        threshold: Collateral or exposure threshold applied after netting.
        netting: When scenario_pnls is 2D, use netted portfolio PnL per scenario.

    Returns:
        ScenarioPFEResult containing the PFE at the given confidence.
    """
    confidence = _validate_confidence(confidence)
    exposures = _scenario_exposures(
        scenario_pnls, threshold=float(threshold), netting=bool(netting)
    )

    quantile = float(np.quantile(exposures, confidence, method="linear"))
    return ScenarioPFEResult(
        pfe=float(quantile),
        confidence=confidence,
        horizon=None if horizon is None else int(horizon),
        quantile=quantile,
        threshold=float(threshold),
        netting=bool(netting),
        num_scenarios=int(exposures.size),
    )


def scenario_pfe_profile(
    scenario_pnls_by_horizon: Mapping[int, Sequence[float] | np.ndarray],
    *,
    confidence: float = 0.95,
    threshold: float | Mapping[int, float] = 0.0,
    netting: bool = True,
) -> dict[int, ScenarioPFEResult]:
    """Compute scenario-based PFE across multiple horizons."""
    confidence = _validate_confidence(confidence)
    thresholds: Mapping[int, float]
    if isinstance(threshold, Mapping):
        thresholds = threshold
    else:
        thresholds = {horizon: float(threshold) for horizon in scenario_pnls_by_horizon}

    results: dict[int, ScenarioPFEResult] = {}
    for horizon, pnls in scenario_pnls_by_horizon.items():
        horizon_threshold = float(thresholds.get(horizon, 0.0))
        results[int(horizon)] = scenario_pfe(
            pnls,
            confidence=confidence,
            horizon=int(horizon),
            threshold=horizon_threshold,
            netting=netting,
        )

    return results


def scenario_pfe_from_revaluation(
    revaluation: ScenarioRevaluation,
    *,
    confidence: float = 0.95,
    horizon: int | None = 1,
    threshold: float = 0.0,
    netting: bool = True,
) -> ScenarioPFEResult:
    """Compute scenario-based PFE from a ScenarioRevaluation output."""
    return scenario_pfe(
        revaluation.pnls,
        confidence=confidence,
        horizon=horizon,
        threshold=threshold,
        netting=netting,
    )


def scenario_pfe_profile_from_revaluations(
    revaluations_by_horizon: Mapping[int, ScenarioRevaluation],
    *,
    confidence: float = 0.95,
    threshold: float | Mapping[int, float] = 0.0,
    netting: bool = True,
) -> dict[int, ScenarioPFEResult]:
    """Compute scenario-based PFE across horizons from revaluations."""
    pnls_by_horizon = {
        int(horizon): revaluation.pnls
        for horizon, revaluation in revaluations_by_horizon.items()
    }
    return scenario_pfe_profile(
        pnls_by_horizon,
        confidence=confidence,
        threshold=threshold,
        netting=netting,
    )


def _extract_underlying_params(
    portfolio: Portfolio, market_data: MarketData
) -> tuple[float, float, float, float, int]:
    spot = None
    vol = None
    rate = market_data.rates.get("risk_free")
    dividend = None
    default_dividend = None
    if len(market_data.dividends) == 1:
        default_dividend = float(next(iter(market_data.dividends.values())))
    underlying_symbol = None
    direction = None

    for position in portfolio:
        instrument = position.instrument
        qty = position.quantity
        if isinstance(instrument, EquityForward):
            inst_symbol = instrument.symbol
            inst_spot = (
                market_data.spots.get(instrument.symbol, instrument.spot)
                if instrument.symbol
                else instrument.spot
            )
            inst_rate = rate if rate is not None else instrument.rate
            if instrument.symbol:
                inst_div = market_data.dividends.get(
                    instrument.symbol, instrument.dividend_yield
                )
            else:
                inst_div = instrument.dividend_yield
            inst_vol = None
            if instrument.symbol:
                inst_vol = market_data.vols.get(instrument.symbol)
            if inst_vol is None:
                raise ValueError("market_data.vols must include forward symbol vol")
            inst_direction = 1.0
        elif isinstance(instrument, EuropeanOption):
            inst_symbol = getattr(instrument, "symbol", None)
            inst_spot = instrument.spot
            inst_rate = instrument.rate
            inst_div = default_dividend if default_dividend is not None else 0.0
            inst_vol = instrument.vol
            option_type = instrument.option_type.lower()
            if option_type == "call":
                inst_direction = 1.0
            elif option_type == "put":
                inst_direction = -1.0
            else:
                raise ValueError("option_type must be 'call' or 'put'")
        else:
            raise ValueError("analytic_pfe supports EquityForward and EuropeanOption only")

        if inst_symbol is not None:
            if underlying_symbol is None:
                underlying_symbol = inst_symbol
            elif underlying_symbol != inst_symbol:
                raise ValueError("all instruments must share the same underlying symbol")

        signed_direction = inst_direction if qty >= 0.0 else -inst_direction
        if direction is None:
            direction = signed_direction
        elif signed_direction * direction < 0.0:
            raise ValueError("portfolio value is not monotonic in spot")

        if spot is None:
            spot = inst_spot
        elif not np.isclose(spot, inst_spot):
            raise ValueError("all instruments must share the same spot")

        if vol is None:
            vol = inst_vol
        elif not np.isclose(vol, inst_vol):
            raise ValueError("all instruments must share the same vol")

        if rate is None:
            rate = inst_rate
        elif not np.isclose(rate, inst_rate):
            raise ValueError("all instruments must share the same rate")

        if dividend is None:
            dividend = inst_div

    if spot is None or vol is None or rate is None:
        raise ValueError("portfolio must contain at least one supported instrument")

    if dividend is None:
        dividend = default_dividend if default_dividend is not None else 0.0

    return float(spot), float(vol), float(rate), float(dividend), int(direction or 1)


def _price_portfolio_at_spot(
    portfolio: Portfolio, spot: float, horizon: float
) -> float:
    bs_model = BlackScholesModel()
    total = 0.0
    for position in portfolio:
        instrument = position.instrument
        qty = position.quantity
        if isinstance(instrument, EquityForward):
            tau = max(instrument.maturity - horizon, 0.0)
            df = np.exp(-instrument.rate * tau)
            forward = spot * np.exp(-instrument.dividend_yield * tau)
            value = forward - instrument.strike * df
        elif isinstance(instrument, EuropeanOption):
            tau = max(instrument.maturity - horizon, 0.0)
            opt = EuropeanOption(
                spot=spot,
                strike=instrument.strike,
                maturity=tau,
                rate=instrument.rate,
                vol=instrument.vol,
                option_type=instrument.option_type,
            )
            value = bs_model.price(opt)
        else:
            raise ValueError("analytic_pfe supports EquityForward and EuropeanOption only")
        total += qty * value
    return float(total)


def analytic_pfe_profile(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    horizons: Sequence[float],
    confidence: float = 0.95,
    threshold: float = 0.0,
    value_adjustment: float = 0.0,
) -> AnalyticPFEResult:
    """Compute analytic PFE profile for simple equity forwards/options.

    Assumes a single underlying spot follows a lognormal process with
    drift (r - q) and constant volatility. Portfolio value must be monotonic
    in spot, otherwise quantile mapping is invalid.
    """
    confidence = _validate_confidence(confidence)
    if not horizons:
        raise ValueError("horizons must contain at least one value")
    if any(h < 0.0 for h in horizons):
        raise ValueError("horizons must be >= 0")

    spot, vol, rate, dividend, direction = _extract_underlying_params(
        portfolio, market_data
    )
    mu = rate - dividend

    pfe_profile: dict[float, float] = {}
    expected_exposure: dict[float, float] = {}

    for horizon in sorted(float(h) for h in horizons):
        quantile_prob = confidence if direction > 0 else 1.0 - confidence
        spot_q = _spot_quantile(spot, mu, vol, horizon, quantile_prob)
        spot_mean = _expected_spot(spot, mu, horizon)

        value_q = _price_portfolio_at_spot(portfolio, spot_q, horizon)
        value_mean = _price_portfolio_at_spot(portfolio, spot_mean, horizon)

        exposure_q = max(value_q - value_adjustment - threshold, 0.0)
        exposure_mean = max(value_mean - value_adjustment - threshold, 0.0)

        pfe_profile[horizon] = float(exposure_q)
        expected_exposure[horizon] = float(exposure_mean)

    return AnalyticPFEResult(
        pfe_profile=pfe_profile,
        expected_exposure=expected_exposure,
        confidence=confidence,
        horizons=tuple(sorted(float(h) for h in horizons)),
        threshold=float(threshold),
        value_adjustment=float(value_adjustment),
        assumption="lognormal spot, monotonic portfolio, exposure approx by value at E[S_t]",
    )


def _roll_instrument(instrument: object, horizon: float) -> object:
    if isinstance(instrument, EquityForward):
        return EquityForward(
            spot=instrument.spot,
            strike=instrument.strike,
            maturity=max(instrument.maturity - horizon, 0.0),
            rate=instrument.rate,
            dividend_yield=instrument.dividend_yield,
            symbol=instrument.symbol,
        )
    if isinstance(instrument, FixedRateBond):
        return FixedRateBond(
            face=instrument.face,
            coupon_rate=instrument.coupon_rate,
            maturity=max(instrument.maturity - horizon, 0.0),
            payments_per_year=instrument.payments_per_year,
        )
    if isinstance(instrument, ZeroCouponBond):
        return ZeroCouponBond(
            face=instrument.face,
            maturity=max(instrument.maturity - horizon, 0.0),
        )
    if isinstance(instrument, EuropeanOption):
        return EuropeanOption(
            spot=instrument.spot,
            strike=instrument.strike,
            maturity=max(instrument.maturity - horizon, 0.0),
            rate=instrument.rate,
            vol=instrument.vol,
            option_type=instrument.option_type,
            symbol=getattr(instrument, "symbol", None),
        )
    return instrument


def _roll_portfolio(portfolio: Portfolio, horizon: float) -> Portfolio:
    positions = [
        Position(
            instrument=_roll_instrument(position.instrument, horizon),
            quantity=position.quantity,
            direction=position.direction,
            label=position.label,
        )
        for position in portfolio
    ]
    return Portfolio(positions=positions)


def _validate_horizons(horizons: Sequence[float], dt: float) -> tuple[list[float], int]:
    if dt <= 0.0:
        raise ValueError("dt must be > 0")
    if not horizons:
        raise ValueError("horizons must contain at least one value")
    times = sorted(float(h) for h in horizons)
    if times[0] < 0.0:
        raise ValueError("horizons must be >= 0")
    max_horizon = times[-1]
    if max_horizon == 0.0:
        raise ValueError("max horizon must be > 0")
    num_steps = int(round(max_horizon / dt))
    if not np.isclose(max_horizon, num_steps * dt):
        raise ValueError("max horizon must align with dt")
    for horizon in times:
        steps = horizon / dt
        if not np.isclose(steps, round(steps)):
            raise ValueError("all horizons must align with dt")
    return times, num_steps


def monte_carlo_pfe_profile(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    horizons: Sequence[float],
    dt: float,
    num_paths: int = 10000,
    confidence: float = 0.95,
    equity_models: Mapping[str, GBMParams | HestonParams],
    rate_model: HullWhiteParams | VasicekParams | None = None,
    threshold: float = 0.0,
    value_adjustment: float = 0.0,
    seed: int | None = None,
) -> MonteCarloPFEResult:
    """Compute Monte Carlo PFE profile using simulated risk factor paths."""
    confidence = _validate_confidence(confidence)
    if num_paths <= 0:
        raise ValueError("num_paths must be > 0")

    horizons_list, num_steps = _validate_horizons(horizons, dt)
    max_step = num_steps

    if not equity_models:
        raise ValueError("equity_models must contain at least one entry")

    for symbol in equity_models:
        if symbol not in market_data.spots:
            raise ValueError(f"market_data.spots missing symbol '{symbol}'")

    base_rate = market_data.rates.get("risk_free")
    if base_rate is None:
        raise ValueError("market_data.rates must include 'risk_free'")

    rng = np.random.default_rng(seed)
    equity_paths: dict[str, np.ndarray] = {}
    for symbol, params in equity_models.items():
        model_seed = int(rng.integers(0, 2**32 - 1))
        if isinstance(params, HestonParams):
            equity_paths[symbol] = simulate_heston_paths(
                spot=float(market_data.spots[symbol]),
                params=params,
                dt=dt,
                num_steps=max_step,
                num_paths=num_paths,
                seed=model_seed,
            )
        else:
            equity_paths[symbol] = simulate_gbm_paths(
                spot=float(market_data.spots[symbol]),
                params=params,
                dt=dt,
                num_steps=max_step,
                num_paths=num_paths,
                seed=model_seed,
            )

    if rate_model is None:
        rate_paths = np.full((num_paths, max_step + 1), float(base_rate), dtype=float)
    else:
        rate_seed = int(rng.integers(0, 2**32 - 1))
        if isinstance(rate_model, VasicekParams):
            rate_paths = simulate_vasicek_paths(
                rate=float(base_rate),
                params=rate_model,
                dt=dt,
                num_steps=max_step,
                num_paths=num_paths,
                seed=rate_seed,
            )
        else:
            rate_paths = simulate_hull_white_paths(
                rate=float(base_rate),
                params=rate_model,
                dt=dt,
                num_steps=max_step,
                num_paths=num_paths,
                seed=rate_seed,
            )

    engine = PricingEngine()
    pfe_profile: dict[float, float] = {}
    expected_exposure: dict[float, float] = {}

    base_spots = dict(market_data.spots)
    base_rates = dict(market_data.rates)
    base_vols = dict(market_data.vols)
    base_dividends = dict(market_data.dividends)
    base_curves = dict(market_data.curves)

    for horizon in horizons_list:
        step_idx = int(round(horizon / dt))
        rolled = _roll_portfolio(portfolio, horizon)
        exposures = np.empty(num_paths, dtype=float)

        for path_idx in range(num_paths):
            spots = dict(base_spots)
            for symbol, path in equity_paths.items():
                spots[symbol] = float(path[path_idx, step_idx])
            rates = dict(base_rates)
            rates["risk_free"] = float(rate_paths[path_idx, step_idx])
            shocked = MarketData(
                spots=spots,
                rates=rates,
                vols=base_vols,
                dividends=base_dividends,
                curves=base_curves,
            )
            value = engine.price_portfolio(rolled, shocked).total
            exposures[path_idx] = max(value - value_adjustment - threshold, 0.0)

        pfe_profile[horizon] = float(
            np.quantile(exposures, confidence, method="linear")
        )
        expected_exposure[horizon] = float(np.mean(exposures))

    return MonteCarloPFEResult(
        pfe_profile=pfe_profile,
        expected_exposure=expected_exposure,
        confidence=confidence,
        horizons=tuple(horizons_list),
        num_paths=int(num_paths),
        dt=float(dt),
        seed=seed,
        threshold=float(threshold),
        value_adjustment=float(value_adjustment),
    )


__all__ = [
    "ScenarioPFEResult",
    "MonteCarloPFEResult",
    "AnalyticPFEResult",
    "scenario_pfe",
    "scenario_pfe_profile",
    "scenario_pfe_from_revaluation",
    "scenario_pfe_profile_from_revaluations",
    "monte_carlo_pfe_profile",
    "analytic_pfe_profile",
]

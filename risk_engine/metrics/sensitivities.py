"""Risk sensitivity metric placeholders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from risk_engine.core.engine import MarketData, PricingEngine
from risk_engine.core.portfolio import Portfolio


@dataclass(frozen=True)
class ScalarSensitivityResult:
    """Container for scalar sensitivity outputs."""

    metric: str
    value: float
    bump: float
    method: str
    units: str


@dataclass(frozen=True)
class BucketedSensitivityResult:
    """Container for bucketed sensitivity outputs."""

    metric: str
    sensitivities: Mapping[str, float]
    bump: float
    method: str
    units: str


def _raise_placeholder(metric: str) -> None:
    raise NotImplementedError(
        f"{metric} sensitivity placeholder. Implement by bumping market data and revaluing."
    )


def delta(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.01,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute spot/forward delta by bumping underlying levels."""
    _raise_placeholder("Delta")


def gamma(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.01,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute second-order spot/forward gamma."""
    _raise_placeholder("Gamma")


def vega(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.01,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute sensitivity to volatility bumps."""
    _raise_placeholder("Vega")


def rho(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.0001,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute sensitivity to rate/discount curve bumps."""
    _raise_placeholder("Rho")


def theta(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 1.0,
    method: str = "forward",
) -> ScalarSensitivityResult:
    """Compute sensitivity to a time roll (time decay)."""
    _raise_placeholder("Theta")


def dv01(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.0001,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute DV01/PV01 for rate curve nodes."""
    _raise_placeholder("DV01")


def cs01(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.0001,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute credit spread sensitivity."""
    _raise_placeholder("CS01")


def fx_delta(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.01,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute FX delta for cross-currency exposures."""
    _raise_placeholder("FX Delta")


def dividend_sensitivity(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.0001,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute sensitivity to dividend or carry inputs."""
    _raise_placeholder("Dividend")


def correlation_sensitivity(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.01,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute sensitivity to correlation assumptions."""
    _raise_placeholder("Correlation")


def basis_sensitivity(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.0001,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute sensitivity to curve/basis spreads (e.g., OIS vs IBOR)."""
    _raise_placeholder("Basis")


def vol_of_vol_sensitivity(
    portfolio: Portfolio,
    market_data: MarketData,
    *,
    engine: PricingEngine | None = None,
    bump: float = 0.01,
    method: str = "central",
) -> BucketedSensitivityResult:
    """Compute sensitivity to vol-of-vol inputs in stochastic vol models."""
    _raise_placeholder("Vol-of-vol")


__all__ = [
    "ScalarSensitivityResult",
    "BucketedSensitivityResult",
    "delta",
    "gamma",
    "vega",
    "rho",
    "theta",
    "dv01",
    "cs01",
    "fx_delta",
    "dividend_sensitivity",
    "correlation_sensitivity",
    "basis_sensitivity",
    "vol_of_vol_sensitivity",
]

"""VaR wrappers aligned to the new package layout."""

from risk_engine.metrics.var import (
    HistoricalVaRResult,
    MonteCarloVaRResult,
    ParametricVaRResult,
    historical_var,
    monte_carlo_var,
    parametric_portfolio_var,
    parametric_var,
    portfolio_var_from_returns,
)

__all__ = [
    "historical_var",
    "parametric_var",
    "parametric_portfolio_var",
    "monte_carlo_var",
    "portfolio_var_from_returns",
    "HistoricalVaRResult",
    "ParametricVaRResult",
    "MonteCarloVaRResult",
]

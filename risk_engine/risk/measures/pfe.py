"""PFE wrappers aligned to the new package layout."""

from risk_engine.metrics.pfe import (
    AnalyticPFEResult,
    MonteCarloPFEResult,
    ScenarioPFEResult,
    analytic_pfe_profile,
    monte_carlo_pfe_profile,
    scenario_pfe,
    scenario_pfe_from_revaluation,
    scenario_pfe_profile,
    scenario_pfe_profile_from_revaluations,
)

__all__ = [
    "scenario_pfe",
    "scenario_pfe_profile",
    "scenario_pfe_from_revaluation",
    "scenario_pfe_profile_from_revaluations",
    "monte_carlo_pfe_profile",
    "analytic_pfe_profile",
    "ScenarioPFEResult",
    "MonteCarloPFEResult",
    "AnalyticPFEResult",
]

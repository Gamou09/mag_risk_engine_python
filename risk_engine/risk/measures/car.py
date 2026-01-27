"""Capital-at-Risk (CaR) placeholders."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalAtRiskResult:
    """Placeholder result type for CaR."""

    car: float | None = None
    notes: str = "TODO: implement capital-at-risk"


def capital_at_risk(*args, **kwargs) -> CapitalAtRiskResult:
    """Placeholder CaR computation."""
    raise NotImplementedError("Capital-at-Risk not implemented yet")


# TODO: integrate with regulatory capital formulas and stress VaR.

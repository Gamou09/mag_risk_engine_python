"""Apply shocks to market state."""

from __future__ import annotations

from collections.abc import Iterable

from risk_engine.core.engine import apply_scenario
from risk_engine.market.state import MarketState
from risk_engine.scenarios.shock import ShockSet, Shock


def apply_shocks_old(state: MarketState, shocks: Shock | Iterable[Shock]) -> list[MarketState]:
    """Apply one or more shocks and return shocked market states."""
    if isinstance(shocks, Iterable) and not isinstance(shocks, Shock):
        return [apply_scenario(state, shock) for shock in shocks]
    return [apply_scenario(state, shocks)]  # type: ignore[arg-type]

def apply_shocks(state: MarketState, shockset: ShockSet) -> MarketState:
    updates = {}
    for s in shockset.shocks:
        base = state.get(s.key)
        if s.shock_type == "abs":
            updates[s.key] = base + s.value
        elif s.shock_type == "rel":
            updates[s.key] = base * (1.0 + s.value)
        else:
            raise ValueError(f"Unknown shock_type: {s.shock_type}")
    return state.with_factors(updates)


# TODO: add composition, bump sets, and netting-set aware transformations.

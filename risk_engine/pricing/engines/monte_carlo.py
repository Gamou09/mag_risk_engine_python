"""Monte Carlo engine placeholder."""

from __future__ import annotations

from risk_engine.simulation.monte_carlo import (
    simulate_gbm_paths,
    simulate_heston_paths,
    simulate_hull_white_paths,
    simulate_vasicek_paths,
)


class MonteCarloEngine:
    """Stub engine to share simulation utilities."""

    def __init__(self, simulator=simulate_gbm_paths) -> None:
        self.simulator = simulator

    def price(self, instrument, **kwargs):
        raise NotImplementedError("Monte Carlo pricing not wired yet")


__all__ = [
    "MonteCarloEngine",
    "simulate_gbm_paths",
    "simulate_heston_paths",
    "simulate_hull_white_paths",
    "simulate_vasicek_paths",
]


# TODO: add path-dependent pricing hooks and control variates.

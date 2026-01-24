"""ScenarioGenerator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from risk_engine.scenarios.shock import ShockSet


class ScenarioGenerator(ABC):
    """Base scenario generator."""

    @abstractmethod
    def generate(self) -> ShockSet:
        """Generate a sequence of shocks."""


# TODO: add seeding/correlation inputs and batch generation controls.

"""Base classes for pricing models and pricers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class PricingModel(ABC):
    """Base class for pricing models."""

    @abstractmethod
    def price(self, instrument: Any, **kwargs: Any) -> float:
        """Return the model price for an instrument."""

    def greeks(self, instrument: Any, **kwargs: Any) -> Mapping[str, float] | None:
        """Optional sensitivities to model parameters (e.g., delta, gamma)."""
        return None

    def sensitivities(
        self, instrument: Any, **kwargs: Any
    ) -> Mapping[str, float] | None:
        """Optional sensitivities to risk factors (e.g., curves, vols)."""
        return None


class Pricer(ABC):
    """Base class for pricers that may wrap models or data sources."""

    @abstractmethod
    def price(self, instrument: Any, **kwargs: Any) -> float:
        """Return the price for an instrument."""

    def greeks(self, instrument: Any, **kwargs: Any) -> Mapping[str, float] | None:
        """Optional sensitivities to model parameters."""
        return None

    def sensitivities(
        self, instrument: Any, **kwargs: Any
    ) -> Mapping[str, float] | None:
        """Optional sensitivities to risk factors."""
        return None

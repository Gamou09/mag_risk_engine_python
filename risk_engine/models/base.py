"""Model interface wrappers."""

from __future__ import annotations

from dataclasses import dataclass

from risk_engine.models.pricing.base import Pricer, PricingModel

ModelId = str


@dataclass(frozen=True)
class ModelSpec:
    """Model identifier with optional parameters."""

    model_id: ModelId
    params: dict[str, object] | None = None


__all__ = ["ModelId", "ModelSpec", "PricingModel", "Pricer"]


# TODO: add parameter validation and serialization helpers.

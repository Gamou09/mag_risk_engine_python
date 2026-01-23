"""Shared instrument interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Instrument(ABC):
    """Base class that enforces minimal instrument metadata."""

    ASSET_CLASS: str

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "ASSET_CLASS", None):
            raise TypeError(f"{cls.__name__} must define ASSET_CLASS")

    @property
    def asset_class(self) -> str:
        return type(self).ASSET_CLASS

    @property
    def instrument_type(self) -> str:
        return type(self).__name__

    @abstractmethod
    def risk_factors(self) -> tuple[str, ...]:
        """Return the primary risk factors for this instrument."""
        raise NotImplementedError

"""Registry of known curve identifiers for validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CurveRegistry:
    """
    Collection of known curve identifiers (e.g., ``OIS_USD_3M``).
    Mutates internally while keeping the dataclass frozen for callers.
    """

    _names: set[str]

    def __init__(self, names: Iterable[str] | None = None) -> None:
        object.__setattr__(self, "_names", set(names or ()))

    def register(self, name: str) -> None:
        self._names.add(name)

    def is_known(self, name: str) -> bool:
        return name in self._names

    def require_known(self, name: str) -> None:
        if not self.is_known(name):
            known = ", ".join(sorted(self._names)) if self._names else "none registered"
            raise ValueError(f"Unknown curve id '{name}'. Known curve ids: {known}")

    @property
    def names(self) -> set[str]:
        return set(self._names)


def default_curve_registry() -> CurveRegistry:
    """Seed registry with a minimal set of common curves."""
    return CurveRegistry(
        names={
            "OIS_USD_3M",
            "SOFR_USD_ON",
            "LIBOR_USD_3M",
        }
    )


__all__ = ["CurveRegistry", "default_curve_registry"]

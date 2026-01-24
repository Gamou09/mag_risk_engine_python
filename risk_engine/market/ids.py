"""Identifiers for market observables."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CurveRole(str, Enum):
    """Curve types supported by the market container."""

    DISCOUNT = "DISCOUNT"
    FORWARD = "FORWARD"
    BASIS = "BASIS"
    INFLATION = "INFLATION"


@dataclass(frozen=True)
class CurveId:
    """Typed wrapper around a curve identifier like ``OIS_USD_3M``."""

    name: str

    def df_key(self, pillar: str) -> str:
        """Build a discount factor risk key."""
        return f"DF.{self.name}.{pillar}"

    def fwd_key(self, pillar: str) -> str:
        """Build a forward rate risk key."""
        return f"FWD.{self.name}.{pillar}"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.name


__all__ = ["CurveId", "CurveRole"]

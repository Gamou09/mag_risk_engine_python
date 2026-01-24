"""Shock objects (re-using legacy Scenario for now)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Literal

# from typing import Sequence

# from risk_engine.core.engine import Scenario as Shock

# ShockSet = Sequence[Shock]

# TODO: add absolute/relative shocks and bucketed factor handling.

ShockType = Literal["abs", "rel"]

@dataclass(frozen=True)
class Shock:
    key: str
    shock_type: ShockType
    value: float  # abs: add value, rel: multiply by (1+value)

@dataclass(frozen=True)
class ShockSet:
    shocks: tuple[Shock, ...]

    @staticmethod
    def from_dict_abs(d: Mapping[str, float]) -> "ShockSet":
        return ShockSet(tuple(Shock(k, "abs", v) for k, v in d.items()))

    @staticmethod
    def from_dict_rel(d: Mapping[str, float]) -> "ShockSet":
        return ShockSet(tuple(Shock(k, "rel", v) for k, v in d.items()))

__all__ = ["Shock", "ShockSet"]

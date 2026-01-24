from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from risk_engine.market.curve_set import CurveSet


def _freeze_mapping(mapping: Mapping) -> Mapping:
    return MappingProxyType(dict(mapping))


@dataclass(frozen=True)
class Market:
    """Immutable market container holding curve sets and FX spots."""

    curve_sets: Mapping[str, CurveSet]
    fx_spot: Mapping[tuple[str, str], float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "curve_sets", _freeze_mapping(self.curve_sets))
        object.__setattr__(self, "fx_spot", _freeze_mapping(self.fx_spot))

    def curves(self, currency: str) -> CurveSet:
        try:
            return self.curve_sets[currency]
        except KeyError as exc:
            raise KeyError(f"Missing CurveSet for currency '{currency}'") from exc

    def spot(self, ccy1: str, ccy2: str) -> float:
        direct = self.fx_spot.get((ccy1, ccy2))
        if direct is not None:
            return direct
        inverse = self.fx_spot.get((ccy2, ccy1))
        if inverse is not None:
            if inverse == 0:
                raise ZeroDivisionError("FX spot cannot be zero when inverting.")
            return 1.0 / inverse
        raise KeyError(f"Missing FX spot for pair {ccy1}/{ccy2}")


__all__ = ["Market"]

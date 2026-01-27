from __future__ import annotations

from dataclasses import dataclass, replace, field
from typing import Mapping, Optional

from risk_engine.market.curves import DiscountCurve, ForwardCurve
from risk_engine.market.ids import CurveId, CurveRole
from risk_engine.utils.collections import freeze_mapping


@dataclass(frozen=True)
class CurveSet:
    """Immutable collection of curves for a single currency."""

    currency: str
    discount: DiscountCurve
    forwards: Mapping[str, ForwardCurve] = field(default_factory=dict)
    basis: Mapping[tuple[str, str], object] = field(default_factory=dict)
    inflation: Optional[object] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "forwards", freeze_mapping(self.forwards))
        object.__setattr__(self, "basis", freeze_mapping(self.basis))

    def forward(self, index: str) -> ForwardCurve:
        try:
            return self.forwards[index]
        except KeyError as exc:
            raise KeyError(f"Missing forward curve for index '{index}'") from exc

    def get(self, role: CurveRole, key: Optional[str] = None) -> object:
        if role is CurveRole.DISCOUNT:
            return self.discount
        if role is CurveRole.FORWARD:
            if key is None:
                raise KeyError("Forward curve key is required for CurveRole.FORWARD")
            return self.forward(key)
        if role is CurveRole.BASIS:
            return self.basis
        if role is CurveRole.INFLATION:
            return self.inflation
        raise KeyError(f"Unsupported curve role '{role}'")

    def bump_curve(self, curve_id: CurveId, bp: float) -> "CurveSet":
        if self.discount.id == curve_id:
            return replace(self, discount=self.discount.bump(bp))

        for idx, fwd_curve in self.forwards.items():
            if fwd_curve.id == curve_id:
                new_forwards = dict(self.forwards)
                new_forwards[idx] = fwd_curve.bump(bp)
                return replace(self, forwards=new_forwards)

        raise KeyError(f"CurveId '{curve_id}' not found in CurveSet for {self.currency}")

    def curve_ids(self) -> tuple[CurveId, ...]:
        ids = [self.discount.id]
        ids.extend(fwd.id for fwd in self.forwards.values())
        return tuple(ids)


__all__ = ["CurveSet"]

"""Curve interfaces, protocols, and lightweight test curves."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from risk_engine.market.ids import CurveId
from risk_engine.models.curves_surfaces.zero_curve import (
    BootstrappedZeroCurve,
    FlatZeroCurve,
    PiecewiseZeroCurve,
)


@runtime_checkable
class DiscountCurve(Protocol):
    @property
    def id(self) -> CurveId: ...

    @property
    def currency(self) -> str: ...

    def df(self, t: float) -> float: ...

    def bump(self, bp: float) -> "DiscountCurve": ...


@runtime_checkable
class ForwardCurve(Protocol):
    @property
    def id(self) -> CurveId: ...

    @property
    def currency(self) -> str: ...

    @property
    def index(self) -> str: ...

    def fwd(self, t1: float, t2: float) -> float: ...

    def bump(self, bp: float) -> "ForwardCurve": ...


@dataclass(frozen=True)
class FlatZeroDiscountCurve:
    """Flat zero rate discount curve for tests."""

    id: CurveId
    currency: str
    r: float

    def df(self, t: float) -> float:
        return math.exp(-self.r * t)

    def bump(self, bp: float) -> "FlatZeroDiscountCurve":
        bumped = self.r + bp * 1e-4
        return FlatZeroDiscountCurve(id=self.id, currency=self.currency, r=bumped)


@dataclass(frozen=True)
class FlatForwardCurve:
    """Flat forward curve for tests."""

    id: CurveId
    currency: str
    index: str
    f: float

    def fwd(self, t1: float, t2: float) -> float:
        return self.f

    def bump(self, bp: float) -> "FlatForwardCurve":
        bumped = self.f + bp * 1e-4
        return FlatForwardCurve(
            id=self.id, currency=self.currency, index=self.index, f=bumped
        )


__all__ = [
    "DiscountCurve",
    "ForwardCurve",
    "FlatZeroDiscountCurve",
    "FlatForwardCurve",
    "FlatZeroCurve",
    "PiecewiseZeroCurve",
    "BootstrappedZeroCurve",
]

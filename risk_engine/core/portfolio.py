"""Portfolio data structures and aggregation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(frozen=True)
class Position:
    """Position in a portfolio."""

    instrument: Any
    quantity: float = 1.0
    label: str | None = None


@dataclass(frozen=True)
class Portfolio:
    """Collection of positions."""

    positions: Sequence[Position] = field(default_factory=tuple)

    def __iter__(self):
        return iter(self.positions)


__all__ = ["Position", "Portfolio"]

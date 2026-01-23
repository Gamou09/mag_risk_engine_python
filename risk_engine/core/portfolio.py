"""Portfolio data structures and aggregation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(frozen=True)
class Position:
    """Position in a portfolio."""

    instrument: Any
    quantity: float = 1.0
    direction: str = "long"
    label: str | None = None

    def __post_init__(self) -> None:
        direction = self.direction.lower()
        if direction not in ("long", "short"):
            raise ValueError("direction must be 'long' or 'short'")
        object.__setattr__(self, "direction", direction)


@dataclass(frozen=True)
class Portfolio:
    """Collection of positions."""

    positions: Sequence[Position] = field(default_factory=tuple)

    def __iter__(self):
        return iter(self.positions)


__all__ = ["Position", "Portfolio"]

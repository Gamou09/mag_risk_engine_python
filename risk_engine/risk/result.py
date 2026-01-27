"""Risk result container."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class RiskResult:
    """Aggregated risk output with optional drilldowns."""

    measures: Mapping[str, Any] = field(default_factory=dict)
    contributions: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] | None = None


# TODO: structure by netting set / desk, include scenario slices.

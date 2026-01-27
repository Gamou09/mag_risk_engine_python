"""Trade metadata wrapper around instruments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from risk_engine.instruments.assets.instrument_base import Instrument


@dataclass(frozen=True)
class Trade:
    """Instrument + trading metadata."""

    instrument: Instrument
    quantity: float = 1.0
    book: str | None = None
    counterparty: str | None = None
    netting_set: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


# TODO: extend with lifecycle events, settlement details, and identifiers.

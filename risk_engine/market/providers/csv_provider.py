"""CSV-backed market data loader (placeholder)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from risk_engine.market.providers.base import MarketDataProvider
from risk_engine.market.state import MarketState


class CsvMarketDataProvider(MarketDataProvider):
    """Sketch of a CSV adapter; wire up parsing later."""

    def __init__(self, paths: Iterable[str | Path]) -> None:
        self.paths = [Path(path) for path in paths]

    def load_state(self, as_of=None) -> MarketState:  # type: ignore[override]
        raise NotImplementedError("CSV provider wiring is TBD")


# TODO: implement schema discovery and mapping into MarketState fields.

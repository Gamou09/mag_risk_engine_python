"""Database-backed market data loader (placeholder)."""

from __future__ import annotations

from typing import Any

from risk_engine.market.providers.base import MarketDataProvider
from risk_engine.market.state import MarketState


class DbMarketDataProvider(MarketDataProvider):
    """Sketch of a DB adapter; keep IO out of the core layer."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def load_state(self, as_of=None) -> MarketState:  # type: ignore[override]
        raise NotImplementedError("DB provider wiring is TBD")


# TODO: provide minimal SQL example and plug in caching/pooling if needed.

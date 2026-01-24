"""Interfaces for loading market data (keep IO concerns outside the core)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime

from risk_engine.market.state import MarketState


class MarketDataProvider(ABC):
    """Base provider interface."""

    @abstractmethod
    def load_state(self, as_of: date | datetime | None = None) -> MarketState:
        """Return a MarketState for the requested as_of."""


# TODO: consider async providers and caching for intraday refresh.

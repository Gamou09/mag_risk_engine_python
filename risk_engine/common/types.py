"""Value objects and basic domain types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

Currency = NewType("Currency", str)


@dataclass(frozen=True)
class Money:
    """Lightweight money container. Extend with FX rules as needed."""

    amount: float
    currency: Currency = Currency("USD")

    def __post_init__(self) -> None:
        if not isinstance(self.amount, (int, float)):
            raise TypeError("amount must be numeric")
        if not isinstance(self.currency, str):
            raise TypeError("currency must be a string-like code")


# TODO: consider richer enums/types for asset classes, tenors, day-count, etc.

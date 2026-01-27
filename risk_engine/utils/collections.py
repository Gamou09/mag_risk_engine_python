"""Small collection utilities."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping, TypeVar

T = TypeVar("T", bound=Mapping)


def freeze_mapping(mapping: T) -> T:
    """Return a shallow, read-only copy of the mapping."""
    return MappingProxyType(dict(mapping))  # type: ignore[arg-type]


__all__ = ["freeze_mapping"]

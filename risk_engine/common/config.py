"""Configuration hooks for global knobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass
class RiskEngineConfig:
    """Mutable configuration placeholder for tuning models/backends."""

    defaults: Mapping[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.defaults.get(key, default)

    def with_override(self, **kwargs: Any) -> "RiskEngineConfig":
        merged = dict(self.defaults)
        merged.update(kwargs)
        return RiskEngineConfig(defaults=merged)


# TODO: replace with validated config (pydantic/dataclasses) and env overrides.

"""Pricer registry (InstrumentType, ModelId, Method) -> pricer."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any, Mapping, MutableMapping, Tuple

# risk_engine/pricing/registry.py
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from risk_engine.pricing.pricer import Pricer, InstrumentLike
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.result import PricingResult

Key = Tuple[str, Optional[str], str]  # (product_type, model_id, method)

@dataclass
class PricerRegistry:
    _map: Dict[Key, Pricer] = field(default_factory=dict)

    def register(self, product_type: str, pricer: Pricer, model_id: Optional[str] = None, method: str = "analytic") -> None:
        self._map[(product_type, model_id, method)] = pricer

    def get(self, product_type: str, model_id: Optional[str], method: str) -> Pricer:
        key = (product_type, model_id, method)
        if key in self._map:
            return self._map[key]
        # fallback: ignore model_id
        key2 = (product_type, None, method)
        if key2 in self._map:
            return self._map[key2]
        raise KeyError(f"No pricer registered for {key} (or fallback {key2})")

    def price(self, instrument: InstrumentLike, ctx: PricingContext) -> PricingResult:
        pricer = self.get(instrument.product_type, ctx.model_id, ctx.method)
        return pricer.price(instrument, ctx)


class PricingRegistry_old:
    """Minimal in-memory registry."""

    def __init__(self) -> None:
        self._registry: MutableMapping[Tuple[Hashable, Hashable | None], Any] = {}

    def register(self, instrument_type: Hashable, model_id: Hashable | None, pricer: Any) -> None:
        self._registry[(instrument_type, model_id)] = pricer

    def get(self, instrument_type: Hashable, model_id: Hashable | None = None) -> Any:
        key = (instrument_type, model_id)
        if key not in self._registry:
            raise KeyError(f"no pricer registered for {key}")
        return self._registry[key]

    def registered(self) -> Mapping[Tuple[Hashable, Hashable | None], Any]:
        return dict(self._registry)


# TODO: add method dimension and fallback resolution; consider entrypoints for plugins.

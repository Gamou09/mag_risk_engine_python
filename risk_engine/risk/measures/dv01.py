"""Rate sensitivity wrappers."""

from risk_engine.metrics.sensitivities import cs01 as cs01
from risk_engine.metrics.sensitivities import dv01 as dv01

# risk_engine/risk/measures/dv01.py
from __future__ import annotations
from dataclasses import dataclass
from risk_engine.scenarios.shock import ShockSet
from risk_engine.scenarios.apply import apply_shocks
from risk_engine.pricing.context import PricingContext
from risk_engine.instruments.base import Instrument
from risk_engine.pricing.registry import PricerRegistry

@dataclass(frozen=True)
class DV01:
    """
    Minimal DV01: bump a single discount factor key (or rate proxy) and reprice.
    In a real system you'd bump a curve node/bucket and use risk-factor mapping.
    """
    name: str = "DV01"
    bump_key: str = "RATE.USD.OIS.1Y"
    bump_size: float = 1e-4  # 1bp

    def run(self, portfolio: list[Instrument], ctx: PricingContext, registry: PricerRegistry):
        base = [registry.price(inst, ctx).pv.amount for inst in portfolio]

        shocked_market = apply_shocks(ctx.market, ShockSet.from_dict_abs({self.bump_key: self.bump_size}))
        shocked_ctx = PricingContext(market=shocked_market, model_id=ctx.model_id, method=ctx.method, settings=ctx.settings)

        bumped = [registry.price(inst, shocked_ctx).pv.amount for inst in portfolio]
        dv01s = [b - a for a, b in zip(base, bumped)]
        return {"measure": self.name, "bump_key": self.bump_key, "dv01s": dv01s, "total": sum(dv01s)}


__all__ = ["dv01", "cs01"]


# TODO: translate bucket labels to curve keys/netting sets.

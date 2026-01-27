from __future__ import annotations

from risk_engine.market.ids import CurveId
from risk_engine.market.market import Market


def bump_market(market: Market, curve_id: CurveId, bp: float) -> Market:
    """
    Bump exactly one curve identified by ``curve_id`` across all curve sets.
    Returns a new Market with only the owning CurveSet replaced.
    """
    bumped_currency: str | None = None
    new_curve_sets = dict(market.curve_sets)

    for currency, curve_set in market.curve_sets.items():
        try:
            bumped_set = curve_set.bump_curve(curve_id, bp)
        except KeyError:
            continue

        new_curve_sets[currency] = bumped_set
        bumped_currency = currency
        break

    if bumped_currency is None:
        raise KeyError(f"CurveId '{curve_id}' not found in market")

    return Market(curve_sets=new_curve_sets, fx_spot=market.fx_spot)


__all__ = ["bump_market"]

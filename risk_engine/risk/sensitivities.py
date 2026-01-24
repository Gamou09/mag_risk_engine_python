from __future__ import annotations

from typing import Iterable, Mapping, Protocol

from risk_engine.market.ids import CurveId
from risk_engine.market.market import Market
from risk_engine.risk.bump import bump_market
from risk_engine.risk.requests import CurveRisk, RiskRequest


class PVPricer(Protocol):
    def pv(self, trade: object, market: Market) -> float: ...


def _portfolio_pv(trades: tuple[object, ...], pricer_map: Mapping[type, PVPricer], market: Market) -> float:
    total = 0.0
    for trade in trades:
        pricer = pricer_map[type(trade)]
        total += pricer.pv(trade, market)
    return total


def _curves_to_bump(market: Market, req: RiskRequest) -> tuple[CurveId, ...]:
    if req.curves is not None:
        return tuple(req.curves)

    collected: list[CurveId] = []
    for curve_set in market.curve_sets.values():
        collected.extend(curve_set.curve_ids())
    return tuple(collected)


def curve_sensitivities(
    trades: Iterable[object],
    pricer_map: Mapping[type, PVPricer],
    market: Market,
    req: RiskRequest,
) -> tuple[CurveRisk, ...]:
    trade_list = tuple(trades)
    curve_ids = _curves_to_bump(market, req)
    base_pv = _portfolio_pv(trade_list, pricer_map, market)

    risks: list[CurveRisk] = []
    for cid in curve_ids:
        bumped_market = bump_market(market, cid, req.bp)
        bumped_pv = _portfolio_pv(trade_list, pricer_map, bumped_market)
        risks.append(CurveRisk(curve_id=cid, dPV=bumped_pv - base_pv))

    return tuple(risks)


__all__ = ["curve_sensitivities"]

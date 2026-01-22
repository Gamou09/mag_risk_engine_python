"""Core risk engine orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from risk_engine.core.instruments import (
    EquityForward,
    EquitySpot,
    FixedRateBond,
    ZeroCouponBond,
)
from risk_engine.core.portfolio import Portfolio, Position
from risk_engine.models.pricing import (
    BlackScholesModel,
    Cashflow,
    CashflowPVModel,
    DiscountingModel,
    EuropeanOption,
)


@dataclass(frozen=True)
class MarketData:
    """Typed container for market risk factors."""

    spots: Mapping[str, float] = field(default_factory=dict)
    rates: Mapping[str, float] = field(default_factory=dict)
    vols: Mapping[str, float] = field(default_factory=dict)
    dividends: Mapping[str, float] = field(default_factory=dict)
    curves: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Scenario:
    """Additive shocks and curve overrides for revaluation."""

    spot_shocks: Mapping[str, float] = field(default_factory=dict)
    rate_shocks: Mapping[str, float] = field(default_factory=dict)
    vol_shocks: Mapping[str, float] = field(default_factory=dict)
    dividend_shocks: Mapping[str, float] = field(default_factory=dict)
    curve_overrides: Mapping[str, object] = field(default_factory=dict)


def apply_scenario(base: MarketData, scenario: Scenario) -> MarketData:
    """Apply a scenario to base market data."""

    def _apply(base_map: Mapping[str, float], shocks: Mapping[str, float]) -> dict[str, float]:
        keys = set(base_map) | set(shocks)
        return {key: base_map.get(key, 0.0) + shocks.get(key, 0.0) for key in keys}

    curves = dict(base.curves)
    curves.update(scenario.curve_overrides)

    return MarketData(
        spots=_apply(base.spots, scenario.spot_shocks),
        rates=_apply(base.rates, scenario.rate_shocks),
        vols=_apply(base.vols, scenario.vol_shocks),
        dividends=_apply(base.dividends, scenario.dividend_shocks),
        curves=curves,
    )


@dataclass(frozen=True)
class PositionValue:
    """Position-level valuation."""

    position: Position
    price: float
    value: float


@dataclass(frozen=True)
class PortfolioValue:
    """Portfolio-level valuation."""

    total: float
    positions: Sequence[PositionValue]


@dataclass(frozen=True)
class ScenarioRevaluation:
    """Scenario revaluation output."""

    base: PortfolioValue
    scenario_values: Sequence[PortfolioValue]
    pnls: Sequence[float]


class PricingEngine:
    """Typed portfolio pricing and scenario revaluation."""

    def __init__(self, *, bs_model: BlackScholesModel | None = None) -> None:
        self._bs_model = bs_model or BlackScholesModel()

    def price_portfolio(self, portfolio: Portfolio, market_data: MarketData) -> PortfolioValue:
        position_values: list[PositionValue] = []
        total = 0.0

        for position in portfolio:
            price = self.price_instrument(position.instrument, market_data)
            value = price * position.quantity
            position_values.append(PositionValue(position=position, price=price, value=value))
            total += value

        return PortfolioValue(total=total, positions=position_values)

    def revalue_scenarios(
        self, portfolio: Portfolio, market_data: MarketData, scenarios: Sequence[Scenario]
    ) -> ScenarioRevaluation:
        base_value = self.price_portfolio(portfolio, market_data)
        scenario_values: list[PortfolioValue] = []
        pnls: list[float] = []

        for scenario in scenarios:
            shocked = apply_scenario(market_data, scenario)
            value = self.price_portfolio(portfolio, shocked)
            scenario_values.append(value)
            pnls.append(value.total - base_value.total)

        return ScenarioRevaluation(
            base=base_value, scenario_values=scenario_values, pnls=pnls
        )

    def price_instrument(self, instrument: Any, market_data: MarketData) -> float:
        if isinstance(instrument, EquitySpot):
            return float(self._spot_for(instrument, market_data))

        if isinstance(instrument, EquityForward):
            spot = self._spot_for(instrument, market_data)
            rate = self._rate_for(market_data)
            dividend = self._dividend_for(instrument, market_data)
            model = DiscountingModel(rate=rate)
            forward = EquityForward(
                spot=spot,
                strike=instrument.strike,
                maturity=instrument.maturity,
                rate=rate,
                dividend_yield=dividend,
                symbol=instrument.symbol,
            )
            return model.price(forward)

        if isinstance(instrument, FixedRateBond):
            model = self._discounting_model(market_data)
            return model.price(instrument)

        if isinstance(instrument, ZeroCouponBond):
            model = self._discounting_model(market_data)
            return model.price(instrument)

        if isinstance(instrument, EuropeanOption):
            spot = self._spot_for(instrument, market_data)
            rate = self._rate_for(market_data)
            vol = self._vol_for(instrument, market_data)
            option = EuropeanOption(
                spot=spot,
                strike=instrument.strike,
                maturity=instrument.maturity,
                rate=rate,
                vol=vol,
                option_type=instrument.option_type,
            )
            return self._bs_model.price(option)

        if isinstance(instrument, Sequence) and instrument and all(
            isinstance(cf, Cashflow) for cf in instrument
        ):
            model = self._cashflow_model(market_data)
            return model.price(instrument)

        raise TypeError("unsupported instrument type")

    def _spot_for(self, instrument: Any, market_data: MarketData) -> float:
        symbol = getattr(instrument, "symbol", None)
        if symbol and symbol in market_data.spots:
            return float(market_data.spots[symbol])
        return float(getattr(instrument, "spot"))

    def _rate_for(self, market_data: MarketData) -> float:
        if "risk_free" in market_data.rates:
            return float(market_data.rates["risk_free"])
        raise ValueError("market_data.rates must include 'risk_free'")

    def _dividend_for(self, instrument: Any, market_data: MarketData) -> float:
        symbol = getattr(instrument, "symbol", None)
        if symbol and symbol in market_data.dividends:
            return float(market_data.dividends[symbol])
        return float(getattr(instrument, "dividend_yield", 0.0))

    def _vol_for(self, instrument: Any, market_data: MarketData) -> float:
        symbol = getattr(instrument, "symbol", None)
        if symbol and symbol in market_data.vols:
            return float(market_data.vols[symbol])
        return float(getattr(instrument, "vol"))

    def _discounting_model(self, market_data: MarketData) -> DiscountingModel:
        curve = market_data.curves.get("discount")
        if curve is not None:
            df = getattr(curve, "df", None)
            if df is None:
                raise ValueError("discount curve must expose df(t)")
            return DiscountingModel(discount_curve=df)
        rate = self._rate_for(market_data)
        return DiscountingModel(rate=rate)

    def _cashflow_model(self, market_data: MarketData) -> CashflowPVModel:
        curve = market_data.curves.get("discount")
        if curve is not None:
            df = getattr(curve, "df", None)
            if df is None:
                raise ValueError("discount curve must expose df(t)")
            return CashflowPVModel(discount_curve=df)
        rate = self._rate_for(market_data)
        return CashflowPVModel(rate=rate)


__all__ = [
    "MarketData",
    "Scenario",
    "apply_scenario",
    "PositionValue",
    "PortfolioValue",
    "ScenarioRevaluation",
    "PricingEngine",
]

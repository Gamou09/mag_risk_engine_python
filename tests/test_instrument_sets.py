from __future__ import annotations

from collections.abc import Sequence
from dataclasses import MISSING, fields, is_dataclass
from types import UnionType
from typing import Union, get_args, get_origin

from risk_engine.instruments.assets import (
    instruments_commodities,
    instruments_credit,
    instruments_equity,
    instruments_fx,
    instruments_hybrid_exotic_mutliAsset_other,
    instruments_rates,
)
from risk_engine.instruments.assets.instrument_base import Instrument
from risk_engine.instruments.assets.risk_factors import ALL_RISK_FACTORS

MODULES = [
    instruments_rates,
    instruments_fx,
    instruments_equity,
    instruments_credit,
    instruments_commodities,
    instruments_hybrid_exotic_mutliAsset_other,
]
ALLOWED_FACTORS = set(ALL_RISK_FACTORS)


def _make_value(annotation: object) -> object:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is None:
        if annotation is float:
            return 1.0
        if annotation is int:
            return 1
        if annotation is bool:
            return True
        if annotation is str:
            return "X"
        return None
    if origin is dict:
        return {}
    if origin is set:
        return set()
    if origin is tuple:
        return ()
    if origin in (Union, UnionType):
        non_none = [arg for arg in args if arg is not type(None)]
        return _make_value(non_none[0]) if non_none else None
    if origin in (list,):
        return []
    if origin is Sequence:
        if args:
            return [_make_value(args[0])]
        return []
    return None


def _instantiate(cls: type[Instrument]) -> Instrument:
    kwargs: dict[str, object] = {}
    for field in fields(cls):
        if field.default is not MISSING or field.default_factory is not MISSING:
            continue
        kwargs[field.name] = _make_value(field.type)
    return cls(**kwargs)


def test_instruments_define_risk_factors() -> None:
    for module in MODULES:
        for name in module.__all__:
            cls = getattr(module, name)
            assert is_dataclass(cls)
            assert issubclass(cls, Instrument)
            instance = _instantiate(cls)
            factors = instance.risk_factors()
            assert isinstance(factors, tuple)
            assert factors
            assert all(factor in ALLOWED_FACTORS for factor in factors)

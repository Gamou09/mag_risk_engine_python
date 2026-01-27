import pytest

from risk_engine.market.curve_registry import CurveRegistry, default_curve_registry
from risk_engine.market.state import MarketState


def test_unknown_curve_id_rejected_with_validation() -> None:
    registry = CurveRegistry({"OIS_USD_3M"})
    state = MarketState(factors={"DF.UNKNOWN.1Y": 0.95}, registry=registry)

    with pytest.raises(ValueError, match="Unknown curve id 'UNKNOWN'"):
        state.validate_factor_keys()

    with pytest.raises(ValueError, match="Unknown curve id 'UNKNOWN'"):
        state.get("DF.UNKNOWN.1Y")


def test_known_curve_id_passes_validation() -> None:
    registry = CurveRegistry({"OIS_USD_3M"})
    state = MarketState(factors={"DF.OIS_USD_3M.1Y": 0.97}, registry=registry)

    # Should not raise
    state.validate_factor_keys()
    assert state.get("DF.OIS_USD_3M.1Y") == pytest.approx(0.97)


def test_typo_curve_id_highlights_known_ids() -> None:
    registry = default_curve_registry()
    state = MarketState(factors={"DF.OIS_USD3M.1Y": 0.97}, registry=registry)

    with pytest.raises(ValueError) as excinfo:
        state.validate_factor_keys()

    # Helpful message should mention known IDs so typos are obvious.
    assert "OIS_USD_3M" in str(excinfo.value)

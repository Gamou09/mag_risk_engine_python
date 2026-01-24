"""Domain-specific exceptions."""


class RiskEngineError(Exception):
    """Base error for risk engine failures."""


class PricingError(RiskEngineError):
    """Pricing failure or invalid instrument/model combination."""


class MarketDataError(RiskEngineError):
    """Market data validation error."""


# TODO: add richer error taxonomy (calibration, scenario, aggregation, etc).

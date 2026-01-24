"""FX option pricer placeholder."""

from __future__ import annotations


class FXOptionPricer:
    """Stub pricer; connect to analytic or tree engines."""

    def price(self, instrument, **kwargs):
        raise NotImplementedError("FX option pricer not implemented yet")


# TODO: support delta/vega quoting conventions and quanto/locals.

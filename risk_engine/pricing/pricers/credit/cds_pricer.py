"""CDS pricer placeholder."""

from __future__ import annotations


class CDSPricer:
    """Stub; hook to hazard-rate or spread curve model."""

    def price(self, instrument, **kwargs):
        raise NotImplementedError("CDS pricer not implemented yet")


# TODO: include accrual-on-default, recovery assumptions, and index handling.

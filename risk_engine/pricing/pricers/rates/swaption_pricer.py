"""Swaption pricer placeholder."""

from __future__ import annotations


class SwaptionPricer:
    """Stub pricer; connect to analytic, lattice, or MC engines."""

    def price(self, instrument, **kwargs):
        raise NotImplementedError("Swaption pricer not implemented yet")


# TODO: add Black/normal model support and calibration hooks.

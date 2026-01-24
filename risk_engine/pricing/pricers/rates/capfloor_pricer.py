"""Cap/floor pricer placeholder."""

from __future__ import annotations


class CapFloorPricer:
    """Stub pricer; hook into lattice/analytic engines later."""

    def price(self, instrument, **kwargs):
        raise NotImplementedError("Cap/Floor pricer not implemented yet")


# TODO: add Black '76 and normal vol support.

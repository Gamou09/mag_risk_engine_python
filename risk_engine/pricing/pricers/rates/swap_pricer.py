"""Swap pricer placeholder."""

from __future__ import annotations


class SwapPricer:
    """Stub; wire to curve bootstrapping and leg builders."""

    def price(self, instrument, **kwargs):
        raise NotImplementedError("Swap pricer not implemented yet")


# TODO: build fixed/float legs from conventions and discount with MarketState.

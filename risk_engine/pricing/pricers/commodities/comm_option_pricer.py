"""Commodity option pricer placeholder."""

from __future__ import annotations


class CommodityOptionPricer:
    """Stub; extend with Black/normal models and convenience yields."""

    def price(self, instrument, **kwargs):
        raise NotImplementedError("Commodity option pricer not implemented yet")


# TODO: integrate forward curves and storage/convenience yield modeling.

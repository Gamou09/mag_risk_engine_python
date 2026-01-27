"""Variance swap pricer placeholder."""

from __future__ import annotations


class VarianceSwapPricer:
    """Stub; will need log-contract replication or model-based pricing."""

    def price(self, instrument, **kwargs):
        raise NotImplementedError("Variance swap pricer not implemented yet")


# TODO: add static replication with option strips and vol surfaces.

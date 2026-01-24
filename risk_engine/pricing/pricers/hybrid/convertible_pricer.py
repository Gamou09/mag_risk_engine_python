"""Convertible bond pricer placeholder."""

from __future__ import annotations


class ConvertibleBondPricer:
    """Stub; integrate credit/equity hybrid model when available."""

    def price(self, instrument, **kwargs):
        raise NotImplementedError("Convertible bond pricer not implemented yet")


# TODO: plug into lattice/MC hybrid engines with credit spread dynamics.

"""FX forward pricer placeholder."""

from __future__ import annotations


class FXForwardPricer:
    """Stub pricer; requires carry inputs and FX basis."""

    def price(self, instrument, **kwargs):
        raise NotImplementedError("FX forward pricer not implemented yet")


# TODO: incorporate interest rate differentials and deliverable vs NDF logic.

"""Volatility/correlation surface placeholders."""


class Surface:
    """Generic surface interface; fill in with concrete implementations."""

    def value(self, *args, **kwargs):  # pragma: no cover - placeholder
        raise NotImplementedError("Surface evaluation not yet implemented")


# TODO: add lognormal vol surfaces, local-vol, and correlation structures.

"""Time grid helpers (placeholder)."""


def build_time_grid(start: float, end: float, steps: int) -> list[float]:
    """Simple evenly spaced grid helper."""
    if steps <= 0:
        raise ValueError("steps must be > 0")
    if end < start:
        raise ValueError("end must be >= start")
    dt = (end - start) / steps
    return [start + i * dt for i in range(1, steps + 1)]


# TODO: add business-day aware grids and MC step alignment.

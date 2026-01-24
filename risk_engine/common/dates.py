"""Date and schedule utilities (placeholder implementations)."""

from __future__ import annotations


def year_fraction(start: float, end: float, basis: str = "act/365") -> float:
    """Very rough year fraction helper until real day-count is added."""
    if end < start:
        raise ValueError("end must be >= start")
    basis_norm = basis.lower()
    if basis_norm not in ("act/365", "act/360"):
        raise ValueError("basis must be 'act/365' or 'act/360'")
    denominator = 365.0 if basis_norm == "act/365" else 360.0
    return (end - start) / denominator


def schedule(start: float, end: float, freq: int) -> list[float]:
    """Simple schedule generator to seed examples/tests."""
    if freq <= 0:
        raise ValueError("freq must be > 0")
    if end < start:
        raise ValueError("end must be >= start")

    step = 1.0 / freq
    current = start + step
    dates: list[float] = []
    while current < end - 1e-9:
        dates.append(round(current, 10))
        current += step
    dates.append(end)
    return dates


# TODO: replace with real calendar, business day roll, and day-count logic.

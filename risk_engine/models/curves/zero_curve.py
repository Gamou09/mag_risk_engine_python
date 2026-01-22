"""Simple zero curve implementations."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence


@dataclass(frozen=True)
class FlatZeroCurve:
    """Flat zero curve with continuous compounding."""

    rate: float

    def df(self, t: float) -> float:
        if t < 0.0:
            raise ValueError("t must be >= 0")
        return math.exp(-self.rate * t)


@dataclass(frozen=True)
class PiecewiseZeroCurve:
    """Piecewise zero curve with linear interpolation on zero rates."""

    times: Sequence[float]
    zero_rates: Sequence[float]

    def df(self, t: float) -> float:
        if t < 0.0:
            raise ValueError("t must be >= 0")
        if len(self.times) == 0:
            raise ValueError("times must be non-empty")
        if len(self.times) != len(self.zero_rates):
            raise ValueError("times and zero_rates length must match")

        if any(time < 0.0 for time in self.times):
            raise ValueError("times must be >= 0")
        for i in range(1, len(self.times)):
            if self.times[i] <= self.times[i - 1]:
                raise ValueError("times must be strictly increasing")

        if t <= self.times[0]:
            rate = self.zero_rates[0]
            return math.exp(-rate * t)
        if t >= self.times[-1]:
            rate = self.zero_rates[-1]
            return math.exp(-rate * t)

        for i in range(1, len(self.times)):
            if t <= self.times[i]:
                t0 = self.times[i - 1]
                t1 = self.times[i]
                r0 = self.zero_rates[i - 1]
                r1 = self.zero_rates[i]
                weight = (t - t0) / (t1 - t0)
                rate = r0 + weight * (r1 - r0)
                return math.exp(-rate * t)

        raise ValueError("failed to interpolate zero rate")


@dataclass(frozen=True)
class BootstrappedZeroCurve:
    """Bootstrapped zero curve backed by discount factors."""

    times: Sequence[float]
    discount_factors: Sequence[float]

    def df(self, t: float) -> float:
        if t < 0.0:
            raise ValueError("t must be >= 0")
        if len(self.times) == 0:
            raise ValueError("times must be non-empty")
        if len(self.times) != len(self.discount_factors):
            raise ValueError("times and discount_factors length must match")

        if any(time < 0.0 for time in self.times):
            raise ValueError("times must be >= 0")
        for i in range(1, len(self.times)):
            if self.times[i] <= self.times[i - 1]:
                raise ValueError("times must be strictly increasing")

        if t <= self.times[0]:
            return float(self.discount_factors[0])
        if t >= self.times[-1]:
            return float(self.discount_factors[-1])

        for i in range(1, len(self.times)):
            if t <= self.times[i]:
                t0 = self.times[i - 1]
                t1 = self.times[i]
                df0 = self.discount_factors[i - 1]
                df1 = self.discount_factors[i]
                if df0 <= 0.0 or df1 <= 0.0:
                    raise ValueError("discount_factors must be > 0")
                log_df0 = math.log(df0)
                log_df1 = math.log(df1)
                weight = (t - t0) / (t1 - t0)
                log_df = log_df0 + weight * (log_df1 - log_df0)
                return math.exp(log_df)

        raise ValueError("failed to interpolate discount factor")

    @classmethod
    def from_instruments(cls, instruments: Sequence[object]) -> "BootstrappedZeroCurve":
        """Placeholder for bootstrapping from market instruments."""
        raise NotImplementedError("bootstrap implementation not yet provided")

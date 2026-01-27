"""Volatility surface helpers for FX GK examples."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol, Sequence


class VolSurface(Protocol):
    """Interface for an implied volatility surface."""

    def vol(self, t: float, k: float) -> float:
        ...


@dataclass
class BilinearVolSurface(VolSurface):
    """Minimal bilinear vol surface with flat extrapolation."""

    tenors: Sequence[float]  # ascending
    strikes: Sequence[float]  # ascending
    vols: Dict[tuple[float, float], float]  # keyed by (T, K)

    def vol(self, t: float, k: float) -> float:
        # Clamp to grid bounds for extrapolation
        T = min(max(t, self.tenors[0]), self.tenors[-1])
        K = min(max(k, self.strikes[0]), self.strikes[-1])

        # Locate surrounding tenors
        t_lo, t_hi = self._bracket(self.tenors, T)
        k_lo, k_hi = self._bracket(self.strikes, K)

        if t_lo == t_hi and k_lo == k_hi:
            return self.vols[(t_lo, k_lo)]

        # Bilinear interpolation
        v_ll = self.vols[(t_lo, k_lo)]
        v_lh = self.vols[(t_lo, k_hi)]
        v_hl = self.vols[(t_hi, k_lo)]
        v_hh = self.vols[(t_hi, k_hi)]

        wt_t = 0.0 if t_hi == t_lo else (T - t_lo) / (t_hi - t_lo)
        wt_k = 0.0 if k_hi == k_lo else (K - k_lo) / (k_hi - k_lo)

        v_lo = v_ll + (v_lh - v_ll) * wt_k
        v_hi = v_hl + (v_hh - v_hl) * wt_k
        return v_lo + (v_hi - v_lo) * wt_t

    @staticmethod
    def _bracket(grid: Sequence[float], x: float) -> tuple[float, float]:
        # assumes grid sorted
        if x <= grid[0]:
            return grid[0], grid[0]
        if x >= grid[-1]:
            return grid[-1], grid[-1]
        for i in range(len(grid) - 1):
            if grid[i] <= x <= grid[i + 1]:
                return grid[i], grid[i + 1]
        return grid[-1], grid[-1]  # fallback, should not hit

    # Optional visualization helper (3D surface)
    def plot(
        self,
        *,
        num_t: int = 30,
        num_k: int = 30,
        show: bool = True,
        save_path: str | None = None,
    ) -> None:
        """
        Plot the implied vol surface using matplotlib, if available.

        Parameters
        ----------
        num_t, num_k: grid resolution for plotting.
        show: whether to call ``plt.show()`` (set False in headless runs).
        save_path: if provided, saves the figure to this path.
        """

        try:
            import matplotlib.pyplot as plt
            from matplotlib import cm
            import numpy as np
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "matplotlib and numpy are required to plot the vol surface"
            ) from exc

        T_grid = np.linspace(self.tenors[0], self.tenors[-1], num_t)
        K_grid = np.linspace(self.strikes[0], self.strikes[-1], num_k)
        TT, KK = np.meshgrid(T_grid, K_grid, indexing="ij")
        vols = np.vectorize(lambda t, k: self.vol(float(t), float(k)))(TT, KK)

        fig = plt.figure(figsize=(8, 5))
        ax = fig.add_subplot(111, projection="3d")
        surf = ax.plot_surface(
            TT,
            KK,
            vols,
            cmap=cm.viridis,
            linewidth=0,
            antialiased=True,
            alpha=0.9,
        )
        ax.set_xlabel("Tenor (y)")
        ax.set_ylabel("Strike")
        ax.set_zlabel("Implied vol")
        fig.colorbar(surf, shrink=0.5, aspect=10, label="Vol")
        ax.set_title("Bilinear implied vol surface")

        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
        if show:
            plt.show()
        else:
            plt.close(fig)


class FlatVol(VolSurface):
    """Flat volatility surface returning a constant sigma."""

    def __init__(self, sigma: float) -> None:
        if sigma < 0.0:
            raise ValueError("sigma must be >= 0")
        self.sigma = float(sigma)

    def vol(self, t: float, k: float) -> float:  # pylint: disable=unused-argument
        return self.sigma


__all__ = ["VolSurface", "BilinearVolSurface", "FlatVol"]

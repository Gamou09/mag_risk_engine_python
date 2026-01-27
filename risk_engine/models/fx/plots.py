"""Matplotlib plotting helpers for FX vol smiles/surfaces."""

from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np

from .smile_interpolator import SmileInterpolator
from .vol_surface import VolSurface

__all__ = [
    "plot_smile_vol",
    "plot_smile_variance",
    "plot_surface_slices",
    "plot_surface_heatmap",
    "plot_quote_fit",
]


def plot_smile_vol(smile: SmileInterpolator, *, ax=None, k_range: tuple[float, float] = (-0.5, 0.5), num: int = 80):
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))
    ks = np.linspace(k_range[0], k_range[1], num)
    strikes = smile.forward * np.exp(ks)
    vols = [smile.vol_from_k(k) for k in ks]
    ax.plot(strikes, vols, label=f"T={smile.expiry:.3f}y")
    ax.set_xlabel("Strike")
    ax.set_ylabel("Vol")
    ax.legend()
    return ax


def plot_smile_variance(smile: SmileInterpolator, *, ax=None, k_range: tuple[float, float] = (-1.0, 1.0), num: int = 120):
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))
    ks = np.linspace(k_range[0], k_range[1], num)
    w = [smile.total_variance_from_k(k) for k in ks]
    ax.plot(ks, w, label=f"T={smile.expiry:.3f}y")
    ax.set_xlabel("log-moneyness k")
    ax.set_ylabel("Total variance w")
    ax.legend()
    return ax


def plot_surface_slices(surface: VolSurface, expiries: Sequence[float] | None = None, *, k_range=(-0.5, 0.5), num=80):
    if expiries is None:
        expiries = surface.expiries()
    _, ax = plt.subplots(figsize=(7, 4))
    for t in expiries:
        smile = surface.smile(t)
        ks = np.linspace(k_range[0], k_range[1], num)
        strikes = smile.forward * np.exp(ks)
        vols = [surface.vol(t, K) for K in strikes]
        ax.plot(strikes, vols, label=f"T={t:.3f}y")
    ax.set_xlabel("Strike")
    ax.set_ylabel("Vol")
    ax.legend()
    ax.set_title("Vol slices")
    return ax


def plot_surface_heatmap(surface: VolSurface, *, num_t: int = 30, num_k: int = 40, k_range=(-0.6, 0.6)):
    T_grid = np.linspace(surface.expiries()[0], surface.expiries()[-1], num_t)
    F_ref = surface.smile(surface.expiries()[len(surface.expiries()) // 2]).forward
    ks = np.linspace(k_range[0], k_range[1], num_k)
    strikes = F_ref * np.exp(ks)
    vols = np.zeros((num_t, num_k))
    for i, t in enumerate(T_grid):
        for j, K in enumerate(strikes):
            vols[i, j] = surface.vol(t, K)
    fig, ax = plt.subplots(figsize=(7, 4))
    im = ax.imshow(
        vols,
        origin="lower",
        aspect="auto",
        extent=[strikes[0], strikes[-1], T_grid[0], T_grid[-1]],
        cmap="viridis",
    )
    ax.set_xlabel("Strike")
    ax.set_ylabel("T (y)")
    ax.set_title("Vol heatmap")
    fig.colorbar(im, ax=ax, label="Vol")
    return ax


def plot_quote_fit(errors: dict, *, ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 3))
    keys = list(errors.keys())
    vals = [errors[k] for k in keys]
    ax.bar(range(len(keys)), vals)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(keys, rotation=45, ha="right")
    ax.set_ylabel("Abs error")
    ax.set_title("Quote reproduction errors")
    return ax


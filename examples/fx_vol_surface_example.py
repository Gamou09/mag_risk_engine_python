"""FX implied vol surface construction and diagnostics example."""

from __future__ import annotations

import matplotlib.pyplot as plt

import sys
import pathlib

# Ensure project root is on sys.path when running this file directly.
# This makes `python examples/fx_vol_surface_example.py` behave like
# `python -m examples.fx_vol_surface_example` by adding the repo root.
project_root = pathlib.Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from risk_engine.models.fx.examples import build_example_surfaces
from risk_engine.models.fx.plots import (
    plot_quote_fit,
    plot_smile_variance,
    plot_smile_vol,
    plot_surface_heatmap,
    plot_surface_slices,
)
def main() -> None:
    surfaces = build_example_surfaces()
    for pair, surface, slices, report_text, report in surfaces:
        print("=" * 80)
        print(pair)
        for ms in slices:
            print("  ", ms.describe())
        print(report_text)

        # plotting per pair
        smile0 = surface.smile(slices[0].expiry)
        plot_smile_vol(smile0)
        plot_smile_variance(smile0)
        plot_surface_slices(surface)
        plot_surface_heatmap(surface)
        if report.metrics.get("quote_repro_errors"):
            plot_quote_fit(report.metrics["quote_repro_errors"])
        plt.suptitle(f"{pair} diagnostics", y=1.02)
        plt.show()


if __name__ == "__main__":
    main()

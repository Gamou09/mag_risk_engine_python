"""Example: pricing FX options on a simple implied-vol surface.

We build a tiny bilinear vol surface from fictitious data (tenors in years,
strikes in absolute FX terms) and price a call/put with the Garman–Kohlhagen
helpers. Outside the quoted grid we flat-extrapolate.
"""

from __future__ import annotations

import os
from pathlib import Path

from risk_engine.models.implementations.fx_gk import (
    FXEuropeanOption,
    FlatDiscountCurve,
    gk_greeks,
    gk_implied_vol,
    gk_price,
)
from risk_engine.models.curves_surfaces.vol_surfaces import BilinearVolSurface


def main() -> None:
    spot = 1.10
    notional = 1_000_000.0  # USD (domestic)
    r_dom = 0.035
    r_for = 0.012
    dom_curve = FlatDiscountCurve(r_dom)
    for_curve = FlatDiscountCurve(r_for)

    # Fictitious vol quotes (tenor, strike) -> sigma
    tenors = [0.25, 0.5, 1.0]  # years
    strikes = [1.00, 1.10, 1.20]
    vols = {
        (0.25, 1.00): 0.155,
        (0.25, 1.10): 0.140,
        (0.25, 1.20): 0.135,
        (0.50, 1.00): 0.150,
        (0.50, 1.10): 0.138,
        (0.50, 1.20): 0.133,
        (1.00, 1.00): 0.148,
        (1.00, 1.10): 0.136,
        (1.00, 1.20): 0.130,
    }
    surface = BilinearVolSurface(tenors, strikes, vols)

    T = 0.75
    K = 1.12
    underlying = "EURUSD"
    call = FXEuropeanOption("C", K, T, notional, direction=1, underlying=underlying)
    put = FXEuropeanOption("P", K, T, notional, direction=1, underlying=underlying)

    call_pv = gk_price(call, spot, dom_curve, for_curve, surface)
    put_pv = gk_price(put, spot, dom_curve, for_curve, surface)
    call_g = gk_greeks(call, spot, dom_curve, for_curve, surface)

    df_d = dom_curve.df(T)
    df_f = for_curve.df(T)
    parity_rhs = spot * df_f * notional - K * df_d * notional

    print("=== FX vol-surface example (GK) ===")
    print(f"Underlying: {underlying} | foreign={underlying[:3]} | domestic={underlying[3:]}")
    print(f"Spot={spot:.6f}, Strike={K:.6f}, T={T:.3f}y, Notional={notional:,.0f}")
    print("Surface nodes (sigma):")
    for t in tenors:
        row = [f"{surface.vol(t, k):.3%}" for k in strikes]
        print(f"  T={t:.2f} : {row}")
    print()
    print(f"Call PV: {call_pv:,.2f}")
    print(f"Put  PV: {put_pv:,.2f}")
    print(f"Put–call parity (C-P vs spot*DFf - K*DFd): {(call_pv - put_pv):,.2f} vs {parity_rhs:,.2f}")
    print(
        f"Call Greeks: delta={call_g['delta_spot']:,.2f}, "
        f"gamma={call_g['gamma_spot']:,.6f}, vega={call_g['vega']:,.2f}"
    )

    # Show implied vol recovered from the priced call (should be close to the interpolated sigma)
    imp_vol = gk_implied_vol(call, spot, call_pv, dom_curve, for_curve, vol_lower=0.01, vol_upper=0.5)
    interp_vol = surface.vol(T, K)
    print(f"\nInterpolated sigma: {interp_vol:.3%}")
    print(f"Implied sigma from price: {imp_vol:.3%}")

    # Optional: plot the surface (headless-safe)
    try:
        out_path = Path(__file__).with_name("fx_vol_surface.png")
        mpl_dir = Path(__file__).with_name(".mplconfig")
        cache_dir = Path(__file__).with_name(".cache")
        os.environ.setdefault("MPLCONFIGDIR", str(mpl_dir))
        os.environ.setdefault("XDG_CACHE_HOME", str(cache_dir))
        mpl_dir.mkdir(exist_ok=True)
        cache_dir.mkdir(exist_ok=True)
        surface.plot(show=False, save_path=str(out_path))
        print(f"\nSurface plot saved to {out_path}")
    except Exception as exc:  # pragma: no cover - plotting optional
        print(f"\nSkipping surface plot (missing optional deps?): {exc}")


if __name__ == "__main__":
    main()

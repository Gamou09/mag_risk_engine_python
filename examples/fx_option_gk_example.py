"""Minimal Garman–Kohlhagen FX option pricing example.

Run with: ``python examples/fx_option_gk_example.py``
Prints PV and Greeks (domestic currency) for a call/put pair, and checks
put–call parity against the forward/discount factors.
"""

from risk_engine.models.implementations.fx_gk import (
    FXEuropeanOption,
    FlatDiscountCurve,
    FlatVol,
    gk_greeks,
    gk_implied_vol,
    gk_price,
)


def main() -> None:
    # Market inputs
    spot = 1.0850  # USD per EUR
    T = 0.75  # 9 months, in year fraction
    sigma = 0.14
    r_dom = 0.032  # domestic (USD) cont. comp.
    r_for = 0.012  # foreign (EUR) cont. comp.

    dom_curve = FlatDiscountCurve(r_dom)
    for_curve = FlatDiscountCurve(r_for)
    vol_surface = FlatVol(sigma)

    strike = 1.10
    notional = 1_000_000.0  # domestic payout

    underlying = "EURUSD"
    base_ccy, quote_ccy = underlying[:3], underlying[3:]  # base=foreign, quote=domestic

    call = FXEuropeanOption("C", strike, T, notional, direction=1, underlying=underlying)
    put = FXEuropeanOption("P", strike, T, notional, direction=1, underlying=underlying)

    call_pv = gk_price(call, spot, dom_curve, for_curve, vol_surface)
    put_pv = gk_price(put, spot, dom_curve, for_curve, vol_surface)
    call_g = gk_greeks(call, spot, dom_curve, for_curve, vol_surface)
    put_g = gk_greeks(put, spot, dom_curve, for_curve, vol_surface)

    print("=== FX option GK example ===")
    print(f"Underlying: {underlying} | foreign={base_ccy} | domestic={quote_ccy}")
    print(f"Spot: {spot:.6f} | Strike: {strike:.6f} | T: {T:.3f}y | sigma: {sigma:.3%}")
    print(f"Domestic rate: {r_dom:.3%}, Foreign rate: {r_for:.3%}")
    print(f"Notional (domestic): {notional:,.0f}")
    print()
    print(f"Call PV: {call_pv:,.2f}")
    print(f"Put  PV: {put_pv:,.2f}")
    print()
    print("Call greeks (domestic numeraire):")
    print(
        f"  delta={call_g['delta_spot']:,.2f}, gamma={call_g['gamma_spot']:,.6f},"
        f" vega={call_g['vega']:,.2f}"
    )
    print("Put greeks (domestic numeraire):")
    print(
        f"  delta={put_g['delta_spot']:,.2f}, gamma={put_g['gamma_spot']:,.6f},"
        f" vega={put_g['vega']:,.2f}"
    )

    # Parity check: C - P = DFf*Spot*Notional - DFd*K*Notional
    df_d = dom_curve.df(T)
    df_f = for_curve.df(T)
    parity_rhs = spot * df_f * notional - strike * df_d * notional
    print()
    print("Put–call parity check:")
    print(f"  C - P        : {call_pv - put_pv:,.2f}")
    print(f"  Spot*DFf*N - K*DFd*N : {parity_rhs:,.2f}")

    # Implied vol inversion sanity check (using the call)
    imp_vol = gk_implied_vol(
        call, spot, call_pv, dom_curve, for_curve, vol_lower=1e-4, vol_upper=2.0
    )
    print()
    print(f"Implied vol from call PV: {imp_vol:.4%}")


if __name__ == "__main__":
    main()

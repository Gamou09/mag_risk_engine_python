from risk_engine.market.curve_registry import default_curve_registry
from risk_engine.market.ids import CurveId
from risk_engine.market.state import MarketState
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.bootstrap import default_registry
from risk_engine.instruments.assets.instruments_fx import PricingFXSwap


def main() -> None:
    pair = "EURUSD"
    usd_disc = CurveId("OIS_USD_3M")

    state = MarketState(
        factors={
            # Discount factors (quote currency = USD)
            "DF.OIS_USD_3M.1M": 0.9990,
            "DF.OIS_USD_3M.6M": 0.9845,
            # Current forwards (outright)
            "FWD.EURUSD.1M": 1.0850,
            "FWD.EURUSD.6M": 1.1000,
            # Parity ingredients (spot + forward points) used for validation/fallback
            "SPOT.EURUSD": 1.0820,
            "FWDPTS.EURUSD.1M": 0.0030,
            "FWDPTS.EURUSD.6M": 0.0180,
        },
        discount_curves={"USD": usd_disc},
        registry=default_curve_registry(),
    )

    ctx = PricingContext(market=state, method="analytic")
    reg = default_registry()

    swap = PricingFXSwap(
        pair=pair,
        notional=5_000_000,
        near_maturity="1M",
        far_maturity="6M",
        near_forward=1.0880,  # contract terms
        far_forward=1.1050,
        direction="buy_base",
    )

    res = reg.price(swap, ctx)
    print(f"FX Swap PV: {res.pv.amount:,.2f} {res.pv.currency}")
    print("Greeks:")
    for k, v in res.greeks.items():
        print(f"  {k}: {v:,.2f}")


if __name__ == "__main__":
    main()

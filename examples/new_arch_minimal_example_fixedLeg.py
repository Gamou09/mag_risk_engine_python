from risk_engine.market.curve_registry import default_curve_registry
from risk_engine.market.ids import CurveId
from risk_engine.market.state import MarketState
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.bootstrap import default_registry
from risk_engine.instruments.asset.rates.fixed_leg import FixedLeg

def main() -> None:
    curve = CurveId("OIS_USD_3M")
    state = MarketState(
        factors={
            "DF.OIS_USD_3M.1Y": 0.97,
            "DF.OIS_USD_3M.2Y": 0.94,
            "DF.OIS_USD_3M.3Y": 0.91,
        },
        discount_curves={"USD": curve},
        registry=default_curve_registry(),
    )

    ctx = PricingContext(market=state, method="analytic")
    reg = default_registry()

    leg = FixedLeg(
        ccy="USD",
        notional=1_000_000,
        fixed_rate=0.03,
        pay_times=("1Y","2Y","3Y"),
        accrual_factors=(1.0,1.0,1.0),
    )

    res = reg.price(leg, ctx)
    print(res.pv, res.greeks)


if __name__ == "__main__":
    main()

from risk_engine.market.state import MarketState
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing import default_registry
from risk_engine.instruments.asset.rates.fixed_leg import FixedLeg

def main() -> None:
    state = MarketState(factors={
    "DF.USD.USD.OIS.1Y": 0.97,
    "DF.USD.USD.OIS.2Y": 0.94,
    "DF.USD.USD.OIS.3Y": 0.91,
    })

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

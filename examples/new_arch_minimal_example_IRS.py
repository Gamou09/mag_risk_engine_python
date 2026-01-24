from risk_engine.market.curve_registry import default_curve_registry
from risk_engine.market.ids import CurveId
from risk_engine.market.state import MarketState
from risk_engine.pricing.context import PricingContext
from risk_engine.pricing.bootstrap import default_registry
from risk_engine.instruments.assets.instruments_rates import PricingInterestRateSwap as InterestRateSwap

curve = CurveId("OIS_USD_3M")

state = MarketState(
    factors={
        # Discount factors
        "DF.OIS_USD_3M.6M": 0.985,
        "DF.OIS_USD_3M.1Y": 0.970,
        "DF.OIS_USD_3M.18M": 0.955,
        "DF.OIS_USD_3M.2Y": 0.940,
        # Forwards (toy)
        "FWD.OIS_USD_3M.6M": 0.028,
        "FWD.OIS_USD_3M.1Y": 0.029,
        "FWD.OIS_USD_3M.18M": 0.030,
        "FWD.OIS_USD_3M.2Y": 0.031,
    },
    discount_curves={"USD": curve},
    registry=default_curve_registry(),
)

ctx = PricingContext(market=state, method="analytic")
reg = default_registry()

irs = InterestRateSwap(
    direction="pay_fixed",
    ccy="USD",
    notional=1_000_000,
    fixed_rate=0.030,
    float_curve=curve,
    pay_times=("6M", "1Y", "18M", "2Y"),
    accrual_factors=(0.5, 0.5, 0.5, 0.5),
)

res = reg.price(irs, ctx)
print("PV:", res.pv)
print("Greeks keys:", list(res.greeks.keys())[:5], "...")
print(res.greeks)

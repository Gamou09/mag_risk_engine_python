"""Example usage of cashflow PV utilities."""

from risk_engine.models.curves import (
    BootstrappedZeroCurve,
    FlatZeroCurve,
    PiecewiseZeroCurve,
)
from risk_engine.models.pricing import Cashflow, CashflowPVModel, present_value


def main() -> None:
    cashflows = [
        Cashflow(time=0.5, amount=5.0),
        Cashflow(time=1.0, amount=5.0),
        Cashflow(time=1.5, amount=5.0),
        Cashflow(time=2.0, amount=105.0),
    ]

    pv = present_value(cashflows, rate=0.03)
    model = CashflowPVModel(rate=0.03)
    model_pv = model.price(cashflows)
    curve = FlatZeroCurve(rate=0.03)
    curve_pv = present_value(cashflows, discount_curve=curve.df)
    curve_model_pv = CashflowPVModel(discount_curve=curve.df).price(cashflows)

    piecewise_curve = PiecewiseZeroCurve(
        times=[0.5, 1.0, 2.0, 3.0],
        zero_rates=[0.025, 0.03, 0.0325, 0.035],
    )
    piecewise_pv = present_value(cashflows, discount_curve=piecewise_curve.df)

    boot_curve = BootstrappedZeroCurve(
        times=[0.5, 1.0, 2.0, 3.0],
        discount_factors=[0.9876, 0.9705, 0.9418, 0.9142],
    )
    boot_pv = present_value(cashflows, discount_curve=boot_curve.df)

    print(f"present_value={pv:.4f}")
    print(f"model_price={model_pv:.4f}")
    print(f"curve_present_value={curve_pv:.4f}")
    print(f"curve_model_price={curve_model_pv:.4f}")
    print(f"piecewise_curve_pv={piecewise_pv:.4f}")
    print(f"bootstrapped_curve_pv={boot_pv:.4f}")


if __name__ == "__main__":
    main()

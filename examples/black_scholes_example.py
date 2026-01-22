"""Example usage of the Black-Scholes pricing model."""

from risk_engine.models.pricing import BlackScholesModel, EuropeanOption


def main() -> None:
    call = EuropeanOption(
        spot=100.0,
        strike=105.0,
        maturity=1.0,
        rate=0.02,
        vol=0.25,
        option_type="call",
    )
    put = EuropeanOption(
        spot=100.0,
        strike=105.0,
        maturity=1.0,
        rate=0.02,
        vol=0.25,
        option_type="put",
    )
    model = BlackScholesModel()
    call_price = model.price(call)
    call_greeks = model.greeks(call)
    put_price = model.price(put)
    put_greeks = model.greeks(put)
    call_iv = model.implied_vol(call, target_price=call_price)
    put_iv = model.implied_vol(put, target_price=put_price)

    print(f"call_price={call_price:.4f}")
    if call_greeks is not None:
        print(
            "call_greeks="
            + ", ".join(f"{name}={value:.6f}" for name, value in call_greeks.items())
        )
    print(f"call_implied_vol={call_iv:.6f}")
    print(f"put_price={put_price:.4f}")
    print(f"put_implied_vol={put_iv:.6f}")
    print(f"input_vol={call.vol:.6f}")
    if put_greeks is not None:
        print(
            "put_greeks="
            + ", ".join(f"{name}={value:.6f}" for name, value in put_greeks.items())
        )


if __name__ == "__main__":
    main()

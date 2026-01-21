import numpy as np

from risk_engine.metrics.var import historical_var


def main() -> None:
    returns = np.array([0.01, -0.02, 0.015, -0.005, 0.0, 0.02, -0.01])
    result = historical_var(returns, confidence=0.95, horizon=1)

    print("Historical VaR")
    print(f"confidence: {result.confidence:.2f}")
    print(f"horizon: {result.horizon}")
    print(f"quantile: {result.quantile:.6f}")
    print(f"VaR: {result.var:.6f}")


if __name__ == "__main__":
    main()

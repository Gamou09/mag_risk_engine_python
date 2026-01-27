import numpy as np

from risk_engine.metrics.var import parametric_var


def main() -> None:
    returns = np.array([0.012, -0.008, 0.005, 0.02, -0.01, 0.0, 0.006])
    result = parametric_var(returns, confidence=0.99, horizon=1)

    print("Parametric VaR (single series)")
    print(f"confidence: {result.confidence:.2f}")
    print(f"horizon: {result.horizon}")
    print(f"mean: {result.mean:.6f}")
    print(f"std: {result.std:.6f}")
    print(f"z: {result.z:.6f}")
    print(f"VaR: {result.var:.6f}")


if __name__ == "__main__":
    main()

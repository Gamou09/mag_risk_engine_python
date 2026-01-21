import numpy as np

from risk_engine.metrics.var import parametric_portfolio_var


def main() -> None:
    weights = np.array([0.6, 0.4])
    covariance = np.array([[0.04, 0.01], [0.01, 0.09]])
    mean = np.array([0.001, 0.002])

    result = parametric_portfolio_var(
        weights, covariance, mean=mean, confidence=0.95, horizon=5
    )

    print("Parametric VaR (portfolio)")
    print(f"confidence: {result.confidence:.2f}")
    print(f"horizon: {result.horizon}")
    print(f"mean: {result.mean:.6f}")
    print(f"std: {result.std:.6f}")
    print(f"z: {result.z:.6f}")
    print(f"VaR: {result.var:.6f}")


if __name__ == "__main__":
    main()

import numpy as np

from risk_engine.metrics.var import monte_carlo_var


def main() -> None:
    returns = np.array([0.012, -0.008, 0.005, 0.02, -0.01, 0.0, 0.006])
    result = monte_carlo_var(
        returns, confidence=0.99, horizon=1, num_sims=20000, seed=42
    )

    print("Monte Carlo VaR (normal model)")
    print(f"confidence: {result.confidence:.2f}")
    print(f"horizon: {result.horizon}")
    print(f"mean: {result.mean:.6f}")
    print(f"std: {result.std:.6f}")
    print(f"num_sims: {result.num_sims}")
    print(f"seed: {result.seed}")
    print(f"VaR: {result.var:.6f}")


if __name__ == "__main__":
    main()

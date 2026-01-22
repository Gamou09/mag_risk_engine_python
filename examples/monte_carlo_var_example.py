import numpy as np

from risk_engine.metrics.var import monte_carlo_var


def main() -> None:
    returns = np.array([0.012, -0.008, 0.005, 0.02, -0.01, 0.0, 0.006])
    normal_result = monte_carlo_var(
        returns, confidence=0.99, horizon=1, num_sims=20000, seed=42, method="normal"
    )
    bootstrap_result = monte_carlo_var(
        returns, confidence=0.99, horizon=1, num_sims=20000, seed=42, method="bootstrap"
    )

    print("Monte Carlo VaR comparison (left tail)")
    print(f"confidence: {normal_result.confidence:.2f}")
    print(f"horizon: {normal_result.horizon}")
    print(f"num_sims: {normal_result.num_sims}")
    print(f"seed: {normal_result.seed}")
    print("")
    print("Normal model")
    print(f"mean: {normal_result.mean:.6f}")
    print(f"std: {normal_result.std:.6f}")
    print(f"VaR: {normal_result.var:.6f}")
    print("")
    print("Bootstrap")
    print(f"mean: {bootstrap_result.mean:.6f}")
    print(f"std: {bootstrap_result.std:.6f}")
    print(f"VaR: {bootstrap_result.var:.6f}")

    right_tail = monte_carlo_var(
        returns, confidence=0.99, horizon=1, num_sims=20000, seed=42, method="normal", tail="right"
    )
    print("")
    print("Monte Carlo VaR (right tail)")
    print(f"confidence: {right_tail.confidence:.2f}")
    print(f"horizon: {right_tail.horizon}")
    print(f"method: {right_tail.method}")
    print(f"VaR: {right_tail.var:.6f}")


if __name__ == "__main__":
    main()

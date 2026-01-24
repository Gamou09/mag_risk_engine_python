import numpy as np

from risk_engine.metrics.var import portfolio_var_from_returns


def main() -> None:
    asset_returns = np.array(
        [
            [0.01, -0.02],
            [0.02, 0.01],
            [-0.01, 0.0],
            [0.0, 0.02],
            [0.015, -0.005],
        ]
    )
    weights = np.array([0.6, 0.4])

    results = portfolio_var_from_returns(
        asset_returns,
        weights,
        method="historical",
        confidence=[0.9, 0.95],
        horizon=[1, 5],
    )

    print("Portfolio VaR from returns (historical)")
    for (confidence, horizon), result in results.items():
        print(
            f"confidence={confidence:.2f} "
            f"horizon={horizon} "
            f"var={result.var:.6f}"
        )

    right_tail = portfolio_var_from_returns(
        asset_returns,
        weights,
        method="historical",
        confidence=0.95,
        horizon=1,
        tail="right",
    )
    print("")
    print("Right-tail example")
    print(f"confidence={right_tail.confidence:.2f} horizon={right_tail.horizon} var={right_tail.var:.6f}")


if __name__ == "__main__":
    main()

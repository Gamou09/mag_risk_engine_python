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
    for result in results:
        print(
            f"confidence={result.confidence:.2f} "
            f"horizon={result.horizon} "
            f"var={result.var:.6f}"
        )


if __name__ == "__main__":
    main()

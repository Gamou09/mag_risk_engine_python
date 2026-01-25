# Risk Engine with Python

Modular quantitative risk engine for pricing simulation, exposure profiles, and risk metrics.

**PS:** This repository consolidates my learnings and serves as a sandbox for experimenting with new ideas (with the good help of my now favourite friend: codex ).  Feel free to leave suggestions, feedback, or other contributions 🙂

## Features

### Implemented
- Value-at-Risk: historical, parametric, and Monte Carlo flavours with portfolio aggregation from return series (`risk_engine/metrics/var.py`).
- Potential Future Exposure: scenario, analytic, and Monte Carlo profiles with netting and threshold support (`risk_engine/metrics/pfe.py`).
- Instruments, pricing, and market stack across FX, rates, credit, commodities, and equities (analytic models: discounting, Black-Scholes/Garman-Kohlhagen, swap PV; pricing registry and context wiring).
- Scenario and Monte Carlo utilities: GBM, Heston, Hull-White, and Vasicek path simulators plus stress/historical/shock scenario builders.
- Market data containers and curve/surface infrastructure with CSV/DB provider hooks.

### To implement next
- Capital-at-Risk metric (placeholder in `risk_engine/metrics/car.py`).
- Greeks/sensitivities and aggregation utilities (delta/vega/rho/etc. plus netting/allocation) currently stubbed in `metrics/sensitivities.py` and `risk/aggregation`.
- Monte Carlo and lattice pricing engines wired to instruments, including path-dependent payoffs and control variates.
- Reporting/export and explain outputs (tables, CSV/Parquet) to accompany risk runs.

## Running examples

Run examples from the repo root so the `risk_engine` package is on the import path.

```bash
. .venv/bin/activate
python -m examples.historical_var_example
python -m examples.parametric_var_example
python -m examples.monte_carlo_var_example
python -m examples.portfolio_parametric_var_example
python -m examples.scenario_pfe_single_position_example
python -m examples.scenario_pfe_three_positions_example
python -m examples.scenario_pfe_profile_example
python -m examples.monte_carlo_pfe_profile_example
python -m examples.monte_carlo_pfe_profile_visual_example
python -m examples.analytic_pfe_profile_example
```

Alternative if you prefer running scripts directly:

```bash
PYTHONPATH=. python examples/historical_var_example.py
```

## Repository Structure

```text
mag_risk_engine_python/
├── risk_engine/
│   ├── common/
│   ├── config/
│   ├── core/
│   ├── instruments/
│   │   └── assets/
│   ├── market/
│   │   └── providers/
│   ├── metrics/
│   ├── models/
│   │   ├── calibration/
│   │   ├── curves_surfaces/
│   │   ├── implementations/
│   │   ├── pricing/
│   │   └── stochastic/
│   ├── pricing/
│   │   ├── engines/
│   │   ├── pricers/
│   │   └── sensitivities/
│   ├── reporting/
│   ├── risk/
│   │   ├── aggregation/
│   │   └── measures/
│   ├── scenarios/
│   │   └── simulation/
│   ├── simulation/
│   ├── utils/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── regression/
├── examples/
│   └── old_architecture_example/
├── tests/
├── docs/
├── notebooks/
├── pyproject.toml
├── README.md
├── LICENSE
└── mag_risk_engine_python.egg-info
```

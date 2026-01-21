# Risk Engine with Python

Modular quantitative risk engine for pricing simulation, exposure profiles, and risk metrics.

**PS:** This repository consolidates my learnings and serves as a sandbox for experimenting with new ideas.  Feel free to leave suggestions, feedback, or other contributions 🙂

## Features to implement
- Modular framework for quantitative risk metrics (VaR, PFE, CaR)
- Monte Carlo and historical simulation engines
- Portfolio-level risk aggregation
- Abstractions supporting equities, fixed income, energy, and derivatives
- Extensible design for additional asset classes
- Suitable for both research and production environments

## Running examples

Run examples from the repo root so the `risk_engine` package is on the import path.

```bash
. .venv/bin/activate
python -m examples.historical_var_example
python -m examples.parametric_var_example
python -m examples.monte_carlo_var_example
python -m examples.portfolio_parametric_var_example
```

Alternative if you prefer running scripts directly:

```bash
PYTHONPATH=. python examples/historical_var_example.py
```

## Suggested Repository Structure

```text
mag_risk_engine_python/
│
├── risk_engine/
│   ├── __init__.py
│   ├── config/
│   │
│   ├── core/
│   │   ├── engine.py
│   │   ├── portfolio.py
│   │   ├── instruments.py
│   │
│   ├── models/
│   │   ├── stochastic/
│   │   ├── pricing/
│   │   └── curves/
│   │
│   ├── metrics/
│   │   ├── var.py
│   │   ├── pfe.py
│   │   ├── car.py
│   │   └── sensitivities.py
│   │
│   ├── simulation/
│   │   ├── monte_carlo.py
│   │   └── scenarios.py
│   │
│   └── utils/
│
├── tests/
├── examples/
├── notebooks/
├── docs/
│
├── pyproject.toml
├── README.md
├── LICENSE
└── CONTRIBUTING.md

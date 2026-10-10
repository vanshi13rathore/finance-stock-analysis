# 🏗️ Architecture

How the project fits together.

## Structure

```text
finance_project.ipynb      # narrative analysis (imports src/*)
app.py                     # Streamlit dashboard (imports src/*)
scripts/run_analysis.py    # headless pipeline (imports src/*)
src/
  config.py                # constants: tickers, dates, params, paths
  data.py                  # download → extract → clean (or synthesize)
  metrics.py               # pure functions: returns → risk tables
  plots.py                 # pure-ish: tables → matplotlib figures
  portfolio.py             # Monte Carlo portfolios
tests/test_metrics.py      # 23 unit tests over metrics/portfolio/data
data/                      # summary.csv, correlation.csv (+ git-ignored cache)
images/                    # generated chart PNGs
docs/                      # you are here
```

Design rules:

1. **All interfaces share `src/`** — the notebook, CLI, and dashboard never
   reimplement logic; they only wire inputs to outputs.
2. **`metrics` and `portfolio` are pure** — no network, no plotting, no global
   state — so they're trivially testable (`pytest tests/` needs no internet).
3. **Config lives in one place** — `src/config.py` is imported everywhere;
   nothing hard-codes tickers, dates, or window sizes.
4. **Plots are functions, not scripts** — each returns `(fig, ax)` and
   optionally saves, so the same chart renders inline, to PNG, or in Streamlit.

## Data flow

```mermaid
flowchart LR
    subgraph sources [Data sources]
        Y[Yahoo Finance]
        C[(CSV cache)]
        S[Synthetic generator]
    end
    L[data.load_prices] --> CL[data.clean_prices]
    Y --> L
    C --> L
    S --> L
    CL --> close[(close prices)]
    close --> R[metrics.daily_returns]
    R --> M[metrics.summary_table]
    R --> CORR[metrics.correlation_matrix]
    R --> PF[portfolio.random_portfolios]
    close --> DD[metrics.drawdown_series]
    M --> P1[plots.*]
    CORR --> P1
    PF --> P1
    DD --> P1
    R --> P1
    close --> P1
    P1 --> OUT([notebook / PNGs / dashboard])
    M --> CSV[(summary.csv)]
    CORR --> CSV2[(correlation.csv)]
```

## Dependency graph

```text
config ─┬─▶ data ─────▶ metrics ─┬─▶ plots
        │                         │
        └─▶ portfolio ◀───────────┘
```

- `config` depends on nothing (stdlib only).
- `data` needs `config` (+ `pandas`/`numpy`). `yfinance` is a **lazy import**
  inside `download_prices()`, so merely importing `src.data` never touches the
  network.
- `metrics` and `portfolio` need only `pandas`/`numpy`.
- `plots` needs `matplotlib`/`seaborn` (+ `pandas` for the crisis shading).

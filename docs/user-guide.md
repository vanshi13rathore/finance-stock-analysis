# 📖 User Guide

This guide walks through the three ways to use the project: the **notebook**,
the **dashboard**, and `src/` **as a library**. (For the headless pipeline, see
the [CLI Reference](cli-reference.md).)

---

## 1. The notebook (`finance_project.ipynb`)

The notebook is the narrative version of the analysis — the best place to
understand *what* is computed and *why*.

### Section map

| # | Section | What it covers |
|---|---------|----------------|
| 0 | Setup | Imports, global plot style, tickers/period |
| 1 | Data collection | `load_prices()` + data-overview table |
| 2 | Price exploration | Raw closing-price trends, 2008 crisis band |
| 3 | Returns | Daily, normalized (base 100), cumulative (growth of $1) |
| 4 | Risk analysis | Summary table, best/worst days, rolling vol, drawdown, risk-vs-return |
| 5 | Correlation & distributions | Heatmap, histograms with ±3σ guides, sampled scatter matrix |
| 6 | Trend | BAC with 30/50-day moving averages |
| 7 | Portfolio simulation | Monte Carlo efficient frontier, max-Sharpe weights |
| 8 | Key findings | Auto-derived bullet findings (never goes stale) |

### Tips

- **Run top to bottom.** Later cells depend on `close`, `returns`, `summary`,
  and `corr` created earlier.
- The notebook prints its **data source** (`yahoo` / `cache` / `synthetic`).
  Numbers in section 8 are derived from the data, so they update automatically
  if the source changes.
- To analyze **different tickers or dates**, edit the `load_prices(...)` call
  (or `src/config.py`) and re-run all cells.

---

## 2. The dashboard (`app.py`)

```bash
pip install -r requirements-dev.txt
streamlit run app.py
```

### Sidebar controls

| Control | Effect |
|---------|--------|
| Banks (multi-select) | Which tickers to analyze |
| Start / End dates | Sample period |
| Risk-free rate | Used for Sharpe/Sortino and the frontier |
| Short / Long MA windows | Moving-average chart |
| Rolling-vol window | Rolling-volatility chart |
| Use synthetic demo data | Force offline mode (ignores Yahoo/cache) |

### Tabs

1. **📊 Prices** — price history, normalized performance, growth of $1, moving averages
2. **⚠️ Risk** — summary table, risk-vs-return, drawdown, rolling volatility, distributions, best/worst days
3. **🔗 Correlations** — heatmap + sortable correlation table
4. **💼 Portfolio** — efficient frontier with adjustable simulation count, max-Sharpe and min-vol allocations

> The caption under the title always shows the active data source and date range.

---

## 3. Using `src/` as a library

Every interface above is a thin wrapper around `src/`. You can drive the same
code from your own scripts:

```python
from src import config, data, metrics, plots, portfolio

# Load (cache → Yahoo → synthetic fallback)
close, source = data.load_prices(
    config.BANKS, config.START_DATE, config.END_DATE,
    cache_path=config.CACHE_FILE,
)
print("source:", source)

# Analyze
returns = metrics.daily_returns(close)
summary = metrics.summary_table(close, returns)
print(summary.round(4))

# Visualize (returns fig/ax; pass savepath= to write a PNG)
plots.setup_style()
fig, ax = plots.plot_correlation_heatmap(metrics.correlation_matrix(returns))

# Simulate portfolios
sims, best = portfolio.random_portfolios(returns, n_portfolios=5_000)
print(best.max_sharpe_weights.round(4))
```

### Changing defaults

All shared constants live in `src/config.py` (tickers, dates, risk-free rate,
window sizes, seeds, paths). Import them instead of hard-coding values:

```python
from src import config
print(config.BANKS, config.RISK_FREE_RATE, config.MA_SHORT_WINDOW)
```

See the [API Reference](api-reference.md) for every public function, and
[Methodology](methodology.md) for what each metric means.

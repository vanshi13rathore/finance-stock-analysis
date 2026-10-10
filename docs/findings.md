# 📊 Findings

Key results from the analysis, how to interpret them, and how to reproduce them.

## Headline results (live Yahoo data, 2006–2016)

| # | Finding | Where to see it |
|---|---------|-----------------|
| 1 | **Citigroup (C)** had the **highest volatility** — the crisis hit it hardest | Summary table, `risk_return.png` |
| 2 | **Goldman Sachs (GS)** was the **most stable** (lowest volatility) | Summary table, `risk_return.png` |
| 3 | **BAC–WFC** had the **strongest positive correlation** | `correlation_heatmap.png` |
| 4 | **Volatility spiked in 2008–2009** across all banks | `rolling_volatility.png`, `drawdown.png` |
| 5 | Banks are **strongly correlated (~0.6–0.9)**, limiting within-sector diversification | Heatmap + frontier |

## How to read the charts

- **Risk vs. return** (`risk_return.png`) — ideal assets sit top-left (high
  return, low risk). Bubble size ∝ Sharpe ratio: bigger means better
  risk-adjusted compensation.
- **Rolling volatility** (`rolling_volatility.png`) — the 2008–2009 surge
  dwarfs everything else; post-2012 volatility stays structurally lower.
- **Drawdown** (`drawdown.png`) — depth below previous peak. C and BAC fell
  furthest and took longest to surface.
- **Return distributions** (`return_distributions.png`) — roughly bell-shaped
  but with **fat tails**: ±3σ days occur far more often than a normal model
  predicts (that's why we use historical, not parametric, VaR).
- **Efficient frontier** (`efficient_frontier.png`) — each dot is a random
  long-only mix; ★ marks max-Sharpe and min-volatility. Because correlations
  are high, the frontier is relatively flat: mixing banks cuts volatility only
  modestly versus holding the best single bank.

## Reproducing these results

```bash
# Live data (requires Yahoo access)
python scripts/run_analysis.py

# Offline demo (deterministic seed 99 — same charts on every machine)
python scripts/run_analysis.py --synthetic --no-cache
```

The notebook's section 8 derives the same bullets from whatever data is loaded,
and `data/summary.csv` + `data/correlation.csv` contain the exact numbers.

> **Note:** the committed `images/` were rendered from synthetic demo data in
> an offline environment, so exact values (e.g. the top-correlated pair) differ
> slightly from live-data results. The headline patterns (1, 2, 4, 5) hold in
> both. Re-run with internet access to regenerate live-data charts.

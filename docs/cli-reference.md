# 🖥️ CLI Reference (`scripts/run_analysis.py`)

The CLI runs the full analysis headless: download → metrics → portfolios →
charts + CSVs + printed findings. Ideal for reproducing results or automation.

## Usage

```bash
python scripts/run_analysis.py [OPTIONS]
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--tickers T [T ...]` | `BAC C GS JPM MS WFC` | Tickers to analyze (any Yahoo tickers work) |
| `--start START` | `2006-01-01` | Sample start date (`YYYY-MM-DD`) |
| `--end END` | `2016-01-01` | Sample end date (`YYYY-MM-DD`) |
| `--risk-free RF` | `0.02` | Annual risk-free rate for Sharpe/Sortino |
| `--images-dir DIR` | `images/` | Where to write chart PNGs |
| `--data-dir DIR` | `data/` | Where to write `summary.csv` / `correlation.csv` |
| `--synthetic` | off | Skip Yahoo/cache; use reproducible demo data |
| `--no-cache` | off | Ignore the cached CSV download (re-download or fallback) |
| `--portfolios N` | `5000` | Random portfolios for the efficient frontier |

## Examples

```bash
# Standard live run (uses cache if present, else downloads)
python scripts/run_analysis.py

# Fully offline, reproducible demo
python scripts/run_analysis.py --synthetic --no-cache

# Custom universe and period, no cache
python scripts/run_analysis.py --tickers AAPL MSFT NVDA \
    --start 2020-01-01 --end 2024-01-01 --no-cache

# Custom risk-free rate and output folders, larger simulation
python scripts/run_analysis.py --risk-free 0.04 \
    --images-dir out/charts --data-dir out/data --portfolios 20000
```

## Outputs

### Terminal

1. Data source, tickers, and date range
2. Risk/return summary table (sorted by Sharpe)
3. Max-Sharpe and min-volatility allocations with return/vol/Sharpe
4. Key findings (riskiest/calmest bank, strongest correlation)

### Files

| File | Contents |
|------|----------|
| `<data-dir>/summary.csv` | Per-ticker risk/return metrics |
| `<data-dir>/correlation.csv` | Return correlation matrix |
| `<data-dir>/bank_prices.csv` | Raw Yahoo download cache *(git-ignored)* |
| `<images-dir>/*.png` | 10 charts (see table below) |

| Chart file | Description |
|------------|-------------|
| `price_history.png` | Closing-price trends |
| `normalized.png` | Rebased performance (base 100) |
| `cumulative_returns.png` | Growth of $1 |
| `correlation_heatmap.png` | Return correlations |
| `return_distributions.png` | Histograms with KDE and ±3σ guides |
| `bac_moving_averages.png` | BAC with 30/50-day MAs |
| `rolling_volatility.png` | 30-day rolling volatility (annualized) |
| `drawdown.png` | Drawdown from peak |
| `risk_return.png` | Risk-vs-return scatter (size ∝ Sharpe) |
| `efficient_frontier.png` | Monte Carlo frontier |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success (including synthetic fallback — check "Data source") |
| non-zero | Traceback printed; see [Troubleshooting](troubleshooting.md) |

> **Note:** when Yahoo is unreachable, `yfinance` prints SSL/connection noise to
> stderr before the fallback kicks in. The analysis itself still succeeds —
> stdout starts with `Data source : synthetic`.

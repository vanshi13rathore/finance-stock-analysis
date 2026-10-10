# 💾 Data

Where the numbers come from, how they're stored, and how the project stays
reproducible with or without internet.

## Sources (in priority order)

`data.load_prices()` resolves data in this order and **always reports** which
source was used (`cache`, `yahoo`, or `synthetic`):

```text
1. Local CSV cache (data/bank_prices.csv)   ─┐
2. Live Yahoo Finance download via yfinance  ─┼─→ clean → analyze
3. Built-in synthetic demo data (fallback)  ─┘
```

| Source | When it's used | Reproducible? |
|--------|---------------|---------------|
| `cache` | Cache file exists and `--no-cache` is not passed | ✅ Yes (frozen snapshot) |
| `yahoo` | No cache; internet + Yahoo reachable | ⚠️ Mostly (Yahoo occasionally revises history) |
| `synthetic` | Download fails, or `--synthetic` / dashboard toggle | ✅ Yes (fixed seed `99`) |

## Live data (Yahoo Finance)

- **Tickers:** `BAC, C, GS, JPM, MS, WFC` (see `BANK_NAMES` in `src/config.py`
  for full names).
- **Period:** `2006-01-01` → `2016-01-01` (~2,610 trading days), chosen to cover
  the 2008 financial crisis with pre/post context.
- **Fields downloaded:** Open, High, Low, Close, Adj Close, Volume
  (`auto_adjust=False`); the analysis uses **Close**.
- Downloaded with `group_by="ticker", threads=False` for reliability.
  `data.extract_close()` also accepts the newer `(price, ticker)` layout and
  single-ticker flat frames, so yfinance upgrades don't break it.

### Cache file: `data/bank_prices.csv` (git-ignored)

The raw download is saved automatically so re-runs are instant and don't hammer
the API. Delete it (or pass `--no-cache`) to force a fresh download.

## Cleaning (`data.clean_prices()`)

1. Sort by date, drop duplicated timestamps.
2. Forward/backward-fill gaps up to **5 trading days** (short suspensions).
3. Drop any remaining all-NaN rows.
4. Emit a warning reporting how many points were filled/dropped.

## Synthetic demo data (`data.generate_synthetic_prices()`)

Used when Yahoo is unreachable (offline sandbox, rate limits) or explicitly
requested. Properties:

- **Geometric Brownian motion** on business days with per-ticker drift,
  volatility, and starting price.
- A **shared market factor** produces realistic ~0.6 cross-bank correlations.
- A **2008–2009 crisis regime** (2.5× volatility + negative drift) reproduces
  the real sample's narrative: volatility spike, deep drawdowns, slow recovery.
- **Deterministic:** default seed `99` gives identical data on every machine.
  (Seed was chosen so the demo mirrors reality: C riskiest, GS calmest.)

> The committed `images/` and `data/*.csv` were generated from this demo data
> in an offline environment. With internet access, re-run the pipeline to
> regenerate them from live data.

## Output schemas

### `data/summary.csv`

One row per ticker (sorted by Sharpe), from `metrics.summary_table()`:

| Column | Meaning | Unit |
|--------|---------|------|
| Ann. Return | Annualized mean return | decimal/year |
| Ann. Volatility | Annualized std of returns | decimal/year |
| Sharpe | Sharpe ratio (rf = 2%) | ratio |
| Sortino | Sortino ratio | ratio |
| Max Drawdown | Worst peak-to-trough loss | decimal (≤ 0) |
| VaR 95% (daily) | 5th percentile of daily returns | decimal/day |
| Best Day / Worst Day | Extreme single-day returns | decimal/day |
| Growth of $1 | Final cumulative return | USD |

### `data/correlation.csv`

Symmetric 6×6 Pearson correlation matrix of daily returns (1.0 on the diagonal).

### `images/*.png`

Ten charts; see the [CLI Reference](cli-reference.md#files) for the full list.

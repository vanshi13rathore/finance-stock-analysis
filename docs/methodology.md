# 📐 Methodology

How every number in this project is computed, and what it means. All
implementations live in `src/metrics.py` / `src/portfolio.py` (see
[API Reference](api-reference.md)); this page explains the *why*.

## Conventions

- **Prices** are daily *closing* prices (raw `Close`, not dividend-adjusted —
  see [Limitations](#limitations)).
- **Returns** are *simple* returns unless stated otherwise.
- **Annualization** assumes **252 trading days** per year
  (`TRADING_DAYS` in `src/config.py`).
- Default **risk-free rate** is **2%** per year (`RISK_FREE_RATE`).

## Returns

### Daily returns — `daily_returns()`

```text
r_t = P_t / P_{t-1} − 1
```

Percentage gain/loss per trading day. The first row is dropped (no prior price).
This is the foundation of all risk math.

### Cumulative returns — `cumulative_returns()`

```text
Growth_t = ∏(1 + r_i)   for i = 1..t
```

Value of a $1 investment over time. The final value appears as **Growth of $1**
in the summary table.

### Normalized prices — `normalized_prices()`

```text
Normalized_t = P_t / P_0 × 100
```

Rebases every ticker to 100 at the start so banks with very different price
levels (e.g. GS ~$130 vs. BAC ~$45) can be compared on one chart.

## Risk and risk-adjusted return

### Annualized return / volatility

```text
Ann. return = mean(daily) × 252
Ann. vol    = std(daily) × √252
```

Volatility (standard deviation of returns) is the headline risk measure:
higher values mean wilder day-to-day swings.

### Sharpe ratio — `sharpe_ratio()`

```text
Sharpe = (Ann. return − r_f) / Ann. vol
```

Excess return per unit of volatility. **> 1** is good, **> 2** very good,
**< 0** means the asset underperformed cash on a risk-adjusted basis. The daily
risk-free rate is derived from the annual rate via `(1 + r_f)^(1/252) − 1`.

### Sortino ratio — `sortino_ratio()`

Same as Sharpe, but the denominator uses only **downside** volatility
(negative excess returns). Rewards assets whose volatility comes from up-days.

### Maximum drawdown — `max_drawdown()`

```text
Drawdown_t = (P_t − max(P_0..P_t)) / max(P_0..P_t)
Max DD     = min(Drawdown)
```

Worst peak-to-trough loss — the pain a buy-and-hold investor actually felt.
Always ≤ 0; e.g. −0.85 means "fell 85% from its peak".

### Value at Risk / Expected Shortfall — `value_at_risk()` / `conditional_var()`

- **VaR 95% (daily):** the 5th percentile of daily returns — the loss that is
  exceeded only ~5% of days.
- **CVaR (a.k.a. expected shortfall):** the *average* return on those worst-5%
  days — always ≤ VaR.

Both are **historical** (empirical quantiles), not parametric — no normality
assumption is made, which matters because return distributions have fat tails
(see the histograms in the notebook).

### Rolling volatility — `rolling_volatility()`

30-day rolling standard deviation of returns, annualized (×√252). Shows *when*
risk spiked — the 2008–2009 surge is the dominant feature.

## Relationships and trends

### Correlation — `correlation_matrix()`

Pearson correlation of daily returns. Banks in the same sector typically score
~0.6–0.9: they rise and fall together, which limits within-sector
diversification.

### Moving averages — `moving_averages()`

Simple 30-day and 50-day rolling means of price. When the short average crosses
above (below) the long one, technicians call it a *golden cross* (*death
cross*) — a crude momentum signal, shown here for illustration, not as advice.

### Best / worst days — `best_worst_days()`

Largest single-day gain and loss per ticker, with dates. Worst days cluster in
2008–2009.

## Portfolios (`src/portfolio.py`)

### Method: Monte Carlo search

1. Draw `N` (default 5,000) random **long-only** weight vectors (weights ≥ 0,
   summing to 1).
2. Annualize each portfolio's return/volatility from the sample mean vector and
   covariance matrix of daily returns.
3. Report the **max-Sharpe** and **min-volatility** portfolios and scatter all
   `N` on the efficient-frontier chart, colored by Sharpe.

This is deliberately optimizer-free (no scipy dependency): it sketches the
frontier well enough for an educational project. For exact constrained
optima, see Future Work in the [README](../README.md).

### Portfolio math — `portfolio_performance()`

```text
R_p = w · μ × 252                  (annualized return)
σ_p = √(wᵀ Σ w) × √252             (annualized volatility)
Sharpe_p = (R_p − r_f) / σ_p
```

where `μ` and `Σ` are the sample mean and covariance of daily returns.

## Limitations

1. **No dividends/splits adjustment** — raw `Close` is used, so total return is
   slightly understated for dividend payers (notably WFC, JPM).
2. **Survivorship bias** — the six banks all survived 2008; failed banks
   (Lehman, Bear Stearns…) are absent, flattering the sector.
3. **Look-ahead in portfolios** — frontier weights use full-sample means, i.e.
   information no 2006 investor had. Illustrative only.
4. **Correlation ≠ causation** — co-movement reflects shared sector/market
   exposure, not one bank driving another.
5. **Not investment advice** — this is an educational analysis of historical data.

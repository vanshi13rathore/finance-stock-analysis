# 🧩 API Reference

Public interface of the `src/` package. All functions are imported as:

```python
from src import config, data, metrics, plots, portfolio
```

For the *meaning* of each metric, see [Methodology](methodology.md).

---

## `src.config` — constants

Single source of truth for tickers, dates, parameters, and paths.

| Name | Value | Purpose |
|------|-------|---------|
| `BANKS` | `["BAC","C","GS","JPM","MS","WFC"]` | Default universe |
| `BANK_NAMES` | dict | Ticker → full bank name |
| `START_DATE` / `END_DATE` | `"2006-01-01"` / `"2016-01-01"` | Default sample period |
| `TRADING_DAYS` | `252` | Annualization factor |
| `RISK_FREE_RATE` | `0.02` | Annual risk-free rate |
| `MA_SHORT_WINDOW` / `MA_LONG_WINDOW` | `30` / `50` | Moving-average windows |
| `ROLLING_VOL_WINDOW` | `30` | Rolling-volatility window |
| `VAR_LEVEL` | `0.05` | VaR/CVaR tail level |
| `N_MONTE_CARLO_PORTFOLIOS` | `5000` | Frontier simulation count |
| `RANDOM_SEED` | `99` | Synthetic-data seed |
| `ROOT_DIR` / `DATA_DIR` / `IMAGES_DIR` | `Path` | Key directories |
| `CACHE_FILE` / `SUMMARY_FILE` | `Path` | `data/bank_prices.csv`, `data/summary.csv` |

---

## `src.data` — loading & cleaning

```python
load_prices(tickers, start, end, cache_path=None, use_cache=True,
            synthetic_fallback=True) -> tuple[pd.DataFrame, str]
```

One-stop loader: tries **cache → Yahoo → synthetic**, returns
`(close_prices, source)` where `source ∈ {"cache","yahoo","synthetic"}`.
`close_prices` is a (dates × tickers) DataFrame.

```python
download_prices(tickers, start, end, auto_adjust=False,
                cache_path=None, use_cache=True) -> pd.DataFrame
```

Raw `yfinance` download with optional CSV caching. Raises
`DataDownloadError` if the result is empty.

```python
extract_close(raw, price_col="Close") -> pd.DataFrame
```

Extracts the (dates × tickers) close frame from a raw download. Handles
`(ticker, price)`, `(price, ticker)`, and flat single-ticker layouts.

```python
clean_prices(close, max_fill_days=5) -> pd.DataFrame
```

Sorts, de-duplicates, fills gaps ≤ 5 days, drops all-NaN rows (warns about
fixes applied).

```python
generate_synthetic_prices(tickers, start="2006-01-01",
                          end="2016-01-01", seed=99) -> pd.DataFrame
```

Deterministic business-day prices (GBM + shared market factor + 2008–2009
crisis regime). Used for offline demos and tests.

```python
describe_data(close) -> pd.DataFrame
```

Overview table: date range, row count, missing values, first/last price.

```python
class DataDownloadError(RuntimeError)
```

Raised when downloading fails and no fallback is allowed.

---

## `src.metrics` — returns & risk (pure functions, fully tested)

All take/return pandas objects; tickers as columns.

| Function | Signature | Returns |
|----------|-----------|---------|
| `daily_returns` | `(prices)` | Daily `pct_change` (first row dropped) |
| `cumulative_returns` | `(returns)` | Growth of $1 |
| `normalized_prices` | `(prices, base=100.0)` | Rebasing to `base` at t₀ |
| `annualized_return` | `(returns)` | Mean × 252 |
| `annualized_volatility` | `(returns)` | Std × √252 |
| `sharpe_ratio` | `(returns, risk_free_rate=0.02)` | Annualized Sharpe (NaN if vol = 0) |
| `sortino_ratio` | `(returns, risk_free_rate=0.02)` | Annualized Sortino |
| `drawdown_series` | `(prices)` | `(P − running_max) / running_max` |
| `max_drawdown` | `(prices)` | Worst drawdown per ticker |
| `value_at_risk` | `(returns, level=0.05)` | Historical daily VaR |
| `conditional_var` | `(returns, level=0.05)` | Historical daily CVaR |
| `rolling_volatility` | `(returns, window=30)` | Annualized rolling std |
| `moving_averages` | `(series, short=30, long=50)` | `Close` + short/long MA columns |
| `correlation_matrix` | `(returns)` | Pearson correlation |
| `best_worst_days` | `(returns)` | Extreme returns + dates |
| `summary_table` | `(prices, returns, risk_free_rate=0.02, var_level=0.05)` | Overview table sorted by Sharpe |

---

## `src.plots` — charts

Call `plots.setup_style()` once first. Every `plot_*` returns `(fig, ax)` (or
`(fig, axes)`) and writes a PNG when `savepath=` is given (parent dirs created
automatically). Time-series charts shade the 2008–2009 crisis band.

| Function | Input | Chart |
|----------|-------|-------|
| `setup_style()` | — | Global seaborn/matplotlib style |
| `plot_price_history` | `close` | Closing-price trends |
| `plot_normalized` | `normalized` | Rebased performance |
| `plot_cumulative` | `cumulative` | Growth of $1 |
| `plot_correlation_heatmap` | `corr` | Annotated heatmap |
| `plot_return_distributions` | `returns` | Histogram grid + KDE + ±3σ |
| `plot_pairwise_scatter` | `returns, sample=500, seed=42` | Sampled scatter matrix |
| `plot_moving_averages` | `ma, ticker` | Price + short/long MAs |
| `plot_rolling_volatility` | `rolling_vol, window=30` | Annualized rolling vol |
| `plot_drawdown` | `drawdown` | Underwater chart |
| `plot_risk_return` | `summary` | Vol-vs-return scatter (size ∝ Sharpe) |
| `plot_efficient_frontier` | `simulations` | Frontier colored by Sharpe |

---

## `src.portfolio` — Monte Carlo portfolios (no scipy needed)

```python
portfolio_performance(weights, mean_returns, cov,
                      risk_free_rate=0.02) -> tuple[float, float, float]
```

Annualized `(return, volatility, Sharpe)` for a weight vector.

```python
random_portfolios(returns, n_portfolios=5000,
                  risk_free_rate=0.02, seed=42) -> tuple[pd.DataFrame, PortfolioResult]
```

Simulates random long-only portfolios. Returns `(simulations, best)` where
`simulations` has `return` / `volatility` / `sharpe` columns and `best` is a
`PortfolioResult` with max-Sharpe and min-vol weights + stats.

---

## Minimal end-to-end example

```python
from src import config, data, metrics, plots, portfolio

close, source = data.load_prices(config.BANKS, config.START_DATE,
                                 config.END_DATE, config.CACHE_FILE)
rets = metrics.daily_returns(close)
summary = metrics.summary_table(close, rets)

plots.setup_style()
plots.plot_risk_return(summary, savepath="images/risk_return.png")

sims, best = portfolio.random_portfolios(rets)
plots.plot_efficient_frontier(sims, savepath="images/efficient_frontier.png")
```

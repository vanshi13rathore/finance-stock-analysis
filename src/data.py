"""Data loading utilities: download, cache, clean, and (offline) simulate prices.

The module is resilient to the two big real-world annoyances of this project:

1. ``yfinance`` changed its default column layout across versions
   (``(Price, Ticker)`` vs ``(Ticker, Price)``), so extraction is layout-aware.
2. The Yahoo API may be unreachable (offline sandbox, rate limits), so every
   entry point can fall back to a deterministic synthetic dataset or a local
   CSV cache instead of crashing.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from .config import RANDOM_SEED


class DataDownloadError(RuntimeError):
    """Raised when price data cannot be downloaded and no fallback is allowed."""


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------
def download_prices(
    tickers: list[str],
    start: str,
    end: str,
    auto_adjust: bool = False,
    cache_path: Path | str | None = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Download OHLCV data with ``yfinance`` (with optional CSV caching).

    Parameters
    ----------
    tickers:
        Stock tickers, e.g. ``["BAC", "C", "GS", "JPM", "MS", "WFC"]``.
    start, end:
        Date range (``YYYY-MM-DD``).
    auto_adjust:
        If False, keep raw ``Close`` plus an ``Adj Close`` column.
    cache_path:
        Where to store the raw download. ``None`` disables caching.
    use_cache:
        If True and the cache file exists, load it instead of downloading.

    Returns
    -------
    Raw ``yfinance`` DataFrame (possibly with MultiIndex columns).

    Raises
    ------
    DataDownloadError
        If the download yields an empty frame (network blocked, bad tickers…).
    """
    import yfinance as yf  # local import so metrics/plots stay lightweight

    if use_cache and cache_path is not None and Path(cache_path).exists():
        return pd.read_csv(cache_path, header=[0, 1], index_col=0, parse_dates=True)

    df = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=auto_adjust,
        group_by="ticker",
        threads=False,
        progress=False,
    )
    if df is None or df.empty:
        raise DataDownloadError(
            "yfinance returned no data. Check your connection/tickers, "
            "or use `synthetic_fallback=True` / a cached CSV."
        )
    if cache_path is not None:
        path = Path(cache_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path)
    return df


# ---------------------------------------------------------------------------
# Extraction / cleaning
# ---------------------------------------------------------------------------
def extract_close(raw: pd.DataFrame, price_col: str = "Close") -> pd.DataFrame:
    """Extract a (dates × tickers) close-price frame from a raw download.

    Handles every ``yfinance`` layout we have seen in the wild:

    * MultiIndex ``(ticker, price)``  (``group_by="ticker"``)
    * MultiIndex ``(price, ticker)``  (newer ``yfinance`` default)
    * Flat columns for a single-ticker download
    """
    if not isinstance(raw.columns, pd.MultiIndex):
        if price_col in raw.columns:
            return raw[[price_col]].copy()
        raise KeyError(f"Column {price_col!r} not found in {list(raw.columns)}")

    level0 = set(raw.columns.get_level_values(0))
    level1 = set(raw.columns.get_level_values(1))

    if price_col in level1:  # (ticker, price) layout
        close = raw.xs(price_col, axis=1, level=1)
    elif price_col in level0:  # (price, ticker) layout
        close = raw.xs(price_col, axis=1, level=0)
    else:  # pragma: no cover - defensive
        raise KeyError(f"Column {price_col!r} not found in {list(level0 | level1)}")

    close.columns = [str(c) for c in close.columns]
    return close


def clean_prices(close: pd.DataFrame, max_fill_days: int = 5) -> pd.DataFrame:
    """Sort, de-duplicate, and fill small gaps in a price frame.

    * sorts the index and drops duplicated dates,
    * forward-fills gaps up to ``max_fill_days`` (short suspensions/holidays),
    * drops any remaining all-NaN rows and reports what was fixed.
    """
    cleaned = close.sort_index()
    cleaned = cleaned[~cleaned.index.duplicated(keep="first")]
    n_missing_before = int(cleaned.isna().sum().sum())
    cleaned = cleaned.ffill(limit=max_fill_days).bfill(limit=max_fill_days)
    cleaned = cleaned.dropna(how="all")
    n_missing_after = int(cleaned.isna().sum().sum())
    if n_missing_before:
        warnings.warn(
            f"Filled/dropped {n_missing_before - n_missing_after} missing price "
            f"points ({n_missing_after} NaNs remain).",
            stacklevel=2,
        )
    return cleaned


# ---------------------------------------------------------------------------
# Offline fallback: deterministic synthetic prices
# ---------------------------------------------------------------------------
def generate_synthetic_prices(
    tickers: list[str],
    start: str = "2006-01-01",
    end: str = "2016-01-01",
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Generate reproducible business-day prices (geometric Brownian motion).

    A high-volatility regime is injected around 2008–2009 so the demo data
    reproduces the narrative of the real sample (crisis spike in volatility).
    Different drifts/volatilities per ticker keep Citigroup the riskiest and
    Goldman Sachs relatively calm — mirroring the real findings.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start=start, end=end)
    n = len(dates)

    # Per-ticker (annual drift, base annual volatility, starting price).
    params = {
        "BAC": (0.02, 0.35, 45.0),
        "C": (0.01, 0.45, 50.0),
        "GS": (0.06, 0.25, 130.0),
        "JPM": (0.05, 0.28, 40.0),
        "MS": (0.03, 0.38, 60.0),
        "WFC": (0.04, 0.27, 35.0),
    }
    crisis = (dates >= "2008-01-01") & (dates <= "2009-12-31")
    # Shared market factor with a mild upward drift so post-crisis years recover.
    market = rng.standard_normal(n) + np.where(crisis, -0.02, 0.035)

    prices = {}
    for i, ticker in enumerate(tickers):
        drift, vol, start_price = params.get(ticker, (0.04, 0.30, 50.0))
        daily_drift = drift / 252
        daily_vol = vol / np.sqrt(252)
        shocks = rng.standard_normal(n)
        # Crisis regime: 2.5x volatility + negative drift.
        daily_vols = np.where(crisis, daily_vol * 2.5, daily_vol)
        daily_drifts = np.where(crisis, -0.0015, daily_drift)
        # Correlate tickers through the shared market factor for realism.
        rets = daily_drifts + daily_vols * (0.45 * shocks + 0.55 * market)
        prices[ticker] = start_price * np.exp(np.cumsum(rets))
    return pd.DataFrame(prices, index=dates)


# ---------------------------------------------------------------------------
# One-stop loader
# ---------------------------------------------------------------------------
def load_prices(
    tickers: list[str],
    start: str,
    end: str,
    cache_path: Path | str | None = None,
    use_cache: bool = True,
    synthetic_fallback: bool = True,
) -> tuple[pd.DataFrame, str]:
    """Load clean close prices, trying cache → download → synthetic, in order.

    Returns
    -------
    (close_prices, source) where ``source`` is one of
    ``"cache"``, ``"yahoo"``, or ``"synthetic"``.
    """
    if use_cache and cache_path is not None and Path(cache_path).exists():
        raw = pd.read_csv(cache_path, header=[0, 1], index_col=0, parse_dates=True)
        return clean_prices(extract_close(raw)), "cache"
    try:
        raw = download_prices(
            tickers, start, end, cache_path=cache_path, use_cache=False
        )
        return clean_prices(extract_close(raw)), "yahoo"
    except Exception as exc:  # network blocked, API changed, … — don't crash
        if not synthetic_fallback:
            raise DataDownloadError(str(exc)) from exc
        warnings.warn(
            f"Live download failed ({exc!r}); using reproducible synthetic "
            "demo data instead.",
            stacklevel=2,
        )
        return generate_synthetic_prices(tickers, start, end), "synthetic"


def describe_data(close: pd.DataFrame) -> pd.DataFrame:
    """Quick overview table: date range, rows, missing values per ticker."""
    return pd.DataFrame(
        {
            "start": [close.index.min()] * len(close.columns),
            "end": [close.index.max()] * len(close.columns),
            "rows": [len(close)] * len(close.columns),
            "missing": close.isna().sum().tolist(),
            "first_price": close.iloc[0].tolist(),
            "last_price": close.iloc[-1].tolist(),
        },
        index=list(close.columns),
    )

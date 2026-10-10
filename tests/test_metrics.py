"""Unit tests for src.metrics, src.portfolio, and src.data.

Everything here uses small deterministic fixtures — no network access.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import data as data_mod
from src import metrics, portfolio


@pytest.fixture()
def prices() -> pd.DataFrame:
    """Deterministic 2-ticker price fixture (60 business days)."""
    return data_mod.generate_synthetic_prices(
        ["AAA", "BBB"], start="2020-01-01", end="2020-03-31", seed=7
    )


@pytest.fixture()
def returns(prices: pd.DataFrame) -> pd.DataFrame:
    return metrics.daily_returns(prices)


# --- returns ---------------------------------------------------------------
def test_daily_returns_shape(prices, returns):
    assert len(returns) == len(prices) - 1
    assert list(returns.columns) == ["AAA", "BBB"]


def test_daily_returns_values():
    px = pd.DataFrame({"A": [100.0, 110.0, 99.0]})
    r = metrics.daily_returns(px)
    assert r["A"].tolist() == pytest.approx([0.10, -0.10])


def test_cumulative_returns():
    r = pd.DataFrame({"A": [0.10, -0.10]})
    cum = metrics.cumulative_returns(r)
    assert cum["A"].tolist() == pytest.approx([1.10, 0.99])


def test_normalized_prices(prices):
    norm = metrics.normalized_prices(prices)
    assert (norm.iloc[0] == 100.0).all()
    assert (norm > 0).all().all()


# --- risk / reward -----------------------------------------------------------
def test_annualized_volatility_matches_manual(returns):
    expected = returns.std() * np.sqrt(252)
    pd.testing.assert_series_equal(
        metrics.annualized_volatility(returns), expected, check_names=False
    )


def test_sharpe_positive_for_uptrend():
    rng = np.random.default_rng(0)
    r = pd.DataFrame({"A": 0.01 + 0.001 * rng.standard_normal(500)})
    assert metrics.sharpe_ratio(r)["A"] > 2.0


def test_sharpe_nan_for_flat_series():
    r = pd.DataFrame({"A": np.zeros(100)})
    assert np.isnan(metrics.sharpe_ratio(r)["A"])


def test_sortino_ignores_upside():
    r = pd.DataFrame({"A": [0.05, 0.05, -0.01, -0.01]})
    assert metrics.sortino_ratio(r)["A"] > metrics.sharpe_ratio(r)["A"]


# --- drawdown / tail risk ------------------------------------------------------
def test_max_drawdown_known_series():
    px = pd.DataFrame({"A": [100.0, 120.0, 90.0, 110.0]})
    assert metrics.max_drawdown(px)["A"] == pytest.approx(-0.25)


def test_drawdown_never_positive(prices):
    dd = metrics.drawdown_series(prices)
    assert (dd <= 1e-12).all().all()


def test_var_cvar_ordering(returns):
    var = metrics.value_at_risk(returns)
    cvar = metrics.conditional_var(returns)
    assert (cvar <= var).all()  # expected shortfall is worse than VaR
    assert (var < 0).all()


# --- helpers -------------------------------------------------------------------
def test_rolling_volatility_window(returns):
    rv = metrics.rolling_volatility(returns, window=10)
    assert rv.iloc[:9].isna().all().all()
    assert rv.iloc[9:].notna().all().all()


def test_moving_averages_columns(prices):
    ma = metrics.moving_averages(prices["AAA"], short=5, long=10)
    assert list(ma.columns) == ["Close", "5 Day MA", "10 Day MA"]
    assert ma["5 Day MA"].iloc[:4].isna().all()


def test_correlation_matrix_properties(returns):
    corr = metrics.correlation_matrix(returns)
    assert corr.shape == (2, 2)
    assert np.allclose(np.diag(corr), 1.0)
    assert corr.equals(corr.T)


def test_best_worst_days(prices, returns):
    bw = metrics.best_worst_days(returns)
    assert list(bw.columns) == [
        "best_day_return", "best_day_date",
        "worst_day_return", "worst_day_date",
    ]
    assert (bw["best_day_return"] >= bw["worst_day_return"]).all()


def test_summary_table_sorted_by_sharpe(prices, returns):
    summary = metrics.summary_table(prices, returns)
    assert summary["Sharpe"].is_monotonic_decreasing
    assert set(summary.columns) >= {
        "Ann. Return", "Ann. Volatility", "Sharpe",
        "Max Drawdown", "Growth of $1",
    }


# --- portfolio -------------------------------------------------------------------
def test_portfolio_performance_known_case():
    mean = pd.Series({"A": 0.001, "B": 0.002})
    cov = pd.DataFrame(np.eye(2) * 0.0001, index=["A", "B"], columns=["A", "B"])
    ret, vol, sharpe = portfolio.portfolio_performance(
        np.array([0.5, 0.5]), mean, cov, risk_free_rate=0.0
    )
    assert ret == pytest.approx(0.0015 * 252)
    assert vol == pytest.approx(np.sqrt(0.5 * 0.0001) * np.sqrt(252))
    assert sharpe == pytest.approx(ret / vol)


def test_random_portfolios_weights_sum_to_one(returns):
    sims, best = portfolio.random_portfolios(returns, n_portfolios=200, seed=1)
    assert len(sims) == 200
    assert best.max_sharpe_weights.sum() == pytest.approx(1.0)
    assert best.min_vol_weights.sum() == pytest.approx(1.0)
    assert (best.max_sharpe_weights >= 0).all()
    assert sims["sharpe"].max() == pytest.approx(best.max_sharpe_ratio)


def test_random_portfolios_reproducible(returns):
    sims1, _ = portfolio.random_portfolios(returns, n_portfolios=50, seed=3)
    sims2, _ = portfolio.random_portfolios(returns, n_portfolios=50, seed=3)
    pd.testing.assert_frame_equal(sims1, sims2)


# --- data ------------------------------------------------------------------------
def _fake_raw(layout: str) -> pd.DataFrame:
    idx = pd.bdate_range("2020-01-01", periods=5)
    if layout == "ticker_first":
        cols = pd.MultiIndex.from_product([["AAA", "BBB"], ["Open", "Close"]])
    else:
        cols = pd.MultiIndex.from_product([["Open", "Close"], ["AAA", "BBB"]])
    return pd.DataFrame(np.arange(20).reshape(5, 4).astype(float),
                        index=idx, columns=cols)


@pytest.mark.parametrize("layout", ["ticker_first", "price_first"])
def test_extract_close_handles_both_yfinance_layouts(layout):
    close = data_mod.extract_close(_fake_raw(layout))
    assert list(close.columns) == ["AAA", "BBB"]
    assert len(close) == 5


def test_generate_synthetic_is_deterministic():
    a = data_mod.generate_synthetic_prices(["BAC", "C"], seed=42)
    b = data_mod.generate_synthetic_prices(["BAC", "C"], seed=42)
    pd.testing.assert_frame_equal(a, b)
    assert (a > 0).all().all()
    assert len(a) > 2000  # ~10 years of business days


def test_clean_prices_fills_small_gaps():
    idx = pd.bdate_range("2020-01-01", periods=10)
    px = pd.DataFrame({"A": np.arange(10, dtype=float)}, index=idx)
    px.iloc[3:5] = np.nan
    with pytest.warns(UserWarning, match="missing price"):
        cleaned = data_mod.clean_prices(px)
    assert cleaned.isna().sum().sum() == 0

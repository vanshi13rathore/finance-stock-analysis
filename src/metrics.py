"""Core financial metrics: returns, risk, and risk-adjusted performance.

All functions are pure (no network, no plotting) so they are easy to test
and reuse from the notebook, the CLI, and the dashboard.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


# ---------------------------------------------------------------------------
# Returns
# ---------------------------------------------------------------------------
def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Simple daily returns: ``P_t / P_{t-1} - 1`` (first row dropped)."""
    return prices.pct_change().iloc[1:]


def cumulative_returns(returns: pd.DataFrame) -> pd.DataFrame:
    """Growth of a $1 investment: ``cumprod(1 + r)``."""
    return (1 + returns).cumprod()


def normalized_prices(prices: pd.DataFrame, base: float = 100.0) -> pd.DataFrame:
    """Rebase every series to ``base`` at the first observation."""
    return prices / prices.iloc[0] * base


# ---------------------------------------------------------------------------
# Annualized risk / reward
# ---------------------------------------------------------------------------
def annualized_return(returns: pd.DataFrame) -> pd.Series:
    """Annualized mean return (252 trading days)."""
    return returns.mean() * TRADING_DAYS


def annualized_volatility(returns: pd.DataFrame) -> pd.Series:
    """Annualized volatility = std of daily returns × √252."""
    return returns.std() * np.sqrt(TRADING_DAYS)


def sharpe_ratio(
    returns: pd.DataFrame, risk_free_rate: float = 0.02
) -> pd.Series:
    """Annualized Sharpe ratio: ``(ann_return − rf) / ann_vol``."""
    daily_rf = (1 + risk_free_rate) ** (1 / TRADING_DAYS) - 1
    excess = returns - daily_rf
    vol = excess.std() * np.sqrt(TRADING_DAYS)
    return (excess.mean() * TRADING_DAYS) / vol.replace(0, np.nan)


def sortino_ratio(
    returns: pd.DataFrame, risk_free_rate: float = 0.02
) -> pd.Series:
    """Annualized Sortino ratio (only downside volatility is penalized)."""
    daily_rf = (1 + risk_free_rate) ** (1 / TRADING_DAYS) - 1
    excess = returns - daily_rf
    downside = excess.clip(upper=0).std() * np.sqrt(TRADING_DAYS)
    return (excess.mean() * TRADING_DAYS) / downside.replace(0, np.nan)


# ---------------------------------------------------------------------------
# Drawdown
# ---------------------------------------------------------------------------
def drawdown_series(prices: pd.DataFrame) -> pd.DataFrame:
    """Drawdown series: ``(P − running_max) / running_max`` (≤ 0)."""
    running_max = prices.cummax()
    return (prices - running_max) / running_max


def max_drawdown(prices: pd.DataFrame) -> pd.Series:
    """Maximum (most negative) drawdown per ticker."""
    return drawdown_series(prices).min()


# ---------------------------------------------------------------------------
# Tail risk
# ---------------------------------------------------------------------------
def value_at_risk(returns: pd.DataFrame, level: float = 0.05) -> pd.Series:
    """Historical daily VaR: the ``level``-quantile of returns (negative)."""
    return returns.quantile(level)


def conditional_var(returns: pd.DataFrame, level: float = 0.05) -> pd.Series:
    """Historical daily CVaR (expected shortfall) at ``level``."""
    var = value_at_risk(returns, level)
    return pd.Series(
        {
            col: returns.loc[returns[col] <= var[col], col].mean()
            for col in returns.columns
        }
    )


# ---------------------------------------------------------------------------
# Rolling / trend helpers
# ---------------------------------------------------------------------------
def rolling_volatility(returns: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """Annualized rolling standard deviation of returns."""
    return returns.rolling(window).std() * np.sqrt(TRADING_DAYS)


def moving_averages(
    series: pd.Series, short: int = 30, long: int = 50
) -> pd.DataFrame:
    """Price plus short/long simple moving averages."""
    return pd.DataFrame(
        {
            "Close": series,
            f"{short} Day MA": series.rolling(short).mean(),
            f"{long} Day MA": series.rolling(long).mean(),
        }
    )


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation of daily returns."""
    return returns.corr()


def best_worst_days(returns: pd.DataFrame) -> pd.DataFrame:
    """Best/worst single-day return (value + date) per ticker."""
    return pd.DataFrame(
        {
            "best_day_return": returns.max(),
            "best_day_date": returns.idxmax(),
            "worst_day_return": returns.min(),
            "worst_day_date": returns.idxmin(),
        }
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def summary_table(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    risk_free_rate: float = 0.02,
    var_level: float = 0.05,
) -> pd.DataFrame:
    """One-row-per-ticker overview of return, risk, and tail risk."""
    table = pd.DataFrame(
        {
            "Ann. Return": annualized_return(returns),
            "Ann. Volatility": annualized_volatility(returns),
            "Sharpe": sharpe_ratio(returns, risk_free_rate),
            "Sortino": sortino_ratio(returns, risk_free_rate),
            "Max Drawdown": max_drawdown(prices),
            f"VaR {int((1 - var_level) * 100)}% (daily)": value_at_risk(
                returns, var_level
            ),
            "Best Day": returns.max(),
            "Worst Day": returns.min(),
            "Growth of $1": cumulative_returns(returns).iloc[-1],
        }
    )
    return table.sort_values("Sharpe", ascending=False)

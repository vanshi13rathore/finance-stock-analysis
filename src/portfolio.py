"""Lightweight portfolio analysis (no scipy dependency).

Uses Monte Carlo simulation over random long-only portfolios to sketch the
efficient frontier and to find the maximum-Sharpe and minimum-volatility
allocations. Good enough for an educational project without pulling in an
optimizer.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

TRADING_DAYS = 252


@dataclass
class PortfolioResult:
    """Best portfolios found by the Monte Carlo search."""

    max_sharpe_weights: pd.Series
    min_vol_weights: pd.Series
    max_sharpe_return: float
    max_sharpe_vol: float
    max_sharpe_ratio: float
    min_vol_return: float
    min_vol_vol: float
    min_vol_ratio: float


def portfolio_performance(
    weights: np.ndarray,
    mean_returns: pd.Series,
    cov: pd.DataFrame,
    risk_free_rate: float = 0.02,
) -> tuple[float, float, float]:
    """Annualized (return, volatility, Sharpe) of a weight vector."""
    w = np.asarray(weights, dtype=float)
    ann_ret = float(np.dot(w, mean_returns) * TRADING_DAYS)
    ann_vol = float(np.sqrt(w @ cov.values @ w) * np.sqrt(TRADING_DAYS))
    sharpe = (ann_ret - risk_free_rate) / ann_vol if ann_vol else float("nan")
    return ann_ret, ann_vol, sharpe


def random_portfolios(
    returns: pd.DataFrame,
    n_portfolios: int = 5_000,
    risk_free_rate: float = 0.02,
    seed: int = 42,
) -> tuple[pd.DataFrame, PortfolioResult]:
    """Simulate random long-only portfolios and pick the best two.

    Returns
    -------
    (simulations, best) where ``simulations`` has columns
    ``return`` / ``volatility`` / ``sharpe`` and ``best`` holds the
    maximum-Sharpe and minimum-volatility allocations.
    """
    rng = np.random.default_rng(seed)
    mean_returns = returns.mean()
    cov = returns.cov()
    n_assets = len(returns.columns)

    weights = rng.random((n_portfolios, n_assets))
    weights /= weights.sum(axis=1, keepdims=True)

    ann_rets = weights @ mean_returns.values * TRADING_DAYS
    ann_vols = np.sqrt(
        np.einsum("ij,jk,ik->i", weights, cov.values, weights)
    ) * np.sqrt(TRADING_DAYS)
    sharpes = (ann_rets - risk_free_rate) / np.where(ann_vols == 0, np.nan, ann_vols)

    simulations = pd.DataFrame(
        {"return": ann_rets, "volatility": ann_vols, "sharpe": sharpes}
    )
    i_sharpe = int(np.nanargmax(sharpes))
    i_minvol = int(np.nanargmin(ann_vols))

    best = PortfolioResult(
        max_sharpe_weights=pd.Series(weights[i_sharpe], index=returns.columns),
        min_vol_weights=pd.Series(weights[i_minvol], index=returns.columns),
        max_sharpe_return=float(ann_rets[i_sharpe]),
        max_sharpe_vol=float(ann_vols[i_sharpe]),
        max_sharpe_ratio=float(sharpes[i_sharpe]),
        min_vol_return=float(ann_rets[i_minvol]),
        min_vol_vol=float(ann_vols[i_minvol]),
        min_vol_ratio=float(sharpes[i_minvol]),
    )
    return simulations, best

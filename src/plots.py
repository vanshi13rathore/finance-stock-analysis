"""Publication-ready charts for the bank-stock analysis.

Every function returns ``(fig, ax)`` (or ``(fig, axes)``) and optionally saves
the figure when ``savepath`` is given, so the notebook, CLI, and dashboard
share one consistent visual style.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

FIGSIZE = (12, 6)
CRISIS_START, CRISIS_END = "2008-01-01", "2009-12-31"


def setup_style() -> None:
    """Apply the project's global matplotlib/seaborn style."""
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.figsize": FIGSIZE,
            "figure.dpi": 120,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
        }
    )


def _save(fig: plt.Figure, savepath: Path | str | None) -> None:
    if savepath is not None:
        path = Path(savepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path)


def _shade_crisis(ax: plt.Axes) -> None:
    ax.axvspan(pd.Timestamp(CRISIS_START), pd.Timestamp(CRISIS_END),
               color="red", alpha=0.08, label="2008 crisis")


def plot_price_history(
    close: pd.DataFrame, savepath: Path | str | None = None
) -> tuple[plt.Figure, plt.Axes]:
    """Raw closing-price trends for all banks."""
    fig, ax = plt.subplots()
    for ticker in close.columns:
        ax.plot(close.index, close[ticker], label=ticker, linewidth=1.5)
    _shade_crisis(ax)
    ax.set_title("Bank Stock Closing Prices (2006–2016)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Closing Price (USD)")
    ax.legend(ncol=len(close.columns), loc="upper left")
    fig.tight_layout()
    _save(fig, savepath)
    return fig, ax


def plot_normalized(
    normalized: pd.DataFrame, savepath: Path | str | None = None
) -> tuple[plt.Figure, plt.Axes]:
    """Rebased prices (base 100) — fair cross-bank comparison."""
    fig, ax = plt.subplots()
    for ticker in normalized.columns:
        ax.plot(normalized.index, normalized[ticker], label=ticker, linewidth=1.5)
    _shade_crisis(ax)
    ax.set_title("Normalized Bank Stock Performance (Base 100)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Normalized Price")
    ax.legend(ncol=len(normalized.columns), loc="upper left")
    fig.tight_layout()
    _save(fig, savepath)
    return fig, ax


def plot_cumulative(
    cumulative: pd.DataFrame, savepath: Path | str | None = None
) -> tuple[plt.Figure, plt.Axes]:
    """Growth of a $1 investment in each bank."""
    fig, ax = plt.subplots()
    for ticker in cumulative.columns:
        ax.plot(cumulative.index, cumulative[ticker], label=ticker, linewidth=1.5)
    _shade_crisis(ax)
    ax.set_title("Cumulative Returns — Growth of $1 (2006–2016)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Portfolio Value (USD)")
    ax.legend(ncol=len(cumulative.columns), loc="upper left")
    fig.tight_layout()
    _save(fig, savepath)
    return fig, ax


def plot_correlation_heatmap(
    corr: pd.DataFrame, savepath: Path | str | None = None
) -> tuple[plt.Figure, plt.Axes]:
    """Annotated heatmap of return correlations."""
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                vmin=-1, vmax=1, square=True, ax=ax)
    ax.set_title("Correlation Between Bank Stocks (Daily Returns)")
    fig.tight_layout()
    _save(fig, savepath)
    return fig, ax


def plot_return_distributions(
    returns: pd.DataFrame, savepath: Path | str | None = None
) -> tuple[plt.Figure, object]:
    """Grid of return histograms with KDE + ±3σ guides."""
    n = len(returns.columns)
    ncols = 3
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 4 * nrows),
                             sharex=True, sharey=True)
    axes = list(axes.flat) if n > 1 else [axes]
    for ax, ticker in zip(axes, returns.columns):
        series = returns[ticker].dropna()
        sns.histplot(series, bins=80, kde=True, ax=ax, color="steelblue")
        std = series.std()
        for k in (-3, 3):
            ax.axvline(k * std, color="red", linestyle="--", linewidth=1)
        ax.set_title(f"{ticker} — Daily Returns")
        ax.set_xlabel("Daily Return")
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle("Distribution of Daily Returns (dashed = ±3σ)", fontweight="bold")
    fig.tight_layout()
    _save(fig, savepath)
    return fig, axes


def plot_pairwise_scatter(
    returns: pd.DataFrame,
    sample: int = 500,
    seed: int = 42,
    savepath: Path | str | None = None,
) -> tuple[plt.Figure, object]:
    """Sampled scatter matrix (full pairplot is too slow on 2,500+ rows)."""
    data = returns.dropna().sample(
        n=min(sample, len(returns)), random_state=seed)
    grid = sns.pairplot(data, diag_kind="kde",
                        plot_kws={"alpha": 0.4, "s": 8})
    grid.fig.suptitle(f"Pairwise Daily Returns (n={len(data)} sampled days)",
                      fontweight="bold", y=1.01)
    _save(grid.fig, savepath)
    return grid.fig, grid.axes


def plot_moving_averages(
    ma: pd.DataFrame,
    ticker: str,
    savepath: Path | str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Close price with short/long moving averages + golden/death crosses."""
    fig, ax = plt.subplots()
    short_col = [c for c in ma.columns if c != "Close"][0]
    long_col = [c for c in ma.columns if c != "Close"][1]
    ax.plot(ma.index, ma["Close"], label="Close", linewidth=1.2, alpha=0.9)
    ax.plot(ma.index, ma[short_col], label=short_col, linewidth=1.5)
    ax.plot(ma.index, ma[long_col], label=long_col, linewidth=1.5)
    _shade_crisis(ax)
    ax.set_title(f"{ticker} Closing Price with Moving Averages")
    ax.set_xlabel("Year")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    fig.tight_layout()
    _save(fig, savepath)
    return fig, ax


def plot_rolling_volatility(
    rolling_vol: pd.DataFrame,
    window: int = 30,
    savepath: Path | str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Annualized rolling volatility for every bank."""
    fig, ax = plt.subplots()
    for ticker in rolling_vol.columns:
        ax.plot(rolling_vol.index, rolling_vol[ticker],
                label=ticker, linewidth=1.2)
    _shade_crisis(ax)
    ax.set_title(f"{window}-Day Rolling Volatility (Annualized)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Volatility")
    ax.legend(ncol=len(rolling_vol.columns), loc="upper left")
    fig.tight_layout()
    _save(fig, savepath)
    return fig, ax


def plot_drawdown(
    drawdown: pd.DataFrame, savepath: Path | str | None = None
) -> tuple[plt.Figure, plt.Axes]:
    """Underwater chart: drawdown from the running peak."""
    fig, ax = plt.subplots()
    for ticker in drawdown.columns:
        ax.plot(drawdown.index, drawdown[ticker], label=ticker, linewidth=1.2)
    _shade_crisis(ax)
    ax.set_title("Drawdown from Peak (Underwater Chart)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Drawdown")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.legend(ncol=len(drawdown.columns), loc="lower left")
    fig.tight_layout()
    _save(fig, savepath)
    return fig, ax


def plot_risk_return(
    summary: pd.DataFrame, savepath: Path | str | None = None
) -> tuple[plt.Figure, plt.Axes]:
    """Risk (volatility) vs. reward (return), sized by Sharpe ratio."""
    fig, ax = plt.subplots()
    sizes = (summary["Sharpe"].clip(lower=0) * 400 + 60).fillna(60)
    ax.scatter(summary["Ann. Volatility"], summary["Ann. Return"],
               s=sizes, alpha=0.7, c=range(len(summary)), cmap="viridis")
    for ticker, row in summary.iterrows():
        ax.annotate(str(ticker), (row["Ann. Volatility"], row["Ann. Return"]),
                    fontsize=11, fontweight="bold",
                    xytext=(6, 4), textcoords="offset points")
    ax.set_title("Risk vs. Return (bubble size ∝ Sharpe ratio)")
    ax.set_xlabel("Annualized Volatility")
    ax.set_ylabel("Annualized Return")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    fig.tight_layout()
    _save(fig, savepath)
    return fig, ax


def plot_efficient_frontier(
    simulations: pd.DataFrame,
    savepath: Path | str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Monte Carlo portfolios colored by Sharpe ratio."""
    fig, ax = plt.subplots()
    sc = ax.scatter(simulations["volatility"], simulations["return"],
                    c=simulations["sharpe"], cmap="viridis",
                    alpha=0.5, s=10)
    best = simulations.loc[simulations["sharpe"].idxmax()]
    minvol = simulations.loc[simulations["volatility"].idxmin()]
    ax.scatter([best["volatility"]], [best["return"]], c="red",
               s=120, marker="*", label="Max Sharpe", edgecolors="black")
    ax.scatter([minvol["volatility"]], [minvol["return"]], c="orange",
               s=120, marker="*", label="Min Volatility", edgecolors="black")
    fig.colorbar(sc, ax=ax, label="Sharpe Ratio")
    ax.set_title("Monte Carlo Efficient Frontier (Long-Only Portfolios)")
    ax.set_xlabel("Annualized Volatility")
    ax.set_ylabel("Annualized Return")
    ax.legend()
    fig.tight_layout()
    _save(fig, savepath)
    return fig, ax

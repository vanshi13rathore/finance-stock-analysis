"""Central configuration for the finance stock analysis project.

Keeping tickers, dates, and analysis parameters in one place makes the
notebook, the CLI script, and the dashboard consistent with each other.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Universe
# ---------------------------------------------------------------------------
BANKS: list[str] = ["BAC", "C", "GS", "JPM", "MS", "WFC"]

BANK_NAMES: dict[str, str] = {
    "BAC": "Bank of America",
    "C": "Citigroup",
    "GS": "Goldman Sachs",
    "JPM": "JPMorgan Chase",
    "MS": "Morgan Stanley",
    "WFC": "Wells Fargo",
}

# ---------------------------------------------------------------------------
# Sample period (covers the 2008 financial crisis)
# ---------------------------------------------------------------------------
START_DATE: str = "2006-01-01"
END_DATE: str = "2016-01-01"

# ---------------------------------------------------------------------------
# Analysis parameters
# ---------------------------------------------------------------------------
TRADING_DAYS: int = 252  # trading days in a year (annualization factor)
RISK_FREE_RATE: float = 0.02  # 2% annual risk-free rate for Sharpe/Sortino ratios
MA_SHORT_WINDOW: int = 30  # short moving-average window (days)
MA_LONG_WINDOW: int = 50  # long moving-average window (days)
ROLLING_VOL_WINDOW: int = 30  # rolling volatility window (days)
VAR_LEVEL: float = 0.05  # 95% VaR / CVaR
N_MONTE_CARLO_PORTFOLIOS: int = 5_000  # random portfolios for the frontier demo
RANDOM_SEED: int = 99  # seed for synthetic data + simulations (reproducibility)

# ---------------------------------------------------------------------------
# Paths (relative to the repository root)
# ---------------------------------------------------------------------------
ROOT_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = ROOT_DIR / "data"
IMAGES_DIR: Path = ROOT_DIR / "images"
CACHE_FILE: Path = DATA_DIR / "bank_prices.csv"
SUMMARY_FILE: Path = DATA_DIR / "summary.csv"

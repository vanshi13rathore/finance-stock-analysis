# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.1.0] - 2026-10-10

### Added

- Full documentation set in `docs/`: getting-started, user guide, CLI
  reference, methodology, data, API reference, architecture, findings, and
  troubleshooting guides.
- `CONTRIBUTING.md` with dev setup, workflow, and code/test/docs guidelines.
- `CHANGELOG.md` (this file).

## [2.0.0] - 2026-10-10

### Added

- `src/` package: `config`, `data`, `metrics`, `plots`, `portfolio` modules.
- Risk metrics: Sharpe/Sortino ratios, max drawdown, VaR/CVaR, rolling
  volatility, annualized return/volatility, best/worst days.
- Monte Carlo efficient frontier with max-Sharpe / min-volatility portfolios.
- `scripts/run_analysis.py` headless pipeline (charts + CSVs + findings).
- Streamlit dashboard (`app.py`) with sidebar controls and 4 tabs.
- `tests/` suite: 23 offline unit tests.
- `images/` with 10 generated charts; `data/` with summary/correlation CSVs.
- `requirements-dev.txt` (pytest, streamlit).

### Changed

- Rewrote `finance_project.ipynb` with a full markdown narrative (12 sections).
- Rewrote `README.md` (quickstart, methodology cheat-sheet, screenshots).
- Pinned `requirements.txt` with minimum versions; expanded `.gitignore`.

### Fixed

- Removed duplicated download cells; single `load_prices()` entry point.
- Layout-aware `yfinance` extraction (works across old/new versions).
- Global plot styling applied first; consistent style on all charts.
- Sampled scatter matrix (full pairplot was too slow on 2,600+ rows).

## [1.0.0] - earlier

- Initial single-notebook exploration: Yahoo download, daily returns,
  volatility, correlation heatmap, histograms, pairplot, moving averages,
  normalized prices, rolling volatility, cumulative returns.

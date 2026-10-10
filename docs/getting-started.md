# 🚀 Getting Started

Get from zero to your first charts in about five minutes.

## 1. Prerequisites

- **Python 3.10+** (3.11 recommended)
- **pip**
- Internet access for live Yahoo Finance data *(optional — the project works
  fully offline with synthetic demo data)*

Check your Python version:

```bash
python3 --version
```

## 2. Clone and install

```bash
git clone https://github.com/vanshi13rathore/finance-stock-analysis.git
cd finance-stock-analysis
pip install -r requirements.txt
```

This installs the core stack: `pandas`, `numpy`, `matplotlib`, `seaborn`,
`yfinance`, and `jupyter`.

For tests and the interactive dashboard, install the dev extras instead:

```bash
pip install -r requirements-dev.txt
```

> 💡 Using a virtual environment is recommended:
> `python3 -m venv .venv && source .venv/bin/activate` (Linux/macOS) or
> `.venv\Scripts\activate` (Windows).

## 3. Run your first analysis

Pick **one** of the three interfaces:

### Option A — Jupyter notebook (recommended for exploration)

```bash
jupyter notebook finance_project.ipynb
```

Then **Run → Run All Cells**. You will see the data source (`yahoo`,
`cache`, or `synthetic`), summary tables, and all charts inline.

### Option B — CLI pipeline (recommended for reproducibility)

```bash
python scripts/run_analysis.py
```

This prints the risk/return summary, portfolio allocations, and key findings,
and writes 10 charts to `images/` plus `summary.csv` / `correlation.csv` to
`data/`. See the [CLI Reference](cli-reference.md) for all options.

### Option C — Interactive dashboard

```bash
streamlit run app.py
```

Opens a browser app with ticker/date controls and four tabs
(Prices, Risk, Correlations, Portfolio).

## 4. Verify your setup

```bash
pytest tests/ -q
```

Expected result: `23 passed`. These tests need no network access.

## 5. Next steps

- New to the analysis? Follow the [User Guide](user-guide.md).
- Want to understand the math? Read [Methodology](methodology.md).
- Something broken? Check [Troubleshooting](troubleshooting.md).

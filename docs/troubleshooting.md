# 🔧 Troubleshooting

Common problems and fixes.

## Data / download issues

### "yfinance returned no data" / SSL / connection errors

Yahoo Finance may be unreachable (offline machine, firewall, rate limit, or a
Yahoo outage). The project handles this automatically:

- The **notebook**, **CLI**, and **dashboard** fall back to synthetic demo data
  and print `Data source : synthetic`.
- To force the demo explicitly: `python scripts/run_analysis.py --synthetic`
  or tick *"Use synthetic demo data"* in the dashboard sidebar.
- `yfinance` prints noisy SSL/connection lines to **stderr** before the
  fallback kicks in — this is cosmetic; the analysis still succeeds.

If you *need* live data: check your connection, wait out rate limits
(`Exception: Too Many Requests` → retry in a few minutes), or upgrade:
`pip install -U yfinance`.

### One ticker fails but others succeed ("N Failed downloads")

Yahoo occasionally drops a ticker (delisted symbol, typo, temporary API gap).
Fixes:

- Check the symbol exists on Yahoo Finance.
- Re-run — transient failures are common.
- Pass `--no-cache` to discard a partially cached download.

### Stale results — I changed tickers/dates but numbers didn't change

You're probably reading the **cache** (`data/bank_prices.csv`), which stores
the *previous* download. Delete it or pass `--no-cache`.

## Notebook issues

### `ModuleNotFoundError: No module named 'src'`

The notebook inserts the repo root into `sys.path` in its setup cell — this
only works if the notebook runs from the repository root. Either:

- Open the notebook as `jupyter notebook finance_project.ipynb` from the root, or
- Run the setup cell (cell 0) before any other cell.

### Cells run out of order / `NameError: close`

Use **Kernel → Restart & Run All**. Later sections depend on variables
(`close`, `returns`, `summary`, `corr`) created earlier.

### Pairplot cell is slow

It's already capped at a 500-day sample (`plot_pairwise_scatter(sample=500)`).
Lower it further if needed: `sample=200`.

## Dashboard issues

### `streamlit: command not found`

Install dev extras: `pip install -r requirements-dev.txt`.

### Blank page / old Streamlit deprecation warnings

Upgrade: `pip install -U streamlit` (requires ≥ 1.35 for the `width=` API used
in `app.py`).

## Test / install issues

### `pytest` fails with import errors

Run from the repo root: `pytest tests/ -q`. The test module adds the root to
`sys.path` itself.

### `pip install` fails with "externally-managed-environment" (PEP 668)

You're on a system Python that blocks global installs. Either use a virtual
environment (recommended):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

or, only if you understand the risk: `pip install --break-system-packages`.

## Still stuck?

1. Check the [Getting Started](getting-started.md) steps in order.
2. Re-run with a clean slate: delete `data/bank_prices.csv`, then
   `python scripts/run_analysis.py --synthetic --no-cache`.
3. Open an issue with your Python version (`python3 --version`), the command
   you ran, and the full error text.

#!/usr/bin/env python3
"""End-to-end bank-stock analysis pipeline (headless, reproducible).

Runs the full workflow — download → returns → risk metrics → portfolio
simulation → charts + CSVs — and prints the key findings to stdout.

Examples
--------
Live data (requires internet access to Yahoo Finance)::

    python scripts/run_analysis.py

Offline demo with reproducible synthetic data::

    python scripts/run_analysis.py --synthetic --no-cache
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no GUI backend needed
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import config, data, metrics, plots, portfolio  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the bank-stock analysis.")
    parser.add_argument("--tickers", nargs="+", default=config.BANKS)
    parser.add_argument("--start", default=config.START_DATE)
    parser.add_argument("--end", default=config.END_DATE)
    parser.add_argument("--risk-free", type=float, default=config.RISK_FREE_RATE)
    parser.add_argument("--images-dir", default=str(config.IMAGES_DIR))
    parser.add_argument("--data-dir", default=str(config.DATA_DIR))
    parser.add_argument("--synthetic", action="store_true",
                        help="Skip Yahoo and use synthetic demo data.")
    parser.add_argument("--no-cache", action="store_true",
                        help="Ignore any cached CSV download.")
    parser.add_argument("--portfolios", type=int,
                        default=config.N_MONTE_CARLO_PORTFOLIOS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    images_dir = Path(args.images_dir)
    data_dir = Path(args.data_dir)
    images_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    plots.setup_style()

    # --- 1. Data ---------------------------------------------------------
    if args.synthetic:
        close = data.generate_synthetic_prices(args.tickers, args.start, args.end)
        source = "synthetic"
    else:
        close, source = data.load_prices(
            args.tickers, args.start, args.end,
            cache_path=data_dir / "bank_prices.csv",
            use_cache=not args.no_cache,
            synthetic_fallback=True,
        )
    print(f"Data source : {source}")
    print(f"Tickers     : {list(close.columns)}")
    print(f"Date range  : {close.index.min().date()} → {close.index.max().date()} "
          f"({len(close)} trading days)")

    # --- 2. Metrics ------------------------------------------------------
    rets = metrics.daily_returns(close)
    summary = metrics.summary_table(close, rets, args.risk_free)
    corr = metrics.correlation_matrix(rets)
    summary.to_csv(data_dir / "summary.csv")
    corr.to_csv(data_dir / "correlation.csv")
    print("\n===== Risk / Return Summary (sorted by Sharpe) =====")
    print(summary.round(4).to_string())

    # --- 3. Portfolio simulation ----------------------------------------
    simulations, best = portfolio.random_portfolios(
        rets, n_portfolios=args.portfolios, risk_free_rate=args.risk_free)
    print("\n===== Max-Sharpe Portfolio (long-only) =====")
    print(best.max_sharpe_weights.round(4).to_string())
    print(f"Return {best.max_sharpe_return:.2%} | Vol {best.max_sharpe_vol:.2%} | "
          f"Sharpe {best.max_sharpe_ratio:.2f}")
    print("\n===== Min-Volatility Portfolio (long-only) =====")
    print(best.min_vol_weights.round(4).to_string())
    print(f"Return {best.min_vol_return:.2%} | Vol {best.min_vol_vol:.2%} | "
          f"Sharpe {best.min_vol_ratio:.2f}")

    # --- 4. Charts -------------------------------------------------------
    plots.plot_price_history(close, images_dir / "price_history.png")
    plots.plot_normalized(metrics.normalized_prices(close),
                          images_dir / "normalized.png")
    plots.plot_cumulative(metrics.cumulative_returns(rets),
                          images_dir / "cumulative_returns.png")
    plots.plot_correlation_heatmap(corr, images_dir / "correlation_heatmap.png")
    plots.plot_return_distributions(rets, images_dir / "return_distributions.png")
    ma = metrics.moving_averages(close["BAC"],
                                 config.MA_SHORT_WINDOW, config.MA_LONG_WINDOW)
    plots.plot_moving_averages(ma, "BAC", images_dir / "bac_moving_averages.png")
    plots.plot_rolling_volatility(
        metrics.rolling_volatility(rets, config.ROLLING_VOL_WINDOW),
        config.ROLLING_VOL_WINDOW, images_dir / "rolling_volatility.png")
    plots.plot_drawdown(metrics.drawdown_series(close),
                        images_dir / "drawdown.png")
    plots.plot_risk_return(summary, images_dir / "risk_return.png")
    plots.plot_efficient_frontier(simulations,
                                  images_dir / "efficient_frontier.png")
    plt.close("all")
    print(f"\nSaved {len(list(images_dir.glob('*.png')))} charts → {images_dir}/")
    print(f"Saved summary.csv + correlation.csv → {data_dir}/")

    # --- 5. Key findings -------------------------------------------------
    riskiest = summary["Ann. Volatility"].idxmax()
    calmest = summary["Ann. Volatility"].idxmin()
    print("\n===== Key Findings =====")
    print(f"• Highest volatility : {riskiest} "
          f"({summary.loc[riskiest, 'Ann. Volatility']:.2%})")
    print(f"• Lowest volatility  : {calmest} "
          f"({summary.loc[calmest, 'Ann. Volatility']:.2%})")
    c = corr.copy()
    for t in c.columns:
        c.loc[t, t] = float("-inf")
    pair = (c.max().idxmax(), c.idxmax()[c.max().idxmax()])
    print(f"• Strongest correlation: {pair[0]}–{pair[1]} "
          f"({corr.loc[pair[0], pair[1]]:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

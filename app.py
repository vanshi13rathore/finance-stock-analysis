"""Interactive Streamlit dashboard for the bank-stock analysis.

Run with::

    pip install -r requirements-dev.txt
    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt  # noqa: E402
import streamlit as st  # noqa: E402

from src import config, data, metrics, plots, portfolio  # noqa: E402

st.set_page_config(page_title="Bank Stock Analysis", page_icon="📈", layout="wide")
plots.setup_style()

st.title("📈 Bank Stock Analysis (2006–2016)")
st.markdown(
    "Explore historical performance, risk, correlations, and portfolios for "
    "six major U.S. banks. Data loads from Yahoo Finance with an offline "
    "synthetic fallback."
)

def pd_to_date(value: str):  # noqa: D103 - tiny local helper
    import datetime as _dt

    return _dt.date.fromisoformat(value)


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    tickers = st.multiselect("Banks", config.BANKS, default=config.BANKS)
    start = st.date_input("Start", value=pd_to_date(config.START_DATE))
    end = st.date_input("End", value=pd_to_date(config.END_DATE))
    risk_free = st.slider("Risk-free rate", 0.0, 0.10, config.RISK_FREE_RATE,
                          step=0.005, format="%.1%%")
    short_ma = st.slider("Short MA window", 5, 100, config.MA_SHORT_WINDOW)
    long_ma = st.slider("Long MA window", 20, 200, config.MA_LONG_WINDOW)
    vol_window = st.slider("Rolling-vol window", 10, 120, config.ROLLING_VOL_WINDOW)
    use_synthetic = st.checkbox("Use synthetic demo data (offline)", value=False)


if not tickers:
    st.warning("Select at least one bank to continue.")
    st.stop()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
with st.spinner("Loading price data…"):
    if use_synthetic:
        close = data.generate_synthetic_prices(
            tickers, str(start), str(end), seed=config.RANDOM_SEED)
        source = "synthetic"
    else:
        close, source = data.load_prices(
            tickers, str(start), str(end),
            cache_path=config.CACHE_FILE, synthetic_fallback=True)
    rets = metrics.daily_returns(close)
    summary = metrics.summary_table(close, rets, risk_free)
    corr = metrics.correlation_matrix(rets)

st.caption(f"Data source: **{source}** · {len(close)} trading days · "
           f"{close.index.min().date()} → {close.index.max().date()}")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_prices, tab_risk, tab_corr, tab_port = st.tabs(
    ["📊 Prices", "⚠️ Risk", "🔗 Correlations", "💼 Portfolio"])

with tab_prices:
    st.subheader("Closing prices")
    fig, _ = plots.plot_price_history(close)
    st.pyplot(fig)
    plt.close(fig)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Normalized (base 100)")
        fig, _ = plots.plot_normalized(metrics.normalized_prices(close))
        st.pyplot(fig)
        plt.close(fig)
    with col2:
        st.subheader("Growth of $1")
        fig, _ = plots.plot_cumulative(metrics.cumulative_returns(rets))
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Moving averages")
    ma_ticker = st.selectbox("Ticker", tickers, index=0)
    ma = metrics.moving_averages(close[ma_ticker], short_ma, long_ma)
    fig, _ = plots.plot_moving_averages(ma, ma_ticker)
    st.pyplot(fig)
    plt.close(fig)

with tab_risk:
    st.subheader("Risk / return summary")
    st.dataframe(summary.style.format("{:.2%}").format(
        {"Sharpe": "{:.2f}", "Sortino": "{:.2f}"}), width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk vs. return")
        fig, _ = plots.plot_risk_return(summary)
        st.pyplot(fig)
        plt.close(fig)
    with col2:
        st.subheader("Drawdown from peak")
        fig, _ = plots.plot_drawdown(metrics.drawdown_series(close))
        st.pyplot(fig)
        plt.close(fig)

    st.subheader(f"{vol_window}-day rolling volatility (annualized)")
    fig, _ = plots.plot_rolling_volatility(
        metrics.rolling_volatility(rets, vol_window), vol_window)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Return distributions")
    fig, _ = plots.plot_return_distributions(rets)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Best / worst days")
    st.dataframe(metrics.best_worst_days(rets), width="stretch")

with tab_corr:
    st.subheader("Correlation heatmap")
    fig, _ = plots.plot_correlation_heatmap(corr)
    st.pyplot(fig)
    plt.close(fig)
    st.dataframe(corr.style.background_gradient(cmap="coolwarm", vmin=-1, vmax=1)
                 .format("{:.2f}"), width="stretch")

with tab_port:
    st.subheader("Monte Carlo efficient frontier (long-only)")
    n_port = st.slider("Portfolios to simulate", 500, 20_000,
                       config.N_MONTE_CARLO_PORTFOLIOS, step=500)
    sims, best = portfolio.random_portfolios(
        rets, n_portfolios=n_port, risk_free_rate=risk_free)
    fig, _ = plots.plot_efficient_frontier(sims)
    st.pyplot(fig)
    plt.close(fig)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Max-Sharpe allocation**")
        st.bar_chart(best.max_sharpe_weights)
        st.write(f"Return **{best.max_sharpe_return:.2%}** · Vol "
                 f"**{best.max_sharpe_vol:.2%}** · Sharpe "
                 f"**{best.max_sharpe_ratio:.2f}**")
    with col2:
        st.markdown("**Min-volatility allocation**")
        st.bar_chart(best.min_vol_weights)
        st.write(f"Return **{best.min_vol_return:.2%}** · Vol "
                 f"**{best.min_vol_vol:.2%}** · Sharpe "
                 f"**{best.min_vol_ratio:.2f}**")

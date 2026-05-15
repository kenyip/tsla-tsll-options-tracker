#!/usr/bin/env python3
"""
Streamlit dashboard for the TSLA / TSLL options engine.

Three tabs:
- Today      — live recommendation for both tickers + feature snapshot
- Performance — full-period backtest with equity curve + recent trades
- Scenarios  — regime suite (huge_down, normal_down, ..., inverse_v) showing
               how the current strategy handles each market type

Run with:  just run
"""

from __future__ import annotations
from dataclasses import asdict
import pandas as pd
import streamlit as st

from data import build
from backtest import Backtester, compute_metrics, trades_to_dataframe
from strategies import StrategyConfig, pick_entry, check_exits, pick_roll, get_config
from scenarios import REGIMES, canonical_window
from live import make_recommendation
from positions import (
    POSITIONS_PATH, load_positions, save_positions, check_position,
    _exit_target_dollars, _DECISION_ACTION,
)


st.set_page_config(page_title="TSLA / TSLL options engine", layout="wide")


# ─── Sidebar: per-ticker strategy config (read-only) ────────────────────
st.sidebar.title("Strategy config")
st.sidebar.caption(
    "Live per-ticker defaults from `strategies.DEFAULT_CONFIG_BY_TICKER` + "
    "`StrategyConfig`. Edit `strategies.py` and reload — run `just scenarios` "
    "first per CLAUDE.md."
)
for tkr in ('TSLA', 'TSLL'):
    tkr_cfg = get_config(tkr)
    with st.sidebar.expander(f"{tkr}  long_dte={tkr_cfg.long_dte}  Δ={tkr_cfg.long_target_delta}", expanded=False):
        for key, value in asdict(tkr_cfg).items():
            st.text(f"{key:25s} = {value}")


# ─── Cached loaders (data + backtest are slow-ish) ──────────────────────
@st.cache_data(ttl=3600)
def load_data(ticker: str, period: str = '5y') -> pd.DataFrame:
    return build(ticker, period=period)


@st.cache_data(ttl=3600)
def run_full_backtest(ticker: str, period: str = '5y') -> tuple[pd.DataFrame, dict]:
    df = load_data(ticker, period)
    cfg = get_config(ticker)
    bt = Backtester(df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker,
                    roll_fn=pick_roll if getattr(cfg, 'roll_on_max_loss', False) else None)
    bt.run()
    trades_df = trades_to_dataframe(bt.trades)
    metrics = compute_metrics(bt.trades)
    if not trades_df.empty:
        trades_df = trades_df.sort_values('exit_date').reset_index(drop=True)
        trades_df['cumulative_pnl'] = trades_df['pnl_per_contract'].cumsum()
    return trades_df, metrics


@st.cache_data(ttl=3600)
def run_scenarios(ticker: str) -> pd.DataFrame:
    df = load_data(ticker)
    cfg = get_config(ticker)
    rows = []
    for regime in REGIMES:
        w = canonical_window(df, ticker, regime)
        if w is None:
            rows.append({'regime': regime, 'available': False})
            continue
        bt = Backtester(df=w, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker,
                        roll_fn=pick_roll if getattr(cfg, 'roll_on_max_loss', False) else None)
        bt.run()
        m = compute_metrics(bt.trades)
        ret = (w['close'].iloc[-1] - w['close'].iloc[0]) / w['close'].iloc[0]
        rows.append({
            'regime': regime,
            'available': True,
            'start': w.index[0].date(),
            'end': w.index[-1].date(),
            'underlying_ret_pct': ret * 100,
            'n_trades': m.get('n_trades', 0),
            'win_rate_pct': m.get('win_rate_pct', 0),
            'total_pnl': m.get('total_pnl_per_contract', 0),
            'max_dd': m.get('max_dd_per_contract', 0),
            'dominant_exit': max(m.get('exit_reasons', {'-': 0}).items(),
                                 key=lambda kv: kv[1])[0],
        })
    return pd.DataFrame(rows)


# ─── Header ─────────────────────────────────────────────────────────────
st.title("TSLA / TSLL options engine")
st.caption(
    "Single source of truth for daily premium-selling decisions. "
    "Live recommendation, full-period backtest, and regime stress-test in one place. "
    "See [STRATEGY.md](STRATEGY.md) for current rules, [ENGINE.md](ENGINE.md) for harness."
)

tab_today, tab_positions, tab_perf, tab_scenarios = st.tabs(
    ["Today", "Positions", "Performance", "Scenarios"]
)


# ─── Today ──────────────────────────────────────────────────────────────
with tab_today:
    st.header("Today's recommendation")
    col_tsla, col_tsll = st.columns(2, gap='large')

    for ticker, col in [('TSLA', col_tsla), ('TSLL', col_tsll)]:
        with col:
            rec = make_recommendation(ticker)
            st.subheader(f"{ticker} — ${rec['spot']:.2f}  ({rec['date'].date()})")

            if rec['action'] == 'STAND_ASIDE':
                st.warning(f"STAND ASIDE — {rec['reason']}")
            else:
                side = 'PUT' if 'PUT' in rec['action'] else 'CALL'
                st.success(
                    f"**SELL {side}**   strike ${rec['strike']:.2f}   "
                    f"exp {rec['expiration'].date()}   ({rec['dte']} DTE)"
                )

                m1, m2, m3 = st.columns(3)
                m1.metric("Est. credit / contract", f"${rec['estimated_credit']*100:,.0f}")
                m2.metric("Daily theta target", f"${rec['daily_theta_target']:.3f}/sh")
                m3.metric("IV used", f"{rec['iv_used']*100:.1f}%")

                e = rec['exit_targets']
                st.markdown("**Exit ladder targets**")
                exit_df = pd.DataFrame([
                    {'rung': 'profit target', 'condition': f"buy back ≤ ${e['profit_target_buyback']:.2f}",
                     'pnl_if_hit': f"+${e['profit_target_credit']*100:,.0f} / contract"},
                    {'rung': 'daily capture', 'condition': f"realised ≥ ${e['daily_capture_per_day']:.3f}/share/day",
                     'pnl_if_hit': 'variable (whenever ahead of schedule)'},
                    {'rung': 'max loss', 'condition': f"buy back ≥ ${e['max_loss_buyback']:.2f}",
                     'pnl_if_hit': f"−${e['max_loss_credit']*100:,.0f} / contract"},
                    {'rung': 'delta breach', 'condition': f"|Δ| > {e['delta_breach']}",
                     'pnl_if_hit': 'closes before max loss usually'},
                    {'rung': 'DTE stop', 'condition': (
                        f"close at ≤ {e['dte_stop_at']} DTE remaining"
                        if e['dte_stop_at'] is not None else 'n/a for this DTE')},
                ])
                st.dataframe(exit_df, hide_index=True, use_container_width=True)

            with st.expander("Features driving today's decision"):
                feat_df = pd.DataFrame([rec['features']]).T
                feat_df.columns = ['value']
                st.dataframe(feat_df, use_container_width=True)


# ─── Positions ──────────────────────────────────────────────────────────
with tab_positions:
    st.header("Active positions")
    st.caption(
        f"Source of truth: `{POSITIONS_PATH.name}` (gitignored). "
        "The engine marks each open position with today's data and runs the "
        "exit ladder. CLOSE-flagged rows mean a rung fired; HOLD means none did. "
        "Estimates use BSM with HV30 as IV proxy — sanity-check against your broker."
    )

    records = load_positions()

    if not records:
        st.info(
            "No active positions tracked. Add one below, or run "
            "`just positions example` for a YAML template."
        )
    else:
        # Build a status table from each position
        rows_for_table = []
        all_statuses = []
        for r in records:
            try:
                s = check_position(r)
                all_statuses.append(s)
                pos = s['position']
                tgt = _exit_target_dollars(pos, s['cfg'])
                action = _DECISION_ACTION.get(s['exit_decision'], 'HOLD')
                rows_for_table.append({
                    'ticker': s['ticker'],
                    'side': pos.side,
                    'strike': f"${pos.strike:.2f}",
                    'exp': pos.expiration.date(),
                    'dte_left': s['dte_remaining'],
                    'mark': f"${s['mark']['price']:.2f}",
                    'delta': f"{s['mark']['delta']:+.2f}",
                    'pnl/sh': f"${s['pnl_per_share']:+.2f}",
                    'pnl_pct': f"{s['pnl_pct_credit']:+.1f}%",
                    'action': '🚨 ' + action if s['exit_decision'] else '✅ HOLD',
                })
            except Exception as e:
                rows_for_table.append({
                    'ticker': r.get('ticker', '?'),
                    'side': r.get('side', '?'),
                    'strike': r.get('strike', '?'),
                    'exp': r.get('expiration', '?'),
                    'dte_left': '—',
                    'mark': '—',
                    'delta': '—',
                    'pnl/sh': '—',
                    'pnl_pct': '—',
                    'action': f'❌ error: {e}',
                })

        st.dataframe(pd.DataFrame(rows_for_table), hide_index=True, use_container_width=True)

        n_close = sum(1 for s in all_statuses if s['exit_decision'] is not None)
        total_pnl = sum(s['pnl_total'] for s in all_statuses)
        c1, c2, c3 = st.columns(3)
        c1.metric("Open positions", len(records))
        c2.metric("Flagged to close", n_close)
        c3.metric("Live P/L (all contracts)", f"${total_pnl:+,.0f}")

        st.markdown("---")
        st.subheader("Per-position detail")
        for i, s in enumerate(all_statuses):
            pos = s['position']
            cfg_p = s['cfg']
            tgt = _exit_target_dollars(pos, cfg_p)
            mark = s['mark']
            pnl_share = s['pnl_per_share']
            daily_rate = pnl_share / s['days_held'] if s['days_held'] > 0 else 0.0

            with st.expander(
                f"{s['ticker']} short {pos.side} ${pos.strike:.2f} (exp {pos.expiration.date()}) — "
                f"{'🚨 ' + _DECISION_ACTION.get(s['exit_decision'], '') if s['exit_decision'] else '✅ HOLD'}",
                expanded=s['exit_decision'] is not None,
            ):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Days held", s['days_held'])
                m2.metric("DTE remaining", s['dte_remaining'])
                m3.metric("Current Δ", f"{mark['delta']:+.3f}")
                m4.metric("P/L", f"${pnl_share:+.2f}/sh", f"{s['pnl_pct_credit']:+.1f}% credit")

                st.markdown("**Exit ladder targets**")
                ladder_df = pd.DataFrame([
                    {'rung': 'profit_target',
                     'condition': f"buyback ≤ ${tgt['profit_target_buyback']:.2f}",
                     'status': '✅ HIT' if pnl_share >= tgt['profit_target_pnl'] else 'not hit'},
                    {'rung': 'daily_capture',
                     'condition': f"pace ≥ ${tgt['daily_capture_rate']:.3f}/sh/day",
                     'status': f"current ${daily_rate:.3f}/day — " + ('✅ HIT' if daily_rate >= tgt['daily_capture_rate'] and pnl_share > 0 else 'not hit')},
                    {'rung': 'max_loss',
                     'condition': f"buyback ≥ ${tgt['max_loss_buyback']:.2f}",
                     'status': '🚨 HIT' if pnl_share <= tgt['max_loss_pnl'] else 'safe'},
                    {'rung': 'delta_breach',
                     'condition': f"|Δ| > {tgt['delta_breach']}",
                     'status': f"current {abs(mark['delta']):.2f} — " + ('🚨 HIT' if abs(mark['delta']) > tgt['delta_breach'] else 'safe')},
                    {'rung': 'regime_flip',
                     'condition': "regime bearish OR reversal flagged",
                     'status': f"regime={s['features']['regime']}, reversal={s['features']['reversal']}"},
                ])
                st.dataframe(ladder_df, hide_index=True, use_container_width=True)

                if s['record'].get('notes'):
                    st.caption(f"Notes: {s['record']['notes']}")

                if st.button(f"Mark as closed (remove from positions.yaml)", key=f"close_{i}"):
                    fresh = load_positions()
                    fresh = [r for r in fresh
                             if not (r['ticker'].upper() == s['ticker'].upper()
                                     and float(r['strike']) == pos.strike
                                     and str(r['expiration']) == str(pos.expiration.date()))]
                    save_positions(fresh)
                    st.success("Removed. Reload the page to refresh.")
                    st.rerun()

    st.markdown("---")
    st.subheader("Add a position")
    with st.form("add_position", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        in_ticker = c1.selectbox("Ticker", ['TSLA', 'TSLL'])
        in_side = c2.selectbox("Side", ['put', 'call'])
        in_strike = c3.number_input("Strike", min_value=0.0, step=2.5, format="%.2f")

        c4, c5, c6 = st.columns(3)
        in_entry = c4.date_input("Entry date")
        in_expiration = c5.date_input("Expiration")
        in_credit = c6.number_input("Credit collected ($/share)", min_value=0.0, step=0.01, format="%.2f")

        c7, c8 = st.columns(2)
        in_contracts = c7.number_input("Contracts", min_value=1, value=1, step=1)
        in_notes = c8.text_input("Notes (optional)")

        submitted = st.form_submit_button("Add position")
        if submitted:
            new_record = {
                'ticker': in_ticker,
                'side': in_side,
                'strike': float(in_strike),
                'entry_date': str(in_entry),
                'expiration': str(in_expiration),
                'credit': float(in_credit),
            }
            if in_contracts != 1:
                new_record['contracts'] = int(in_contracts)
            if in_notes:
                new_record['notes'] = in_notes
            fresh = load_positions()
            fresh.append(new_record)
            save_positions(fresh)
            st.success(f"Added {in_ticker} {in_side} ${in_strike:.2f}. Reload to see status.")
            st.rerun()


# ─── Performance ────────────────────────────────────────────────────────
with tab_perf:
    st.header("Backtest performance — current config, full history")

    for ticker in ('TSLA', 'TSLL'):
        st.subheader(ticker)
        trades_df, metrics = run_full_backtest(ticker)

        if metrics.get('n_trades', 0) == 0:
            st.info("No trades.")
            continue

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Trades", metrics['n_trades'])
        m2.metric("Win rate", f"{metrics['win_rate_pct']:.1f}%")
        m3.metric("Total P/L", f"${metrics['total_pnl_per_contract']:,.0f}")
        m4.metric("Max drawdown", f"${metrics['max_dd_per_contract']:,.0f}")

        if 'cumulative_pnl' in trades_df.columns:
            chart_df = trades_df[['exit_date', 'cumulative_pnl']].set_index('exit_date')
            st.line_chart(chart_df, height=250)

        st.markdown("**Last 10 closed trades**")
        cols = ['entry_date', 'exit_date', 'side', 'strike', 'credit',
                'exit_price', 'exit_reason', 'days_held', 'pnl_per_contract']
        st.dataframe(trades_df[cols].tail(10).iloc[::-1], hide_index=True,
                     use_container_width=True)

        with st.expander(f"Exit reason breakdown ({ticker})"):
            ex = (trades_df.groupby('exit_reason')['pnl_per_contract']
                  .agg(['count', 'mean', 'sum']).round(2)
                  .sort_values('sum', ascending=False))
            st.dataframe(ex, use_container_width=True)


# ─── Scenarios ──────────────────────────────────────────────────────────
with tab_scenarios:
    st.header("Regime stress-test suite")
    st.caption(
        "Per CLAUDE.md, this view is the source of truth for whether a strategy "
        "change improves or breaks each market regime. Run this BEFORE and AFTER "
        "every tweak — aggregate P/L alone hides regime-specific failures."
    )

    for ticker in ('TSLA', 'TSLL'):
        st.subheader(ticker)
        df = run_scenarios(ticker)
        available = df[df['available']].copy()
        if available.empty:
            st.info(f"No canonical windows for {ticker}.")
            continue

        for col in ('underlying_ret_pct', 'win_rate_pct', 'total_pnl', 'max_dd'):
            available[col] = available[col].round(1)

        st.dataframe(available.drop(columns=['available']), hide_index=True,
                     use_container_width=True)

        profitable = (available['total_pnl'] > 0).sum()
        total = len(available)
        suite_pnl = available['total_pnl'].sum()
        worst = available.loc[available['total_pnl'].idxmin()]
        c1, c2, c3 = st.columns(3)
        c1.metric("Profitable regimes", f"{profitable} / {total}")
        c2.metric("Suite total P/L", f"${suite_pnl:+,.0f}")
        c3.metric(f"Worst: {worst['regime']}", f"${worst['total_pnl']:+,.0f}")

        unavailable = df[~df['available']]
        if not unavailable.empty:
            st.caption(f"Skipped: {', '.join(unavailable['regime'])} "
                       "(no canonical window — see scenarios.py)")

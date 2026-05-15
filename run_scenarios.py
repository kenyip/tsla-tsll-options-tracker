#!/usr/bin/env python3
"""
Run the current strategy across the canonical regime suite.

Use this BEFORE and AFTER changing strategy code/config so you can see how a
tweak affects each regime — not just aggregate P/L. Per CLAUDE.md, this is the
required check for any strategy change.

Output: per-regime row with trades / win rate / P/L / max DD / dominant exit
reason, plus a summary of profitable-regimes-out-of-7.
"""

from __future__ import annotations
import argparse
from dataclasses import replace
import pandas as pd

from data import build
from backtest import Backtester, compute_metrics
from strategies import StrategyConfig, pick_entry, check_exits, pick_covered_call, pick_roll, get_config
from scenarios import REGIMES, CANONICAL_SCENARIOS, canonical_window


def _dominant_exit(metrics: dict) -> str:
    reasons = metrics.get('exit_reasons', {})
    if not reasons:
        return '-'
    return max(reasons.items(), key=lambda kv: kv[1])[0]


def run_suite(ticker: str, df: pd.DataFrame, cfg: StrategyConfig) -> list[dict]:
    rows = []
    for regime in REGIMES:
        w = canonical_window(df, ticker, regime)
        if w is None:
            rows.append({'regime': regime, 'available': False})
            continue
        bt = Backtester(
            df=w, config=cfg, entry_fn=pick_entry, exit_fn=check_exits,
            wheel_cc_fn=pick_covered_call if cfg.wheel_enabled else None,
            roll_fn=pick_roll if getattr(cfg, 'roll_on_max_loss', False) else None,
        )
        bt.run()
        m = compute_metrics(bt.trades)
        ret = (w['close'].iloc[-1] - w['close'].iloc[0]) / w['close'].iloc[0]
        rows.append({
            'regime': regime,
            'available': True,
            'start': w.index[0].date(),
            'end': w.index[-1].date(),
            'underlying_ret_pct': ret * 100,
            'metrics': m,
        })
    return rows


def print_suite(ticker: str, rows: list[dict], cfg: StrategyConfig):
    print(f"\n=== {ticker} scenario suite ===")
    print(f"{'regime':<12} {'window':<26} {'undlyR%':>8} {'n':>3} {'win%':>6} {'P/L':>9} {'maxDD':>8} {'dom.exit':<14}")
    print('-' * 92)

    profitable = 0
    available = 0
    total_pnl = 0.0
    worst = None

    for r in rows:
        if not r['available']:
            print(f"{r['regime']:<12} (no canonical window defined)")
            continue
        m = r['metrics']
        pnl = m.get('total_pnl_per_contract', 0)
        n = m.get('n_trades', 0)
        wr = m.get('win_rate_pct', 0)
        dd = m.get('max_dd_per_contract', 0)
        dom = _dominant_exit(m)

        print(f"{r['regime']:<12} {str(r['start']):>10} → {str(r['end']):>10}  "
              f"{r['underlying_ret_pct']:>+7.1f}% "
              f"{n:>3} "
              f"{wr:>5.1f}% "
              f"${pnl:>+7.0f} "
              f"${dd:>6.0f} "
              f"{dom:<14}")

        available += 1
        total_pnl += pnl
        if pnl > 0:
            profitable += 1
        if worst is None or pnl < worst[1]:
            worst = (r['regime'], pnl)

    print('-' * 92)
    print(f"profitable regimes: {profitable}/{available}")
    print(f"total P/L across suite: ${total_pnl:+.2f}")
    if worst:
        print(f"worst regime: {worst[0]} (${worst[1]:+.0f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tickers', nargs='+', default=['TSLA', 'TSLL'])
    ap.add_argument('--period', default='5y')
    ap.add_argument('--wheel', action='store_true', help='Enable wheel mode')
    args = ap.parse_args()

    for ticker in args.tickers:
        cfg = get_config(ticker, wheel_enabled=args.wheel)
        print(f"\nstrategy config ({ticker}): long_dte={cfg.long_dte}  long_target_delta={cfg.long_target_delta}  wheel={cfg.wheel_enabled}")
        df = build(ticker, period=args.period)
        rows = run_suite(ticker, df, cfg)
        print_suite(ticker, rows, cfg)


if __name__ == "__main__":
    main()

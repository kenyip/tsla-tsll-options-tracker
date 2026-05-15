#!/usr/bin/env python3
"""
Driver: run the baseline single-leg short-premium strategy on TSLA and TSLL.

This is the v1 smoke test for the engine. Once this runs cleanly we move into
Phase 4 (walk-forward optimization over the StrategyConfig knobs).
"""

import argparse
import pandas as pd

from data import build
from backtest import Backtester, compute_metrics, format_metrics, trades_to_dataframe
from strategies import StrategyConfig, pick_entry, check_exits, pick_covered_call, pick_roll, get_config


def run_one(ticker: str, period: str, cfg: StrategyConfig, dump_trades: bool):
    df = build(ticker, period=period)
    bt = Backtester(
        df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker,
        wheel_cc_fn=pick_covered_call if cfg.wheel_enabled else None,
        roll_fn=pick_roll if cfg.roll_on_max_loss else None,
    )
    trades = bt.run()
    metrics = compute_metrics(trades)
    header = f"=== {ticker}  {df.index.min().date()} → {df.index.max().date()} ==="
    print(f"  config: long_dte={cfg.long_dte}  long_target_delta={cfg.long_target_delta}  wheel={cfg.wheel_enabled}")
    print(format_metrics(metrics, header))

    if dump_trades and trades:
        out = trades_to_dataframe(trades)
        path = f".cache/{ticker}_trades.csv"
        out.to_csv(path, index=False)
        print(f"  trade log         {path}")

    return trades, metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tickers', nargs='+', default=['TSLA', 'TSLL'])
    ap.add_argument('--period', default='5y')
    ap.add_argument('--dump-trades', action='store_true')
    ap.add_argument('--wheel', action='store_true', help='Enable wheel mode (accept put assignment, sell covered calls)')
    args = ap.parse_args()

    for tkr in args.tickers:
        print()
        cfg = get_config(tkr, wheel_enabled=args.wheel)
        run_one(tkr, args.period, cfg, args.dump_trades)


if __name__ == "__main__":
    main()

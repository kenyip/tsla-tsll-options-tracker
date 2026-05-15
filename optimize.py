#!/usr/bin/env python3
"""
Walk-forward optimizer for StrategyConfig knobs.

Rolling window: train on the prior `train_days`, optimise by composite score,
then evaluate the winning config out-of-sample on the next `test_days`. Roll
forward by `test_days` each step. Aggregate OOS results and inspect which knob
values consistently win.

Composite score (per backtest window):
    score = total_pnl_per_contract  -  0.5 * max_dd_per_contract

This rewards total profit but penalises drawdown linearly, so the optimiser
won't chase strategies that print P/L into a tail blow-up. Configurations with
fewer than `min_trades` are scored as -inf to avoid degenerate windows.
"""

from __future__ import annotations
import argparse
import itertools
from collections import Counter
from dataclasses import replace
import numpy as np

from data import build
from backtest import Backtester, compute_metrics
from strategies import StrategyConfig, pick_entry, check_exits, pick_roll, get_config


# Phase 4a sweep — see STRATEGY.md "Next tuning targets" for why these four.
PARAM_GRID = {
    'max_loss_mult':            [1.2, 1.5, 1.8],
    'long_target_delta':        [0.15, 0.20, 0.25],
    'daily_capture_mult_long':  [1.5, 2.0],
    'profit_target':            [0.45, 0.55, 0.65],
}


def score(metrics: dict, min_trades: int = 5) -> float:
    if metrics.get('n_trades', 0) < min_trades:
        return float('-inf')
    return metrics['total_pnl_per_contract'] - 0.5 * metrics['max_dd_per_contract']


def _run(df, cfg):
    bt = Backtester(df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits,
                    roll_fn=pick_roll if getattr(cfg, 'roll_on_max_loss', False) else None)
    bt.run()
    return compute_metrics(bt.trades)


def _rolling_windows(df, train_days: int, test_days: int):
    windows = []
    start = 0
    while start + train_days + test_days <= len(df):
        windows.append((start, start + train_days, start + train_days + test_days))
        start += test_days
    return windows


def walk_forward(df, train_days=252, test_days=63, base_cfg=None):
    base_cfg = base_cfg or StrategyConfig()
    keys = list(PARAM_GRID.keys())
    combos = list(itertools.product(*PARAM_GRID.values()))

    results = []
    for w_idx, (t0, t1, t2) in enumerate(_rolling_windows(df, train_days, test_days)):
        train_df = df.iloc[t0:t1]
        test_df = df.iloc[t1:t2]

        best_score = float('-inf')
        best_cfg = base_cfg
        best_train = None
        for vals in combos:
            cfg = replace(base_cfg, **dict(zip(keys, vals)))
            m = _run(train_df, cfg)
            s = score(m)
            if s > best_score:
                best_score = s
                best_cfg = cfg
                best_train = m

        oos = _run(test_df, best_cfg)
        results.append({
            'window': w_idx + 1,
            'train_period': (df.index[t0].date(), df.index[t1 - 1].date()),
            'test_period': (df.index[t1].date(), df.index[t2 - 1].date()),
            'best_params': {k: getattr(best_cfg, k) for k in keys},
            'train_score': best_score,
            'train_metrics': best_train,
            'oos_metrics': oos,
        })

    return results


def walk_forward_static(df, cfg: StrategyConfig, train_days=252, test_days=63):
    """No sweep — apply `cfg` across rolling OOS windows. Tests whether a fixed
    config generalizes vs being overfit to the aggregate backtest."""
    results = []
    for w_idx, (t0, t1, t2) in enumerate(_rolling_windows(df, train_days, test_days)):
        # train window not used for tuning — just labelled for context
        test_df = df.iloc[t1:t2]
        oos = _run(test_df, cfg)
        results.append({
            'window': w_idx + 1,
            'train_period': (df.index[t0].date(), df.index[t1 - 1].date()),
            'test_period': (df.index[t1].date(), df.index[t2 - 1].date()),
            'best_params': {k: getattr(cfg, k) for k in ('long_dte', 'long_target_delta', 'min_credit_pct')},
            'train_score': None,
            'train_metrics': None,
            'oos_metrics': oos,
        })
    return results


def summarize(results, ticker: str):
    if not results:
        print(f"  no usable windows for {ticker}")
        return

    oos_pnl = np.array([r['oos_metrics'].get('total_pnl_per_contract', 0.0) for r in results])
    oos_dd = np.array([r['oos_metrics'].get('max_dd_per_contract', 0.0) for r in results])
    oos_n = np.array([r['oos_metrics'].get('n_trades', 0) for r in results])
    win_windows = (oos_pnl > 0).sum()

    print(f"\n--- {ticker}: OOS aggregate over {len(results)} windows ---")
    print(f"  windows P/L > 0      {win_windows}/{len(results)}  ({100 * win_windows / len(results):.0f}%)")
    print(f"  total OOS P/L        ${oos_pnl.sum():.2f}")
    print(f"  mean OOS P/L         ${oos_pnl.mean():.2f}")
    print(f"  median OOS P/L       ${np.median(oos_pnl):.2f}")
    print(f"  OOS trades / window  avg {oos_n.mean():.0f}, total {oos_n.sum()}")
    print(f"  OOS max DD / window  mean ${oos_dd.mean():.2f}, max ${oos_dd.max():.2f}")

    print(f"\n  per-window detail:")
    for r in results:
        m = r['oos_metrics']
        p = r['best_params']
        pstr = ', '.join(f"{k}={v}" for k, v in p.items())
        print(f"    W{r['window']:2d}  test {r['test_period'][0]} → {r['test_period'][1]}  "
              f"n={m.get('n_trades', 0):3d}  "
              f"pnl=${m.get('total_pnl_per_contract', 0):8.2f}  "
              f"wr={m.get('win_rate_pct', 0):5.1f}%  "
              f"dd=${m.get('max_dd_per_contract', 0):7.2f}  "
              f"[{pstr}]")

    # Param-value frequency only makes sense in sweep mode; skip for static runs
    sample_params = results[0]['best_params']
    if any(k in sample_params for k in PARAM_GRID.keys()):
        print(f"\n  winning param value frequency across windows:")
        for key in PARAM_GRID.keys():
            if key not in sample_params:
                continue
            counts = Counter(r['best_params'][key] for r in results)
            ordered = sorted(counts.items(), key=lambda kv: -kv[1])
            modal = ordered[0][0]
            print(f"    {key:25s}  modal={modal}  ({dict(ordered)})")


def recommended_config(results) -> dict:
    """Modal value of each knob across windows — the 'most robust' config."""
    rec = {}
    for key in PARAM_GRID.keys():
        counts = Counter(r['best_params'][key] for r in results)
        rec[key] = counts.most_common(1)[0][0]
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tickers', nargs='+', default=['TSLA', 'TSLL'])
    ap.add_argument('--period', default='5y')
    ap.add_argument('--train-days', type=int, default=252)
    ap.add_argument('--test-days', type=int, default=63)
    ap.add_argument('--static', action='store_true',
                    help='Skip grid sweep; just validate get_config(ticker) across rolling OOS windows')
    args = ap.parse_args()

    if args.static:
        print(f"static walk-forward — using per-ticker get_config()")
        print(f"train={args.train_days}d  test={args.test_days}d")
    else:
        print(f"sweep grid: {PARAM_GRID}")
        n_combos = 1
        for v in PARAM_GRID.values():
            n_combos *= len(v)
        print(f"combos per window: {n_combos}  |  train={args.train_days}d  test={args.test_days}d")

    for ticker in args.tickers:
        print(f"\n{'=' * 72}")
        mode = 'static walk-forward validation' if args.static else 'walk-forward optimization'
        print(f"{ticker} {mode}")
        print('=' * 72)
        df = build(ticker, period=args.period)

        if args.static:
            cfg = get_config(ticker)
            print(f"  using cfg: long_dte={cfg.long_dte} long_target_delta={cfg.long_target_delta} min_credit_pct={cfg.min_credit_pct}")
            results = walk_forward_static(df, cfg, train_days=args.train_days, test_days=args.test_days)
            summarize(results, ticker)
        else:
            results = walk_forward(df, train_days=args.train_days, test_days=args.test_days)
            summarize(results, ticker)
            rec = recommended_config(results)
            print(f"\n  RECOMMENDED CONFIG for {ticker} (modal-best across windows):")
            for k, v in rec.items():
                print(f"    {k:25s} = {v}")


if __name__ == "__main__":
    main()

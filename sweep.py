#!/usr/bin/env python3
"""
Reusable knob-sweep harness — the operational tool behind the LLM-critic loop.

Replaces the bespoke `sweep_*.py` scripts (delta_breach, daily_capture, iv_rank,
profit_target) with one CLI. Take a `StrategyConfig` knob name + candidate
values, hold all other knobs at the per-ticker defaults, and report:

    - 5y backtest: P/L, max DD, profit factor, win rate, trade count, exit-reason mix
    - 12-regime scenario suite: total + worst regime
    - cost-function score (P/L - dd_weight × max_DD; default dd_weight = 1.0)
    - flag (⚠) when a value catastrophically regresses a regime vs the default

Supports 1-D (single knob) or 2-D (grid of two knobs) sweeps.

Examples:

    just sweep max_loss_mult --values 1.2,1.5,1.8,2.5,3.0
    just sweep delta_breach --values 0.30,0.38,0.45,0.50,0.55,0.60
    just sweep long_dte --values 3,5,7,14,21,30 --tickers TSLA
    just sweep long_dte --values 3,5,7 --vs long_target_delta --vs-values 0.15,0.20,0.30  # 2-D
    just sweep iv_rank_min --values 5,10,20,30,50 --dd-weight 0.5
"""

from __future__ import annotations
import argparse
import itertools
import sys
from dataclasses import replace
from typing import Any

from data import build
from backtest import Backtester, compute_metrics
from strategies import StrategyConfig, pick_entry, check_exits, pick_roll, get_config
from scenarios import REGIMES, canonical_window


def _coerce(v: str) -> Any:
    """Coerce a CLI string into int / float / bool / str."""
    s = v.strip()
    if s.lower() in ('true', 'false'):
        return s.lower() == 'true'
    try:
        i = int(s)
        return i
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


def _values_arg(s: str) -> list:
    return [_coerce(x) for x in s.split(',') if x.strip()]


def _run_5y(ticker: str, cfg: StrategyConfig) -> dict:
    df = build(ticker, period='5y')
    bt = Backtester(df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker,
                    roll_fn=pick_roll if getattr(cfg, 'roll_on_max_loss', False) else None)
    bt.run()
    m = compute_metrics(bt.trades)
    reasons = m.get('exit_reasons', {})
    return {
        'pnl': m.get('total_pnl_per_contract', 0.0),
        'n': m.get('n_trades', 0),
        'wr': m.get('win_rate_pct', 0.0),
        'dd': m.get('max_dd_per_contract', 0.0),
        'pf': m.get('profit_factor', 0.0),
        'days': m.get('avg_days_held', 0.0),
        'reasons': reasons,
    }


def _run_suite(ticker: str, cfg: StrategyConfig) -> tuple[float, float, dict]:
    df = build(ticker, period='5y')
    per_regime = {}
    for r in REGIMES:
        w = canonical_window(df, ticker, r)
        if w is None:
            continue
        bt = Backtester(df=w, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker)
        bt.run()
        m = compute_metrics(bt.trades)
        per_regime[r] = m.get('total_pnl_per_contract', 0.0)
    total = sum(per_regime.values())
    worst = min(per_regime.values()) if per_regime else 0.0
    return total, worst, per_regime


def _config_for_point(base: StrategyConfig, point: dict) -> StrategyConfig:
    """Apply a {knob: value} override dict to a base config."""
    return replace(base, **point)


def sweep_grid(
    knobs: dict[str, list],
    tickers: list[str],
    dd_weight: float = 1.0,
) -> dict[str, list[dict]]:
    """Run a sweep over the cross-product of `knobs` values for each ticker.
    Returns {ticker: [{point, metrics, suite_total, worst_regime, score}, ...]}."""
    keys = list(knobs.keys())
    combos = list(itertools.product(*(knobs[k] for k in keys)))
    results: dict[str, list[dict]] = {}
    for ticker in tickers:
        base = get_config(ticker)
        rows = []
        for vals in combos:
            point = dict(zip(keys, vals))
            cfg = _config_for_point(base, point)
            f = _run_5y(ticker, cfg)
            suite_total, worst, per_regime = _run_suite(ticker, cfg)
            score = f['pnl'] - dd_weight * f['dd']
            rows.append({
                'point': point,
                'is_default': all(getattr(base, k) == v for k, v in point.items()),
                'metrics': f,
                'suite_total': suite_total,
                'worst_regime': worst,
                'per_regime': per_regime,
                'score': score,
            })
        results[ticker] = rows
    return results


def print_sweep(
    ticker: str,
    rows: list[dict],
    knobs: list[str],
    dd_weight: float = 1.0,
    catastrophe_threshold: float = -500.0,
):
    """Print a 1-D or 2-D sweep table with winner / default / catastrophe annotations."""
    if not rows:
        print(f"  no results for {ticker}")
        return

    cfg = get_config(ticker)
    print(f"\n=== {ticker} === (defaults: " + ', '.join(f"{k}={getattr(cfg, k)}" for k in knobs) + ")")
    print(f"score = P/L - {dd_weight}×DD  ·  ⚠ = worst regime < ${catastrophe_threshold:+.0f} (potential tail blow-up)")
    print()

    cols = knobs + ['P/L (5y)', 'n', 'wr%', 'DD', 'PF', 'days', 'suite', 'worst', 'score', '']
    widths = {c: max(len(c), 8) for c in cols}
    # Pre-format rows
    out_rows = []
    best_score = max(r['score'] for r in rows)
    base_score = next((r['score'] for r in rows if r['is_default']), None)
    for r in rows:
        f = r['metrics']
        cells = {}
        for k in knobs:
            v = r['point'][k]
            cells[k] = f"{v:.4g}" if isinstance(v, float) else str(v)
        cells['P/L (5y)'] = f"${f['pnl']:+.0f}"
        cells['n'] = str(f['n'])
        cells['wr%'] = f"{f['wr']:.1f}%"
        cells['DD'] = f"${f['dd']:.0f}"
        cells['PF'] = f"{f['pf']:.2f}"
        cells['days'] = f"{f['days']:.1f}"
        cells['suite'] = f"${r['suite_total']:+.0f}"
        cells['worst'] = f"${r['worst_regime']:+.0f}"
        cells['score'] = f"{r['score']:+.0f}"
        flags = []
        if r['is_default']:
            flags.append('← current')
        if r['score'] == best_score:
            flags.append('🏆 best')
        if r['worst_regime'] < catastrophe_threshold:
            flags.append('⚠')
        cells[''] = ' '.join(flags)
        out_rows.append(cells)
        for c in cols:
            widths[c] = max(widths[c], len(cells[c]))

    # Header
    header = '  '.join(f"{c:>{widths[c]}}" for c in cols)
    print(header)
    print('  '.join('-' * widths[c] for c in cols))
    for r in out_rows:
        print('  '.join(f"{r[c]:>{widths[c]}}" for c in cols))

    if base_score is not None:
        delta = best_score - base_score
        print(f"\nbest score = {best_score:+.0f}  ·  current default score = {base_score:+.0f}  ·  Δ {delta:+.0f}")
    else:
        print(f"\nbest score = {best_score:+.0f}  (current default not in sweep)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Knob sweep harness for the LLM-critic loop.")
    ap.add_argument('knob', help='StrategyConfig field name (e.g. max_loss_mult)')
    ap.add_argument('--values', '-v', type=_values_arg, required=True,
                    help='comma-separated values (e.g. 1.2,1.5,1.8,2.5)')
    ap.add_argument('--vs', help='optional second knob for a 2-D grid')
    ap.add_argument('--vs-values', type=_values_arg, default=None,
                    help='values for the second knob (required if --vs is given)')
    ap.add_argument('--tickers', nargs='+', default=['TSLA', 'TSLL'])
    ap.add_argument('--dd-weight', type=float, default=1.0,
                    help='cost-function DD penalty (default 1.0 — heavier than optimize.py\'s 0.5)')
    ap.add_argument('--catastrophe-threshold', type=float, default=-500.0,
                    help='flag a value if its worst regime falls below this (default -$500)')
    args = ap.parse_args()

    knobs: dict[str, list] = {args.knob: args.values}
    if args.vs:
        if args.vs_values is None:
            print("--vs requires --vs-values", file=sys.stderr)
            return 1
        knobs[args.vs] = args.vs_values

    # Validate knob names against StrategyConfig
    sentinel = StrategyConfig()
    for k in knobs:
        if not hasattr(sentinel, k):
            print(f"Unknown StrategyConfig knob: {k!r}", file=sys.stderr)
            print(f"Available knobs: {sorted(vars(sentinel).keys())}", file=sys.stderr)
            return 1

    print(f"sweep knob(s): {dict((k, v) for k, v in knobs.items())}")
    print(f"tickers: {args.tickers}  ·  dd_weight: {args.dd_weight}")

    results = sweep_grid(knobs, args.tickers, dd_weight=args.dd_weight)
    for ticker, rows in results.items():
        print_sweep(ticker, rows, list(knobs.keys()),
                    dd_weight=args.dd_weight,
                    catastrophe_threshold=args.catastrophe_threshold)

    return 0


if __name__ == "__main__":
    sys.exit(main())

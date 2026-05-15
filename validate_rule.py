#!/usr/bin/env python3
"""
v1.13 — A/B validation harness for adaptive rules.

Given a ticker and a candidate `adaptive_rules` tuple, runs:
  1. 5y backtest (P/L, DD, WR, trades, exit-reasons)
  2. 12-regime scenario suite (per-regime + total + worst)
  3. Walk-forward static OOS (rolling 252/63 windows)

…against the current per-ticker default. Reports per-surface deltas plus a
final ship-or-null verdict per the cost-function policy (manage tail; calm-case
opportunity cost acceptable).

Usage:
    .venv/bin/python validate_rule.py --ticker TSLL --rule tsll_skip_low_gamma
    .venv/bin/python validate_rule.py --ticker TSLL --rules tsll_skip_marginal_up,tsll_skip_low_gamma
"""

from __future__ import annotations
import argparse
import sys
from dataclasses import replace

from data import build
from backtest import Backtester, compute_metrics
from strategies import get_config, pick_entry, check_exits, pick_roll, ADAPTIVE_RULES
from scenarios import REGIMES, canonical_window
from optimize import walk_forward_static


def _bt(ticker: str, cfg) -> dict:
    df = build(ticker, period='5y')
    bt = Backtester(df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker,
                    roll_fn=pick_roll if getattr(cfg, 'roll_on_max_loss', False) else None)
    bt.run()
    m = compute_metrics(bt.trades)
    return {
        'pnl': m.get('total_pnl_per_contract', 0.0),
        'n': m.get('n_trades', 0),
        'wr': m.get('win_rate_pct', 0.0),
        'dd': m.get('max_dd_per_contract', 0.0),
        'pf': m.get('profit_factor', 0.0),
        'reasons': m.get('exit_reasons', {}),
    }


def _suite(ticker: str, cfg) -> tuple[float, float, dict]:
    df = build(ticker, period='5y')
    per = {}
    for r in REGIMES:
        w = canonical_window(df, ticker, r)
        if w is None:
            continue
        bt = Backtester(df=w, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker)
        bt.run()
        m = compute_metrics(bt.trades)
        per[r] = m.get('total_pnl_per_contract', 0.0)
    total = sum(per.values())
    worst = min(per.values()) if per else 0.0
    return total, worst, per


def _oos(ticker: str, cfg) -> dict:
    df = build(ticker, period='5y')
    results = walk_forward_static(df=df, cfg=cfg, train_days=252, test_days=63)
    total_pnl = sum(r['oos_metrics'].get('total_pnl_per_contract', 0.0) for r in results)
    total_dd = max((r['oos_metrics'].get('max_dd_per_contract', 0.0) for r in results), default=0.0)
    n_windows = len(results)
    n_wins = sum(1 for r in results if r['oos_metrics'].get('total_pnl_per_contract', 0.0) > 0)
    return {'total_pnl': total_pnl, 'worst_dd': total_dd, 'n_windows': n_windows, 'n_wins': n_wins}


def _verdict(label_a: str, a: dict, label_b: str, b: dict, dd_weight: float = 1.0) -> str:
    """Score: pnl - dd_weight * dd. Higher is better. No catastrophe regression
    (worst regime drop > $500) allowed.
    """
    score_a = a['bt']['pnl'] - dd_weight * a['bt']['dd']
    score_b = b['bt']['pnl'] - dd_weight * b['bt']['dd']
    pnl_d = b['bt']['pnl'] - a['bt']['pnl']
    dd_d = b['bt']['dd'] - a['bt']['dd']
    suite_d = b['suite_total'] - a['suite_total']
    oos_d = b['oos']['total_pnl'] - a['oos']['total_pnl']
    worst_d = b['suite_worst'] - a['suite_worst']

    triple_win = pnl_d >= 0 and suite_d >= 0 and oos_d >= 0 and worst_d > -500
    msg = []
    msg.append(f"  cost score: {score_a:+.1f} → {score_b:+.1f} ({score_b - score_a:+.1f})")
    msg.append(f"  P/L 5y:     ${a['bt']['pnl']:+.0f} → ${b['bt']['pnl']:+.0f}  ({pnl_d:+.0f})")
    msg.append(f"  DD 5y:      ${a['bt']['dd']:.0f}  → ${b['bt']['dd']:.0f}   ({dd_d:+.0f})")
    msg.append(f"  Suite:      ${a['suite_total']:+.0f} → ${b['suite_total']:+.0f}  ({suite_d:+.0f})")
    msg.append(f"  Suite-worst:${a['suite_worst']:+.0f} → ${b['suite_worst']:+.0f}  ({worst_d:+.0f})")
    msg.append(f"  OOS:        ${a['oos']['total_pnl']:+.0f} → ${b['oos']['total_pnl']:+.0f}  ({oos_d:+.0f})")
    msg.append("")
    if triple_win:
        msg.append("  VERDICT: TRIPLE-WIN — ship candidate.")
    elif pnl_d > 0 and suite_d > 0 and oos_d >= -50 and worst_d > -500:
        msg.append("  VERDICT: 5y+Suite win; OOS within noise; no DD/catastrophe regression — likely ship.")
    elif pnl_d > 0 and suite_d >= -50 and oos_d > 0 and worst_d > -500:
        msg.append("  VERDICT: 5y+OOS win; Suite within noise; no DD/catastrophe regression — likely ship.")
    elif pnl_d <= 0 and suite_d <= 0 and oos_d <= 0:
        msg.append("  VERDICT: NULL — no surface improved.")
    else:
        msg.append("  VERDICT: MIXED — review tradeoff in STRATEGY.md.")
    return '\n'.join(msg)


def _run_all(ticker: str, cfg) -> dict:
    bt = _bt(ticker, cfg)
    total, worst, per = _suite(ticker, cfg)
    oos = _oos(ticker, cfg)
    return {
        'bt': bt,
        'suite_total': total,
        'suite_worst': worst,
        'suite_per': per,
        'oos': oos,
    }


def main():
    ap = argparse.ArgumentParser(description="v1.13 — A/B validation of an adaptive rule")
    ap.add_argument('--ticker', required=True, choices=['TSLA', 'TSLL'])
    ap.add_argument('--rule', help='single rule name to add to current rule set')
    ap.add_argument('--rules', help='full comma-separated rule set (overrides default)')
    args = ap.parse_args()

    base_cfg = get_config(args.ticker)

    if args.rules:
        candidate_rules = tuple(r.strip() for r in args.rules.split(',') if r.strip())
    elif args.rule:
        candidate_rules = tuple(list(base_cfg.adaptive_rules) + [args.rule])
    else:
        print("Need --rule or --rules", file=sys.stderr)
        return 1

    for r in candidate_rules:
        if r not in ADAPTIVE_RULES:
            print(f"Unknown rule: {r}. Known: {list(ADAPTIVE_RULES)}", file=sys.stderr)
            return 1

    cand_cfg = replace(base_cfg, adaptive_rules=candidate_rules)

    print(f"=== A/B validation: {args.ticker} ===")
    print(f"  baseline rules:  {tuple(base_cfg.adaptive_rules)}")
    print(f"  candidate rules: {candidate_rules}")
    print()

    print("Running baseline …")
    base = _run_all(args.ticker, base_cfg)
    print("Running candidate …")
    cand = _run_all(args.ticker, cand_cfg)

    print()
    print("--- baseline trade summary ---")
    print(f"  trades={base['bt']['n']}  wr={base['bt']['wr']:.1f}%  pnl=${base['bt']['pnl']:+.0f}  dd=${base['bt']['dd']:.0f}  pf={base['bt']['pf']:.2f}")
    print("--- candidate trade summary ---")
    print(f"  trades={cand['bt']['n']}  wr={cand['bt']['wr']:.1f}%  pnl=${cand['bt']['pnl']:+.0f}  dd=${cand['bt']['dd']:.0f}  pf={cand['bt']['pf']:.2f}")

    print()
    print("--- per-regime scenario suite (deltas) ---")
    for r in REGIMES:
        a = base['suite_per'].get(r)
        b = cand['suite_per'].get(r)
        if a is None and b is None:
            continue
        a = a if a is not None else 0.0
        b = b if b is not None else 0.0
        d = b - a
        flag = ''
        if d < -500:
            flag = ' ⚠ catastrophe'
        elif abs(d) < 1:
            flag = ' ='
        print(f"  {r:20s}  ${a:+8.0f} → ${b:+8.0f}  ({d:+.0f}){flag}")

    print()
    print(_verdict('baseline', base, 'candidate', cand))
    return 0


if __name__ == "__main__":
    sys.exit(main())

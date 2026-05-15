#!/usr/bin/env python3
"""v1.10 — archetype bake-off.

Runs every archetype × ticker through the standard validation gauntlet:
  1. 5y backtest → group-level + capital-time metrics
  2. 12-regime scenario suite → worst regime + suite total
  3. Walk-forward static OOS → aggregate OOS metrics
  4. Per-quarter group-P/L slice → count of negative quarters

Prints a comparative scoreboard. No per-archetype tuning — the point is the
SHAPE of strategy space, not knob-level optimization within one shape.
"""

from __future__ import annotations
import argparse
import warnings

import data
import strategies
from backtest import Backtester, compute_metrics, groupwise_pnl_by_period
from run_scenarios import run_suite
from optimize import walk_forward_static
from archetypes import ARCHETYPES

warnings.filterwarnings('ignore')


def run_5y(df, cfg, ticker):
    bt = Backtester(
        df=df, config=cfg,
        entry_fn=strategies.pick_entry, exit_fn=strategies.check_exits,
        ticker=ticker,
        wheel_cc_fn=strategies.pick_covered_call if cfg.wheel_enabled else None,
        roll_fn=strategies.pick_roll if cfg.roll_on_max_loss else None,
    )
    bt.run()
    return compute_metrics(bt.trades), bt.trades


def scenario_summary(rows: list[dict]) -> dict:
    """Aggregate per-regime metrics into worst / total / profitable count."""
    total = 0.0
    profitable = 0
    available = 0
    worst_regime = None
    worst_pnl = float('inf')
    catastrophe = False  # any regime below -$500
    for r in rows:
        if not r['available']:
            continue
        available += 1
        m = r['metrics']
        pnl = m.get('total_pnl_per_contract', 0.0)
        total += pnl
        if pnl > 0:
            profitable += 1
        if pnl < worst_pnl:
            worst_pnl = pnl
            worst_regime = r['regime']
        if pnl < -500.0:
            catastrophe = True
    return {
        'available': available,
        'profitable': profitable,
        'total_pnl': total,
        'worst_regime': worst_regime,
        'worst_pnl': worst_pnl if available else 0.0,
        'catastrophe': catastrophe,
    }


def oos_summary(df, cfg):
    """Walk-forward static OOS aggregate. Suppresses per-window noise."""
    results = walk_forward_static(df, cfg)
    if not results:
        return {'n_windows': 0, 'total_pnl': 0.0, 'worst_window_pnl': 0.0, 'mean_window_pnl': 0.0}
    pnls = [r['oos_metrics'].get('total_pnl_per_contract', 0.0) for r in results]
    return {
        'n_windows': len(pnls),
        'total_pnl': sum(pnls),
        'worst_window_pnl': min(pnls),
        'mean_window_pnl': sum(pnls) / len(pnls),
    }


def per_quarter_negatives(trades):
    """Count quarters with negative group-P/L total."""
    per_q = groupwise_pnl_by_period(trades, freq='Q')
    if per_q.empty:
        return 0, 0
    n_neg = int((per_q['group_pnl'] < 0).sum())
    return n_neg, len(per_q)


def run_one_archetype(name, cfg, ticker, df):
    """Returns a row dict ready for the scoreboard."""
    m, trades = run_5y(df, cfg, ticker)
    suite_rows = run_suite(ticker, df, cfg)
    scen = scenario_summary(suite_rows)
    oos = oos_summary(df, cfg)
    n_neg_q, n_q = per_quarter_negatives(trades)
    return {
        'archetype': name,
        'ticker': ticker,
        '5y_pnl': m.get('total_pnl_per_contract', 0.0),
        '5y_max_dd': m.get('max_dd_per_contract', 0.0),
        'n_trades': m.get('n_trades', 0),
        'n_groups': m.get('n_groups', 0),
        'group_win_rate': m.get('group_win_rate_pct', 0.0),
        'worst_group': m.get('worst_group_pnl_per_contract', 0.0),
        'avg_positions_per_group': m.get('avg_positions_per_group', 1.0),
        'pnl_per_cap_yr': m.get('pnl_per_capital_year_pct', 0.0),
        'trade_density': m.get('trade_density_per_year', 0.0),
        'suite_total': scen['total_pnl'],
        'suite_worst': scen['worst_pnl'],
        'suite_worst_regime': scen['worst_regime'],
        'suite_catastrophe': scen['catastrophe'],
        'suite_profitable': f"{scen['profitable']}/{scen['available']}",
        'oos_total': oos['total_pnl'],
        'oos_worst': oos['worst_window_pnl'],
        'oos_windows': oos['n_windows'],
        'neg_quarters': n_neg_q,
        'total_quarters': n_q,
    }


def print_scoreboard(rows: list[dict], ticker: str):
    rows = [r for r in rows if r['ticker'] == ticker]
    print(f"\n{'=' * 110}")
    print(f"=== {ticker} — archetype scoreboard ===")
    print('=' * 110)
    header = (
        f"{'archetype':<14}  "
        f"{'5y P/L':>9}  {'maxDD':>7}  {'grps':>5}  {'WR%':>5}  "
        f"{'worst':>8}  {'pos/grp':>7}  {'cap/yr%':>8}  {'dens/yr':>8}  "
        f"{'suiteΣ':>8}  {'worstR':>7}  {'OOSΣ':>8}  {'-Qrs':>5}"
    )
    print(header)
    print('-' * 110)
    for r in rows:
        cata = '⚠' if r['suite_catastrophe'] else ' '
        print(
            f"{r['archetype']:<14}  "
            f"${r['5y_pnl']:>8.0f}  ${r['5y_max_dd']:>6.0f}  "
            f"{r['n_groups']:>5d}  {r['group_win_rate']:>5.1f}  "
            f"${r['worst_group']:>7.0f}  {r['avg_positions_per_group']:>7.2f}  "
            f"{r['pnl_per_cap_yr']:>7.1f}%  {r['trade_density']:>7.1f}  "
            f"${r['suite_total']:>7.0f}{cata} ${r['suite_worst']:>5.0f}  "
            f"${r['oos_total']:>7.0f}  {r['neg_quarters']:>2d}/{r['total_quarters']:<2d}"
        )
    print('-' * 110)
    print("legend:")
    print("  grps        = trade groups (chain of rolls = one group)")
    print("  WR%         = group win rate (% of groups with P/L ≥ 0)")
    print("  worst       = worst group P/L (per contract)")
    print("  pos/grp     = avg positions per group (>1 means chains formed)")
    print("  cap/yr%     = annualized return on capital-at-risk × days")
    print("  dens/yr     = groups per market-year")
    print("  suiteΣ      = sum of regime P/Ls; ⚠ = any regime below −$500 (catastrophe)")
    print("  worstR      = worst single regime P/L")
    print("  OOSΣ        = walk-forward static OOS aggregate")
    print("  -Qrs        = quarters with negative group-P/L total / total quarters")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tickers', nargs='+', default=['TSLA', 'TSLL'])
    ap.add_argument('--archetypes', nargs='+', default=None,
                    help='subset of archetypes to run (default: all)')
    ap.add_argument('--period', default='5y')
    args = ap.parse_args()

    archetype_names = args.archetypes or list(ARCHETYPES.keys())

    all_rows = []
    for ticker in args.tickers:
        df = data.build(ticker, period=args.period)
        for name in archetype_names:
            cfg = ARCHETYPES[name].get(ticker)
            if cfg is None:
                continue
            print(f"  running {name} × {ticker}…", flush=True)
            row = run_one_archetype(name, cfg, ticker, df)
            all_rows.append(row)

    for ticker in args.tickers:
        print_scoreboard(all_rows, ticker)

    print("\nNext step: pick the winner per ticker; re-derive adaptive rules from its trade log via `just analyze`.")


if __name__ == '__main__':
    main()

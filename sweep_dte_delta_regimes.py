"""Validate top DTE × delta candidates against the 12-regime scenario suite.

Per cost function: a config can't be a winner if any regime catastrophically loses.
"""

from data import build
from backtest import Backtester, compute_metrics
from strategies import StrategyConfig, pick_entry, check_exits
from scenarios import REGIMES, canonical_window


# Top candidates from sweep_dte_delta.py
CANDIDATES = {
    'TSLA': [
        ('v1.3 baseline', 30, 0.15),
        ('7d × 0.20 (top score)', 7, 0.20),
        ('10d × 0.15 (top PF)', 10, 0.15),
        ('5d × 0.20', 5, 0.20),
        ('7d × 0.15 (low DD)', 7, 0.15),
        ('3d × 0.25', 3, 0.25),
    ],
    'TSLL': [
        ('v1.3 baseline', 30, 0.15),
        ('3d × 0.30 (top score)', 3, 0.30),
        ('3d × 0.25', 3, 0.25),
        ('21d × 0.15 (most trades)', 21, 0.15),
        ('3d × 0.10', 3, 0.10),
    ],
}


def run_suite(ticker: str, df, cfg: StrategyConfig):
    rows = {}
    for regime in REGIMES:
        w = canonical_window(df, ticker, regime)
        if w is None:
            continue
        bt = Backtester(df=w, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker)
        bt.run()
        m = compute_metrics(bt.trades)
        rows[regime] = {
            'pnl': m.get('total_pnl_per_contract', 0),
            'n': m.get('n_trades', 0),
            'dd': m.get('max_dd_per_contract', 0),
        }
    return rows


for ticker, candidates in CANDIDATES.items():
    df = build(ticker, period='5y')
    print(f"\n========== {ticker}: per-regime P/L across candidates ==========\n")

    # Header
    print(f"{'regime':<18} " + " | ".join([f"{label:>22}" for label, _, _ in candidates]))
    print('-' * (20 + 25 * len(candidates)))

    # One row per regime
    suite_results = {label: run_suite(ticker, df, StrategyConfig(long_dte=dte, long_target_delta=delta)) for label, dte, delta in candidates}

    available_regimes = REGIMES
    for regime in available_regimes:
        cells = []
        for label, _, _ in candidates:
            r = suite_results[label].get(regime)
            if r is None:
                cells.append(f"{'—':>22}")
            else:
                cells.append(f"  ${r['pnl']:>+7.0f} (n={r['n']:>2}) DD${r['dd']:>4.0f}")
        print(f"{regime:<18} " + " | ".join(cells))

    # Suite totals
    print('-' * (20 + 25 * len(candidates)))
    totals = []
    for label, _, _ in candidates:
        total = sum(r['pnl'] for r in suite_results[label].values())
        worst = min((r['pnl'] for r in suite_results[label].values()), default=0)
        total_n = sum(r['n'] for r in suite_results[label].values())
        totals.append((label, total, worst, total_n))
    print(f"{'TOTAL P/L':<18} " + " | ".join([f"  ${t[1]:>+7.0f} (n={t[3]:>3})       " for t in totals]))
    print(f"{'WORST regime':<18} " + " | ".join([f"  ${t[2]:>+7.0f}                  " for t in totals]))

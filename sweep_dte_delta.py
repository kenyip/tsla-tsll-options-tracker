"""Grid sweep: long_dte × long_target_delta on the 5y backtest.

Scoring: P/L - 1.0 × max_dd (heavier DD weight than optimizer's 0.5 — per cost function).
Min trades = 10 to avoid degenerate winners with tiny trade counts.
"""

import itertools

from data import build
from backtest import Backtester, compute_metrics
from strategies import StrategyConfig, pick_entry, check_exits


DTES = [3, 5, 7, 10, 14, 21, 30, 45]
DELTAS = [0.10, 0.15, 0.20, 0.25, 0.30]
MIN_TRADES = 10


def run_one(ticker: str, df, dte: int, delta: float) -> dict:
    cfg = StrategyConfig(long_dte=dte, long_target_delta=delta)
    bt = Backtester(df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker)
    bt.run()
    m = compute_metrics(bt.trades)
    reasons = m.get('exit_reasons', {})
    return {
        'dte': dte,
        'delta': delta,
        'pnl': m.get('total_pnl_per_contract', 0),
        'n': m.get('n_trades', 0),
        'wr': m.get('win_rate_pct', 0),
        'dd': m.get('max_dd_per_contract', 0),
        'pf': m.get('profit_factor', 0),
        'days_held': m.get('avg_days_held', 0),
        'max_loss_n': reasons.get('max_loss', 0),
        'expired_n': reasons.get('expired', 0),
    }


for ticker in ('TSLA', 'TSLL'):
    df = build(ticker, period='5y')
    print(f"\n========== {ticker} sweep ({len(DTES)}×{len(DELTAS)} = {len(DTES)*len(DELTAS)} configs) ==========")

    results = []
    for dte, delta in itertools.product(DTES, DELTAS):
        r = run_one(ticker, df, dte, delta)
        r['score'] = r['pnl'] - 1.0 * r['dd']
        results.append(r)

    # Filter by min trade count, then sort by score
    eligible = [r for r in results if r['n'] >= MIN_TRADES]
    eligible_sorted = sorted(eligible, key=lambda r: r['score'], reverse=True)

    # Also rank by individual metrics
    by_pnl = sorted(eligible, key=lambda r: r['pnl'], reverse=True)
    by_pf = sorted(eligible, key=lambda r: r['pf'], reverse=True)
    by_dd_inv = sorted(eligible, key=lambda r: r['dd'])  # lowest DD

    print(f"\n--- Top 10 by composite score (P/L - 1.0 × DD), min trades = {MIN_TRADES} ---")
    print(f"{'DTE':>4} {'Δ':>5} {'P/L':>9} {'n':>4} {'wr%':>5} {'DD':>7} {'PF':>5} {'days':>5} {'ML':>3} {'score':>9}")
    for r in eligible_sorted[:10]:
        print(f"{r['dte']:>4} {r['delta']:>5.2f} ${r['pnl']:>+7.0f} {r['n']:>4} {r['wr']:>4.1f}% ${r['dd']:>6.0f} {r['pf']:>5.2f} {r['days_held']:>5.1f} {r['max_loss_n']:>3} {r['score']:>+9.0f}")

    print(f"\n--- Top 5 by raw P/L ---")
    print(f"{'DTE':>4} {'Δ':>5} {'P/L':>9} {'n':>4} {'wr%':>5} {'DD':>7} {'PF':>5}")
    for r in by_pnl[:5]:
        print(f"{r['dte']:>4} {r['delta']:>5.2f} ${r['pnl']:>+7.0f} {r['n']:>4} {r['wr']:>4.1f}% ${r['dd']:>6.0f} {r['pf']:>5.2f}")

    print(f"\n--- Top 5 by lowest DD (still profitable) ---")
    print(f"{'DTE':>4} {'Δ':>5} {'P/L':>9} {'n':>4} {'wr%':>5} {'DD':>7} {'PF':>5}")
    for r in [x for x in by_dd_inv if x['pnl'] > 0][:5]:
        print(f"{r['dte']:>4} {r['delta']:>5.2f} ${r['pnl']:>+7.0f} {r['n']:>4} {r['wr']:>4.1f}% ${r['dd']:>6.0f} {r['pf']:>5.2f}")

    # Show the full grid in compact form
    print(f"\n--- Full grid (P/L per contract, $) ---")
    header = 'DTE / Δ'
    print(f"{header:>8} | " + " ".join([f"{d:>7.2f}" for d in DELTAS]))
    print("-" * (12 + 8 * len(DELTAS)))
    for dte in DTES:
        row = [f"{dte:>4}d   |"]
        for delta in DELTAS:
            r = next((x for x in results if x['dte'] == dte and x['delta'] == delta), None)
            cell = f"{r['pnl']:>+7.0f}" if r and r['n'] >= MIN_TRADES else f"{'—':>7}"
            row.append(cell)
        print(" ".join(row))

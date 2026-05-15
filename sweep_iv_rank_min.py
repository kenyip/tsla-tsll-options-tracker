"""LLM-critic round 3: sweep iv_rank_min at v1.7 per-ticker defaults.

Hypothesis: iv_rank_min=10 (v1.1 default) is too low. Most filtering is done by
min_credit_pct, so iv_rank_min has been dormant. Raising it filters for richer
relative premium — high iv_rank means the market is pricing in more risk than
usual, which is exactly when a premium seller wants to be in.
"""

from dataclasses import replace
from data import build
from backtest import Backtester, compute_metrics
from strategies import pick_entry, check_exits, get_config
from scenarios import REGIMES, canonical_window


def run_5y(ticker, cfg):
    df = build(ticker, period='5y')
    bt = Backtester(df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker)
    bt.run()
    m = compute_metrics(bt.trades)
    return {
        'pnl': m.get('total_pnl_per_contract', 0),
        'n': m.get('n_trades', 0),
        'wr': m.get('win_rate_pct', 0),
        'dd': m.get('max_dd_per_contract', 0),
        'pf': m.get('profit_factor', 0),
        'per_trade': m.get('avg_pnl_per_contract', 0),
    }


def run_suite(ticker, cfg):
    df = build(ticker, period='5y')
    results = {}
    for r in REGIMES:
        w = canonical_window(df, ticker, r)
        if w is None:
            continue
        bt = Backtester(df=w, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker)
        bt.run()
        m = compute_metrics(bt.trades)
        results[r] = m.get('total_pnl_per_contract', 0)
    total = sum(results.values())
    worst = min(results.values())
    return total, worst


for ticker in ('TSLA', 'TSLL'):
    base = get_config(ticker)
    print(f"\n========== {ticker} (current iv_rank_min={base.iv_rank_min}) ==========")
    print(f"{'iv_rank_min':>12}  {'P/L (5y)':>10} {'n':>4} {'wr%':>5} {'DD':>7} {'PF':>5}  {'per-trade':>10}  {'suite':>9}  {'worst':>9}")
    for v in [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0]:
        cfg = replace(base, iv_rank_min=v)
        f = run_5y(ticker, cfg)
        suite_total, worst = run_suite(ticker, cfg)
        mark = '←' if v == base.iv_rank_min else ' '
        print(f"{v:>12.0f}  ${f['pnl']:>+8.0f} {f['n']:>4} {f['wr']:>4.1f}% ${f['dd']:>6.0f} {f['pf']:>5.2f}   ${f['per_trade']:>+7.0f}    ${suite_total:>+7.0f}  ${worst:>+7.0f}  {mark}")

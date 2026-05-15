"""LLM-critic round 4: sweep profit_target at v1.7 per-ticker defaults.

Hypothesis: profit_target=0.55 (v1.1 default) is too low under v1.7's relaxed
daily_capture_mult_short=2.0 (TSLA) / 1.25 (TSLL). At 7-DTE, steady theta is
~14%/day, so 0.55 fires around day 4. Raising to 0.70-0.75 would let slow-decay
winners ride to day 5-6, capturing more of the available theta. Risk: more
gamma exposure during high-gamma final days.
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
    reasons = m.get('exit_reasons', {})
    return {
        'pnl': m.get('total_pnl_per_contract', 0),
        'n': m.get('n_trades', 0),
        'wr': m.get('win_rate_pct', 0),
        'dd': m.get('max_dd_per_contract', 0),
        'pf': m.get('profit_factor', 0),
        'days': m.get('avg_days_held', 0),
        'pt': reasons.get('profit_target', 0),
        'dc': reasons.get('daily_capture', 0),
        'exp': reasons.get('expired', 0),
        'ml': reasons.get('max_loss', 0),
        'db': reasons.get('delta_breach', 0),
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
    return sum(results.values()), min(results.values())


for ticker in ('TSLA', 'TSLL'):
    base = get_config(ticker)
    print(f"\n========== {ticker} (current profit_target={base.profit_target}) ==========")
    print(f"{'pt':>5}  {'P/L (5y)':>10} {'n':>4} {'wr%':>5} {'DD':>7} {'PF':>5}  {'days':>5}  {'PT':>3} {'DC':>3} {'EXP':>3} {'ML':>3} {'DB':>3}  {'suite':>9}  {'worst':>9}")
    for v in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.90]:
        cfg = replace(base, profit_target=v)
        f = run_5y(ticker, cfg)
        suite_total, worst = run_suite(ticker, cfg)
        mark = '←' if v == base.profit_target else ' '
        print(f"{v:>5.2f} ${f['pnl']:>+8.0f} {f['n']:>4} {f['wr']:>4.1f}% ${f['dd']:>6.0f} {f['pf']:>5.2f}  {f['days']:>4.1f}  {f['pt']:>3} {f['dc']:>3} {f['exp']:>3} {f['ml']:>3} {f['db']:>3}  ${suite_total:>+7.0f}  ${worst:>+7.0f}  {mark}")

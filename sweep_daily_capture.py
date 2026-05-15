"""LLM-critic round 2: sweep daily_capture_mult_short at v1.6 per-ticker defaults.

Hypothesis: daily_capture_mult_short=1.0 (v1.1 default) is too eager for v1.5+ short-DTE entries.
At DTE=7, theta is ~14% of credit per day, so the rung fires on day 1 with only ~14% of credit
captured. Higher multipliers might let winners run further toward expired-OTM.
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
        'dc': reasons.get('daily_capture', 0),
        'exp': reasons.get('expired', 0),
        'ml': reasons.get('max_loss', 0),
        'db': reasons.get('delta_breach', 0),
        'days': m.get('avg_days_held', 0),
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
    print(f"\n========== {ticker} (DTE={base.long_dte}, Δ={base.long_target_delta}, daily_capture_mult_short={base.daily_capture_mult_short}) ==========")
    print(f"{'mult':>5}  {'P/L (5y)':>10} {'n':>4} {'wr%':>5} {'DD':>7} {'PF':>5}  {'days':>5}  {'DC':>3} {'EXP':>3} {'ML':>3} {'DB':>3}  {'suite':>9} {'worst':>9}")
    for v in [0.5, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]:
        cfg = replace(base, daily_capture_mult_short=v)
        f = run_5y(ticker, cfg)
        suite_total, worst = run_suite(ticker, cfg)
        mark = '←' if v == base.daily_capture_mult_short else ' '
        print(f"{v:>5.2f} ${f['pnl']:>+8.0f} {f['n']:>4} {f['wr']:>4.1f}% ${f['dd']:>6.0f} {f['pf']:>5.2f}  {f['days']:>4.1f}  {f['dc']:>3} {f['exp']:>3} {f['ml']:>3} {f['db']:>3}  ${suite_total:>+7.0f}  ${worst:>+7.0f}  {mark}")

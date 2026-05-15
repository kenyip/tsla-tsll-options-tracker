"""LLM-critic proposal: sweep delta_breach at v1.5 per-ticker defaults.

Hypothesis: delta_breach=0.38 was calibrated for 30-DTE puts. With v1.5's
short-DTE puts (TSLA 7d, TSLL 3d), gamma is much higher and 0.38 fires on
routine noise, converting potential winners to realized losers.
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
        'db_exits': reasons.get('delta_breach', 0),
        'ml_exits': reasons.get('max_loss', 0),
        'dc_exits': reasons.get('daily_capture', 0),
        'exp_exits': reasons.get('expired', 0),
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
        results[r] = {
            'pnl': m.get('total_pnl_per_contract', 0),
            'n': m.get('n_trades', 0),
        }
    total = sum(r['pnl'] for r in results.values())
    worst = min((r['pnl'] for r in results.values() if r['n'] > 0), default=0)
    return total, worst, results


for ticker in ('TSLA', 'TSLL'):
    base = get_config(ticker)
    print(f"\n========== {ticker} (DTE={base.long_dte}, Δ={base.long_target_delta}) ==========")
    print(f"{'delta_breach':>14}  {'P/L (5y)':>10} {'n':>4} {'wr%':>5} {'DD':>7} {'PF':>5}  {'DB':>3} {'ML':>3} {'DC':>3} {'EXP':>3}  {'suite':>9} {'worst regime':>13}")

    for v in [0.30, 0.35, 0.38, 0.45, 0.50, 0.55, 0.60]:
        cfg = replace(base, delta_breach=v)
        f = run_5y(ticker, cfg)
        suite_total, worst, _ = run_suite(ticker, cfg)
        mark = '←' if v == base.delta_breach else ' '
        print(f"{v:>14.2f} ${f['pnl']:>+8.0f} {f['n']:>4} {f['wr']:>4.1f}% ${f['dd']:>6.0f} {f['pf']:>5.2f} {f['db_exits']:>4} {f['ml_exits']:>3} {f['dc_exits']:>3} {f['exp_exits']:>4}  ${suite_total:>+7.0f}  ${worst:>+11.0f}  {mark}")

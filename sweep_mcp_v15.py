"""Sweep min_credit_pct with v1.5 DTE/delta defaults to find the right floor."""

from dataclasses import replace
from data import build
from backtest import Backtester, compute_metrics
from strategies import StrategyConfig, pick_entry, check_exits, get_config


def run(ticker, cfg):
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
        'ml': m.get('exit_reasons', {}).get('max_loss', 0),
    }


for ticker in ('TSLA', 'TSLL'):
    print(f"\n=== {ticker} (DTE/delta from v1.5 per-ticker default) ===")
    base = get_config(ticker)
    print(f"{'mcp':>8}   {'P/L':>9}   {'n':>4} {'wr%':>5} {'DD':>7} {'PF':>5} {'ML':>3} {'score (P/L - DD)':>16}")
    for v in [0.000, 0.003, 0.005, 0.007, 0.008, 0.010, 0.012, 0.015, 0.020]:
        cfg = replace(base, min_credit_pct=v)
        r = run(ticker, cfg)
        score = r['pnl'] - r['dd']
        print(f"{v:>8.4f}  ${r['pnl']:>+7.0f}   {r['n']:>4} {r['wr']:>4.1f}% ${r['dd']:>6.0f} {r['pf']:>5.2f} {r['ml']:>3} {score:>+16.0f}")

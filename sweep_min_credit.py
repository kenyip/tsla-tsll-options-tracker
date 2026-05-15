from data import build
from backtest import Backtester, compute_metrics
from strategies import StrategyConfig, pick_entry, check_exits
from scenarios import REGIMES, canonical_window


def suite_total(ticker, cfg):
    df = build(ticker, period='5y')
    total = 0.0
    n_total = 0
    for r in REGIMES:
        w = canonical_window(df, ticker, r)
        if w is None:
            continue
        bt = Backtester(df=w, config=cfg, entry_fn=pick_entry, exit_fn=check_exits)
        bt.run()
        m = compute_metrics(bt.trades)
        total += m.get('total_pnl_per_contract', 0)
        n_total += m.get('n_trades', 0)
    return total, n_total


def full_total(ticker, cfg):
    df = build(ticker, period='5y')
    bt = Backtester(df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits)
    bt.run()
    m = compute_metrics(bt.trades)
    return m.get('total_pnl_per_contract', 0), m.get('n_trades', 0), m.get('max_dd_per_contract', 0)


hdr = f"{'mcp':>6}  {'TSLA suite':>11}  {'TSLL suite':>11}   {'TSLA 5y':>9}/{'n':>3}/{'dd':>5}    {'TSLL 5y':>9}/{'n':>3}/{'dd':>5}"
print(hdr)
print('-' * len(hdr))
for v in [0.0, 0.003, 0.005, 0.008, 0.010, 0.015, 0.020, 0.030]:
    cfg = StrategyConfig(min_credit_pct=v)
    tsla_s, _ = suite_total('TSLA', cfg)
    tsll_s, _ = suite_total('TSLL', cfg)
    tsla_f, tsla_fn, tsla_fdd = full_total('TSLA', cfg)
    tsll_f, tsll_fn, tsll_fdd = full_total('TSLL', cfg)
    print(f"{v:>6.4f}  ${tsla_s:>+10.0f}  ${tsll_s:>+10.0f}   ${tsla_f:>+8.0f}/{tsla_fn:>3}/${tsla_fdd:>5.0f}    ${tsll_f:>+8.0f}/{tsll_fn:>3}/${tsll_fdd:>5.0f}")

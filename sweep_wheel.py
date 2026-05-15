"""Sweep wheel-mode configurations to see how max_loss tolerance affects results."""

from dataclasses import replace
from data import build
from backtest import Backtester, compute_metrics
from strategies import StrategyConfig, pick_entry, check_exits, pick_covered_call


def run(ticker: str, cfg: StrategyConfig):
    df = build(ticker, period='5y')
    bt = Backtester(
        df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker,
        wheel_cc_fn=pick_covered_call if cfg.wheel_enabled else None,
    )
    bt.run()
    m = compute_metrics(bt.trades)
    reasons = m.get('exit_reasons', {})
    return {
        'pnl': m.get('total_pnl_per_contract', 0),
        'n': m.get('n_trades', 0),
        'wr': m.get('win_rate_pct', 0),
        'dd': m.get('max_dd_per_contract', 0),
        'pf': m.get('profit_factor', 0),
        'assigned': reasons.get('assigned', 0),
        'assigned_away': reasons.get('assigned_away', 0),
        'wheel_closes': reasons.get('wheel_close', 0),
        'max_loss': reasons.get('max_loss', 0),
        'reasons': reasons,
    }


configs = [
    ('cash-only v1.3 baseline', StrategyConfig(wheel_enabled=False)),
    ('wheel, 14-DTE puts, max_loss=3.0, skip regime_flip', StrategyConfig(
        wheel_enabled=True, wheel_put_dte=14, wheel_put_max_loss_mult=3.0, wheel_skip_regime_flip=True)),
    ('wheel, 14-DTE puts, max_loss=1.8, skip regime_flip', StrategyConfig(
        wheel_enabled=True, wheel_put_dte=14, wheel_put_max_loss_mult=1.8, wheel_skip_regime_flip=True)),
    ('wheel, 14-DTE puts, max_loss=5.0, skip regime_flip', StrategyConfig(
        wheel_enabled=True, wheel_put_dte=14, wheel_put_max_loss_mult=5.0, wheel_skip_regime_flip=True)),
    ('wheel, 14-DTE puts, max_loss=3.0, KEEP regime_flip', StrategyConfig(
        wheel_enabled=True, wheel_put_dte=14, wheel_put_max_loss_mult=3.0, wheel_skip_regime_flip=False)),
    ('wheel, 7-DTE puts, max_loss=3.0, skip regime_flip', StrategyConfig(
        wheel_enabled=True, wheel_put_dte=7, wheel_put_max_loss_mult=3.0, wheel_skip_regime_flip=True)),
    ('wheel, 30-DTE puts, max_loss=3.0, skip regime_flip', StrategyConfig(
        wheel_enabled=True, wheel_put_dte=30, wheel_put_max_loss_mult=3.0, wheel_skip_regime_flip=True)),
]

print(f"{'configuration':>48}   {'P/L':>8}   {'n':>4} {'wr%':>5} {'DD':>6} {'PF':>5}  {'assigned':>8} {'cycled':>6} {'max_loss':>8}")
print('-' * 130)
for ticker in ('TSLA', 'TSLL'):
    print(f"\n  --- {ticker} ---")
    for label, cfg in configs:
        r = run(ticker, cfg)
        print(f"{label:>48}  ${r['pnl']:>+7.0f}   {r['n']:>4} {r['wr']:>4.1f}% ${r['dd']:>5.0f} {r['pf']:>5.2f}  {r['assigned']:>8} {r['wheel_closes']:>6} {r['max_loss']:>8}")
        if r['n'] > 0 and cfg.wheel_enabled:
            print(f"{'':>48}   exits: {r['reasons']}")

#!/usr/bin/env python3
"""
Live daily recommendation — runs the engine's entry signal on today's market state.

This is the single source of truth for live recommendations. It uses the SAME
`pick_entry()` function as the backtest engine, so any tuning of `strategies.py`
or `StrategyConfig` defaults automatically flows through to what we'd recommend
to trade today. No parallel codebase, no drift between backtest and live.

CLI: `just test` (prints recs for TSLA + TSLL).
Dashboard: imported by `tsla_options_dashboard.py`.
"""

from __future__ import annotations
from dataclasses import asdict
import pandas as pd

from data import build
from strategies import StrategyConfig, pick_entry, get_config


def make_recommendation(ticker: str, cfg: StrategyConfig | None = None,
                        df: pd.DataFrame | None = None) -> dict:
    """
    Compute today's recommendation for `ticker`.

    Returns a dict that the CLI pretty-prints and the dashboard renders. If no
    trade signals, returns {'action': 'STAND_ASIDE', 'reason': '...'}.
    """
    cfg = cfg or get_config(ticker)
    if df is None:
        df = build(ticker, period='2y')

    today_row = df.iloc[-1]
    today_date = df.index[-1]
    spot = float(today_row['close'])

    position = pick_entry(today_row, cfg, spot, today_date)

    features = {
        'iv_rank':         float(today_row['iv_rank']),
        'iv_proxy':        float(today_row['iv_proxy']),
        'ret_14d_pct':     float(today_row['ret_14d']) * 100,
        'rsi_14':          float(today_row['rsi_14']),
        'macd_hist':       float(today_row['macd_hist']),
        'volume_surge':    float(today_row['volume_surge']),
        'intraday_ret_pct': float(today_row['intraday_return']),
        'regime':          str(today_row['regime']),
        'reversal':        bool(today_row['reversal']),
        'high_iv':         bool(today_row['high_iv']),
    }

    base = {
        'ticker': ticker,
        'date': today_date,
        'spot': spot,
        'features': features,
        'config_snapshot': asdict(cfg),
    }

    if position is None:
        base['action'] = 'STAND_ASIDE'
        base['reason'] = _why_no_trade(today_row, cfg)
        return base

    base['action'] = f"SELL_{position.side.upper()}"
    base['strike'] = float(position.strike)
    base['expiration'] = position.expiration
    base['dte'] = position.dte_at_entry
    base['estimated_credit'] = float(position.credit)
    base['iv_used'] = float(position.iv_at_entry)
    base['daily_theta_target'] = float(position.daily_theta_target)
    base['regime_at_entry'] = position.regime_at_entry

    base['exit_targets'] = {
        'profit_target_credit':  float(position.credit * cfg.profit_target),
        'profit_target_buyback': float(position.credit * (1 - cfg.profit_target)),
        'max_loss_credit':       float(position.credit * cfg.max_loss_mult),
        'max_loss_buyback':      float(position.credit * (1 + cfg.max_loss_mult)),
        'daily_capture_per_day': float(position.daily_theta_target * position.daily_capture_mult),
        'delta_breach':          cfg.delta_breach,
        'dte_stop_at':           cfg.dte_stop if position.dte_at_entry > cfg.dte_stop_min_entry else None,
    }
    return base


def _why_no_trade(row, cfg: StrategyConfig) -> str:
    if not pd.notna(row['iv_proxy']) or row['iv_proxy'] <= 0:
        return "no valid IV"
    if row['iv_rank'] < cfg.iv_rank_min:
        return f"iv_rank {row['iv_rank']:.1f} below floor {cfg.iv_rank_min}"
    if row['regime'] == 'bearish' and cfg.bear_dte <= 0:
        return "regime classified bearish — bear_dte=0 so skip premium selling"

    # If we got past the gates, the most likely cause is the credit/strike floor.
    # Compute what the rejected entry would have looked like for the side we'd
    # have picked (call in bearish when bear_dte>0; put otherwise).
    import pricing
    iv = float(row['iv_proxy'])
    S = float(row['close'])
    if row['regime'] == 'bearish':
        side, dte, td = 'call', cfg.bear_dte, cfg.bear_target_delta
    else:
        side, dte, td = 'put', cfg.long_dte, cfg.long_target_delta
    try:
        K_exact = pricing.strike_from_delta(S, dte / 365.0, iv, td, side, r=cfg.risk_free_rate)
        K = pricing.round_strike(K_exact, 2.5)
        credit = pricing.price(S, K, dte / 365.0, iv, side, r=cfg.risk_free_rate) * (1.0 - cfg.slippage_pct)
        if K > 0 and credit / K < cfg.min_credit_pct:
            return (
                f"premium too thin — {dte}-DTE Δ{td} {side} at ${K:.2f} would "
                f"collect ${credit:.2f} = {credit/K*100:.2f}% of strike "
                f"(floor {cfg.min_credit_pct*100:.1f}%). Need higher IV to enter."
            )
    except Exception:
        pass
    return "filtered (check classifier)"


def format_recommendation(rec: dict) -> str:
    lines = []
    lines.append(f"=== {rec['ticker']}  spot ${rec['spot']:.2f}  {rec['date'].date()} ===")
    f = rec['features']
    lines.append(f"  regime={f['regime']}  reversal={f['reversal']}  high_iv={f['high_iv']}")
    lines.append(f"  iv_rank={f['iv_rank']:.1f}  ret_14d={f['ret_14d_pct']:+.1f}%  "
                 f"rsi={f['rsi_14']:.1f}  intraday={f['intraday_ret_pct']:+.2f}%")

    if rec['action'] == 'STAND_ASIDE':
        lines.append(f"  >>> STAND ASIDE — {rec['reason']}")
        return '\n'.join(lines)

    side = rec['action'].split('_', 1)[1]
    lines.append(f"  >>> {rec['action']} ${rec['strike']:.2f} strike  "
                 f"exp {rec['expiration'].date() if hasattr(rec['expiration'], 'date') else rec['expiration']}  "
                 f"({rec['dte']} DTE)")
    lines.append(f"      estimated credit:  ${rec['estimated_credit']:.2f}/share  "
                 f"(${rec['estimated_credit']*100:.0f} per contract)")
    lines.append(f"      daily theta target: ${rec['daily_theta_target']:.3f}/share")

    e = rec['exit_targets']
    lines.append(f"  exit targets:")
    lines.append(f"    profit target  — buy back at ≤ ${e['profit_target_buyback']:.2f} "
                 f"(profit ≥ ${e['profit_target_credit']:.2f})")
    lines.append(f"    daily capture  — close when realised P/L per day held "
                 f"≥ ${e['daily_capture_per_day']:.3f}")
    lines.append(f"    max loss       — buy back at ≥ ${e['max_loss_buyback']:.2f} "
                 f"(loss ≥ ${e['max_loss_credit']:.2f})")
    lines.append(f"    delta breach   — close if |Δ| > {e['delta_breach']}")
    if e['dte_stop_at'] is not None:
        lines.append(f"    DTE stop       — close at ≤ {e['dte_stop_at']} DTE remaining")
    return '\n'.join(lines)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--tickers', nargs='+', default=['TSLA', 'TSLL'])
    args = ap.parse_args()

    for ticker in args.tickers:
        rec = make_recommendation(ticker)
        print(format_recommendation(rec))
        print()


if __name__ == "__main__":
    main()

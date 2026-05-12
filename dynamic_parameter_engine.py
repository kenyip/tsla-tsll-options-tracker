#!/usr/bin/env python3
"""
Dynamic Parameter Engine v6.3 - With Intraday Reversal Detection
"""

from datetime import datetime, timedelta

def get_expiration(dte):
    today = datetime(2026, 5, 12)
    exp = today + timedelta(days=dte)
    if exp.weekday() != 4:
        exp += timedelta(days=(4 - exp.weekday()) % 7)
    return exp.strftime("%b %d, %Y")

def estimate_strike(current_price, delta, dte, iv_rank, ticker='TSLA'):
    otm_pct = 0.065 + (delta - 0.20) * 0.15
    if iv_rank > 50: otm_pct *= 0.85
    strike = round(current_price * (1 - otm_pct), 0)
    if ticker == 'TSLL': strike = round(strike * 0.98, 0)
    return int(strike)

def get_dynamic_params(features, ticker='TSLA', current_price=445):
    iv = features.get('iv_rank', 13)
    ret_14d = features.get('recent_14d_return', 11.2)
    bias = features.get('bias', 'bullish')
    intraday_return = features.get('intraday_return', 0.0)  # NEW
    volume_surge = features.get('volume_surge', 1.0)
    
    # === NEW: Intraday Reversal Detection ===
    reversal = False
    if intraday_return < -3.0 and volume_surge > 1.5:
        reversal = True
    
    if ticker == 'TSLA':
        if reversal:
            direction = 'DEFENSIVE - SELL CALLS or IRON CONDOR'
            delta = 0.20
            dte = 22
            profit_target = 0.45
            size_note = "0.8% risk max - tight stops"
        elif bias == 'bullish' and ret_14d > 5 and iv < 40 and not reversal:
            direction = 'SELL PUTS'
            delta = 0.25
            dte = 30
            profit_target = 0.55
            size_note = "1-2% risk"
        elif bias == 'bearish' or ret_14d < -10:
            direction = 'SELL CALLS'
            delta = 0.19
            dte = 20
            profit_target = 0.45
            size_note = "0.8% risk"
        else:
            direction = 'SELL PUTS (reduced)'
            delta = 0.22
            dte = 26
            profit_target = 0.50
            size_note = "1% risk"
    else:  # TSLL
        if reversal:
            direction = 'REDUCE RISK - No new puts'
            delta = 0.16
            dte = 18
            profit_target = 0.40
            size_note = "0.3% risk max - focus on core"
        elif bias == 'bullish' and ret_14d > 5 and iv < 40:
            direction = 'SELL PUTS (smaller)'
            delta = 0.19
            dte = 24
            profit_target = 0.50
            size_note = "0.5-0.8% risk"
        else:
            direction = 'SELL PUTS (conservative)'
            delta = 0.18
            dte = 22
            profit_target = 0.45
            size_note = "0.5% max"
    
    exp_date = get_expiration(dte)
    strike = estimate_strike(current_price, delta, dte, iv, ticker)
    
    return {
        'ticker': ticker,
        'direction': direction,
        'delta': delta,
        'dte': dte,
        'expiration': exp_date,
        'strike': strike,
        'profit_target': profit_target,
        'size_note': size_note,
        'reversal_detected': reversal,
        'reason': f"14d={ret_14d}%, Intraday={intraday_return}%, IV={iv}"
    }

if __name__ == "__main__":
    # Current real-time example
    current = {'iv_rank': 13, 'recent_14d_return': 11.2, 'intraday_return': -4.4, 'volume_surge': 1.8, 'bias': 'bullish'}
    print("TSLA:", get_dynamic_params(current, 'TSLA', 425))
    print("TSLL:", get_dynamic_params(current, 'TSLL', 14.5))

#!/usr/bin/env python3
"""
Dynamic Parameter + Direction Engine (v6.2 - With Exact Expiration + Strike)
"""

from datetime import datetime, timedelta

def get_expiration(dte):
    """Calculate next valid expiration date (weeklies + monthlies)"""
    today = datetime(2026, 5, 12)
    exp = today + timedelta(days=dte)
    # Round to nearest Friday for weeklies or standard monthly
    if exp.weekday() != 4:  # Not Friday
        exp += timedelta(days=(4 - exp.weekday()) % 7)
    return exp.strftime("%b %d, %Y")

def estimate_strike(current_price, delta, dte, iv_rank, ticker='TSLA'):
    """Rough strike estimation for target delta (puts)"""
    # Approximate using Black-Scholes rule of thumb
    # For 0.25 delta put: ~7-9% OTM at 30 DTE, IV ~43%
    otm_pct = 0.065 + (delta - 0.20) * 0.15  # adjust for delta
    if iv_rank > 50:
        otm_pct *= 0.85  # tighter in high IV
    strike = round(current_price * (1 - otm_pct), 0)
    if ticker == 'TSLL':
        strike = round(strike * 0.98, 0)  # slightly more OTM for safety
    return int(strike)

def get_dynamic_params(features, ticker='TSLA', current_price=445):
    iv = features['iv_rank']
    ret = features['recent_14d_return']
    bias = features['bias']
    
    if ticker == 'TSLA':
        if bias == 'bullish' and ret > 5 and iv < 40:
            direction = 'SELL PUTS'
            delta = 0.25
            dte = 30
            profit_target = 0.55
            size_note = "1-2% risk"
        elif bias == 'bearish' or ret < -10:
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
        if bias == 'bullish' and ret > 5 and iv < 40:
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
        'reason': f"IV={iv}, 14d_ret={ret}%"
    }

if __name__ == "__main__":
    today = {'iv_rank': 13, 'recent_14d_return': 11.2, 'bias': 'bullish'}
    print(get_dynamic_params(today, 'TSLA'))
    print(get_dynamic_params(today, 'TSLL'))

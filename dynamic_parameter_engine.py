#!/usr/bin/env python3
"""
Dynamic Parameter Engine v6.6 - Clear Expiration Dates + Management Rules
"""

from datetime import datetime, timedelta

def get_expiration(dte):
    today = datetime(2026, 5, 12)
    target = today + timedelta(days=dte)
    # Find next Friday
    days_until_friday = (4 - target.weekday()) % 7
    if days_until_friday == 0 and target.weekday() != 4:
        days_until_friday = 7
    exp = target + timedelta(days=days_until_friday)
    return exp.strftime("%b %d, %Y (Friday)")

def estimate_strike(current_price, delta, dte, iv_rank, direction, ticker='TSLA'):
    is_call = 'CALL' in direction.upper()
    otm_pct = 0.065 + (delta - 0.20) * 0.12
    if iv_rank > 50: otm_pct *= 0.85
    if is_call:
        strike = round(current_price * (1 + otm_pct), 0)
    else:
        strike = round(current_price * (1 - otm_pct), 0)
    if ticker == 'TSLL':
        strike = round(strike * 0.97, 0)
    return int(strike)

def get_dynamic_params(features, ticker='TSLA', current_price=445):
    iv = features.get('iv_rank', 13)
    ret_14d = features.get('recent_14d_return', 11.2)
    bias = features.get('bias', 'bullish')
    intraday_return = features.get('intraday_return', 0.0)
    volume_surge = features.get('volume_surge', 1.0)
    
    reversal = intraday_return < -3.0 and volume_surge > 1.5
    high_iv = iv > 50
    use_short_term_calls = reversal or high_iv
    
    if ticker == 'TSLA':
        if use_short_term_calls:
            direction = 'SELL SHORT-TERM CALLS'
            delta = 0.20
            dte = 5
            profit_target = 0.45
            size_note = "0.6% risk - tight management"
        elif reversal:
            direction = 'DEFENSIVE - SELL CALLS or IRON CONDOR'
            delta = 0.20
            dte = 22
            profit_target = 0.45
            size_note = "0.8% risk max"
        elif bias == 'bullish' and ret_14d > 5 and iv < 40:
            direction = 'SELL PUTS'
            delta = 0.25
            dte = 30
            profit_target = 0.55
            size_note = "1-2% risk"
        else:
            direction = 'SELL PUTS (reduced)'
            delta = 0.22
            dte = 26
            profit_target = 0.50
            size_note = "1% risk"
    else:
        if use_short_term_calls:
            direction = 'SELL SHORT-TERM CALLS (small)'
            delta = 0.17
            dte = 4
            profit_target = 0.40
            size_note = "0.4% risk max"
        else:
            direction = 'SELL PUTS (conservative)'
            delta = 0.18
            dte = 22
            profit_target = 0.45
            size_note = "0.5% max"
    
    exp_date = get_expiration(dte)
    strike = estimate_strike(current_price, delta, dte, iv, direction, ticker)
    
    return {
        'ticker': ticker,
        'direction': direction,
        'delta': delta,
        'dte': dte,
        'expiration': exp_date,
        'strike': strike,
        'profit_target': profit_target,
        'size_note': size_note,
        'short_term_calls_active': use_short_term_calls,
        'reason': f"Reversal={reversal}, HighIV={high_iv}"
    }

if __name__ == "__main__":
    current = {'iv_rank': 13, 'recent_14d_return': 11.2, 'intraday_return': -4.4, 'volume_surge': 1.8, 'bias': 'bullish'}
    print(get_dynamic_params(current, 'TSLA', 425))
    print(get_dynamic_params(current, 'TSLL', 14.5))

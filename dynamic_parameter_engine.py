#!/usr/bin/env python3
"""
Dynamic Parameter + Direction Engine (v6.1 - TSLA + TSLL)
Outputs recommendations for both TSLA options and TSLL (core + options).
"""

def get_dynamic_params(features, ticker='TSLA'):
    iv = features['iv_rank']
    ret = features['recent_14d_return']
    bias = features['bias']
    
    if ticker == 'TSLA':
        if bias == 'bullish' and ret > 5 and iv < 40:
            direction = 'SELL PUTS'
            delta = 0.24 if iv < 20 else 0.26
            dte = 32 if iv < 25 else 28
            profit_target = 0.55
            size_note = "1-2% portfolio risk"
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
    else:  # TSLL - 2x leveraged, higher vol, lower liquidity
        if bias == 'bullish' and ret > 5 and iv < 40:
            direction = 'SELL PUTS (smaller size)'
            delta = 0.19          # Lower delta due to 2x gamma
            dte = 24             # Shorter DTE for gamma control
            profit_target = 0.50
            size_note = "0.5-0.8% risk (or just add core shares)"
        elif bias == 'bearish' or ret < -10:
            direction = 'REDUCE or HEDGE TSLL CORE'
            delta = 0.16
            dte = 18
            profit_target = 0.40
            size_note = "Minimal options - focus on core"
        else:
            direction = 'SELL PUTS (very conservative)'
            delta = 0.18
            dte = 22
            profit_target = 0.45
            size_note = "0.5% risk max"
    
    return {
        'ticker': ticker,
        'direction': direction,
        'delta': delta,
        'dte': dte,
        'profit_target': profit_target,
        'size_note': size_note,
        'reason': f"IV={iv}, 14d_ret={ret}%, bias={bias}"
    }

if __name__ == "__main__":
    today = {'iv_rank': 13, 'recent_14d_return': 11.2, 'rsi': 61, 'volume_surge': 1.55, 'bias': 'bullish'}
    print("TSLA:", get_dynamic_params(today, 'TSLA'))
    print("TSLL:", get_dynamic_params(today, 'TSLL'))

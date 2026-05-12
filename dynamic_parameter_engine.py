#!/usr/bin/env python3
"""
Dynamic Parameter + Direction Engine (v6)
Reads market features and outputs optimal DTE, delta, profit target, and put/call direction.
"""

def get_dynamic_params(features):
    """
    features = {
        'iv_rank': 13,
        'recent_14d_return': 11.2,
        'rsi': 61,
        'volume_surge': 1.55,
        'bias': 'bullish',          # from classify_scenario()
        'price_vs_ema200': 'above'
    }
    """
    iv = features['iv_rank']
    ret = features['recent_14d_return']
    bias = features['bias']
    
    # === DIRECTION DECISION ===
    if bias == 'bullish' and ret > 5 and iv < 40:
        direction = 'SELL PUTS'
        delta = 0.24 if iv < 20 else 0.26
        dte = 32 if iv < 25 else 28
        profit_target = 0.55
    elif bias == 'bearish' or ret < -10:
        direction = 'SELL CALLS'
        delta = 0.19
        dte = 20
        profit_target = 0.45
    else:
        direction = 'SELL PUTS (reduced)'
        delta = 0.22
        dte = 26
        profit_target = 0.50
    
    return {
        'direction': direction,
        'delta': delta,
        'dte': dte,
        'profit_target': profit_target,
        'reason': f"IV={iv}, 14d_ret={ret}%, bias={bias}"
    }

# Example for today (May 12 2026)
if __name__ == "__main__":
    today = {
        'iv_rank': 13,
        'recent_14d_return': 11.2,
        'rsi': 61,
        'volume_surge': 1.55,
        'bias': 'bullish'
    }
    params = get_dynamic_params(today)
    print("Today's Recommendation:")
    print(params)
    print(f"\nAction: {params['direction']} @ {params['delta']} delta, {params['dte']} DTE, target {params['profit_target']*100}% profit")

#!/usr/bin/env python3
"""
TSLA/TSLL Strategy v6 - Fully Dynamic (May 12 2026)
Integrates scenario classifier + dynamic DTE/delta/direction engine + TSLL core.
"""

from dynamic_parameter_engine import get_dynamic_params

class DynamicTSLA_TSLL_Strategy:
    def __init__(self):
        self.core_tsll = 350   # Long-term 2x directional core
    
    def daily_recommendation(self, current_price=445, iv_rank=13, recent_14d_return=11.2, rsi=61, volume_surge=1.55):
        features = {
            'iv_rank': iv_rank,
            'recent_14d_return': recent_14d_return,
            'rsi': rsi,
            'volume_surge': volume_surge,
            'bias': 'bullish' if current_price > 420 else 'bearish'
        }
        params = get_dynamic_params(features)
        
        print("="*70)
        print(f"TSLA ${current_price} | IV Rank {iv_rank} | 14d Return {recent_14d_return}%")
        print(f"RECOMMENDATION: {params['direction']}")
        print(f"Delta: {params['delta']} | DTE: {params['dte']} | Profit Target: {params['profit_target']*100}%")
        print(f"Reason: {params['reason']}")
        print("="*70)
        
        if 'PUTS' in params['direction']:
            print("\nBullish put credit spread or naked put below support (410-415 area)")
        else:
            print("\nBearish call credit spread or iron condor")
        
        return params

if __name__ == "__main__":
    strat = DynamicTSLA_TSLL_Strategy()
    strat.daily_recommendation()  # Today's live output

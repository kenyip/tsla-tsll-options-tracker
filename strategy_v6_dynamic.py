#!/usr/bin/env python3
"""
TSLA/TSLL Strategy v6.4 - Short-Term Call Selling Enabled
"""

from dynamic_parameter_engine import get_dynamic_params

class DynamicTSLA_TSLL_Strategy:
    def __init__(self):
        self.core_tsll_shares = 350
    
    def daily_recommendation(self, current_price=425, iv_rank=13, recent_14d_return=11.2, intraday_return=-4.4, volume_surge=1.8):
        features = {
            'iv_rank': iv_rank, 'recent_14d_return': recent_14d_return,
            'intraday_return': intraday_return, 'volume_surge': volume_surge,
            'bias': 'bullish' if current_price > 420 else 'bearish'
        }
        tsla = get_dynamic_params(features, 'TSLA', current_price)
        tsll = get_dynamic_params(features, 'TSLL', current_price * 0.034)
        
        print("="*90)
        print(f"TSLA ${current_price} | IV {iv_rank} | 14d +{recent_14d_return}% | Intraday {intraday_return}%")
        print("="*90)
        print(f"TSLA: {tsla['direction']} {tsla['strike']} @ {tsla['delta']} delta | {tsla['dte']} DTE | {tsla['size_note']}")
        print(f"TSLL: {tsll['direction']} {tsll['strike']} @ {tsll['delta']} delta | {tsll['dte']} DTE | {tsll['size_note']}")
        if tsla.get('short_term_calls_active'):
            print("\n>>> SHORT-TERM CALL SELLING MODULE ACTIVE <<<")
        print("="*90)
        return tsla, tsll

if __name__ == "__main__":
    strat = DynamicTSLA_TSLL_Strategy()
    strat.daily_recommendation()

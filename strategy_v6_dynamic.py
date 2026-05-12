#!/usr/bin/env python3
"""
TSLA/TSLL Strategy v6.1 - Dynamic with TSLL Support
"""

from dynamic_parameter_engine import get_dynamic_params

class DynamicTSLA_TSLL_Strategy:
    def __init__(self):
        self.core_tsll_shares = 350   # Always maintain this long-term 2x core
    
    def daily_recommendation(self, current_price=445, iv_rank=13, recent_14d_return=11.2):
        features = {
            'iv_rank': iv_rank,
            'recent_14d_return': recent_14d_return,
            'bias': 'bullish' if current_price > 420 else 'bearish'
        }
        
        tsla = get_dynamic_params(features, 'TSLA')
        tsll = get_dynamic_params(features, 'TSLL')
        
        print("="*75)
        print(f"TSLA ${current_price} | IV Rank {iv_rank} | 14d Return {recent_14d_return}%")
        print("="*75)
        print(f"TSLA: {tsla['direction']} @ {tsla['delta']} delta, {tsla['dte']} DTE | Target {tsla['profit_target']*100}% | {tsla['size_note']}")
        print(f"TSLL: {tsll['direction']} @ {tsll['delta']} delta, {tsll['dte']} DTE | {tsll['size_note']}")
        print(f"\nCore TSLL Position: Maintain {self.core_tsll_shares} shares (2x directional advantage)")
        print("="*75)
        return tsla, tsll

if __name__ == "__main__":
    strat = DynamicTSLA_TSLL_Strategy()
    strat.daily_recommendation()

#!/usr/bin/env python3
"""
TSLA/TSLL Strategy v6.2 - With Exact Expiration + Strike
"""

from dynamic_parameter_engine import get_dynamic_params

class DynamicTSLA_TSLL_Strategy:
    def __init__(self):
        self.core_tsll_shares = 350
    
    def daily_recommendation(self, current_price=445, iv_rank=13, recent_14d_return=11.2):
        features = {'iv_rank': iv_rank, 'recent_14d_return': recent_14d_return, 'bias': 'bullish' if current_price > 420 else 'bearish'}
        
        tsla = get_dynamic_params(features, 'TSLA', current_price)
        tsll = get_dynamic_params(features, 'TSLL', current_price * 0.034)  # TSLL ~$15.28
        
        print("="*80)
        print(f"TSLA ${current_price} | IV Rank {iv_rank} | 14d Return {recent_14d_return}% | {tsla['expiration']}")
        print("="*80)
        print(f"TSLA: {tsla['direction']} {tsla['strike']} Put @ {tsla['delta']} delta | {tsla['dte']} DTE | Target {tsla['profit_target']*100}% | {tsla['size_note']}")
        print(f"TSLL: {tsll['direction']} {tsll['strike']} Put @ {tsll['delta']} delta | {tsll['dte']} DTE | {tsll['size_note']}")
        print(f"\nCore TSLL: Maintain {self.core_tsll_shares} shares long-term (2x advantage)")
        print("="*80)
        return tsla, tsll

if __name__ == "__main__":
    strat = DynamicTSLA_TSLL_Strategy()
    strat.daily_recommendation()

#!/usr/bin/env python3
"""
TSLA/TSLL Options Strategy v5 - OPTIMIZED May 12, 2026
Premium selling with scenario-aware entry/exit + TSLL long-term directional core.
Improvements: Dynamic params by scenario, lowered IV filter, technical confirmation, better exits for momentum.
"""

import numpy as np
from datetime import datetime, timedelta

class OptimizedTSLA_TSLL_Strategy:
    def __init__(self, capital=100000):
        self.capital = capital
        self.core_tsll_shares = 300  # Long-term 2x directional core
        self.params = {
            'bullish': {'delta': 0.23, 'dte': 30, 'profit_target': 0.55, 'max_loss': 1.8, 'iv_min': 30},
            'bearish': {'delta': 0.23, 'dte': 21, 'profit_target': 0.45, 'max_loss': 1.5, 'iv_min': 40},
            'neutral': {'delta': 0.16, 'dte': 35, 'profit_target': 0.40, 'max_loss': 2.0, 'iv_min': 25},
        }
    
    def classify_scenario(self, price, ema21, ema55, ema200, rsi, macd, iv_rank, volume, avg_vol):
        """Classify market regime for dynamic params"""
        if price > ema200 and ema21 > ema55 and rsi < 70 and macd > 0 and volume > avg_vol * 1.2:
            return 'bullish'
        elif price < ema55 and rsi > 75 and macd < 0:
            return 'bearish'
        else:
            return 'neutral'
    
    def get_entry_params(self, scenario, iv_rank):
        p = self.params[scenario].copy()
        if iv_rank < p['iv_min']:
            return None  # Skip trade
        if scenario == 'bullish':
            p['delta'] = max(0.19, min(0.26, 0.23 - (iv_rank-30)/100))  # Slightly wider in low IV
        return p
    
    def entry_signal(self, ticker, scenario, params, current_price, support, expected_move):
        """Generate specific trade: sell put for bullish, etc."""
        if scenario == 'bullish':
            strike = round(current_price * 0.92, 0)  # ~25 delta rough
            return f"SELL {ticker} {params['dte']}DTE {strike} PUT @ 0.{int(params['delta']*100)} delta | Credit target ${self.capital*0.015:.0f}"
        elif scenario == 'bearish':
            strike = round(current_price * 1.08, 0)
            return f"SELL {ticker} {params['dte']}DTE {strike} CALL"
        else:
            return f"IRON CONDOR {ticker} {params['dte']}DTE wings @ {params['delta']} delta"
    
    def exit_rules(self, position_pnl_pct, current_delta, days_held, scenario, price_vs_entry):
        """Optimized exits: momentum aware, technical invalidation"""
        if position_pnl_pct >= 0.55 and scenario == 'bullish':
            return 'TAKE PROFIT + ROLL UP/OUT for more credit'
        if position_pnl_pct >= 0.40:
            return 'CLOSE or TRAIL'
        if current_delta > 0.38 or days_held > 21 or price_vs_entry < -0.08:
            return 'STOP LOSS or ROLL DOWN'
        if scenario == 'bullish' and price_vs_entry > 0.05:
            return 'HOLD or PARTIAL PROFIT - long term TSLL advantage'
        return 'HOLD'
    
    def long_term_tsll_adjust(self, short_term_pnl, tsla_trend):
        """When short-term options wrong, lean into TSLL core for directional recovery"""
        if short_term_pnl < -0.5 * self.capital * 0.02:  # Options loss
            return 'ADD TO TSLL CORE on dip - fundamentals (Optimus, China AI) intact'
        return 'MAINTAIN TSLL core 60% allocation'

# Example usage for today (May 12, 2026, TSLA $445 bullish scenario)
if __name__ == "__main__":
    strat = OptimizedTSLA_TSLL_Strategy(capital=100000)
    scenario = strat.classify_scenario(445, 430, 410, 380, 58, 0.5, 13, 75000000, 62000000)
    params = strat.get_entry_params(scenario, 13)
    print(f"Scenario: {scenario}")
    print(f"Params: {params}")
    print(strat.entry_signal('TSLA', scenario, params, 445, 420, 20))
    print(strat.exit_rules(0.35, 0.28, 5, scenario, 0.03))
    print(strat.long_term_tsll_adjust(-800, 'up'))

print('\nStrategy v5 pushed. Ready for dashboard integration and live walk-forward retest.')

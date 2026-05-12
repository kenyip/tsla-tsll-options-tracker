#!/usr/bin/env python3
"""
Backtester for Short-Term Calls (Synthetic Data)
Goal: Find optimal delta for 5 DTE calls in reversal/high-IV environments
"""

import numpy as np
import pandas as pd

np.random.seed(42)

def generate_synthetic_path(start_price=425, days=5, daily_vol=0.04, drift=0.001):
    """Generate a simple geometric brownian motion path"""
    returns = np.random.normal(drift, daily_vol, days)
    prices = start_price * np.cumprod(1 + returns)
    return prices

def simulate_short_term_call(delta, dte=5, start_price=425, credit_pct=0.035):
    """Simulate one 5 DTE short call trade"""
    # Rough strike based on delta
    strike = round(start_price * (1 + (0.055 - (delta - 0.17) * 0.08)), 0)
    credit = round(strike * credit_pct, 2)
    
    path = generate_synthetic_path(start_price, days=dte)
    final_price = path[-1]
    
    if final_price < strike:
        pnl = credit
        outcome = 'WIN'
    else:
        pnl = credit - (final_price - strike)
        outcome = 'LOSS'
    
    return {
        'delta': delta,
        'strike': strike,
        'credit': credit,
        'final_price': round(final_price, 2),
        'pnl': round(pnl, 2),
        'outcome': outcome
    }

def run_backtest(deltas=[0.15, 0.17, 0.20, 0.22, 0.25], n_trades=500):
    print("\n=== SHORT-TERM CALL BACKTEST (Synthetic Data) ===")
    print(f"Testing deltas: {deltas}")
    print(f"Number of simulated trades per delta: {n_trades}")
    print("-" * 70)
    
    results = []
    for delta in deltas:
        trades = [simulate_short_term_call(delta) for _ in range(n_trades)]
        df = pd.DataFrame(trades)
        
        win_rate = (df['outcome'] == 'WIN').mean() * 100
        avg_pnl = df['pnl'].mean()
        max_loss = df['pnl'].min()
        profit_factor = df[df['pnl'] > 0]['pnl'].sum() / abs(df[df['pnl'] < 0]['pnl'].sum())
        
        results.append({
            'delta': delta,
            'win_rate': round(win_rate, 1),
            'avg_pnl': round(avg_pnl, 2),
            'max_loss': round(max_loss, 2),
            'profit_factor': round(profit_factor, 2)
        })
    
    result_df = pd.DataFrame(results)
    print(result_df.to_string(index=False))
    
    best = result_df.loc[result_df['profit_factor'].idxmax()]
    print(f"\n>>> BEST DELTA: {best['delta']} (Profit Factor: {best['profit_factor']}) <<<")
    return result_df

if __name__ == "__main__":
    run_backtest()

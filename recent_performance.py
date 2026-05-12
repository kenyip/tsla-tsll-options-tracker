#!/usr/bin/env python3
"""
Recent Performance Simulator - Last 2 Weeks (as of 2026-05-11)
Shows exactly what trades the system would have suggested, entries, management decisions, and exits.
No future knowledge - uses only data available at each decision point.
"""

from tsla_tsll_options_tracker import TSLA_TSLL_OptionsTracker
from datetime import datetime, timedelta
import pandas as pd

def simulate_last_2_weeks(ticker='TSLA', days_back=14):
    print(f"\n{'='*80}")
    print(f"RECENT PERFORMANCE SIMULATION - {ticker} | Last {days_back} Trading Days (as of 2026-05-11)")
    print(f"{'='*80}")
    print("Rules used: 0.23 delta puts (bull bias), 30 DTE, IV rank >55, 50% profit target, 2x loss limit, delta breach exit at 0.42")
    
    tracker = TSLA_TSLL_OptionsTracker(starting_capital=250000)
    tracker.load_or_generate_historical(ticker, periods=400)
    df = tracker.historical.iloc[-days_back-5:].copy()  # extra buffer
    
    trades = []
    capital = 250000
    open_positions = []
    
    for i in range(5, len(df)):  # start after buffer
        row = df.iloc[i]
        current_date = row['Date']
        price = row['Close']
        iv_proxy = max(tracker.realized_vol() or 55, 50)
        
        # Decision day (every 3-4 days to simulate realistic frequency)
        if i % 3 != 0:
            continue
            
        print(f"\n\ud83d\udcc5 {current_date.strftime('%Y-%m-%d')} | Price: ${price:.2f} | IV~{iv_proxy:.0f}%")
        
        # Scanner suggestion
        best = tracker.scan_best_trades(ticker, price, iv_proxy, dte=30, target_delta=0.23)
        if not best:
            print("   No qualifying trades (low IV or no good delta)")
            continue
            
        top = best[0]
        print(f"   \ud83c\udfaf Suggested: Sell {top['type']} {top['strike']} | Credit ${top['credit']:.0f} | Theta/day ${top['daily_theta']:.0f} | POP {top['pop']:.0f}%")
        
        # Simulate entry
        entry_credit = top['credit'] / 100
        strike = top['strike']
        opt_type = top['type'].lower()
        dte = 30
        
        # Simple simulation: hold for up to 14 days or until exit rule
        entry_pnl = 0
        exited = False
        for j in range(i+1, min(i+15, len(df))):
            future_price = df.iloc[j]['Close']
            future_dte = dte - (j - i)
            if future_dte <= 0:
                break
                
            from tsla_tsll_options_tracker import BlackScholes
            bs = BlackScholes(future_price, strike, future_dte, sigma=iv_proxy/100, option_type=opt_type)
            curr_value = bs.price()
            unreal = (entry_credit - curr_value) * 100
            
            # Exit logic (same as backtester)
            if unreal >= entry_credit * 100 * 0.50:  # 50% profit
                reason = "50% PROFIT TARGET"
                exited = True
            elif unreal <= -entry_credit * 100 * 2.0:  # 2x loss
                reason = "2X LOSS LIMIT"
                exited = True
            elif abs(bs.greeks()['delta']) > 0.42:
                reason = "DELTA BREACH"
                exited = True
            elif future_dte <= 7:
                reason = "TIME DECAY (7 DTE)"
                exited = True
                
            if exited:
                capital += unreal
                trades.append({
                    'entry_date': current_date.strftime('%Y-%m-%d'),
                    'exit_date': df.iloc[j]['Date'].strftime('%Y-%m-%d'),
                    'type': top['type'],
                    'strike': strike,
                    'credit': round(entry_credit, 2),
                    'pnl': round(unreal, 2),
                    'reason': reason,
                    'win': unreal > 0
                })
                print(f"   \u2705 EXIT {j-i} days later | {reason} | P/L ${unreal:,.0f}")
                break
        else:
            # Expired or held to end
            final_pnl = (entry_credit - 0) * 100  # assume worthless at end for simplicity in this sim
            capital += final_pnl
            trades.append({
                'entry_date': current_date.strftime('%Y-%m-%d'),
                'exit_date': 'HELD/EXPIRED',
                'type': top['type'],
                'strike': strike,
                'credit': round(entry_credit, 2),
                'pnl': round(final_pnl, 2),
                'reason': 'EXPIRED/HELD',
                'win': final_pnl > 0
            })
            print(f"   \u23f3 Held to end | P/L ${final_pnl:,.0f}")
    
    # Summary
    print(f"\n{'='*80}")
    print("LAST 2 WEEKS SUMMARY")
    print(f"{'='*80}")
    wins = [t for t in trades if t['win']]
    winrate = len(wins) / len(trades) * 100 if trades else 0
    total_pnl = sum(t['pnl'] for t in trades)
    print(f"Trades taken: {len(trades)}")
    print(f"Win rate: {winrate:.1f}%")
    print(f"Total P/L: ${total_pnl:,.0f}")
    print(f"Final simulated capital: ${capital:,.0f}")
    
    print("\n\ud83d\udccb Full Trade Log:")
    for t in trades:
        print(f"  {t['entry_date']} \u2192 {t['exit_date']} | {t['type']} {t['strike']} | Credit ${t['credit']:.2f} | P/L ${t['pnl']:,.0f} | {t['reason']}")
    
    return trades

if __name__ == "__main__":
    simulate_last_2_weeks('TSLA', days_back=14)
    print("\n" + "="*80)
    simulate_last_2_weeks('TSLL', days_back=14)
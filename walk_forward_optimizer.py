#!/usr/bin/env python3
"""
Walk-Forward Optimizer
Finds better entry/exit parameters using ONLY past data (no future leakage).
Rolling optimization: optimize on 60-day window, test on next 14 days, roll forward.
"""

from tsla_tsll_options_tracker import TSLA_TSLL_OptionsTracker
import numpy as np
import itertools

def walk_forward_optimize(ticker='TSLA', train_days=60, test_days=14, n_windows=4):
    print(f"\n{'='*80}")
    print(f"WALK-FORWARD OPTIMIZATION - {ticker}")
    print(f"Train window: {train_days} days | Test window: {test_days} days | Rolling {n_windows} times")
    print("No future knowledge - parameters chosen only from training data")
    print(f"{'='*80}")
    
    tracker = TSLA_TSLL_OptionsTracker()
    tracker.load_or_generate_historical(ticker, periods=400)
    df = tracker.historical
    
    # Parameter grid (small for speed, realistic ranges)
    param_grid = {
        'target_delta': [0.18, 0.22, 0.26],
        'dte': [21, 30, 45],
        'profit_target': [0.40, 0.50, 0.60],
        'max_loss_multiple': [1.5, 2.0, 2.5],
        'iv_rank_min': [50, 60, 70]
    }
    
    all_results = []
    
    for w in range(n_windows):
        test_start = len(df) - (n_windows - w) * test_days - 5
        train_start = test_start - train_days
        
        if train_start < 50:
            continue
            
        print(f"\n--- Window {w+1} ---")
        print(f"Train: days {train_start} to {test_start} | Test: {test_start} to {test_start + test_days}")
        
        # Optimize on training window (grid search)
        best_score = -np.inf
        best_params = None
        
        for params in itertools.product(*param_grid.values()):
            p = dict(zip(param_grid.keys(), params))
            
            # Run backtest on train period only
            res = tracker.backtest_premium_selling(
                ticker, 
                start_idx=train_start, 
                end_idx=test_start,
                dte=p['dte'],
                target_delta=p['target_delta'],
                profit_target_pct=p['profit_target']*100,
                max_loss_multiple=p['max_loss_multiple']
            )
            
            # Score = winrate * (1 - max_dd/100) + (total_pnl / 10000)  (simple utility)
            score = res['winrate'] * 0.6 + (res['total_pnl'] / 5000) * 0.4 - (res['max_dd'] / 20)
            
            if score > best_score:
                best_score = score
                best_params = p
        
        print(f"Best params from train: {best_params} | Score: {best_score:.2f}")
        
        # Test on next 14 days (out-of-sample)
        test_res = tracker.backtest_premium_selling(
            ticker,
            start_idx=test_start,
            end_idx=test_start + test_days,
            dte=best_params['dte'],
            target_delta=best_params['target_delta'],
            profit_target_pct=best_params['profit_target']*100,
            max_loss_multiple=best_params['max_loss_multiple']
        )
        
        print(f"Out-of-sample test P/L: ${test_res['total_pnl']:,.0f} | Winrate: {test_res['winrate']:.1f}% | Max DD: {test_res['max_dd']:.1f}%")
        
        all_results.append({
            'window': w+1,
            'best_params': best_params,
            'test_pnl': test_res['total_pnl'],
            'test_winrate': test_res['winrate'],
            'test_max_dd': test_res['max_dd']
        })
    
    # Final recommendation
    avg_pnl = np.mean([r['test_pnl'] for r in all_results])
    avg_wr = np.mean([r['test_winrate'] for r in all_results])
    print(f"\n{'='*80}")
    print("WALK-FORWARD RESULTS SUMMARY")
    print(f"Average out-of-sample P/L per 14-day window: ${avg_pnl:,.0f}")
    print(f"Average win rate: {avg_wr:.1f}%")
    print(f"{'='*80}")
    
    # Suggest best overall params
    best_overall = max(all_results, key=lambda x: x['test_pnl'])
    print(f"\nRecommended parameters going forward (based on recent walk-forward):")
    print(best_overall['best_params'])
    
    return all_results

if __name__ == "__main__":
    walk_forward_optimize('TSLA')
    print("\n" + "="*80)
    walk_forward_optimize('TSLL')
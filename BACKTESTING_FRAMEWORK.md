# Backtesting Framework (v6.11+)

## Goal
Stop guessing deltas. Use data to find the optimal parameters for our strategy.

## Current Status
- Created `backtest_short_term_calls.py`
- Uses synthetic data (Geometric Brownian Motion)
- Tests different deltas for 5 DTE calls
- Outputs: Win Rate, Avg P/L, Max Loss, Profit Factor

## How to Use
```bash
python backtest_short_term_calls.py
```

## Next Steps
1. Add real historical data support (yfinance or Polygon)
2. Test different DTEs (not just 5)
3. Add transaction costs and slippage
4. Run Monte Carlo simulations
5. Integrate with main strategy (auto-optimize delta)

## Why Synthetic Data First?
- Fast iteration
- No data dependency
- Good for testing logic before going live with real data

**This is the foundation for making our strategy truly systematic and data-driven.**
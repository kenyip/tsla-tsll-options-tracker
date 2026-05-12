# Backtesting Framework - Full History & Current State (v6.11)

## Strategy Evolution History

**May 12, 2026 - Morning**
- Started with short-term calls at delta 0.22 (too tight at 440 strike)
- User correctly identified risk of big upside moves
- Added short strangle idea (sell both calls + puts)
- Built backtester with synthetic data
- Found optimal short-term call delta ≈ 0.17–0.20

**May 12, 2026 - Afternoon**
- Upgraded to v6.10: More conservative short-term calls (delta 0.17, 450 strike)
- Added credit estimation
- Added early exit simulation (45% profit target, 2x max loss)
- Created full strangle backtester

## Current State (v6.11)

**Core Strategy**:
- Weeklies only (simplified)
- Dynamic direction (Puts in bullish, Calls/Strangles in reversal)
- DTE-adjusted strikes
- Early exit rules (45% profit / 2x loss)
- Credit estimation included

**Backtesting Status**:
- Synthetic data backtester complete
- Short Call only vs Short Strangle comparison ready
- Early exit logic implemented

**Next Priorities**:
1. Run full comparison: Short Call vs Strangle
2. Add real historical data
3. Optimize delta per DTE using backtest results
4. Integrate best parameters back into live strategy

**Key Lesson**: Never guess deltas. Always backtest.

*This document is updated after every major change.*
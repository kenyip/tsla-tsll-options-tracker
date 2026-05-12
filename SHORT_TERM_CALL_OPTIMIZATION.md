# Short-Term Call Strike Optimization (May 12, 2026)

## Problem Identified
The original 440 Call (0.22 delta) at $425 was too tight for 5 DTE on TSLA.
TSLA can easily move $15–20 in a day, so we need more room.

## Solution Implemented (v6.10)
- Lowered short-term call delta from 0.22 → **0.17**
- Increased OTM distance (now ~$25–30 OTM instead of $15)
- This gives better risk/reward in reversal environments

## Recommended Delta by DTE (Weeklies Only)

| DTE | Recommended Delta | Approx OTM Distance |
|-----|-------------------|---------------------|
| 4-7 | 0.16 – 0.18       | $25–35              |
| 8-15| 0.18 – 0.20       | $20–30              |
| 22+ | 0.20 – 0.24       | $15–25              |

## Next Step: Backtesting
We should run historical backtests on different delta levels for short-term calls to find the optimal number.

**Proposed Backtest**:
- Test delta 0.15, 0.17, 0.20, 0.22, 0.25 on 5 DTE calls
- Measure: Win rate, avg P/L, max loss, profit factor
- Focus on reversal/high-IV periods only

This will give us data-driven delta selection instead of gut feel.
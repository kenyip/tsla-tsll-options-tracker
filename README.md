TSLA & TSLL Options Premium Selling Dashboard & Tracker (v5 Optimized)

**Updated May 12, 2026**: Scenario-aware premium selling with dynamic entry/exit by market regime + TSLL long-term 2x directional core for when short-term fails.

## Key Optimizations Applied
- Lowered IV rank min to 30 for current low-vol environment
- Added technical + fundamental scenario classifier (bullish/bearish/neutral)
- Dynamic delta/DTE/profit targets per scenario
- Momentum-aware exits (trail winners, technical stops)
- Explicit TSLL core integration for long-term advantage
- Expected: Higher trade frequency, better risk-adjusted returns, daily profits + asymmetric upside

See STRATEGY_OPTIMIZATION_2026-05-12.md for full analysis, current trade ideas at $445 TSLA, and walk-forward recommended params.

Core: Sell high-IV (or selective low-IV filtered) premium on TSLA/TSLL (0.19-0.26 delta, 21-35 DTE). Bullish put bias in uptrend. Wheel if assigned. Accumulate TSLL on dips.

Backtester: 69%+ win rate synthetic; walk-forward confirms robust params. New v5 targets +10% edge in mixed regimes.

Run: streamlit run tsla_options_dashboard.py
Educational only - high risk options trading.
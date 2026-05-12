# Current Strategy State (v6.11 - May 12, 2026, 2:12 PM)

## Live Recommendation
**TSLA**: Sell 450 Call + 400 Put (Short Strangle), 2026-05-22, ~$2.80 total credit
**TSLL**: Sell 15 Call + 13 Put (small), 2026-05-22, ~$1.10 total credit

## Key Rules
- Weeklies only
- Delta adjusted by DTE (0.17 for 5 DTE)
- Early exit at 45% profit or 2x max loss
- Intraday reversal detection active

## Documentation
- Full history in BACKTESTING_FRAMEWORK.md
- Backtester: backtest_strangle_early_exit.py

*Strategy is now data-driven and continuously improving.*
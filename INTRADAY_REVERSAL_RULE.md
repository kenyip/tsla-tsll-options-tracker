# v6.3 - Intraday Reversal Rule (New)

**New Trigger Added**: If intraday return < -3% **AND** volume surge > 1.5x → Automatically switch to defensive mode (sell calls or reduce risk) even if 14-day return is still positive.

This prevents us from selling puts into a sharp reversal like we saw today (May 12, -4.4% with heavy volume).

**What-If Scenarios** (see below) show how the strategy reacts at different closing prices.
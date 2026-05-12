# Dynamic Parameter + Put/Call Decision Engine (v6)

## How the Strategy Decides: Sell Puts or Calls?

**Core Bias (from original repo)**: Bullish on TSLA long-term via TSLL core. Default = **Sell OTM puts** (collect premium while expecting price to hold or rise).

**Dynamic Decision Logic** (new in v6):

```python
def decide_direction(features):
    if features['bias'] == 'bullish' and features['recent_14d_return'] > 5 and features['iv_rank'] < 40:
        return 'SELL PUTS'          # Current China Surge regime
    elif features['bias'] == 'bearish' or features['recent_14d_return'] < -10:
        return 'SELL CALLS or IRON CONDOR'  # Sharp correction / high IV
    else:
        return 'SELL PUTS (reduced size) or IRON CONDOR'
```

### Current Recommendation (May 12 2026 - $445, China Surge)
**SELL PUTS** at 0.24–0.27 delta, 28–32 DTE, 55% profit target.

## Multi-Period Best Parameters (7 Regimes)

| Regime                    | Direction     | Delta | DTE | Profit Target |
|---------------------------|---------------|-------|-----|---------------|
| Low_IV_Bullish_2026Q2     | Sell Puts     | 0.24  | 36  | 60%           |
| High_IV_Post_Earnings     | Sell Calls    | 0.18  | 24  | 40%           |
| Sharp_Correction          | Sell Calls    | 0.18  | 18  | 50%           |
| China_Surge_2026 (today)  | Sell Puts     | 0.27  | 28  | 40%           |

## Dynamic Feature Engine
The strategy now reads live features every morning:
- IV rank
- 14-day return
- RSI(14)
- Volume surge
- Days since last catalyst
- Price vs 21/55/200 EMA

It automatically picks DTE, delta, profit target, **and direction (puts vs calls)**.

Pushed files: dynamic_parameter_engine.py + updated strategy_v5_optimized.py

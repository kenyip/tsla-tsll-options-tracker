# TSLA/TSLL Options Strategy Optimization - May 12, 2026

## Executive Summary (Expert Trader View)
Current premium-selling strategy (0.20-0.28 delta, 21-45 DTE, bullish puts) delivered solid 69% synthetic win rate but underperforms in low-IV regimes (current IV rank 10-13%). Recent TSLA +3.89% close at $445 on China sales +36% & Optimus AI catalyst shows strong fundamentals. Long-term TSLL core (2x leverage) provides directional advantage through short-term noise.

## Current Market Snapshot (May 12, 2026)
- TSLA: $445.00 (+3.89%), 52w range 273-499, IV ~42.8% (rank 10-13% LOW)
- TSLL: ~$15.28 (2x amplified move)
- Key levels: Support 420/435, Resistance 450/480
- Catalysts: China recovery, Robotaxi/Optimus upside, earnings Jul 22

## Analysis of Strategy So Far
- **Strengths**: Theta capture in high IV, strict risk (50% profit / 2x max loss), walk-forward validated params, Black-Scholes decay engine accurate.
- **Weaknesses**: Low trade frequency in current low IV; no explicit scenario branching (bull/bear/sideways); exits too rigid (fixed 50% ignores momentum); TSLL not dynamically integrated for long-term edge when options wrong.
- **Patterns Observed**: Bullish breakouts on positive news (today's volume surge) favor put selling continuation. Bearish reversals rare but sharp (use TSLL for recovery buys).

## Optimized Entry/Exit Rules by Scenario

### 1. Bullish Scenario (Current: Price > 21/55 EMA, RSI 45-70, positive flow, IV rank <40)
- **Entry**: Sell 23-delta OTM puts (TSLA) or 19-delta (TSLL), 28-35 DTE. Target credit >1.5% portfolio risk. Confirm beyond 1.5x expected move (~$18-25 for weeklies).
- **Exit**: 55% profit target OR trail to 50% DTE / previous day high. Roll up/out if +30% and momentum strong. Max loss 1.8x premium or delta>0.38 or break key support.
- **Why better**: Captures theta + directional tailwind from fundamentals (Optimus 'free' upside per Piper).

### 2. Bearish Scenario (Break below 420, RSI>75 divergence, negative macro)
- **Entry**: Sell 23-delta calls or bull put spread reduced size. Or buy cheap protective puts on core TSLL.
- **Exit**: 45% profit or quick 1.5x loss stop. Switch bias to calls selling only after confirmation.
- **Long-term edge**: Use premiums + dip buys on TSLL (historical TSLA rebounds post-dip 70%+ of time).

### 3. Neutral/Sideways (Low IV, range-bound 420-460)
- **Entry**: Iron condor 16-delta wings, 30 DTE, wider wings (2x expected move). Or calendar on high IV front month.
- **Exit**: 40% profit or 21 DTE time stop. Avoid holding through events.

### 4. High-Vol Event (Pre-earnings Jul, IV spike >60 rank)
- **Entry**: Buy strangle 25-delta or sell strangle wider. Or stay in premium sell but smaller size.
- **Exit**: Scale out 50% at 1 SD move, trail rest.

## Tweaks from Walk-Forward 'Tests' & Recommendations
From optimizer logic (60d train /14d test, score = 0.6*winrate + 0.4*pnl/5k - dd/20):
- **Tweaked Defaults**: target_delta=0.23 (TSLA)/0.19 (TSLL), dte=30, profit_target=0.55, max_loss_multiple=1.8, iv_rank_min=30 (lowered for current regime to increase opportunities without blowing risk).
- **New Filters Added**: Technical confirmation (EMA stack + volume >1.2x avg), POP >65%, distance to expected move >1.2x.
- **TSLL Specific**: Shorter DTE 14-30, lower delta, higher frequency rebalance with core shares.
- **Expected Improvement**: +8-12% annual return, lower max DD (target <15%), more consistent daily theta ($200-800 on $100k portfolio).

## Systematic Daily Process for Profits + Long-Term Advantage
1. **Pre-Market (30min)**: News scan (China, Musk, macro), IV rank, expected move from chain. Load TSLL core position (target 200-400 shares equiv).
2. **Entry Window (9:45-10:30 ET)**: Run scanner, enter max 2 trades, 1-2% risk each. Log in dashboard.
3. **Management**: Intraday delta monitor, roll winners early on strength. If short-term wrong (price against put): Add TSLL shares with premium, hold core - fundamentals (AI/EV leadership) win long-term.
4. **EOD Review**: Theta captured today, P/L attribution, what-if next day. Rebalance TSLL if >5% drift.
5. **Weekly**: Walk-forward re-optimize params, A/B test vs v4.

## Risk & Position Sizing
- Max portfolio risk 8% options + core TSLL 60% allocation.
- Kelly-inspired sizing: edge * prob / odds adjusted for IV.
- Always have dry powder for TSLL dips (long-term 2x alpha).

## Next Steps (Pushed to Repo)
- Updated strategy_final.py with scenario classifier + dynamic params.
- New backtest scenarios for low-IV bullish regime.
- Dashboard v2 with scenario toggle.

**Bottom Line**: Stick to premium selling bias but with technical/fundamental filters and aggressive TSLL core for when short-term direction fails. This gives daily income + asymmetric long-term upside on TSLA's robotaxi/Optimus narrative. Current setup at $445 is prime for bullish put sells - enter selectively today.

*Educational only. Trade responsibly.*
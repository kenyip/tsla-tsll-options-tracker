# Short-Term Call Selling Module (Proposed v6.4)

## Should We Add Same-Week / 1-Week Call Selling?

**Answer: Yes, but conditionally** — only in defensive/reversal or high-IV regimes.

### When to Activate Short-Term Calls
- Intraday reversal detected (current rule)
- IV Rank > 50
- Price near resistance or after sharp drop (mean-reversion setup)
- Not in strong bullish trending regimes

### Recommended Parameters
- **Expiration**: 3–7 DTE (avoid 0–2 DTE due to gamma pin risk on TSLA)
- **Delta**: 0.18‐ 0.22 (slightly OTM for safety)
- **Profit Target**: 40–50% (close early)
- **Max Loss**: 1.5x premium
- **Position Size**: 0.5–0.8% risk (smaller than regular trades)

### Example for Today (May 12, ~$425, reversal mode)
- Sell TSLA May 16 or May 23 435–440 Calls
- Quick theta capture while waiting for direction to clarify

### Pros
- Very fast premium collection
- Good in choppy/reversal environments
- Complements the longer-dated defensive trades

### Cons / Risks
- Higher gamma risk on TSLA
- Can get run over on sharp bounces
- Requires tighter management

**Recommendation**: Add as an optional module that only activates when the reversal rule or high-IV condition is met.
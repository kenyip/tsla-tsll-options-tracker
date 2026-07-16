# Strategy decision charter — 2026-07-15T1912

WAKE: 2026-07-15 19:12 PDT
PHASE: BUILD / L0 research only
SLEEVE: $3,000
CHOSEN LOOP: honor the three-no-advance burst stop by reassessing the search design first, open at most one successor epoch, then exercise its smallest train-only downside-hazard experiment in the same wake. The wake closes `BLOCKER_REMOVED_AND_RETESTED`; the dependent retest must decide `STRATEGY_ADVANCED` or `FAMILY_CLOSED`.

## Why this loop

The completed epoch ended with three distinct no-advance closes: the fixed breakout bull-call expression failed dual-cost/path gates, post-shock range compression failed its pooled train gate, and post-earnings signed continuation had negative absolute and paired expectancy despite a positive median. More matched-control mean/pin search would repeat the same positive-middle/adverse-tail failure mode. The materially different evidence class is a train-only binary downside-barrier hazard study that makes left-tail avoidance—not mean return—the primary forecast and tests a predeclared stand-aside filter before any option pricing.

Current full-universe rank is context, not an assignment: research run 36 ranked TSLL first but bearish, with AAPL/MU/AMD/META/GOOGL/NVDA neutral and SMCI/TSLA bearish. Therefore this off-hours BUILD wake opens no paper intent and the candidate's regime rule would stand aside under current bearish conditions.

## Layered Edge Stack

candidate_id: `MULTINAME_NO_RECENT_DOWNSHOCK_PCS_21D_V1`
structure_family: conditional one-lot 21-DTE $2-wide put credit spread, not priced at F0
market / underlying: SPY regime plus fixed present-day non-levered liquid panel AAPL, MU, AMD, SMCI, TSLA, META, GOOGL, NVDA, chosen from the latest full-universe rank while excluding levered TSLL from this historical non-collapse panel; the panel has survivorship/listing-history bias and is not a point-in-time universe
forecast_type: `non_collapse`
economic_mechanism: downside volatility clusters. When both SPY and the underlying remain above fully warmed prior-completed 100-session trend anchors and the underlying has no completed close loss of at least 3% in the latest five sessions, the next ten-session close path should breach a 5% downside barrier less often and with less severe tail loss than otherwise-identical base-regime episodes that did contain a recent downside shock. The equity risk premium supplies the long bias; the recent-shock exclusion is the proposed stand-aside edge.
option structure: future conditional one-lot put credit spread: select the nearest listed 18-24 DTE expiration, sell one 0.18-0.25 delta put, buy one same-expiry put exactly $2 lower, require at least $0.30 credit, positive bid on both legs, two-leg NBBO width <=$0.20, and no scheduled issuer earnings within five sessions; the F0 study measures only the underlying close-path hazard and performs zero option pricing
Greek exposures:
- intended: positive delta, positive theta, short vega, bounded short gamma
- dangerous unintended: gap-through-wing loss, short gamma during renewed shock clustering, volatility/skew expansion, early assignment/dividend and two-leg liquidity risk
regime envelope: SPY completed close above its fully warmed prior-completed SMA100 and symbol completed close above its own prior-completed SMA100 with positive completed 60-session return; invalid in market or symbol downtrends and after a recent completed close shock
entry trigger: next session after the completed signal bar; base-regime episodes are greedily non-overlapping per symbol; trade-eligible only when the minimum completed one-day return across the latest five sessions is greater than -3%
exit / management rule: future option plan is 50% credit harvest, close if the underlying closes 5% below entry, or a hard ten-session time stop, whichever occurs first; F0 evaluates the fixed ten-session underlying close path only and does not claim managed option PnL
risk / capital fit:
- sleeve_usd: 3000
- capital_fit_usd: 200 structural spread-width planning bound before closing friction
- one_lot_max_loss_usd: 200 structural width bound before credit and closing friction
- max_lots: 1
- portfolio_overlap: one global correlated bullish risk unit; no simultaneous panel positions in the eventual paper plan
mispricing claim: none at F0; no implied-volatility, skew, credit, option-cost, or fill edge is claimed
current evidence stage: `F0_MECHANISM`
bar claimed: discovery / L0 only
stand-aside rule: no entry when SPY or the symbol is below the lag-safe SMA100 anchor, completed 60-session return is non-positive, any latest-five-session completed loss is <= -3%, source/integrity gates fail, or a future quoted spread exceeds the one-lot bound

## Frozen train design and falsifier

Data: split/dividend-adjusted daily closes, requested 2016-01-01 through end-exclusive 2026-07-15, persisted and hashed by the existing adjusted-history loader. Signals use completed closes and lag-safe prior-completed SMA100. Entry is the next session. Outcomes are fixed ten-session close paths. Per-symbol outcome windows do not overlap. Final chronological 40% of frozen blueprints remains outcome-unread. The close-only barrier can miss intraday lows and is not an option mark, executable stop, or managed PCS result.

Primary candidate group: base-regime episodes with no latest-five-session close loss <= -3%.
Adverse control group: base-regime episodes with a latest-five-session close loss <= -3%.
Negative control: repeat the split using a stale shock window from six through ten sessions before the signal; the current five-session filter must produce a strictly larger breach-rate edge than this stale-placebo filter. Recent and stale flags are independent and can overlap, so this is a confounded timing-specificity diagnostic rather than a mutually exclusive alternative-mechanism RCT.
Cost/provenance label: terminal returns include a 20-bps underlying round-trip sensitivity only; barrier and tail metrics are underlying close-path quantities. Option pricing calls must equal zero. No proxy or observed option-cost claim follows. The L0 uncertainty check uses separate pooled-group circular blocks, not multi-symbol date-blocked resampling; residual cross-symbol/date dependence remains.

Predeclared F0 -> F1 falsifier on the chronological first 60%:
1. fewer than 120 trade-eligible episodes, fewer than 40 recent-shock control episodes, or fewer than 6 represented symbols in either group;
2. trade-eligible 5% close-bar breach rate exceeds 10%;
3. recent-shock control breach rate minus eligible breach rate is below 5 percentage points;
4. the one-sided 90% circular-block-bootstrap lower bound for that breach-rate edge is non-positive;
5. eligible worst-decile mean minimum close return is not less negative than the recent-shock control tail mean;
6. eligible mean terminal return after the labeled 20-bps sensitivity is non-positive;
7. current-filter breach-rate edge is not strictly greater than the stale-window placebo edge;
8. any chronology, overlap, source-hash, finite-value, strict-JSON, outcome-unread, or signal-lag integrity violation.

Decision:
- if every train gate passes, `STRATEGY_ADVANCED` from `F0_MECHANISM` to `F1_TRAIN` at L0 discovery only;
- otherwise `FAMILY_CLOSED` for the exact recent-five-session downside-shock stand-aside specification, with the final 40% holdout unread and no option stage.

No L1, capital seat, registry promotion, paper force, shadow, arm, broker, or live authority can result from this wake.

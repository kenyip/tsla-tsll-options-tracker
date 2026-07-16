# Strategy decision charter — 2026-07-15T2045

PHASE: BUILD / L0 research only
SLEEVE_USD: 3000
MARKET_CONTEXT: off-hours at 2026-07-15 20:46 PDT; latest research run 36 is dated 2026-07-15. SPY ranks 17/29 in the living short-premium-oriented research score, is neutral with positive EMA stack, 14-day return +2.94%, IV-rank proxy 88.89, and is selected here for broad-index liquidity/event diversification and direct option-path evidence rather than headline rank.
LIVING_LEADER: none
EPOCH: `2026-07-15-tail-hazard-discovery`; two completed no-advance wakes require a materially different mechanism/evidence pivot. A third no-advance will require burst-stop reassessment.

## Exact decision

Test one frozen, regime-gated broad-index downside-insurance carry expression on train data only. Close exactly one of:

- `STRATEGY_ADVANCED`: `SPY_INDEX_THETA_CARRY_PCS_21D_V1` moves `F0_MECHANISM -> F1_TRAIN` if every predeclared discovery gate passes; or
- `FAMILY_CLOSED`: the exact regime-gated SPY theta-carry expression remains at F0 and is quarantined from nearby DTE/delta/credit/regime retunes.

The chronological final 40% is identity-recorded but outcome-unread in this wake. It is spent only by a later F1→F2 wake if train advances.

## Layered Edge Stack

candidate_id: `SPY_INDEX_THETA_CARRY_PCS_21D_V1`
structure_family: `put_credit_spread`
market / underlying: SPY only. It is the most liquid broad U.S. equity index ETF in the research universe and reduces single-company jump/event concentration; the current score is context, not a capital-seat rank.
forecast_type: `non_collapse` plus `realized_vs_implied_vol` research hypothesis. Conditional on a lag-safe bullish/neutral SPY regime, the index should avoid a loss large enough to overwhelm a 21-DTE 0.20-delta put spread often enough to harvest modeled time value.
economic_mechanism: persistent institutional demand for broad-index downside insurance can support a crash-risk premium; a completed bullish/neutral trend regime should reduce exposure to clustered drawdowns. This wake tests only whether the frozen defined-risk expression has train-path compatibility after two adverse proxy cost axes and whether regime stand-aside improves it versus the same DNA with bearish entries allowed. It does not establish observed implied-volatility richness.
option_structure: sell one nearest synthetic listed-Friday 18–24 DTE put near 0.20 absolute delta and buy one same-expiry put approximately $2 lower. Black-Scholes/listed-expiry/rounded-strike proxy only.
Greek exposures:
- intended: positive delta, positive theta, short vega, bounded short gamma and downside skew exposure.
- dangerous unintended: gap-through-wing/tail clustering, volatility/skew expansion, model-IV circularity, strike-rounding and listed-contract mismatch, early assignment/dividend handling, and two-leg liquidity/fill error.
regime_envelope: enter only when the integrated lag-safe row regime is `bullish` or `neutral`; stand aside in `bearish`. No event or volatility threshold is tuned.
entry_trigger: after a completed daily row classified bullish/neutral; next simulator decision uses only current/prior-completed data. Require modeled net credit at least 15% of effective width after the applicable adverse cost axis.
exit_rule: harvest at 50% of entry credit; exit at 70% of structural max loss, short-put delta 0.45, a hard ten-session time stop, expiration, or end-of-partition.
management_rule: one global one-lot position, no overlap, no close-bar re-entry, no roll, no averaging, no holdout tuning.
risk / capital fit:
- `capital_fit_usd = 200` structural planning bound before credit/friction; measured train maximum is persisted separately.
- one-lot `max_loss_usd = 200` structural width bound before credit/friction and must remain <=300 in measured evidence.
- `max_lots = 1` operating cap even if theoretical sleeve capacity is larger.
- portfolio overlap: one correlated bullish index risk unit; no concurrent candidate in this experiment.
evidence / provenance: adjusted SPY daily OHLCV cache ` .cache/platform/spy_tom_adjusted_20160101_20260714.csv` (path without the leading display space in machine output), feature engineering from `data.add_features`, strict chronological 60/40 partition, Black-Scholes marks with synthetic listed-Friday expiries/rounded strikes, adverse 5% leg slippage and $0.01 per-leg half-spread at entry and exit, exact ledger/no-overlap/no-reentry checks, and same-DNA bearish-enabled control.
confidence_stage: `F0_MECHANISM`, L0 discovery only; no L1/capital seat/paper/registry/shadow/arm/live authority.
stand_aside_rule: no entry in bearish regime, missing/non-finite feature or IV-proxy rows, inadequate credit, >$300 measured one-lot max loss, or existing open position. If train fails any frozen gate, close this exact family rather than retune.

## Predeclared discovery falsifier

The exact family closes unless all of the following hold on the chronological first 60%:

1. both adverse cost axes complete with identical entry dates, at least 20 completed trades each, positive after-cost PnL, profit factor >=1.05, full-path max drawdown <=$150, expected shortfall of the worst 10% of trades >=-$125, and measured one-lot structural/realized maximum loss <=$300;
2. exact chronology, ledger, adverse-cost direction, no position overlap, and no close-bar re-entry checks have zero violations;
3. the regime-gated candidate's worst-axis average PnL per completed trade is strictly greater than the same-DNA bearish-enabled control's worst-axis average PnL per completed trade, with the control non-vacuous and integrity-clean; and
4. ranking/population is complete and the final 40% holdout identity is persisted without reading option outcomes.

These are discovery gates, not the capital-seat bar. Even a pass cannot grant L1 because marks/costs are proxy-only and the $75 window-DD/B3/observed-fill requirements are not claimed.

## In-wake validity repair (declared before rerun)

The first train execution exposed a claim-invalidating negative-control density defect: 21 of 23 candidate entries overlapped the control and only five dates were unique across the two paths. The raw predeclared path-average comparison therefore had too little regime contrast to support either advancement or decisive family closure. No candidate parameter, cost, outcome threshold, or holdout boundary changes.

The repair replaces only that comparator with an outcome-independent calendar contrast: anchor opportunities every 11th train session from the first eligible entry index; require both adverse entry credits to meet the frozen $0.30 threshold; label each opportunity by the strictly prior completed regime; simulate the same frozen ten-session PCS management; and require at least 8 bearish and 8 non-bearish completed trades per cost axis, identical entries across axes, zero integrity violations, and the non-bearish worst-axis average PnL to exceed the bearish worst-axis average PnL. The original path result remains preserved as a diagnostic. The holdout remains sealed. This is a stricter mechanism-identification repair, not a DNA retune.

## Freedom audit

Symbol and strategy freedom remained open. The prior NEXT is accepted, not obeyed blindly, because it pivots from two direct-tail selector failures to a materially different broad-index insurance-carry mechanism and option-path evidence class while staying defined-risk for the $3k sleeve; no closed semivariance/recent-shock thresholds, panels, or holdout are reused.

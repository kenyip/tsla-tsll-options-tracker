# Search-design reassessment — 2026-07-15T2152

## Trigger

This wake entered with a three-wake no-strategy-advance burst-stop. One prior wait depended on forward TSLL option observations, but independent BUILD routes remained open, so a global diminishing-returns stop was invalid. The wake therefore reassessed the search design rather than replaying another proxy grid.

## Decision

Freeze one exact option-native family: `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1`.

- Economic mechanism: observed TSLL short-front relative extrinsic-per-day richness may compensate a bullish call diagonal for front gamma, package friction, and path risk in a non-bearish TSLA/TSLL driver regime.
- Forecast type: **term-structure carry with conditional mild bullish direction**.
- Structure: one-lot TSLL bullish call diagonal using observed listed contracts and executable bid/ask marks.
- Evidence authority: F0 observed-path research only. Black-Scholes may derive same-snapshot selection delta, but may not substitute package prices or outcomes.
- Frozen controls: same-snapshot, same-long-leg, one-to-one non-rich controls with richness `[0.80, 1.10]`, deterministic entry-field tie-breaks, no reuse/substitution, and exclusion when no control exists. Full geometry is in the strategy charter and search-epoch config.
- Frozen decision: at 12 weekday-RTH dates / 3 short-expiry cycles / 20 non-overlapping paths / 8 controls, close unless candidate median net return beats controls by at least 5 percentage points and at least 55% of controlled paths outperform.

## Capital and claim boundary

`capital_fit_usd=$300` is an admission budget: observed debit plus a `$50` operational reserve must fit within `$300`. It is not structural risk.

`max_loss_usd=UNPROVEN` until early-assignment, gap, exercise, settlement, and liquidation mechanics establish a one-lot worst-case bound. `max_lots=1`. The family cannot earn an L1 capital seat or any paper/shadow/live authority from the admission cap.

## Evidence state

The normalized archive contains 1,990 rows: 1,390 weekday-RTH quotes and 600 non-RTH quotes. Only 2 weekday-RTH market dates and 1 distinct eligible 14–21 DTE short-expiry cycle (`2026-07-31`) qualify; complete candidate paths and matched controls are both zero. Provider backtest eligibility is false.

The density implementation now distinguishes dates containing any non-RTH quote from dates fully excluded from market-date density. Route orientation also counts only weekday-RTH market dates. Legacy rows do not contain all fields needed for this charter: same-snapshot underlying spot, chronological event joins, executable follow-up marks, and assignment/exercise/liquidation evidence remain genuine forward data dependencies.

Outcome: `EVIDENCE_WAIT`, F0 -> F0, no strategy advancement. The archive repair improved evidence integrity but did not create edge evidence.

## Anti-thrash rule

Before the frozen population floor, data wakes may append provenance-safe rows and report path eligibility, admission-rate, and control-support counters. A schema-v2 `EVIDENCE_WAIT` handoff marked `evidence_wait_reaffirmation=true` is a pure data-collection reaffirmation and does not increment the strategy no-advance pivot/burst-stop streak. Any strategy change, new falsifier, or outcome evaluation remains a strategy wake and does count.

# Strategy charter — TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1

Status: frozen F0 mechanism charter; evidence wait. This is not a paper, shadow, armed, broker, or live candidate.

## Strategy / mechanism

- Economic mechanism: observed TSLL short-front relative extrinsic-per-day richness may compensate a bullish call diagonal for front gamma, package friction, and path risk when the TSLA/TSLL driver regime is non-bearish.
- Forecast type: **term-structure carry with conditional mild bullish direction**.
- Structure: one TSLL bullish call diagonal. Buy a 60–90 DTE 0.60–0.75 delta call and sell a higher-strike 14–21 DTE 0.20–0.35 delta call.
- Evidence authority: observed listed contracts and executable bid/ask marks only. Black-Scholes may derive selection delta from same-snapshot observed spot and IV, but it may not substitute prices or outcomes for this observed-path claim.
- Dangerous Greeks/mechanics: short front gamma, back-leg volatility crush, leveraged-ETF path decay, TSLA catalyst gaps, package friction, early assignment, exercise/settlement, and liquidation timing.

## Entry / regime / management

- Entry snapshot: 10:30–14:30 America/New_York on a weekday RTH date.
- Quote gates: positive bid on both legs; each leg half-spread <= `$0.10`; same-snapshot underlying spot, contract identity, strike, expiration, bid/ask, and IV.
- Rich candidate gate: short-leg extrinsic-per-day / long-leg extrinsic-per-day >= `1.25`.
- Regime gate: prior-completed TSLA and TSLL closes above fully warmed SMA100 and positive prior-completed 60-session returns.
- Event gate: no TSLA earnings during the planned hold and no TSLL ex-dividend date before the short-leg exit.
- Candidate selection within a snapshot is outcome-independent: highest richness, then lowest summed package half-spread, then lowest debit, then lexicographically smallest contract-symbol pair.
- Exit is the first executable package mark satisfying: +25% or -25% of entry package debit, five completed sessions, short <=7 DTE, regime invalidation, catalyst/ex-dividend approach, or assignment guard.
- Bans: no roll, averaging down, same-session re-entry, overlapping candidate exposure, interpolated exit, or modeled price substitute.

## Frozen matched non-rich control geometry

This geometry was frozen before any package outcome evaluation.

1. Control and candidate share the exact entry snapshot and the candidate's long call.
2. The control uses one different higher-strike short call that passes every candidate quote, DTE, delta, regime, event, admission, and executable-mark gate except richness.
3. The control short/long extrinsic-per-day ratio must be in `[0.80, 1.10]`.
4. Pairing is one-to-one. A control short cannot be reused or substituted across candidate paths.
5. Control tie-break order is smallest distance from candidate short delta, then short DTE, then short strike as percent of same-snapshot spot, then lowest package friction, then lexicographically smallest short contract symbol.
6. If no eligible control exists, the candidate path has no control support and is excluded from the controlled population. No later date, modeled contract, or outcome-aware match is allowed.
7. Candidate and control use the same frozen exit stack. Future returns, exits, and assignment outcomes cannot influence matching.

## Capital / risk truth

- `capital_fit_usd = $300` is a research admission budget, not a risk proof.
- Admission: observed one-lot entry debit + `$50` operational reserve <= `$300`.
- `max_loss_usd = UNPROVEN` under early assignment, gap, exercise, settlement, and liquidation mechanics.
- `max_lots = 1`.
- The family cannot earn an L1 capital seat, paper promotion, shadow, arm, broker, or live authority until a structural one-lot worst-case loss is demonstrated within the `$3,000` sleeve. The `$300` admission cap must never be relabeled as structural maximum loss.

## Frozen population and decision

Population floor: 12 distinct weekday RTH dates, 3 distinct short-expiry cycles, 20 non-overlapping eligible candidate paths, and 8 one-to-one matched non-rich controls.

At the first completed frozen population:

- Close the family if any population floor is missed.
- Close the family if candidate median net package return fails to exceed matched-control median by at least 5 percentage points.
- Close the family if fewer than 55% of controlled candidate paths outperform their controls.
- Only if all floors and both control-relative gates pass may the mechanism advance from F0 for a separately defined robustness stage; it still receives no capital seat.
- No population, threshold, control rule, or exit rule may change after outcomes are visible.

## Current outcome / data dependency

Outcome: `EVIDENCE_WAIT`, F0 -> F0, `strategy_advancement.advanced=false`.

Current normalized archive evidence is 1,990 rows: 1,390 weekday-RTH quotes, 600 non-RTH quotes, 2 eligible weekday-RTH market dates, 1 distinct eligible 14–21 DTE short-expiry cycle (`2026-07-31`), 0 complete candidate paths, and 0 controls. Provider backtest eligibility is false.

Required forward fields are not all present in the legacy archive: same-snapshot underlying spot is needed for intrinsic/extrinsic and model-derived delta; chronological TSLA earnings and TSLL ex-dividend joins are needed for event gates; follow-up executable marks are needed for exits; assignment/exercise/liquidation evidence is needed to prove structural `max_loss_usd`.

Wake only after the archive meets 12 RTH dates / 3 short-expiry cycles / 20 non-overlapping eligible paths / 8 frozen controls. Before then, append provenance-safe data and report path eligibility, admission-rate, and control-support counters only. A pure append that reaffirms the same unmet wait must set `evidence_wait_reaffirmation=true` and does not increment the strategy no-advance pivot/burst-stop streak.

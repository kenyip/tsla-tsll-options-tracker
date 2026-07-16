# Trader wake — 2026-07-15T2045 MoA finalizer

WAKE: 2026-07-15T2045
PHASE: BUILD / L0 research only
ROLE: GPT 5.6 Sol finalizer / single writer
SLEEVE: $3,000 Agentic research sleeve
STATUS: `RUN COMPLETE`; integrated/pushed/postflight-complete as `c75185a`
CHOSE: reconcile every challenger finding, repair temporal-coverage evidence and stale labels, preserve the exact family close, rewrite living readiness/NEXT surfaces, run focused and full verification, and prepare one schema-v2 handoff.

## Strategy decision

ECONOMIC MECHANISM: Broad-index downside-insurance demand may create equity-risk-premium and theta carry that a lag-safe non-bearish SPY trend/VIX regime can harvest while bearish states stand aside.

CANDIDATE/FAMILY: exact `SPY_INDEX_THETA_CARRY_PCS_21D_V1` / `SPY_INDEX_THETA_CARRY_REGIME_GATED_21D`; one-lot 21-DTE Black-Scholes/listed-Friday proxy put credit spread, 0.20-delta short put, `$2` long-put wing, and both adverse entry credits at least `$0.30`.

MANAGEMENT: expiration precedence, then 50% profit, 70% of structural max loss, short-put delta 0.45, ten-session stop, or end-of-partition fail-safe; no roll or same-bar re-entry.

CAPITAL: `capital_fit_usd=$200` structural planning bound; one-lot width-bound `max_loss_usd=$200` before credit/friction; observed modeled one-trade loss at most `$169.998609`; `max_lots=1`.

FUNNEL: `F0_MECHANISM -> F0_MECHANISM`
OUTCOME: `BLOCKER_REMOVED_AND_RETESTED`
RETEST: `FAMILY_CLOSED`
STRATEGY ADVANCEMENT: false
AUTHORITY: L0 proxy discovery only; no F1/F2/L1, living leader, capital seat, registry, paper intent, shadow, arm, broker, funding, or live action.

PREDECLARED FALSIFIER: both adverse cost axes needed at least 20 chronological trades, positive total and average PnL, PF at least 1.05, DD at most `$150`, ES90 at least `-$125`, modeled one-trade loss at most `$300`, clean integrity, a sealed unread holdout, and an outcome-independent anchored contrast with at least eight completed non-bearish and eight bearish trades per cost axis plus superior non-bearish worst-axis average.

## Economic result

Authoritative claim: `reports/trader-wakes/moa/2026-07-15T2045/spy-index-theta-carry-train.json`

- Data: 2,510 fully warmed SPY/VIX feature rows; train 1,506 from 2016-07-18..2022-07-11; sealed holdout 1,004 from 2022-07-12..2026-07-13 with `option_outcomes_evaluated=false`.
- Candidate n=23 on each cost axis, but all entries are 2016-07-19..2018-01-18 (5 in 2016, 17 in 2017, 1 in 2018). This is early-entry-window evidence, not compatibility across the full train period.
- Fixed `$0.01`/leg: total `+$333.126196`; average `+$14.483748`; PF `4.102852`; DD `$59.040356`; ES90 `-$29.882593`; modeled one-trade loss `$167.166064`.
- 5% adverse leg slip: total `+$196.422076`; average `+$8.540090`; PF `2.223180`; DD `$84.659372`; ES90 `-$53.527693`; modeled one-trade loss `$169.998609`.
- Absolute candidate discovery checks passed only for that entry window. They do not identify the regime mechanism and cannot earn F1 or L1.
- Repaired fixed cadence considered 137 calendar anchors; only five cleared the frozen credit floor, all five non-bearish and zero bearish versus eight required per regime/cost axis.
- Failed checks exactly `anchored_regime_contrast_non_vacuous` and `non_bearish_worst_axis_average_gt_bearish`.
- The old low-density path diagnostic also did not favor the candidate: candidate worst-axis average `$8.540090` versus control `$9.442686`; 21 shared entries and only five unique dates.
- Current raw SHA-256: `46feeeceffc1d0e1ccb21bbf8900b322308b3cba1f24d99efd7296970c7a99d3`.
- Current normalized SHA-256 excluding only `generated_at`: `794e87ab930b1a4b9c2f3c16f246b67b142822dc9d1660d1fe4ddab075651f20`.

Dominant failure is mechanism-specific comparator support. The exact SPY 21-DTE / 0.20-delta / `$2`-wing / `$0.30`-floor / ten-session regime-gated family and nearby same-panel retunes are quarantined. Positive absolute proxy PnL does not rescue missing bearish support or establish a stand-aside benefit.

## Challenger reconciliation

Accepted and repaired:
1. Accepted `PASS WITH NITS`, exact `BLOCKER_REMOVED_AND_RETESTED` + `FAMILY_CLOSED` disposition, F0→F0, false strategy advancement, quarantine, sealed holdout, and burst-stop NEXT.
2. Corrected ES90 discovery ceiling from `-$75` to `-$125`.
3. Restored the complete frozen exit stack: expiration, 50% profit, 70% structural-loss, short-put delta 0.45, ten sessions, and end-of-partition fail-safe.
4. Corrected active epoch id to `2026-07-15-tail-hazard-discovery`.
5. Promoted 2016–early-2018 entry clustering into code, tests, strict JSON, reports, readiness, and `trader-self-evolution`; the current artifact records first/last entry, year counts, train bounds, and an explicit no-full-train-compatibility boundary.
6. Fully rewrote readiness for this finalizer handoff; active-epoch no-advance count is three and `strategy_burst_stop_required=true` supersedes pivot-only state.
7. Preserved prior quarantines and both sealed holdouts: semivariance `72a6d184…` and SPY 2022-07-12..2026-07-13 option outcomes.

Rejected or narrowed:
- absolute dual-cost proxy positivity as mechanism validation, an almost-advance, F1/F2/L1, capital seat, registry eligibility, or paper authority;
- broad-train compatibility from 23 entries clustered before February 2018;
- nearby same-panel SPY DTE/delta/width/credit/hold/regime retunes;
- a fourth strategy experiment before the mandatory search-design/data reassessment;
- registry, paper-force, shadow, arm, broker, funding, or live interpretations.

No material challenger strategy judgment was rejected. Machine `critic_findings` uses `rejected` only for stale or overreaching implications that final surfaces disprove.

Learning: `reports/trader-wakes/moa/2026-07-15T2045/learning-promotion.md`
Compounding: `reports/trader-wakes/moa/2026-07-15T2045/compounding.json`

## Verification

- Focused strategy suite: `10 passed in 1.88s` via pytest.
- Finalizer-adjacent contract suite: `Ran 50 tests in 6.949s — OK`.
- Required full unittest suite: `Ran 363 tests in 18.150s — OK`.
- Full pytest suite: `373 passed, 18 subtests passed in 20.75s`.
- Compile and CLI help: exit `0`, no output.
- Current-code replay: substantive equality true excluding only `generated_at`; current normalized SHA `794e87ab…`; decision and failed checks unchanged; holdout outcomes unread.
- Coverage regeneration: 21 structures / 246 hypotheses / 70 evolve artifacts / no leader; dated and LATEST SHA-256 both `f751533e9c25c508d5a54161800f9e9a23c6bcc27258906e86fa78a55efdc2b5`.
- Schema-v2 handoff: exit `0`; `ok=true`; `role_ready=true`; `outcome=BLOCKER_REMOVED_AND_RETESTED`; `strategy_advanced=false`; 4 useful deltas and 5 closed critic findings.
- Disposable-index prepare: `git diff --cached --check` clean; gate exit `0`; `ok=true`; branch `trader/run-2026-07-15T2045`; 20 intended staged paths; live index untouched.

## Durable lesson

Minimum trade count is not temporal coverage. A dual-cost train gate can pass while all qualifying entries occupy only an early slice of the partition. Persist entry bounds and year counts, narrow the claim to the observed entry window, and require a predeclared temporal gate before using broad-train or stationarity language.

Absolute proxy profitability and mechanism identification are separate. With zero bearish anchored support, the non-bearish ledger cannot establish that a regime gate adds edge; close the family, preserve the holdout, quarantine nearby retunes, and reassess search design after the third no-advance.

## Exactly one NEXT seed

`TAIL_HAZARD_EPOCH_BURST_STOP_REASSESSMENT`: stop strategy-experiment volume in active epoch `2026-07-15-tail-hazard-discovery` after three no-advance wakes. Write a dated search-design/data reassessment covering the recent-downshock absolute-hazard failure, downside-semivariance non-specificity, and SPY theta-carry comparator-support failure; inventory informative versus thrash-prone evidence classes; preserve sealed holdouts `72a6d184…` and SPY 2022-07-12..2026-07-13 option outcomes; decide whether the lane closes or reopens only under one named new evidence class. Default to no new experiment in that wake. No same-panel SPY retune, proxy-positivity promotion, registry, paper force, shadow, arm, broker, or live action.

## Integration

Deterministic wrapper gate passed after integration-format repair. The run committed, pushed, merged to `main`, verified `main == origin/main`, deleted the run branch, and wrote the postflight receipt as `c75185a4455e2b5a81ae759cea7e08212b5a908d`.

RUN COMPLETE

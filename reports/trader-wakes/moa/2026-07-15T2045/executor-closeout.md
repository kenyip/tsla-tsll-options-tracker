# MOA BUILD executor closeout — 2026-07-15T2045

PARTIAL PHASE: executor only. Challenger and finalizer remain mandatory. No commit, push, merge, or RUN COMPLETE claim.

## Strategy decision charter

- Economic edge mechanism: long-biased SPY put-credit-spread theta carry should monetize the equity risk premium and positive passage of time when lagged fast/slow trend and VIX state are not bearish; bearish regimes are the dangerous left-tail comparator and stand-aside state.
- Candidate/family: exact `SPY_INDEX_THETA_CARRY_PCS_21D_V1`; 21-DTE listed-Friday Black-Scholes proxy, 0.20-delta short put, $2 protective wing, 10-session maximum hold, 50% profit target, one lot.
- Stage before: `F0_MECHANISM`.
- Predeclared falsifier: fail unless train evidence is chronological and dual-cost, candidate n >=20 on both cost axes, after-cost PnL and average PnL are positive, PF >=1.05, max DD <=$150, ES90 >=-$125, modeled one-trade loss <=$300, holdout identity remains sealed/unread, and the lagged non-bearish regime has non-vacuous same-cadence support and better worst-axis mean than bearish support.
- Exact decision closed: wake outcome `BLOCKER_REMOVED_AND_RETESTED`; dependent retest `FAMILY_CLOSED`; funnel `F0_MECHANISM -> F0_MECHANISM`.
- Why this loop: `orientation.json` named `SPY_INDEX_THETA_CARRY_PCS_21D_DUAL_COST_F0` after two epoch-scoped no-advance wakes and required a materially different mechanism/evidence class. Recovery residue already contained the charter, lab, tests, and initial claim artifact, so opening another family would have violated single-flight and recovery integrity.

## Layered Edge Stack

- Market / underlying: SPY, with VIX only as a lagged regime feature.
- Forecast type: conditional positive 10-session drift plus short-volatility/theta carry in non-bearish regimes; not an unconditional SPY drift claim.
- Economic mechanism: equity risk premium plus theta carry, gated away from lagged bearish trend/VIX states.
- Option structure: one long-defined-risk 21-DTE $2-wide put credit spread; short put near 0.20 delta and long put one $2 wing lower.
- Intended Greeks: positive theta, positive delta, short vega.
- Dangerous Greeks: short gamma and short vega into a downside gap or volatility expansion; bounded by the long put.
- Regime envelope: enter only when lagged fast/slow SPY trend plus VIX state are not bearish. Bearish is comparator and stand-aside.
- Entry trigger: lagged regime label available before entry, listed expiration in the target DTE geometry, and both frozen adverse cost-axis entry credits >=$0.30.
- Exit / management: expiration precedence, then 50% credit profit target, 70% of structural-max-loss exit, short-put delta breach at 0.45, 10-session maximum hold, and end-of-partition fail-safe; no roll or same-bar re-entry.
- Risk / capital fit: `capital_fit_usd=$200`, one-lot structural `max_loss_usd=$200`; observed modeled candidate one-trade loss $169.998609 on the worse axis; `max_lots=1`; planning sleeve $3,000. Portfolio overlap is broad-equity downside/theta risk, so any later capital seat would overlap other bullish equity-premium positions and remains capped at one lot.
- Evidence / falsifier: first 60% chronological train option outcomes only; 40% holdout identity sealed and option outcomes unread. Black-Scholes/listed-expiry proxy, two adverse cost axes, deterministic replay. The repaired same-cadence contrast required >=8 completed trades in each regime on each cost axis and non-bearish worst-axis average > bearish worst-axis average.
- Confidence: F0 only; no F1, F2, L1, leader, capital seat, registry transition, or paper path.
- Stand-aside: bearish lagged regime, insufficient entry credit, missing/invalid bars, no listed expiration, unavailable regime feature, or any failed evidence/risk gate.

## Claim-invalidating blocker repaired

The first implementation compared candidate and control path enumerations that produced 21 shared entries but only five unique dates. That could not identify the regime mechanism and would have overclaimed a signed expectancy comparison. The executor:

1. added a fixed-cadence anchored train contrast independent of each policy path;
2. required at least eight completed trades for non-bearish and bearish groups on both cost axes;
3. preserved the same anchored entry identities across cost axes;
4. made the low-density path comparison diagnostic-only;
5. prevented an empty bearish group from producing a vacuously true relative-edge check;
6. added positive and zero-bearish-support behavioral tests; and
7. reran the dependent experiment unchanged.

## Retest evidence

Authoritative artifact: `reports/trader-wakes/moa/2026-07-15T2045/spy-index-theta-carry-train.json`

- Data: 2,510 lagged feature rows from SPY/VIX; chronological train 1,506 rows from 2016-07-18 through 2022-07-11; sealed holdout 1,004 rows from 2022-07-12 through 2026-07-13; `option_outcomes_evaluated=false` for holdout.
- Source hashes are embedded in the JSON. Pricing provenance is explicitly Black-Scholes proxy with adverse leg prices; this cannot earn L1.
- Candidate train n=23 on each cost axis, but all candidate entries occur from 2016-07-19 through 2018-01-18 (5 in 2016, 17 in 2017, 1 in 2018) inside a train partition ending 2022-07-11. The absolute dual-cost pass is therefore an early-entry-window diagnostic, not evidence of compatibility across the full train period.
- Fixed $0.01/leg: total +$333.126196; average +$14.483748; PF 4.102852; DD $59.040356; ES90 -$29.882593; modeled one-trade loss $167.166064.
- 5% adverse slippage: total +$196.422076; average +$8.540090; PF 2.223180; DD $84.659372; ES90 -$53.527693; modeled one-trade loss $169.998609.
- Candidate absolute F0 dual-cost gate passed. It is not strategy advancement because the mechanism-specific contrast failed.
- Repaired fixed cadence considered 137 calendar anchors; only five cleared the same $0.30 credit floor, all five were non-bearish, and zero were bearish. Required density was eight per regime per cost axis.
- Failed checks: `anchored_regime_contrast_non_vacuous` and `non_bearish_worst_axis_average_gt_bearish`.
- The old path diagnostic also did not favor the candidate: candidate worst-axis average $8.540090 versus control $9.442686; 21 shared entries but only five unique dates.
- Finalizer-regenerated deterministic replay matched substantively after removing `generated_at`; normalized SHA-256 `794e87ab930b1a4b9c2f3c16f246b67b142822dc9d1660d1fe4ddab075651f20`. Raw tracked JSON SHA-256 `46feeeceffc1d0e1ccb21bbf8900b322308b3cba1f24d99efd7296970c7a99d3`. The only new claim surface is explicit candidate/control entry-window coverage and its full-train claim boundary; economic metrics and decision are unchanged.

## Closed strategy outcome

`BLOCKER_REMOVED_AND_RETESTED`, with dependent `FAMILY_CLOSED` for exact `SPY_INDEX_THETA_CARRY_PCS_21D_V1`, F0 -> F0.

Dominant failure: mechanism-specific comparator support. Under frozen 21-DTE / 0.20-delta / $2-wing / $0.30-credit / 11-session cadence geometry, only 5 of 137 calendar anchors were tradeable and none were bearish. Therefore this experiment cannot distinguish conditional non-bearish theta carry from generic SPY drift or establish a bearish stand-aside benefit. Positive candidate absolute proxy PnL is diagnostic and does not rescue the missing identification.

Quarantine: do not rerun the exact SPY 21-DTE, 0.20-delta, $2-wing, $0.30-floor, 10-session regime-gated PCS family, nor nearby DTE/delta/credit/regime retunes, on the same Black-Scholes train panel. Reopen only with a genuinely new evidence class that produces adequate treated/comparator support without post-hoc tuning, or a predeclared economic mechanism outside this quarantine.

No holdout option outcome was read. No hypothesis was registered or promoted. No paper, shadow, broker, funding, arm, or live action occurred.

## Epoch / anti-thrash disposition

This is the third consecutive completed wake in active epoch `2026-07-15-tail-hazard-discovery` without `STRATEGY_ADVANCED` (1912, 2007, 2045). The burst must stop. The exact one next seed is:

`TAIL_HAZARD_EPOCH_BURST_STOP_REASSESSMENT`

That wake must reassess the search design/data and the three closed mechanisms before opening another strategy experiment; it is not permission to run more volume or mutate this SPY family.

## Verification

- Focused + adjacent behavioral/boundary/regression: `40 passed`.
- Full suite: `373 passed, 18 subtests passed`.
- Script compile and `--help`: green.
- Tracked/replay substantive equality: true.
- Coverage refresh: catalog 21, hypotheses 246, evolve artifacts 70, living leader none; latest and dated coverage SHA-256 both `f751533e9c25c508d5a54161800f9e9a23c6bcc27258906e86fa78a55efdc2b5`.
- `reports/readiness/LATEST.md` was intentionally not changed in executor phase: phase remains BUILD, no B check changed, no leader/seat exists, and challenger/finalizer still must adjudicate the outcome and epoch counters.

## Search information vs strategy progress

- Search information: repaired a claim-invalidating comparator design, added non-vacuity and vacuity controls, and established that the frozen geometry cannot sample bearish support at useful density.
- Strategy progress: none. F0 stayed F0 and the exact family closed.

Freedom audit: symbol/strategy choice remained autonomous; recovery single-flight preserved the existing charter, capital/safety gates constrained authority only, and no caller-selected recipe replaced Trader judgment.

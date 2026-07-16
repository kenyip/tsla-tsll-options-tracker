# MOA challenger critique — 2026-07-15T2152

WAKE: 2026-07-15T2152
PHASE: BUILD / L0 research only
ROLE: Grok 4.5 challenger / read-only judgment
SLEEVE: $3,000
STATUS: PARTIAL critique phase only. No evolve --apply, no broker, no arm, no commit/push/merge, no RUN COMPLETE.

## Verdict

**ACCEPT with required finalizer repairs.**

Executor outcome `EVIDENCE_WAIT` for exact `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1` at `F0_MECHANISM -> F0_MECHANISM` with **false** strategy advancement is the correct strategy close. Burst-stop reassessment and the RTH-aware density repair are real search information. Do not promote, register, paper-force, or proxy-substitute.

## Rubric (PASS/FAIL + one line)

1. **Strategy charter — PASS.** Economic mechanism, candidate/family, F0→F0, predeclared falsifier, and exactly one outcome (`EVIDENCE_WAIT`) are explicit in charter/closeout/stack.
2. **Strategy vs operations — PASS.** Density repair is evidence-integrity support for the wait, not strategy progress; executor correctly did **not** claim `STRATEGY_ADVANCED` or misuse `BLOCKER_REMOVED_AND_RETESTED`.
3. **Goal progress — PASS.** Mandatory three-no-advance stop was honored; a materially different option-native evidence class opened with a concrete wake condition rather than thrash retune.
4. **Creativity / independence — PASS.** Observed term-carry diagonal is not a closed tail-hazard/semivariance/SPY-PCS retune; prior NEXT was not blindly executed as an order.
5. **Claim validity — PASS with NARROWS.** Wait is claim-appropriate; forecast_type, control geometry, and max-loss admission semantics need finalizer narrowing before any future evaluation.
6. **Evidence / test quality — PASS with repairs.** Density JSON and independent archive audit agree on 2 RTH dates / 1390 RTH / 600 non-RTH / provider false; label and counter-semantics still need cleanup.
7. **Falsification — PASS.** Current vacuity (0 complete paths) honestly forces wait; future development gates and unread 40% reserve are predeclared.
8. **Capital honesty — PASS.** No living leader/seat/L1; `$300` is labeled admission bound with `max_lots=1`; levered-ETF path risk is named; stand-aside in bearish regime is correct.
9. **Research freedom — PASS with NEXT fix.** Candidate-scoped wait correctly leaves unrelated historical L0 open; the written NEXT must not be read as a multi-week freeze of all BUILD discovery.
10. **ONE NEXT — PASS with amendment.** Keep RTH append-only data wake as primary for this candidate; amend freedom + no-advance-counter semantics so pure waits do not re-trigger burst-stop thrash.

## Independent evidence audit

Cited density artifact `.cache/platform/option_quote_archive_density_2026-07-15T2152.json` and raw archive recomputation:

| Claim | Executor | Challenger recompute | Disposition |
|---|---|---|---|
| archive rows | 1,990 | 1,990 | ACCEPT |
| archive-date labels | 2026-07-11/13/14 | same | ACCEPT |
| weekday RTH market dates | 2 (`07-13`, `07-14`) | 2 | ACCEPT |
| RTH / non-RTH rows | 1,390 / 600 | 1,390 / 600 | ACCEPT |
| Saturday off-hours false positive | 2026-07-11 23:36 NY from `2026-07-12T03:36Z` | confirmed Saturday | ACCEPT |
| `provider_backtest_eligible` | false | false | ACCEPT |
| complete managed paths | 0 | 0 (no path join exists) | ACCEPT |
| aggregate median half-spread | $0.625 | $0.625 via unfiltered `(ask-bid)/2` on all 1,990 rows | ACCEPT as **aggregate chain statistic only** |
| current TSLL regime | bearish / stand-aside | not re-scored live; accept as labeled research-run context | ACCEPT as context, not edge |

Liquidity feasibility note (not a reject of the wait): unfiltered median `$0.625` is widened by deep OTM/ITM quotes. Restricting to positive-bid calls with strike 8–20 and half-spread `<=$0.10` still yields ~70 contracts on each RTH date, so the frozen `$0.10` leg gate is strict but not obviously impossible. Exact diagonal pair admission rate remains unmeasured and must be reported as path-eligibility density **without** PnL before any F1 claim.

## Acceptances

1. **Burst stop was mandatory.** Prior epoch three exact no-advances (recent-downshock, downside-semivariance, SPY theta-carry) correctly barred a fourth nearby retune.
2. **Observed term-carry is a valid successor class** for this economic claim. Assumed-IV / BS diagonal replay would answer a different question and was correctly refused for this candidate.
3. **`EVIDENCE_WAIT` is honest.** Two RTH dates and zero complete entry-to-exit packages cannot support F1 under the predeclared floors.
4. **RTH-aware density repair is useful search information.** Old any-local-date counting inflated plumbing to a false three-date story; corrected summarizer fails closed. This is **not** strategy advancement.
5. **Capital / authority restraint is clean.** No L1, leader, registry, paper force, shadow, arm, broker, or live claim.
6. **Candidate-scoped wait** correctly preserves unrelated historical-underlying / BS-proxy L0 discovery for independent mechanisms.

## Required finalizer repairs (claim-invalidating or thrash-risk)

### R1. Freeze matched non-rich control geometry before any evaluation

Stack names “eight frozen matched non-rich term-slope controls” but does **not** freeze match geometry: residual on front/back extrinsic-per-day, delta/DTE/strike/date distance, same-snapshot requirement, one-to-one vs many-to-one, or exclusion when no control exists. Without this, the first non-vacuous dataset can quietly invent the control after seeing outcomes.

**Required before first outcome evaluation:** write a frozen control spec into the charter/epoch (even while still waiting). Until frozen, no F1 claim is possible even if path count hits 20.

### R2. Clarify max-loss semantics

`$300` is an **entry admission bound** (debit + `$50` reserve), not a proved structural worst-case under assignment, gap, or stressed liquidation on levered TSLL. Keep that language everywhere capital fields appear. Do not let `max_loss_usd=$300` be skimmed as capital-seat defined-risk equivalence. Discovery DD ceiling `$150` is looser than capital-seat window DD `$75` and must remain labeled discovery-only.

### R3. Correct forecast_type label

Charter uses `timing + realized_vs_implied_vol + direction_up`. The economic claim is **observed term-structure / front-vs-back extrinsic carry** plus mild direction, not classic RV-vs-IV. Relabel to something like `timing + term_structure_extrinsic_carry + direction_up` so forecast and option structure stay aligned under Layered Edge Doctrine.

### R4. Fix `excluded_non_rth_dates` semantics / naming

Current implementation is “dates that contain at least one non-RTH quote,” which can include a valid RTH market date that also has an after-hours print (test fixture expects `2026-07-14` in both market and excluded lists). Rename or document as `dates_with_non_rth_quotes` / keep a separate `fully_excluded_dates` for pure non-RTH labels. Do not let readers think RTH market dates were excluded.

### R5. No-advance counter must not thrash pure evidence waits

New epoch already records `completed_wakes_in_epoch=1`, `consecutive_no_strategy_advance=1` for this `EVIDENCE_WAIT`. If every distinct-RTH append reaffirmation is counted as a completed no-advance strategy wake, the epoch will hit pivot/burst-stop after two/three data collects while the frozen wake condition is still unmet. That is thrash.

**Required:** pure data-append reaffirmations of the same unmet `EVIDENCE_WAIT` condition do **not** increment the strategy no-advance streak toward pivot/burst-stop. Count a no-advance strategy close only when a discriminating strategy decision is possible and fails, or when the design is reassessed for a new reason. Keep candidate wait alive across multi-session collection.

### R6. Amend ONE NEXT so off-hours freedom is explicit

Executor NEXT is correct for the candidate data path, but incomplete as the sole global seed: it can be misread as “only TSLL capture forever.” Finalizer must keep exactly one seed while encoding:

- **If distinct weekday RTH and condition unmet:** one all-expiration TSLL append + density/path-eligibility update; no outcome evaluation.
- **If off-hours / condition still unmet:** free independent L0 discovery on a **different** economic mechanism is allowed and preferred over idle re-digest; do not reopen quarantined families; do not evaluate this candidate early; do not proxy-satisfy observed gates.
- **If wake condition met:** resume exact `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1` decision under frozen gates/control geometry.

## Soft findings (do not overturn outcome)

1. **Aggregate median half-spread is the wrong fill prior.** Executor already says exact legs must pass `$0.10`; keep that. Optional: persist filtered near-money median as a second diagnostic so `$0.625` is not over-read.
2. **Orientation snapshot still embeds pre-repair world** (`orientation.json` shows prior tail-hazard epoch active and observed plumbing `TSLL:3` / `plumbing_gate_met:true`). That is acceptable as start-of-wake orientation only; living readiness/epoch files must remain the post-repair truth after integration.
3. **12 dates / 20 paths / 8 controls is ambitious.** Not a fail. Require intermediate **admission-rate / pair-count / control-support** reporting on the data path without opening outcomes, so sparse liquidity is detected early.
4. **Income coverage text now correctly says 2/3 dates** and plumbing-only floor; keep that after regenerate.
5. **Preferred lanes.** Bullish diagonal is inside preferred long-biased diagonal income lane; supersession of tail-hazard was justified by mechanism/evidence-class change, not recipe hopping.

## Dispositions on executor claims

| Claim | Disposition |
|---|---|
| Outcome `EVIDENCE_WAIT`, funnel F0→F0, advancement false | **ACCEPT** |
| Search information from reassessment + density repair | **ACCEPT** |
| No capital seat / L1 / registry / paper / shadow / live | **ACCEPT** |
| Observed claim cannot use BS substitution | **ACCEPT** |
| Complete Layered Edge Stack ready for F1 evaluation | **NARROW** — freeze control geometry + max-loss/forecast labels first |
| ONE NEXT = only RTH TSLL append | **AMEND** — add off-hours independent-discovery freedom + no-advance counter rule |
| Density repair tests/green suite | **ACCEPT pending finalizer re-verification** (challenger did not re-run full suite; recomputed archive density agrees) |

## What finalizer must not do

- Do not convert wait into proxy F1.
- Do not reopen closed tail-hazard / semivariance / SPY theta families.
- Do not spend sealed holdouts.
- Do not auto-promote shadow/live or arm agentic.
- Do not claim RUN COMPLETE from this critique phase.
- Do not treat tooling/coverage alone as strategy advancement.

## Challenger judgment on strategy outcome

Keep: **`EVIDENCE_WAIT`**.

Do **not** reclassify as `FAMILY_CLOSED` (mechanism not tested).
Do **not** reclassify as `STRATEGY_ADVANCED` (no path outcomes).
Do **not** reclassify as `BLOCKER_REMOVED_AND_RETESTED` unless finalizer both freezes control/geometry repairs **and** still can only reaffirm wait or close — density repair alone already retested to wait and is not strategy advancement.

## Paths reviewed

- `reports/trader-wakes/moa/2026-07-15T2152/meta.json`
- `reports/trader-wakes/moa/2026-07-15T2152/executor-closeout.md`
- `reports/trader-wakes/moa/2026-07-15T2152/strategy-charter.md`
- `reports/trader-wakes/2026-07-15T2152-moa-exec.md` / `LATEST.md`
- `reports/readiness/LATEST.md`
- `reports/readiness/income-coverage-LATEST.md`
- `configs/search_epoch.json`
- `docs/SEARCH_DESIGN_REASSESSMENT_2026-07-15T2152.md`
- `docs/BUILD_LAB_ENVIRONMENT.md`, `docs/INCOME_STRATEGY_COVERAGE.md`, `docs/TRADER_LAYERED_EDGE_DOCTRINE.md`
- `.cache/platform/option_quote_archive_density_2026-07-15T2152.json`
- `.cache/platform/option_quotes/TSLL_archive.csv` (independent recompute)
- code/tests delta: `trader_platform/research/option_quote_observations.py`, `tests/test_option_quote_observations.py`

MOA_CHALL_DONE

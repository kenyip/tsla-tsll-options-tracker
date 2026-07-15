# MOA challenger critique — 2026-07-15T1350 (Grok 4.5)

PHASE: BUILD / L0. Sleeve USD 3000. PARTIAL critique phase only.
Roles: read-only judgment. No evolve --apply, no broker, no arm, no commit/push/merge, no RUN COMPLETE.

## Executive disposition

**PASS WITH NITS** on strategy substance.

Accept executor decision `FAMILY_CLOSED` for exact family `MONTHLY_OPEX_POST_EXPIRY_BROAD_INDEX_DRIFT` (candidate `MONTHLY_OPEX_POST_EXPIRY_BULL_CALL_14D_V1`) at `F0_MECHANISM → F0_MECHANISM`. Strategy advancement: **false**. Search information: **yes**.

Independent checks (this challenger session):
- Canonical evidence: `reports/trader-wakes/moa/2026-07-15T1350/monthly-opex-post-expiry.json`
- Challenger-time SHA-256: `249b3124b131c6a45d7eee21fe73f1117b12f56a953c979225209c6b504505b4` (matched executor; finalizer later regenerated only `generated_at` plus explicit population-bias semantics at final SHA `15359b3d...`)
- `strategy_outcome=FAMILY_CLOSED`; `decision=CLOSE_MONTHLY_OPEX_POST_EXPIRY_TRAIN_FAMILY`; funnel `F0_MECHANISM → F0_MECHANISM`
- Config: equal-weight SPY/QQQ/IWM/DIA; next session after holiday-adjusted third-Friday OPEX vs first-Friday same-month control; 5-session hold; train_fraction 0.60; min_train 48; 10 bps labeled underlying RT; bootstrap n=10000, block_length=3, one-sided 90%
- Train: n=74 episodes (2016-02 through 2022-04)
  - event basket mean after 10 bps: `+0.4000275589%` (pass absolute)
  - control mean after 10 bps: `+0.0831803451%`
  - paired excess mean / median: `+0.3168472137%` / `+0.2233612315%` (pass point excess)
  - paired positive frequency: `54.05405405%`
  - bootstrap LB90: `-0.2541751435%` — **decisive fail** (`paired_excess_bootstrap_lb90_positive=false`)
  - integrity_violations: `[]` / gate_pass: `false`
- Manual episode recomputation of event/control/paired means and pos-frequency matches JSON within float noise; sequential control-before-event / non-overlap walk finds 0 integrity issues
- Holdout: 50 blueprints (2022-05 through 2026-06); `outcome_metrics_read=false`, `simulation_run=false`
- Option stage: `pricing_calls=0`, `pricing_run=false`, status `NOT_RUN_TRAIN_GATE_FAILED`
- Future structure labels only: 14-DTE $2 bull call; `capital_fit_usd=max_loss_usd=200`; `max_lots=1`; not a seat
- Population: fixed basket; `survivorship_bias=true`, `listing_bias=true`, `generalization_allowed=false` — honest
- Focused lab tests re-run: **7/7 OK** (`tests/test_monthly_opex_post_expiry_train_lab.py`) — holiday OPEX adjust + outcome-free blueprint, train gates, bootstrap-only reject control, absolute-vs-paired non-rescue, holdout/option unread payload, invalid chronology fail-close, CLI import
- Active epoch: `2026-07-15-viable-path` (`started_stamp=2026-07-15T0024`); prior epoch no-advance = 2 (`TSLL_TSLA_5D_TRACKING_SHORTFALL_REBOUND`, `ONE_RISK_UNIT_CADENCE_POLICY_F0`); accepting this close → active-epoch no-advance **3** → **strategy_burst_stop_required**
- Living leader / capital path: none / empty
- Executor-claimed full suite 304/304, shared 20/20, smoke, and substantive reproduction **not** fully re-run here beyond focused 7/7 + artifact math; finalizer must re-verify independently

## Canonical evidence (challenger-inspected)

| Item | Path / value |
|---|---|
| Artifact | `reports/trader-wakes/moa/2026-07-15T1350/monthly-opex-post-expiry.json` |
| Challenger-time SHA-256 | `249b3124b131c6a45d7eee21fe73f1117b12f56a953c979225209c6b504505b4` (final current SHA is recorded by finalizer) |
| Lab | `scripts/monthly_opex_post_expiry_train_lab.py` |
| Tests | `tests/test_monthly_opex_post_expiry_train_lab.py` |
| Closeout | `reports/trader-wakes/moa/2026-07-15T1350/executor-closeout.md` |
| Outcome | `FAMILY_CLOSED` |
| Funnel | `F0_MECHANISM` → `F0_MECHANISM` |
| Closed family | `MONTHLY_OPEX_POST_EXPIRY_BROAD_INDEX_DRIFT` |
| Candidate | `MONTHLY_OPEX_POST_EXPIRY_BULL_CALL_14D_V1` |
| Holdout | unread; no option sim |
| Evidence level | L0 underlying discovery; labeled 10 bps sensitivity; no option marks |
| Living leader / seat | none / none |
| Challenger re-run tests | 7/7 OK |
| Executor-claimed full suite | 304/304 (finalizer re-verify) |

## Rubric

### 1. Strategy charter — PASS
Economic mechanism (post-monthly-OPEX dealer/rebalance unwind → short positive broad-index drift vs outcome-free first-Friday control), candidate/family scope, F0 train-only target, predeclared multi-gate falsifier (n≥48, positive after-cost event mean, positive paired excess, positive block-bootstrap LB90, zero integrity), and exact close decision are explicit in closeout + JSON + exec report. Layered Edge Stack fields are present for the eventual bull-call expression and correctly withheld from pricing. One closed outcome: `FAMILY_CLOSED`.

### 2. Strategy vs operations — PASS
New holiday-aware paired event-study lab + tests are capability, but the dependent frozen experiment ran to an advance-or-close decision in the same wake. Capability is correctly labeled search information, not strategy advancement. Not capability-only theater; not a fake `BLOCKER_REMOVED_AND_RETESTED` without retest.

### 3. Goal progress — PASS
Honest F0 close of a novel calendar-event mechanism improves later paper odds by rejecting unconditional post-OPEX five-session broad-index drift under a dependence-aware uncertainty bar. Discriminating evidence: positive point estimate and positive absolute after-cost mean, but LB90 remains negative — classic non-rescue uncertainty fail, not integrity fail. Holdout unspent; options unpriced. No false advance. Capital-first correct.

### 4. Creativity and independence — PASS
Prior NEXT `MONTHLY_OPEX_POST_EXPIRY_DRIFT_F0` was executed with justification (pivot after no-advance 2; materially different from closed cadence / tracking-shortfall / monthly **cross-section** HV-momentum / VRP / **TOM first-session** / session-time families). Not a familiar TSLL PCS retune. Freedom audit holds: caller did not assign DNA. After accept, epoch no-advance = 3 forces **burst-stop reassessment**, not another volume experiment.

### 5. Claim validity — PASS
Prerequisites match the experiment: historical adjusted closes only; labeled underlying 10 bps sensitivity (not option fill); train before holdout; no observed option marks, L1, registry, paper, shadow, arm. Capital shape for future structure stated as structural ceiling only. Survivorship/listing bias and non-independence of four index ETFs disclosed; no cross-product generalization claimed. Equal event/control costs correctly noted as canceling from paired excess, so absolute after-cost gate remains necessary — and it passed while uncertainty still closed the family.

### 6. Evidence and test quality — PASS WITH NITS
Real tools with cited paths; SHA verified; holdout unread verified; option stage zero; integrity empty; focused tests cover the right boundaries (holiday OPEX, outcome-free blueprint, bootstrap-only reject, absolute-vs-paired non-rescue, unread holdout/options, chronology fail-close).

Nits (non-blocking):
- Do not overclaim full-suite 304/304 or `SUBSTANTIVE_REPRODUCTION_OK` without independent finalizer re-run on unchanged sources (exclude only `generated_at`).
- `population_pure: true` coexists with survivorship/listing bias flags — acceptable if read as “fixed complete basket membership,” but keep generalization_allowed false on living surfaces.
- Shared event-study/bootstrap 20/20 claimed by executor; challenger re-ran only the OPEX module 7/7.

### 7. Falsification — PASS
Predeclared conjunction fires clearly on the uncertainty gate alone. Dominant failure is correctly **insufficiently certain incremental train drift vs first-Friday control**, not negative point edge or integrity. Quarantine exact SPY/QQQ/IWM/DIA + first-Friday control + next-session entry + five-session hold + 60/40 + 10 bps + three-month block-bootstrap family from unchanged reruns. Correct ban on holdout peek and option pricing rescue. Nearby calendar/control/hold mutations must not reopen without a genuinely new economic mechanism or evidence class.

### 8. Capital honesty — PASS
No living leader, no B-check, no L1/seat. Future one-lot defined-debit labels `$200` structural width bound / `max_lots=1` only; no path DD or paid debit simulated. No shadow/live/arm language. Readiness phase/B checks correctly unchanged by strategy result (only NEXT needs update after accept).

### 9. Research freedom — PASS
Did not freeze on observed-option archive density (3/3 plumbing remains non-edge). Used independent historical-underlying event-study route. Did not reopen quarantined families. Did not tunnel TSLL PCS. No unnecessary allowlist.

### 10. ONE highest-information NEXT — PASS (with tight merge)
Executor seed `SEARCH_BURST_STOP_REASSESS_2026-07-15` is correct after third consecutive active-epoch no-advance. Merged seed below locks quarantine boundaries, forbids holdout/options rescue, and requires written search-design/data reassessment before any new strategy experiment. Not another volume wake. Not paper/shadow/arm/live.

## Material findings for finalizer

**Accept**
1. `FAMILY_CLOSED` F0→F0; no strategy advancement.
2. Exact family `MONTHLY_OPEX_POST_EXPIRY_BROAD_INDEX_DRIFT` / candidate `MONTHLY_OPEX_POST_EXPIRY_BULL_CALL_14D_V1` quarantined from unchanged reruns.
3. Search information: reusable holiday-aware paired OPEX event-study lab with train/unread-holdout, bootstrap uncertainty, option-stage fail-close, provenance hashes, and behavioral/boundary/negative controls.
4. Capital path empty; leader none; L0 underlying only; pricing_calls=0.
5. Active-epoch no-advance becomes **3**; `strategy_burst_stop_required=true`; pivot alone is insufficient — stop the burst.
6. Merged NEXT: `SEARCH_BURST_STOP_REASSESS_2026-07-15` (refined).

**Repair before integration**
1. Independently re-run focused OPEX tests + shared event-study regressions + full suite; do not reuse executor counts alone.
2. Independently re-run substantive reproduction on unchanged source hashes (exclude only `generated_at`); keep holdout unread and pricing_calls=0.
3. On integration, set readiness next strategy action to merged burst-stop reassessment; active-epoch streak **3**; `strategy_burst_stop_required=true`; `strategy_pivot_required=true` (superseded by burst-stop).
4. Promote closed family into compounding/orientation closed-family surfaces with dominant failure = uncertainty-bounded paired excess fail (not “no drift”).
5. Optional: clarify `population_pure` wording vs survivorship flags in any durable doctrine touch.

**Reject**
- Reading the 50 reserved holdout outcomes or pricing the bull-call after train fail.
- Reopening via nearby OPEX window / control Friday / hold-length / block-length retunes without a new mechanism class.
- Claiming L1 / capital seat / paper path from positive point estimates alone.
- Treating three-date option archive as edge evidence or as the reason for burst-stop.
- Another strategy-volume BUILD wake inside this epoch before written reassessment.
- Live/shadow/arm/broker/funding actions.

## Disposition line

`PASS WITH NITS` — accept `FAMILY_CLOSED` for `MONTHLY_OPEX_POST_EXPIRY_BROAD_INDEX_DRIFT` (train n74; LB90 −0.2542%); quarantine exact family; epoch no-advance=3 → burst-stop NEXT; finalizer re-verifies suite/reproduction and updates readiness streak/NEXT.

PARTIAL phase only. Finalizer owns verification, learning promotion, staging, and integration.

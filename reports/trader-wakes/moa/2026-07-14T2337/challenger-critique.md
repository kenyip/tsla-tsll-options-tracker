# MOA challenger critique — 2026-07-14T2337 (Grok 4.5)

PHASE: BUILD / L0. Sleeve USD 3000. PARTIAL critique phase only.
Roles: read-only judgment. No evolve --apply, no broker, no arm, no commit/push/merge, no RUN COMPLETE.

## Executive disposition

**PASS WITH NITS** on strategy substance.

Accept executor decision `FAMILY_CLOSED` for exact family `MONTHLY_CROSS_SECTION_12_1_MOMENTUM_FORWARD_DRIFT` / candidate `CROSS_SECTION_12_1_MOMENTUM_PCS_21D_V1` at `F0_MECHANISM → F0_MECHANISM`.

Independent checks (this challenger session):
- Canonical JSON present at `reports/trader-wakes/moa/2026-07-14T2337/cross-section-momentum-train.json`.
- Live SHA-256 of current file: `ad9a8c415b1d8503156856bc9709104c7c6dc63b32f23313becad57dfc0d4311` (executor closeout cited `3e5ce119…`; substantive train metrics match the claimed close — treat executor SHA as pre-regeneration if finalizer already rewrote `generated_at`/file; metrics, not hash branding, drive the strategy judgment).
- Train gates: n40; top +2.9494%; bottom +2.0029%; paired excess +0.9465%; median +0.3411%; positive frequency 52.5%; block-bootstrap LB90 −1.3561% (10k samples, block=3, seed 20260714). Only `paired_excess_bootstrap_lb90_positive` is false among declared gates; integrity empty; holdout unread; `pricing_calls=0`.
- Decision / outcome: `CLOSE_CROSS_SECTION_12_1_MOMENTUM_TRAIN_FAMILY` / `FAMILY_CLOSED`; `registration_eligible=false`; `f2_or_l1_claim=false`.
- Population validity: `survivorship_bias=true`, `listing_bias=true`, `generalization_allowed=false`, `ranking_complete=true`, `population_pure=true`.
- Focused lab tests re-run: **6/6 OK** (`tests/test_cross_section_momentum_train_lab.py`), including the real failure-mode control `test_positive_point_edge_with_nonpositive_bootstrap_bound_closes_family`.

Strategy advancement: **false**. Search information: **yes** (new 12−1 harness + honest F0 close + uncertainty-gate discipline). This is useful falsification, not a capital seat.

Because this is the **third consecutive active-epoch no-advance close** after integrated/accepted 2203 and 2302, accept `strategy_burst_stop_required=true` and make NEXT unconditional: `SEARCH_BURST_STOP_REASSESS_2026-07-14`. Do not open a fourth strategy-search wake in this burst.

## Canonical evidence (challenger-inspected)

| Item | Path / value |
|---|---|
| Artifact | `reports/trader-wakes/moa/2026-07-14T2337/cross-section-momentum-train.json` |
| Current SHA-256 | `ad9a8c415b1d8503156856bc9709104c7c6dc63b32f23313becad57dfc0d4311` |
| Executor-cited SHA | `3e5ce119da7966709fca68a412df5c5c6868cd50c96b0bfe88807de0f8c25088` (pre-regen claim; metrics match) |
| Lab | `scripts/cross_section_momentum_train_lab.py` |
| Tests | `tests/test_cross_section_momentum_train_lab.py` |
| Outcome | `FAMILY_CLOSED` / `CLOSE_CROSS_SECTION_12_1_MOMENTUM_TRAIN_FAMILY` |
| Funnel | `F0_MECHANISM` → `F0_MECHANISM` |
| Closed family | `MONTHLY_CROSS_SECTION_12_1_MOMENTUM_FORWARD_DRIFT` |
| Train n | 40 (≥24) |
| Top mean after 20bps | +0.029494364456613974 |
| Bottom mean after 20bps | +0.020028869955858015 |
| Paired excess mean / median / pos freq | +0.00946549450075596 / +0.0034113213988100077 / 0.525 |
| Bootstrap LB90 | −0.013561302557407338 |
| Gate pass | false (`paired_excess_bootstrap_lb90_positive` only false among declared gates) |
| Holdout | 27 blueprints reserved (first rank 2022-08-31; first entry 2022-09-01); `outcome_metrics_read=false`, `simulation_run=false` |
| Option stage | `NOT_RUN_TRAIN_GATE_FAILED`, `pricing_calls=0` |
| Capital context | structural `capital_fit_usd=max_loss_usd=100`, `max_lots=1` (not simulated trade loss) |
| Living leader / seat | none / none |
| Population | fixed present-day 14 names; survivorship+listing bias labeled; no generalization |
| Challenger re-run tests | 6/6 OK |
| Executor-claimed full suite | 281/281 (not re-run in this critique phase; finalizer must re-verify) |

## Rubric

### 1. Strategy charter — PASS
Economic mechanism (intermediate 12−1 relative strength via underreaction), candidate/family scope, F0-only funnel, predeclared multi-part falsifier (n, absolute top drift, paired point excess, bootstrap LB90, integrity), and exact binary advance-or-close decision are explicit in closeout, exec report, and JSON. One closed outcome: `FAMILY_CLOSED`.

### 2. Strategy vs operations — PASS
Harness/tests are capability, but the wake ran the dependent train-only experiment to an advance-or-close decision in-session. Capability is correctly labeled as search information, not strategy advancement. Not capability-only theater.

### 3. Goal progress — PASS
Honest F0 falsification of a new cross-sectional momentum pre-screen improves later paper odds by removing a non-working mechanism before option marks, and correctly escalates the epoch to burst-stop reassessment. No false advance. Stand-aside/close is valid progress under capital-first doctrine.

### 4. Creativity and independence — PASS
Honors `strategy_pivot_required` after two epoch no-advances. Mechanism is materially different from closed low-HV selector (risk ranking) and from closed daily PCS momentum/entry-filter families: monthly 252-session lookback with explicit 21-session skip, top3 vs bottom3, non-overlapping 21-session outcomes, train-only. No TSLL PCS volume tunnel; no holdout peek; no control inversion.

Nit for reassessment design (not a reject): same fixed present-day 14-name panel as 2302. Acceptable when labeled non-generalizing L0; still a shared convenience/survivorship limitation that the burst-stop reassessment must confront rather than paper over.

### 5. Claim validity — PASS
Prerequisites match the experiment: adjusted underlying closes; labeled 20-bps friction; discovery/L0 only; train before holdout; no option marks/fills/tradable option PnL; no L1/seat/registry/paper/shadow/arm. Positive absolute and paired point estimates are **not** treated as survivors under the frozen uncertainty gate. Good discipline.

### 6. Evidence and test quality — PASS WITH NITS
Real code, multi-name panel (2,645 common rows 2016-01-04→2026-07-13), non-overlapping monthly episodes, prior-completed features (`feature_end = rank − 21`), next-session entry, disjoint groups, integrity checks, strict JSON, deterministic bootstrap, unread-holdout reservation, SHA-cited artifact, CLI import path. Challenger re-ran 6/6 lab tests including bootstrap-only reject control.

Nits for finalizer (non-blocking if already repaired; re-verify):
- Prefer a negative control where top mean and paired excess mean are positive but bootstrap LB90 ≤ 0 must fail `gate_pass` (this wake’s real failure mode). Present tests include that control — keep it green.
- Do not overclaim full-suite counts in finalizer without independent re-run.
- Reuse of shared low-HV panel/bootstrap helpers is good; keep shared contracts from drifting between the two cross-section families.
- Reconcile SHA narrative: if the artifact is regenerated, state which fields changed and that substantive payload matched excluding only nondeterministic metadata.

### 7. Falsification — PASS
Predeclared density, absolute top drift, paired point excess, bootstrap LB90, and integrity. Dominant failure is correctly the **uncertainty-bounded incremental edge** (LB90 −1.36% with only 52.5% positive excess), not absolute top drift (which was positive). Quarantine exact family plus unchanged 252/21/top3/21-session fixed-panel reruns. Explicit ban on holdout peek, nearby retune, and control inversion is correct.

### 8. Capital honesty — PASS
No living leader, no B-check, no L1/seat. Structure remains `conditional_put_credit_spread_not_yet_priced`. Structural one-lot $1-wide PCS bound $100 only. No shadow/live/arm language as authority.

### 9. Research freedom — PASS
Did not freeze on observed-option archive density. Used an independent historical-underlying pre-screen route. No allowlist or familiar-recipe lock. Good use of free search under capital envelope.

### 10. ONE NEXT seed — PASS (make unconditional)
Executor’s conditional phrasing is fine for partial closeout. After challenger accept, NEXT is unconditional:

`SEARCH_BURST_STOP_REASSESS_2026-07-14`

Stop strategy-search volume. Reassess search design/data using the three active-epoch outcomes (2203 PCS early-exit, 2302 low-HV cross-section, 2337 12−1 momentum). Distinguish mechanism weakness from fixed present-day panel, uncertainty/density, and pre-option selector limits. Inventory genuinely independent evidence routes; open at most one new predeclared epoch **or** emit `DIMINISHING_RETURNS`. No holdout peek, nearby momentum/HV retune, option pricing, paper, shadow, arm, broker, or live action.

## Disposition summary

| Decision | Value |
|---|---|
| Overall | **PASS WITH NITS** |
| Strategy outcome accepted | `FAMILY_CLOSED` |
| Funnel | F0 → F0 |
| Strategy advanced | false |
| Active-epoch no-advance streak after accept | **3** |
| Burst stop | **required** |
| Capital / authority change | none |
| Hard stops crossed | none observed |

## Finalizer must

1. Preserve `FAMILY_CLOSED` / no holdout peek / no option pricing / no point-estimate rescue.
2. Keep or reconfirm bootstrap-LB-only reject negative control; re-verify focused tests.
3. Reproduce substantive payload excluding only `generated_at` (and any true nondeterministic metadata); cite final SHA honestly.
4. Write `learning-promotion.md` with quarantine of `MONTHLY_CROSS_SECTION_12_1_MOMENTUM_FORWARD_DRIFT` and unconditional burst-stop NEXT.
5. Update readiness/compounding surfaces so epoch streak=3, `strategy_burst_stop_required=true`, living leader still none.
6. Run verification + deterministic integration; only the gate may claim RUN COMPLETE. If foreign concurrent NEXT/new-epoch paths appear again, fail closed rather than absorb them into 2337.

## What not to do

- Do not reinterpret +0.95% paired mean as F1 advance.
- Do not inspect reserved holdout outcomes.
- Do not invert to a bottom-momentum long thesis without a new predeclared mechanism.
- Do not retune 252/21/top3/hold lengths on this panel as a “continuation.”
- Do not open another strategy-volume wake before reassessment.
- Do not promote, register, paper, shadow, arm, or live.

PHASE BOUNDARY: challenger partial only. Finalizer + deterministic integration remain.

MOA_CHALL_DONE

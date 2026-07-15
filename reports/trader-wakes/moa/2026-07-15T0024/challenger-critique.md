# MOA challenger critique — 2026-07-15T0024 (Grok 4.5)

PHASE: BUILD / L0. Sleeve USD 3000. PARTIAL critique phase only.
Roles: read-only judgment. No evolve --apply, no broker, no arm, no commit/push/merge, no RUN COMPLETE.

## Executive disposition

**PASS WITH NITS** on strategy substance.

Accept executor decision `FAMILY_CLOSED` for exact family `TSLL_TSLA_5D_TRACKING_SHORTFALL_REBOUND` / candidate `TSLL_RELATIVE_DISLOCATION_BULL_CALL_14D_V1` at `F0_MECHANISM → F0_MECHANISM`.

Independent checks (this challenger session):
- Canonical evidence present at `.cache/platform/tsll_tracking_dislocation_train_2026-07-15T0024.json`.
- Live SHA-256: `6206bdf11d28f09edc5e033eb5f44a3b7b80ec5bedcc4ff132bf02c3f3d541f1` (matches executor closeout).
- Selection diagnostics: eligible_signal_dates 454; treated_signal_candidates 36; neutral_control_candidates 274; matched_blueprints 0.
- Train: `n_pairs=0` (< predeclared minimum 20); return / paired-excess / bootstrap metrics are strict JSON `null`; `gate_pass=false`; integrity_violations empty; `zero_integrity_violations=true`.
- Decision / outcome: `CLOSE_TSLL_TRACKING_SHORTFALL_REBOUND_TRAIN_FAMILY` / `FAMILY_CLOSED`; `registration_eligible=false`; `f2_or_l1_claim=false`.
- Holdout: `n_blueprints=0`, `outcome_metrics_read=false`, `simulation_run=false`.
- Option stage: `NOT_RUN_TRAIN_GATE_FAILED`, `pricing_calls=0`, provenance `null`.
- Population validity: fixed TSLA/TSLL pair; `survivorship_bias=true`, `listing_bias=true`, `generalization_allowed=false`, `ranking_complete=true`, `population_pure=true`.
- Focused lab tests re-run: **6/6 OK** (`tests/test_tsll_tracking_dislocation_train_lab.py`), including vacuous-population fail-close and unread-holdout / no-option-pricing boundary.
- Active search epoch: `configs/search_epoch.json` = `2026-07-15-viable-path`, `started_stamp=2026-07-15T0024`, `reassessment_complete=true`. This is the first strategy-volume wake of the new epoch (prior-epoch burst-stop is historical, not a freeze on this run).

Strategy advancement: **false**. Search information: **yes** (new relative-dislocation harness + honest control-support F0 close). No capital seat.

## Canonical evidence (challenger-inspected)

| Item | Path / value |
|---|---|
| Artifact | `.cache/platform/tsll_tracking_dislocation_train_2026-07-15T0024.json` |
| SHA-256 | `6206bdf11d28f09edc5e033eb5f44a3b7b80ec5bedcc4ff132bf02c3f3d541f1` |
| Lab | `scripts/tsll_tracking_dislocation_train_lab.py` |
| Tests | `tests/test_tsll_tracking_dislocation_train_lab.py` |
| Charter | `reports/trader-wakes/moa/2026-07-15T0024/strategy-charter.md` |
| Outcome | `FAMILY_CLOSED` / `CLOSE_TSLL_TRACKING_SHORTFALL_REBOUND_TRAIN_FAMILY` |
| Funnel | `F0_MECHANISM` → `F0_MECHANISM` |
| Closed family | `TSLL_TSLA_5D_TRACKING_SHORTFALL_REBOUND` |
| Treated / controls / matched | 36 / 274 / 0 |
| Train n_pairs | 0 (min 20) |
| Dominant failure | control-support: no earlier neutral residual inside frozen match geometry |
| Holdout | unread; not simulated |
| Option stage | not run; pricing_calls=0 |
| Capital context | planned future bull_call_debit_spread 14DTE $1-wide; structural `capital_fit_usd=max_loss_usd=100`, `max_lots=1` (not simulated loss) |
| Living leader / seat | none / none |
| Active epoch | `2026-07-15-viable-path` (this stamp is epoch start) |
| Challenger re-run tests | 6/6 OK |
| Executor-claimed full suite | 288/288 (not re-run in critique phase; finalizer must re-verify) |

## Rubric

### 1. Strategy charter — PASS
Economic mechanism (TSLL vs 2×TSLA five-session tracking shortfall as leveraged-ETF dislocation rebound under TSLA trend/floor filters), candidate/family scope, F0-only target, predeclared multi-part falsifier (min pairs, integrity/match bounds, treated mean, paired excess, bootstrap LB90), and exact binary advance-or-close decision are explicit in charter, closeout, exec report, and JSON. One closed outcome: `FAMILY_CLOSED`.

### 2. Strategy vs operations — PASS
New train lab + tests are capability, but the wake exercised the dependent frozen experiment to an advance-or-close decision in-session. Capability is correctly labeled search information, not strategy advancement. Not capability-only theater.

### 3. Goal progress — PASS
Honest F0 close of the first new-epoch mechanism improves later paper odds by removing a non-operational control design before option marks or holdout spend. No false advance. Control-support failure is discriminating evidence, not thrash. Stand-aside/close is valid under capital-first doctrine.

### 4. Creativity and independence — PASS
New epoch `2026-07-15-viable-path` correctly supersedes prior burst-stop. Mechanism is materially distinct from quarantined daily PCS selectors, cross-section HV/momentum panels, SPY VRP/TOM, and session-time short-premium: residual is a TSLL−2×TSLA tracking shortfall with neutral-residual placebos and planned debit-vertical expression. Aligns with reassessment open route B (high-beta / TSLA–TSLL swing class) without reopening closed DNA. No familiar TSLL PCS tunnel; no holdout peek; no post-hoc match widening.

### 5. Claim validity — PASS
Prerequisites match the experiment: adjusted underlying closes only; labeled 20-bps underlying round-trip sensitivity; discovery/L0 only; train gate before holdout/options; no fills, observed option marks, L1, registry, paper, shadow, arm. Zero pairs correctly yield null expectancy metrics rather than fabricated zeros-as-edge. Structural debit bound is labeled context, not trade loss.

### 6. Evidence and test quality — PASS WITH NITS
Real code/tests/sims with cited paths. Challenger verified SHA, counts, gate_pass, null metrics, unread holdout, and pricing_calls=0. Focused tests cover chronology/prior controls, positive-gate behavior, bootstrap-only reject pattern, unread holdout / no option pricing, CLI import, and vacuous-population fail-close.

Nits for finalizer (non-blocking if already handled; re-verify):
- Residual diagnostics show treated residual is a thin tail (p05 ≈ −4.87% near the −4% threshold; 36 treated of 454 eligible). Keep that as **design-feasibility context**, not as evidence of rebound or non-rebound.
- With `n_pairs=0`, expectancy/bootstrap gate flags are correctly fail-closed false; do not later reinterpret null metrics as “no edge measured.”
- Do not overclaim full-suite 288/288 without independent finalizer re-run.
- Living readiness banner still names epoch `2026-07-14-reassess` and burst-stop NEXT (see rubric 10 / readiness patch). That is orientation debt, not a strategy-result defect.

### 7. Falsification — PASS
Predeclared minimum train pairs fires first. Dominant failure is correctly **control-support / frozen match geometry**, not a signed rebound expectancy. Quarantine exact family plus unchanged residual/threshold/match-bound/horizon reruns. Explicit ban on widening match tolerances after inspecting zero matches is correct and must survive learning promotion.

### 8. Capital honesty — PASS
No living leader, no B-check, no L1/seat. Structure remains conditional bull-call debit not yet priced. Structural one-lot $100 bound only. No shadow/live/arm authority language.

### 9. Research freedom — PASS
Did not freeze on observed-option archive density. Used independent historical-underlying relative-dislocation route allowed by the new-epoch reassessment. No allowlist lock; TSLL is mechanism-native pair, not capital-path privilege. No unnecessary freeze of unrelated open routes (cadence/policy, structure classes, stand-aside policy remain free).

### 10. ONE NEXT seed — PASS WITH NIT (tighten, keep direction)
Executor seed `ONE_RISK_UNIT_CADENCE_POLICY_F0` is the right **class** (reassessment route D: portfolio/inventory/cadence policy) and correctly bans reopening tracking-shortfall or closed daily selectors.

Nit / merged tightening required:
- Predeclare the **exact frozen signal stream** (which defined-risk structures/symbols/DNA sources; not closed-family retunes).
- Predeclare the cadence policy knobs (one open risk unit; correlation/symbol-cluster cap definition; concurrent-position rule) versus identical uncapped stream.
- Train-only first; dual-cost or labeled after-cost path realism on already available chronological defined-risk simulations; require non-vacuous after-cost drawdown improvement **and** non-negative expectancy; reserve holdout until train passes.
- Discovery-bar only on any F0→F1; capital-seat bar still separate; no paper/shadow/arm/live.

## Disposition summary

| Decision | Value |
|---|---|
| Overall | **PASS WITH NITS** |
| Strategy outcome accepted | `FAMILY_CLOSED` |
| Funnel | F0 → F0 |
| Strategy advanced | false |
| Active-epoch no-advance streak after accept | **1** (epoch `2026-07-15-viable-path`; not burst-stop) |
| Burst stop | **not required** for this new epoch |
| Capital / authority change | none |
| Hard stops crossed | none observed |

## Finalizer must

1. Preserve `FAMILY_CLOSED` / no match-bound rescue / no holdout peek / no option pricing / no rebound-mean fabrication.
2. Promote quarantine of `TSLL_TSLA_5D_TRACKING_SHORTFALL_REBOUND` (and unchanged residual/match-threshold variants) into compounding/orientation closed families + learning artifact.
3. Reproduce substantive payload excluding only `generated_at`; cite final SHA honestly.
4. Re-verify focused lab tests + full suite; write `learning-promotion.md` with VERIFICATION / DURABLE / LESSON / one NEXT.
5. Fix living readiness orientation: active epoch is `2026-07-15-viable-path` (not burst-stop on `2026-07-14-reassess`); living leader still none; prepend this close; set NEXT to merged cadence seed.
6. Only deterministic postflight may claim RUN COMPLETE.

## What not to do

- Do not widen residual, return-distance, trend-distance, or calendar match bounds after seeing zero matches.
- Do not invent treated/control returns from n_pairs=0.
- Do not price options or inspect a synthetic holdout to “rescue” the family.
- Do not treat structural $100 debit as observed max loss or a capital seat.
- Do not keep readiness advertising prior-epoch burst-stop as current strategy action.

MOA_CHALL_DONE

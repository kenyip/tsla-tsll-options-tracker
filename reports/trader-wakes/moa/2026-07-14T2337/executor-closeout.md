# Executor strategy charter — 2026-07-14T2337

WAKE: 2026-07-14T2337 local
PHASE: BUILD / L0 discovery
SLEEVE_USD: 3000
ROLE: GPT 5.6 Sol executor; only writer; partial phase
MARKET_CONTEXT: off-hours; no RTH paper action

## Strategy decision charter (predeclared before experiment)

- ECONOMIC MECHANISM: Gradual information diffusion and investor underreaction can make intermediate-horizon relative strength persist: liquid equities with the strongest prior completed 12-minus-1-month return should have better next-21-session drift than same-date weakest-momentum controls.
- CANDIDATE/FAMILY SCOPE: `CROSS_SECTION_12_1_MOMENTUM_PCS_21D_V1` in new family `MONTHLY_CROSS_SECTION_12_1_MOMENTUM_FORWARD_DRIFT`; month-end top-three versus bottom-three ranks on a fixed present-day liquid-equity panel, 252-session lookback skipping the most recent 21 sessions, one next-session entry, non-overlapping 21-session outcomes, chronological first 60% train only. A future one-lot $1-wide PCS is structural context only and will not be priced unless the underlying mechanism advances.
- FUNNEL: `F0_MECHANISM -> F1_TRAIN` only if the frozen discovery gate passes; otherwise `F0_MECHANISM -> F0_MECHANISM` and close the exact family.
- PREDECLARED FALSIFIER: On the chronological first 60% of eligible non-overlapping episodes, close the family if n<24, top-momentum mean return<=0, top-minus-bottom paired mean<=0, one-sided 90% circular-block-bootstrap lower bound<=0, or any chronology/overlap/group/population-integrity check fails. Holdout outcomes remain unread in this executor wake.
- EXACT DECISION TO CLOSE: `STRATEGY_ADVANCED` if every train discovery gate passes, otherwise `FAMILY_CLOSED` with the dominant failure recorded and unchanged 12-1/top-three/21-session fixed-panel reruns quarantined.

## Choice and anti-thrash judgment

The prior NEXT is accepted only at the mechanism-pivot level, not as a recipe. The active epoch has two no-advance wakes and requires a materially different mechanism. This loop pivots from the closed low-volatility selector and closed daily PCS entry-signal families to a pre-option cross-sectional intermediate-momentum mechanism. It does not invert the inspected low-HV result, reopen any closed family, use observed-option archive blockage as a stop, or run familiar PCS volume.

## Claim and capital boundary

- Evidence target: L0 train-only underlying discovery; adjusted closes with a labeled 20-bps underlying round-trip friction sensitivity applied before the first real-data run; no option marks, observed fills, option-cost/tradable-PnL claim, L1, capital seat, registry, paper, shadow, arm, broker, or live authority.
- Structure context: conditional one-lot put credit spread, not yet priced.
- `capital_fit_usd`: $100 structural upper bound for a future $1-wide PCS before net credit and closing friction.
- `max_loss_usd` one lot: $100 structural upper bound only; not an observed or simulated trade loss.
- `max_lots`: 1.

## Closed outcome

OUTCOME: `FAMILY_CLOSED`
FUNNEL: `F0_MECHANISM -> F0_MECHANISM`

Canonical artifact: `reports/trader-wakes/moa/2026-07-14T2337/cross-section-momentum-train.json`
SHA-256: `3e5ce119da7966709fca68a412df5c5c6868cd50c96b0bfe88807de0f8c25088`

- Train episodes: 40; untouched holdout blueprints: 27.
- Top-momentum mean after labeled 20-bps sensitivity: `+2.9494%`.
- Bottom-momentum same-date control: `+2.0029%`.
- Paired excess mean / median / positive frequency: `+0.9465%` / `+0.3411%` / `52.5%`.
- One-sided 90% circular-block-bootstrap LB: `-1.3561%` (10,000 samples, block length 3, seed 20260714).
- Failed frozen gate: `paired_excess_bootstrap_lb90_positive`; every density, absolute-return, point-excess, and integrity gate passed.
- Holdout remains unread (`outcome_metrics_read=false`, `simulation_run=false`); option stage did not run (`pricing_calls=0`).

Dominant failure: the fixed selector did not establish uncertainty-bounded incremental train drift over the same-date weakest-momentum control. Positive point estimates are insufficient under the predeclared dependence-aware gate. Quarantine the exact 252/21/top-three/21-session fixed-panel family and nearby unchanged reruns; do not peek at holdout, invert the control, or tune around the failed lower bound.

Search information is separate: the new harness adds prior-completed 12-minus-1 ranks, non-overlapping chronology, disjoint controls, labeled friction, deterministic block bootstrap, strict JSON, direct-script CLI use, unread-holdout reservation, and advance/reject fixtures. This capability is not strategy advancement.

Validation: new tests 5/5; focused shared-harness regression 12/12; full suite 281/281; compile, exact substantive reproduction, strict-JSON/assertion audit, platform smoke, coverage refresh, and pre-closeout `git diff --check` green. Fixed present-day survivorship/listing bias and no-generalization scope remain explicit. No living leader or readiness/authority transition.

Freedom audit: materially different cross-sectional momentum mechanism across 14 names; no allowlist, stale leader, observed-option block, or familiar PCS-volume loop constrained the choice.

## ONE NEXT SEED

`SEARCH_BURST_STOP_REASSESS_2026-07-14`: if challenger/finalizer accepts this third active-epoch no-advance close, stop strategy-search volume and reassess search design/data before opening a new epoch or declaring diminishing returns. No holdout peek, nearby momentum/HV retune, option pricing, paper, shadow, arm, broker, or live action.

PHASE BOUNDARY: executor partial only; challenger and finalizer pending; no commit/push/merge or RUN COMPLETE claim.

MOA_EXEC_DONE

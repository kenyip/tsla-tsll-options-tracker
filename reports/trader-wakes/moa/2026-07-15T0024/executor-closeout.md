# MOA BUILD executor closeout — 2026-07-15T0024

PHASE: BUILD / L0 discovery
SLEEVE_USD: 3000
ROLE: GPT 5.6 Sol executor; only writer
SESSION: premarket recovery of the existing exact-stamp loop
PAPER_ONLY: true
OUTCOME: `FAMILY_CLOSED`
STRATEGY ADVANCEMENT: false; `F0_MECHANISM -> F0_MECHANISM`

## Strategy decision charter

- Economic edge mechanism: a path-dependent five-session TSLL tracking shortfall versus twice TSLA's five-session return may represent transient leveraged-ETF rebalance/noise dislocation rather than a generic pullback. When TSLA is above a fully warmed SMA100 and its five-session return is at least -5%, an unusually negative residual may mean-revert over the next five sessions.
- Candidate/family: `TSLL_RELATIVE_DISLOCATION_BULL_CALL_14D_V1` / `TSLL_TSLA_5D_TRACKING_SHORTFALL_REBOUND`. Frozen selector: `r_TSLL(5d) - 2*r_TSLA(5d) <= -4%`; next-session entry; five-session hold; non-overlapping treated episodes; earlier neutral-residual controls (`-1%..+1%`) matched without replacement on TSLA five-session return, TSLA trend distance, and calendar distance. No nearby threshold, horizon, structure, or symbol mutation was authorized.
- Funnel: `F0_MECHANISM`; target was `F0_MECHANISM -> F1_TRAIN` only. Holdout outcomes and option marks were reserved.
- Predeclared falsifier: close the exact family if train has fewer than 20 valid matched non-overlapping pairs; any chronology, overlap, control-reuse, residual-group, or frozen match-bound violation; non-positive treated mean after the labeled 20-bps underlying round-trip sensitivity; non-positive treated-minus-control mean; or a non-positive one-sided 90% circular-block-bootstrap lower bound.
- Exact decision closed: `FAMILY_CLOSED`.

The original charter remains at `reports/trader-wakes/moa/2026-07-15T0024/strategy-charter.md`. Recovery did not supersede it or open another family.

## Executor judgment

The fixed family fails before return estimation because the frozen treated population has no comparable prior control support. On the 984-row common TSLA/TSLL adjusted-close panel (2022-08-09 through 2026-07-13), the runner found 454 eligible signal dates, 36 treated shortfall candidates, and 274 neutral-residual control candidates, but zero matched blueprints under the predeclared prior-only, 63-session, 5-percentage-point TSLA-return, 15-percentage-point trend-distance, no-reuse, and disjoint-window constraints. Therefore train `n_pairs=0`, below the predeclared minimum 20; return, paired-excess, and bootstrap metrics correctly remain JSON `null` rather than being fabricated.

Dominant failure mechanism: eligible TSLL tracking-shortfall events did not admit an earlier neutral-residual control inside the frozen match bounds and disjoint chronology. This is a control-support failure, not evidence of rebound or non-rebound expectancy. Do not rescue it by widening the residual, return-distance, trend-distance, or calendar thresholds after inspecting this result.

Canonical evidence:
- `.cache/platform/tsll_tracking_dislocation_train_2026-07-15T0024.json`
- Current SHA-256: `6206bdf11d28f09edc5e033eb5f44a3b7b80ec5bedcc4ff132bf02c3f3d541f1`
- Lab: `scripts/tsll_tracking_dislocation_train_lab.py`
- Tests: `tests/test_tsll_tracking_dislocation_train_lab.py`

## Evidence validity

- Chronology: both features are computed on the signal close; entry is the next session and exit is five sessions later. Controls must precede treated signals. Entry-bar shock testing leaves the first selection unchanged.
- Density: the predeclared minimum is non-vacuous at 20 train pairs. The exact run produced zero, so the family fails closed before any expectancy claim.
- Controls: matching is outcome-independent and without replacement. Zero matched blueprints means there is no defensible same-design counterfactual population for the inspected selector.
- Costs: 20 bps is labeled underlying round-trip sensitivity only. Because no pair reached evaluation, no after-cost edge exists to report. No option cost, bid/ask, assignment, or fill claim was made.
- Holdout: `outcome_metrics_read=false`, `simulation_run=false`; no holdout pair outcomes are persisted.
- Option stage: `pricing_run=false`, `pricing_calls=0`, option mark provenance `null`.
- Provenance: yfinance `auto_adjust=True` caches; common panel is an inner join with no forward fill. Per-symbol paths, row counts, hashes, and discarded trailing-row counts are embedded in the JSON.
- Population: fixed TSLA/TSLL economic pair only; survivorship and listing bias are explicit; generalization is forbidden.
- Reproduction: an unchanged second run matched the complete substantive payload after excluding only `generated_at`.
- Living comparison: readiness has no living quality leader and the capital path is empty. This L0 underlying close creates neither.

## Search information versus strategy progress

Search information: the wake adds a deterministic train-only relative-dislocation harness with prior-only controls, strict chronology, overlap/control-reuse checks, labeled underlying sensitivity, uncertainty gating, strict JSON nulls for unavailable metrics, unread-holdout boundaries, and no-option-stage assertions. The exact experiment was exercised and decisively closed.

Strategy progress: none. `TSLL_TSLA_5D_TRACKING_SHORTFALL_REBOUND` remains at F0 and is quarantined from unchanged reruns. Reopening requires a materially new economic mechanism or evidence class, not wider matching or nearby threshold tuning.

## Capital / readiness / authority

- Planned future structure only: `bull_call_debit_spread`, 14 DTE, $1 width.
- `capital_fit_usd=100`.
- One-lot `max_loss_usd=100` structural width bound before closing friction; not an observed or simulated trade loss.
- `max_lots=1` operating cap.
- No L1, capital seat, B-check, registry, paper, shadow, funding, broker, arm, or live transition.
- `reports/readiness/LATEST.md` was not changed because phase and B checks did not change; its living-leader-none / empty-capital-path state remains applicable, while `configs/search_epoch.json` is authoritative for the newly active epoch.

Freedom audit: Trader retained the already-predeclared TSLL/TSLA relative-dislocation mechanism because recovery residue was valid and claim-bearing; neither the caller, a structure allowlist, a stale leader, nor observed-option blockage selected it. The close does not privilege TSLL for a capital seat.

## Verification

- Focused behavioral/boundary/negative-control plus shared bootstrap regression: `.venv/bin/python -m unittest tests.test_tsll_tracking_dislocation_train_lab tests.test_low_hv_cross_section_train_lab` -> 13/13 `OK`.
- Changed-file compile: `.venv/bin/python -m py_compile scripts/tsll_tracking_dislocation_train_lab.py tests/test_tsll_tracking_dislocation_train_lab.py` -> exit 0.
- Exact dependent experiment: `FAMILY_CLOSED`, treated candidates 36, neutral controls 274, matched/train pairs 0, holdout outcomes unread, pricing calls 0.
- Independent unchanged-source reproduction: substantive payload equality `true` after excluding only `generated_at`.
- Full suite: `.venv/bin/python -m unittest discover -s tests` -> 288/288 `OK`.
- Coverage refresh, diff checks, secret-path review, and final executor-phase status are recorded in the companion wake report after derived surfaces are regenerated.

## One next seed

`ONE_RISK_UNIT_CADENCE_POLICY_F0`: in the next zero-input BUILD wake, predeclare and test one materially distinct portfolio/cadence mechanism on already available chronological defined-risk signals: compare a one-position, correlation-capped cadence policy with the identical uncapped signal stream on train only, require a non-vacuous after-cost drawdown improvement without non-positive expectancy, reserve untouched holdout unless train passes, and do not reopen this tracking-shortfall family or any closed daily-selector DNA.

## Phase boundary

Executor evidence is partial. Grok 4.5 challenge, GPT 5.6 Sol finalization, deterministic staging/commit/integration/push, remote equality, and the completion receipt remain required. No commit, push, merge, branch switch, broker action, or `RUN COMPLETE` claim occurred.

MOA_EXEC_DONE

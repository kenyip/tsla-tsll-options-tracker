# MOA BUILD executor closeout — 2026-07-14T0859

PHASE: BUILD / research only
SLEEVE_USD: 3000
ROLE: GPT 5.6 Sol executor; only writer; challenger/finalizer/integration pending
PAPER_ONLY: true

## Strategy decision charter

ECONOMIC EDGE MECHANISM: Persistent index-option insurance demand can make observed VIX exceed subsequent SPY realized volatility; the frozen high same-close VIX/RV20 ratio in a positive SPY trend was proposed as a selector for bounded bullish carry.

CANDIDATE/FAMILY SCOPE: Frozen candidate `SPY_VRP_PCS_VIX_RV_21D_V1` in canonical family `SPY_VRP_VIX_RV_21D`: same-close VIX/RV20 >=1.25, close above fully warmed SMA200, non-overlapping 21-session outcomes, outcome-independent positive-trend low-ratio controls, and only conditionally a one-lot 21-DTE approximately 0.20-delta $1-wide PCS. No threshold, timing, DTE, width, symbol, matching tolerance, or management mutation.

FUNNEL: `F0_MECHANISM -> F0_MECHANISM`.

PREDECLARED FALSIFIER: Preserve the integrated frozen gates. Close the family if any assessment has fewer than 10 non-overlapping treated episodes, treated mean below 1 vol point, treated positive frequency below 60%, fewer than 8 outcome-independent matched controls, or matched treated-minus-control mean <=0; also close if pooled treated count <45, pooled matched count <24, either one-sided 95% circular-block-bootstrap lower bound <=0, any chronology/overlap/integrity counter is nonzero, or option pricing is reached after mechanism failure. The regenerated artifact also had to match a second current-code run on source hashes and every substantive payload field.

EXACT DECISION: `BLOCKER_REMOVED_AND_RETESTED`.
RETEST DECISION: `FAMILY_CLOSED`.
STRATEGY ADVANCEMENT: false.

## Why this loop superseded prior NEXT

The advisory `POST_VRP_SEARCH_DESIGN_REASSESSMENT` was superseded because Jarvis's independent integrity review found the prior claim-bearing 0612 artifact irreproducible from integrated code. A code-aligned same-fold, half-open persisted-row audit found control-treated outcome-window overlaps in 33 of 35 old matched rows and three assessment-boundary crossings (two treated, one control); the old JSON omitted both current integrity counters. Doctrine forbids a successor BUILD while a claim-invalidating evidence gate is open. Orientation also had `consecutive_no_strategy_advance=18`, `strategy_pivot_required=true`, and `strategy_burst_stop_required=true`.

## Closed outcome

The current integrated overlap-safe runner was exercised unchanged against the same source hashes and closed `SPY_VRP_VIX_RV_21D` at F0 for insufficient disjoint matched-control density:

- Source hashes: SPY `f15bfd1830d86085bb9159ffb4bd0ccbb1f6b7f92254b9852314b1a0b23d35e7`; VIX `4545e9eb167bb8cd40bd379d2fa80d8fc7e5aab629cfcb0db65f5f3d3361499b`.
- Treated episodes: 51 pooled; assessments 19 / 9 / 23. The middle assessment failed the frozen >=10 treated gate.
- Disjoint matched controls: 6 pooled; assessments 0 / 6 / 0, versus frozen >=8 per assessment and >=24 pooled.
- Raw treated VIX-minus-forward-RV remained positive: mean `4.092018447174995`, positive frequency `0.8823529411764706`, LB95 `1.2164416436145766`. This is broad raw VRP, not selector alpha.
- The six pooled pairs had mean `4.410136537446031` and LB95 `2.96908707214889`, but the density gate failed decisively; positive statistics on six pairs are underpowered and cannot establish incremental selector edge.
- Current integrity counters are complete and zero for assessment boundaries, treated/control overlap, control/control overlap, duplicates, thresholds, tolerances, warm-up, episode overlap, and forward-window chronology.
- Mechanism failure kept `pricing_calls=0`, option status `NOT_RUN_MECHANISM_GATE_FAILED`, `candidate_pass=false`, and `registration_eligible=false`.
- Structure: `put_credit_spread`; `capital_fit_usd=100`; one-lot `max_loss_usd=100`; `max_lots=1`. These are a structural $1-wide upper bound only, not a fill, PnL observation, capital seat, F1 result, or paper plan.
- Canonical executor artifact: `reports/trader-wakes/moa/2026-07-14T0859/spy-vrp-pcs-study.json`, SHA-256 `71822cdf55bdc1b63c91a4047e0dc631e77940fcabda1cf35a2c7f8168ae3bfb`.
- Machine-readable old-vs-current integrity and reproducibility receipt: `reports/trader-wakes/moa/2026-07-14T0859/artifact-integrity-audit.json`.

The family remains quarantined. The previous 53-treated/35-control, 2020-2021 paired mean, pooled paired LB95, and zero-integrity story is superseded and must not be used.

## Blocker repair and retest

Search information, separate from strategy advancement:

1. Regenerated the claim-bearing artifact from integrated overlap-safe code and verified a second run is substantively identical after excluding only `generated_at`.
2. Repaired `scripts/spy_vrp_pcs_study.py` so `dominant_failure_mechanism` is derived from actual frozen gate failures. It now names the 0/6/0 assessment pair counts, pooled 6<24 density failure, and middle-fold treated count 9 instead of falsely citing a negative pooled bootstrap.
3. Added a behavioral regression in `tests/test_spy_vrp_pcs_study.py` requiring the sparse-control failure label, exact assessment/pooled counts, underpowered wording, and absence of the stale pooled-bootstrap claim.
4. Exact-reran the dependent experiment after the repair. Decision remained `FAMILY_CLOSED`; no strategy was rescued.
5. Patched the profile-local `trader-self-evolution` skill with the reusable claim-artifact reconciliation rule: direct row-integrity audit, same-hash/current-code regeneration, substantive-payload equality, complete counters, and explicit supersession of stale living surfaces.

## Evidence validity audit

- Leakage/lookahead: VIX, RV20, and SMA200 are same-close mechanism-screen inputs; outcomes begin on later sessions. The option branch did not run. This is inspected development data, not untouched F2 evidence.
- Controls/population purity: current controls are positive-trend, ratio<1.25, outcome-independent matches; every control outcome window is assessment-bounded and disjoint from all treated and previously selected control windows. Sparse density is a falsifier, not permission to reuse overlapping rows.
- Costs/fills/contracts: no option pricing, cost, quote, fill, contract availability, or PnL claim was made. Structural risk fields are bounds only.
- Provenance: observed daily VIX plus adjusted SPY OHLC; no observed historical option surface. No proxy result earned L1.
- Ranking/leader: this was a frozen single-family reconciliation, not a population rank. Living leader remains none; historical `b195f5fe` is not a seat.
- Path/risk: no option path was reached. No drawdown or after-cost claim exists.
- Archive boundary: the three-date TSLL forward archive is unrelated plumbing and was not used to justify this decision or a global data stop.

## Verification

- Focused behavioral/boundary/negative-control suite: `.venv/bin/python -m unittest tests.test_spy_vrp_pcs_study -v` -> `Ran 14 tests in 2.262s`, `OK`.
- Compounding/completion regressions: `.venv/bin/python -m unittest tests.test_trader_build_compounding tests.test_trader_run_completion_gate -v` -> `Ran 36 tests in 5.787s`, `OK`.
- Refreshed income-coverage behavior: `.venv/bin/python -m unittest tests.test_trader_income_coverage -v` -> `Ran 1 test in 0.695s`, `OK`.
- Full suite: `.venv/bin/python -m unittest discover -s tests` -> `Ran 263 tests in 12.402s`, `OK`.
- Compile: `.venv/bin/python -m py_compile scripts/spy_vrp_pcs_study.py tests/test_spy_vrp_pcs_study.py` -> exit 0.
- Platform smoke: `just platform-smoke` -> exit 0, `platform smoke OK`; `agentic_live` remained blocked at Stage1 OAuth.
- Reproducibility: second 10,000-bootstrap run against the same sources -> `substantive_payload_equal True` after excluding only `generated_at`; current JSON includes both new integrity counters.
- Old-artifact negative control: persisted 0612 rows independently recompute 33/35 same-fold, half-open control-treated outcome-window overlaps and three assessment-boundary crossings; old JSON omitted both counters.

## Readiness and authority

BUILD/L0 remains unchanged. No living candidate or quality leader exists. B1-B7 did not advance; B6 remains thin. Registry counts remain 246 total (`paper=1`, `testing=14`, `candidate=230`, `rejected=1`) and no hypothesis status changed. No paper order, shadow/live promotion, broker login, funding, spend, arm, or main-account action occurred.

## Freedom audit

Trader remained free across symbols and structures; the loop narrowed only because an open claim-integrity gate and mandatory 18-wake burst stop outranked new search volume, not because SPY, PCS, NEXT, plumbing, or an allowlist was imposed.

## Search information vs strategy advancement

SEARCH INFORMATION: a stale claim-bearing artifact was replaced by reproducible overlap-safe evidence; failure labeling and its regression were repaired; the canonical family close is now based on insufficient disjoint-control density rather than invalid overlapping pairs.

STRATEGY ADVANCEMENT: none; `F0_MECHANISM -> F0_MECHANISM`; no F1/F2/F3/F4 movement.

## Next seed

`DIMINISHING_RETURNS`

This stops the current no-advance burst after mandatory evidence reconciliation. It is not an archive-based global freeze. A later wake may restart only after a materially new search-design/data reassessment establishes a route beyond another inspected F0 screen.

Executor phase only. Do not commit, push, merge, or claim RUN COMPLETE. Challenger/finalizer/deterministic integration remain pending.

POST-RESIDUE CONCURRENCY: the separate `2026-07-14T0930-rth` wake wrote a newer RTH `LATEST.md`, prepended INDEX, and prepended readiness after this executor residue was complete. It preserved the 0859 executor row and readiness correction and explicitly did not absorb the dirty MOA branch. This executor does not overwrite the newer RTH living pointers merely to reclaim latest position; `reports/trader-wakes/2026-07-14T0859-moa-exec.md` remains the canonical executor report.

MOA_EXEC_DONE

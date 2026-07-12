# Learning promotion — 2026-07-12T1323

## VERIFICATION — commands and exact results

- `.venv/bin/python scripts/pcs_momentum_walkforward_lab.py --out .cache/platform/pcs_momentum_walkforward_lab_2026-07-12T1323.json` → exit 0; `REJECT_BULLISH_MOMENTUM_PCS_WALKFORWARD`, `n_selected=8`, `n_holdout_pass=0`, `errors=[]`; post-run audit found 88/88 persisted selected/control/window summaries with `integrity=true`.
- `.venv/bin/python scripts/trader_income_coverage.py --write --stamp 2026-07-12T1323` → exit 0; regenerated dated and LATEST coverage at 20 structures / 245 hypotheses / living leader none.
- `.venv/bin/python -m unittest tests.test_pcs_momentum_walkforward_lab tests.test_pcs_expiry_grid` → 17 tests, OK.
- `.venv/bin/python -m unittest discover -s tests` → 92 tests, OK.
- `git diff --check` → exit 0, no whitespace errors.
- Finalizer repair reran the exact experiment after making the inclusive zero-return mirror boundary disjoint and making result status/unrounded hard metrics fail closed; selected DNA, the 0/8 decision, BAC train/holdout metrics, SOFI control metrics, and 88/88 integrity result were unchanged.

Accepted challenger findings: the bullish-momentum family rejection stands; BAC and all bearish-mirror controls remain unregistered and off the capital path; formal readiness and the empty living-leader state do not advance; proxy evidence remains L0 and cannot earn L1; the merged NEXT is pinned to the exact 7-DTE, `entry_ret_1d_max=-0.005`, RSI 35–50 mirror DNA (or train-only selection within each fold), with no SOFI reverse-engineering or grid expansion. The optional both-cost window scan is deferred because it cannot change this family rejection: BAC already fails untouched holdout fixed-cost PnL and both holdout DD gates. The current artifact and falsifier now explicitly label dense-negative windows as fixed-cost-only rather than implying both-cost window coverage. AAPL remains a documented example that dual-axis positive train PnL/SHIP does not override the absolute DD gate.

Rejected challenger actions were upheld: no SOFI/F/PLTR control promotion, no bullish-grid retune, no L1/paper seat, no provider-backed history before three distinct New York market dates, and no live/shadow/arm action. No challenger finding was rejected by the finalizer.

Integration is pending the deterministic wrapper gate; this file is a green handoff, not a RUN COMPLETE claim.

## DURABLE — files/skills/memory updated, or evidence-backed no-promotion reason

- Current project truth: `docs/INCOME_STRATEGY_COVERAGE.md`, `reports/readiness/LATEST.md`, `reports/readiness/income-coverage-2026-07-12T1323.md`, and `reports/readiness/income-coverage-LATEST.md` record the family rejection, L0 status, empty leader, and observed-data boundary.
- Reusable capability: `scripts/pcs_momentum_walkforward_lab.py` now enforces conjunctive train+holdout gating, fail-closed result status, unrounded hard gates, prior-bar signal purity, exact ledger/no-reentry integrity, disjoint zero-boundary mirrors, deterministic report regeneration, and explicit fixed-cost window semantics; `tests/test_pcs_momentum_walkforward_lab.py` protects the negative and boundary cases.
- Reusable lesson: the trader-profile `trader-self-evolution` skill now records that holdout success must never bypass a failed train gate and that inclusive mirror boundaries require a zero-boundary disjointness test.
- Profile memory was not changed: the result is dated project evidence and the reusable procedure belongs in repo truth plus the skill; it adds no stable Ken preference or routing fact.
- No superseded contradictory guidance was stacked; final wake/readiness/NEXT surfaces were rewritten to the finalizer state.

## LESSON — what future Trader now knows/can do

Future Trader can run a strict chronological direction-bias PCS falsification where selection reads train only, final success requires both train and untouched holdout gates, mirrored controls cannot overlap at an inclusive zero boundary, and fixed-cost-only window evidence is labeled precisely. Positive proxy SHIP on one cost axis—or a positive unselected mirror control—cannot become a capital seat when absolute after-cost and drawdown gates fail.

## NEXT

Run one predeclared rolling-origin mild bearish-pullback PCS walk-forward on BAC, F, SOFI, PLTR, TSLL, SMCI, AMD, and AAPL using the exact mirror DNA (7 DTE, `entry_ret_1d_max=-0.005`, RSI 35–50, lag 1, unchanged management/cost axes), with train-gate required before every next fold and rejection unless both cost axes plus fold/window DD ≤$75 clear throughout; do not grid-expand or use the current SOFI/F/PLTR controls as candidates. If a distinct New York RTH date occurs during that same run, append the TSLL all-expiration archive from 1/3 to 2/3 without starting provider-backed history before 3/3.

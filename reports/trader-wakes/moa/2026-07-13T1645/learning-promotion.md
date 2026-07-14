# Learning promotion — 2026-07-13T1645

## VERIFICATION

- Focused behavioral/boundary/negative-control suite: `.venv/bin/python -m unittest tests.test_evolve_pre_registration_stress -v` → 8/8 passed.
- Artifact regeneration: `.venv/bin/python scripts/evolve_pre_registration_stress.py --evolve-report reports/trader-wakes/moa/2026-07-13T1645/evolve-discovery.json --period 5y --out reports/trader-wakes/moa/2026-07-13T1645/evolve-pre-registration-stress.json` → 3 candidates, `complete_proxy_gate_ids=[]`, `registration_eligible_ids=[]`, decision `REJECT_ALL_DRY_RUN_SHIPS_BEFORE_REGISTRATION`.
- Capital-label check after regeneration: required `capital_fit_usd` now equals observed one-lot max loss (`$192.60`, `$195.78`, `$199.56`); `sleeve_usd=$3,000`, open-risk budget `$750`, and operating `max_lots=1` are separate.
- Coverage regeneration: `.venv/bin/python scripts/trader_income_coverage.py --write --stamp 2026-07-13T1645` → 21 structures / 245 hypotheses / 70 evolve artifacts / living leader none; dated and LATEST surfaces regenerated.
- Platform smoke: `just platform-smoke` → `platform smoke OK`; agentic-live remained blocked at the Stage1 OAuth gate.
- Full regression: `.venv/bin/python -m unittest discover -s tests` → 209/209 passed in 7.381s.
- Syntax: `.venv/bin/python -m py_compile scripts/evolve_pre_registration_stress.py tests/test_evolve_pre_registration_stress.py` → exit 0.
- Diff hygiene: `git diff --check` → exit 0; dated merge and `LATEST.md` are byte-identical.
- Structured handoff: `.venv/bin/python scripts/trader_build_compounding.py validate-handoff --repo . --stamp 2026-07-13T1645 --base-head f722b2a9fe28a514651d10d7fb112a23a926c008` → `ok=true`, outcome `CAPABILITY`, 3 useful deltas, 4 critic findings closed, role ready.
- Isolated temporary-index completion prepare: 20 intended staged paths; `scripts/trader_run_completion_gate.py prepare` → `ok=true`. Its sensitive-path and raw-secret checks passed. The temporary index was removed and the real Git index remained untouched.
- Complete base-diff audit: 20 intended paths / 8,700 insertions / 26 deletions. No private position files, credentials, tokens, raw secrets, `.cache`, prompt/session logs, or generated preflight errors are included. Prompt/session/preflight runtime residue is covered by existing project ignores; no ignore rule was changed.

## DURABLE

- Accepted F1 and repaired it in `scripts/evolve_pre_registration_stress.py`: `capital_fit_usd` is derived from observed one-lot required capital rather than copied from the `$3,000` sleeve. The payload now separates `sleeve_usd`, `open_risk_budget_usd`, and explicit fit booleans; operating `max_lots=1` remains unchanged. `tests/test_evolve_pre_registration_stress.py` asserts the repaired semantics.
- Accepted F2 as a reusable lesson, not a scoring retune: two PLTR rows prove that evolve `SHIP`/`positive_sim` can coexist with negative composite score. Raw SHIP is a discovery trigger only; pre-registration quality is governed by absolute stress and chronology.
- Accepted F3 and added cheap explicit boundaries for multi-symbol DNA and unsupported structures. Both fail closed before market-data loading or stress execution.
- Rejected F4 as a defect: `evolve-pre-registration-stress.json` records SNAP full-history `verdict=NULL`, positive `$31.09`, and failed baseline/B3 gates. “B3/base SHIP failed” is precise shorthand for the complete-gate outcome and does not claim negative baseline PnL.
- Dated/current project truth is preserved in the run evidence, final merge/LATEST/INDEX, readiness, and coverage reports. The reusable raw-SHIP/capital-label pitfall was promoted to the `trader-self-evolution` skill. Profile memory was not changed because this is a procedure/evidence lesson, not a stable user preference or routing fact.
- Integration is pending the deterministic wrapper gate. No commit, push, merge, branch switch, broker login, order, shadow/live promotion, or arm occurred in finalization.

## LESSON

Future Trader can reject registry pollution before mutation: dry evolve provenance must be explicit, candidate DNA must be structure-pure and single-symbol, every transient SHIP must survive non-vacuous baseline/B3/5%/fixed-cost plus max-loss/window-DD/dense-negative gates, and even a complete overlapping proxy pass remains registration-ineligible without chronological train selection and untouched-holdout confirmation. Capital required by one lot must be reported separately from the available sleeve.

## NEXT

Build one chronological pre-registration adapter that performs fixed-seed train-only free defined-risk multi-structure evolve selection and evaluates every selected DNA once on an untouched chronological holdout with the existing baseline/B3/5%/fixed-`$0.01`/max-loss≤`$300`/window-DD≤`$75`/dense-negative≤5 gates; require train AND holdout, register nothing on the first pass, keep Black-Scholes proxy/L0 labels, and do not reopen closed families or paper/shadow/arm/live.

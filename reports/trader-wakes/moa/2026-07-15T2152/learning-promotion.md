# Learning promotion — 2026-07-15T2152

## VERIFICATION

- Focused behavioral, boundary, negative-control, regression, and handoff-contract suite:
  - command: `.venv/bin/python -m unittest -v tests.test_option_quote_observations tests.test_trader_build_compounding tests.test_trader_build_progress tests.test_trader_income_coverage tests.test_trader_run_completion_gate`
  - exact result: `Ran 59 tests in 8.877s — OK`.
  - boundaries exercised include exact-contract as-of joins, synthetic/crossed/stale/missing quote rejection, weekday-RTH density versus archive labels, frozen control/capital epoch validation, pure-wait streak exclusion, same-bar and candidate-scoped anti-thrash routing, schema-v2 outcome rules, generated coverage language, and completion-gate fail-close behavior.
- Required full unittest suite:
  - command: `.venv/bin/python -m unittest discover -s tests`
  - exact result: `Ran 368 tests in 18.730s — OK`.
- Full pytest regression suite, including tests not collected by unittest:
  - command: `.venv/bin/python -m pytest -q`
  - exact result: `378 passed, 18 subtests passed in 21.25s`.
- Syntax and repository checks:
  - command: `.venv/bin/python -m compileall -q scripts trader_platform tests && git diff --check && .venv/bin/python -m json.tool configs/search_epoch.json >/dev/null`
  - exact result: exit `0`; `compileall=OK json=OK diff_check=OK`.
- RTH archive recomputation:
  - command: `.venv/bin/python scripts/option_quote_observations.py --input .cache/platform/option_quotes/TSLL_archive.csv --summary-out .cache/platform/option_quote_archive_density_2026-07-15T2152.json`
  - exact result: 1,990 total rows; 1,390 weekday-RTH; 600 non-RTH; 3 archive-date labels; 2 eligible weekday-RTH market dates; 13 RTH expirations; provider eligibility `false`; the corrected density object contains `dates_with_non_rth_quotes` and `fully_excluded_dates` and no `excluded_non_rth_dates` key.
- Derived income coverage regeneration:
  - command: `.venv/bin/python scripts/trader_income_coverage.py --write --stamp 2026-07-15T2152 && cmp -s reports/readiness/income-coverage-2026-07-15T2152.md reports/readiness/income-coverage-LATEST.md`
  - exact result: exit `0`; 21 catalog structures / 246 hypotheses / 70 evolve artifacts / no living leader; dated and LATEST SHA-256 both `9f6afe641685294441e4a0762dfc728494e5a147c51249da875e1789dae380c9`.
- Schema-v2 handoff validation:
  - command: `.venv/bin/python scripts/trader_build_compounding.py validate-handoff --repo . --stamp 2026-07-15T2152 --base-head 440e0ccc1b3a4a6703d549244e1552696d1f70b5`
  - exact result: exit `0`; `ok=true`; `role_ready=true`; `schema_version=2`; `outcome=EVIDENCE_WAIT`; `strategy_advanced=false`; `useful_delta_count=4`; `critic_findings_closed=3`.
- Disposable-index deterministic prepare:
  - command: initialize a temporary `GIT_INDEX_FILE` from `HEAD`, stage all 28 intended integration paths there, run `git diff --cached --check`, then `.venv/bin/python scripts/trader_run_completion_gate.py prepare --repo . --stamp 2026-07-15T2152 --base-head 440e0ccc1b3a4a6703d549244e1552696d1f70b5 --run-branch trader/run-2026-07-15T2152`.
  - exact result: exit `0`; `ok=true`; `mode=prepare`; branch `trader/run-2026-07-15T2152`; `staged_files=28`; the live Git index remained untouched.

Integration is pending the deterministic wrapper gate. This finalizer has not committed, pushed, merged, switched branches, edited `.gitignore`, or claimed `RUN COMPLETE`.

## DURABLE

Strategy charter/outcome:
- Mechanism: lag-safe non-bearish TSLA/TSLL regimes may support an observed TSLL call term-structure carry edge when front-expiry extrinsic decays faster per day than the farther-dated long call after executable two-leg costs.
- Exact candidate: `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1`; one observed listed-contract long 60–90 DTE 0.60–0.75 delta call and one higher-strike short 14–21 DTE 0.20–0.35 delta call; front/back extrinsic-per-day >=1.25; each leg half-spread <=`$0.10`; +25%/−25% package exits; five-session, short<=7 DTE, regime, event, dividend, and assignment exits; no roll, averaging down, same-session re-entry, or overlap.
- Capital: `capital_fit_usd=$300` is a research admission budget (observed debit + `$50` reserve <=`$300`), not a proved loss bound. One-lot structural `max_loss_usd=UNPROVEN` until assignment/gap/exercise/liquidation mechanics are evidenced; `max_lots=1`; no overlapping TSLA/TSLL bullish option risk.
- Outcome: `EVIDENCE_WAIT`; `F0_MECHANISM -> F0_MECHANISM`; strategy advancement false; evidence_wait_reaffirmation false because this is the epoch's initial strategy decision, not a later pure append.
- Current evidence: 1,990 observed rows but only 2 distinct weekday-RTH dates, 1 distinct eligible 14–21 DTE short-expiry cycle (`2026-07-31`), 0 complete non-overlapping package paths, and 0 frozen controls. No option-path PnL/outcome, mispricing, after-cost edge, F1/F2/L1, living leader, capital seat, registry, or paper authority exists.
- Frozen wake condition: at least 12 RTH dates / 3 distinct short cycles / 20 complete paths / 8 frozen one-to-one controls. Evaluate only the chronological development 60% under the predeclared falsifier and retain the final 40% unread for later F1→F2.

Accepted challenger findings and repairs:
1. R1 accepted: control geometry is now frozen before outcome evaluation—same snapshot and long leg, one-to-one, richness ratio `[0.80,1.10]`, outcome-independent candidate/control tie-breaks, deterministic match order, no reuse/substitution, and path exclusion when no control exists. The active epoch and schema-v2 validator/tests pin it.
2. R2 accepted: `$300` is only an admission budget. Every living capital surface now labels structural one-lot `max_loss_usd` unproven/null and names assignment/gap/exercise/liquidation evidence as a dependency.
3. R3 accepted: forecast type is `term_structure_extrinsic_carry` with a mild bullish directional overlay; Layered Edge doctrine now names this distinct forecast class rather than conflating it with realized-vs-implied volatility.
4. R4 accepted: archive density now separates archive labels, dates containing any non-RTH quotes, fully excluded dates, and eligible weekday-RTH market dates. The misleading `excluded_non_rth_dates` label is gone from current generated evidence.
5. R5 accepted: schema-v2 pure append-only wait handoffs set `evidence_wait_reaffirmation=true`; compounding orientation and readiness progress skip those rows when calculating no-advance pivot/burst-stop streaks. The initial 2152 wait still counts once.
6. R6 accepted: one merged NEXT now routes distinct-RTH append, off-hours independent L0 discovery, or exact-candidate evaluation after the frozen floor, so the observed candidate's wait does not freeze global BUILD freedom.

Soft challenger notes:
- Accepted observed-data dependence, honest initial F0 wait, five-session versus short<=7 DTE precedence, same-snapshot spot for model-derived delta, event/dividend hard gates, and diagonal assignment/exercise/liquidation risk as explicit forward dependencies.
- Corrected an additional finalizer audit finding: both RTH dates share one eligible 14–21 DTE short expiration (`2026-07-31`), so current evidence is one distinct short-expiry cycle, not two.
- No material challenger finding was rejected. No option outcome was opened, no current bearish stand-aside was converted into a strategy failure, and no proxy evidence was allowed to satisfy the observed claim.

Promotion routing:
- Dated/current project truth: `strategy-charter.md`, search-design reassessment, active `configs/search_epoch.json`, executor/challenger/finalizer reports, merged NEXT, readiness, coverage, INDEX/LATEST, this learning record, and schema-v2 compounding handoff.
- Reusable machinery/tests: RTH density in `trader_platform/research/option_quote_observations.py`; frozen search-epoch and pure-wait contracts in `scripts/trader_build_compounding.py` and `scripts/trader_build_progress.py`; focused tests in `tests/test_option_quote_observations.py`, `tests/test_trader_build_compounding.py`, and `tests/test_trader_build_progress.py`.
- Doctrine: `docs/TRADER_LAYERED_EDGE_DOCTRINE.md` now recognizes term-structure extrinsic carry; `docs/BUILD_LAB_ENVIRONMENT.md` records pure-wait anti-thrash semantics.
- Skill: no new patch needed. The loaded `trader-self-evolution` skill already contains the frozen-control requirement, admission-cap versus max-loss distinction, candidate-scoped observed-wait routing, and pure-append reaffirmation exclusion. Stacking duplicate guidance would create drift.
- Memory: no addition. Candidate metrics, archive counts, epoch state, and dated wait conditions belong in repository evidence; stable autonomy, capital, proxy-evidence, and anti-thrash preferences already exist in trader memory.

## LESSON

Future Trader can distinguish four things that previously blurred together: archive labels versus weekday-RTH evidence dates; a research admission budget versus proved structural max loss; realized-versus-implied volatility versus observed option term-structure carry; and an initial strategy evidence wait versus later pure data-append reaffirmations. Those distinctions are now machine-checked and boundary-tested.

Future Trader can also keep a sparse observed-data candidate frozen without freezing discovery. Control geometry and outcome gates stay immutable, same-date append churn is forbidden, pure append reaffirmations do not create false pivot pressure, and off-hours BUILD remains free to pursue a genuinely independent L0 mechanism. The observed candidate resumes only when its exact population floor is met.

## NEXT

`TSLL_OBSERVED_TERM_CARRY_DATA_OR_INDEPENDENT_L0`: on a distinct weekday-RTH date while the frozen floor is unmet, append one all-expiration TSLL snapshot and report only density/path/admission/control counters; off-hours while unmet, autonomously pursue a genuinely independent non-quarantined L0 mechanism without proxy-satisfying or mutating the parked diagonal; once at least 12 RTH dates, 3 distinct eligible short-expiry cycles, 20 complete observed paths, and 8 frozen controls exist, evaluate exact `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1` on the development 60% under the predeclared falsifier while keeping the final 40% unread. Pure append reaffirmations set `evidence_wait_reaffirmation=true` and do not increment pivot/burst-stop streaks. No same-date churn, registry/paper force, shadow, arm, broker, funding, or live action.

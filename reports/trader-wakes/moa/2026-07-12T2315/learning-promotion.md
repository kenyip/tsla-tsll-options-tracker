# Learning promotion — 2026-07-12T2315

## VERIFICATION

- `.venv/bin/python -m unittest tests.test_dividend_event_crosscheck tests.test_dividend_event_archive tests.test_corporate_action_risk tests.test_debit_vertical_sim tests.test_diagonal_oos_stress tests.test_defined_risk_fixed_cost -v` → `Ran 41 tests in 0.175s` / `OK`. This includes behavioral coverage, exact-set complete/missing/unexpected boundaries, source/schema/identity/duplicate failures, malformed amount and chronology fail-close, corporate-action precedence, provider coverage, and defined-risk regressions.
- `.venv/bin/python scripts/dividend_exdate_crosscheck.py --nasdaq-archive .cache/platform/dividend_events/AAPL_nasdaq.json --issuer-crosscheck .cache/platform/dividend_event_crosscheck_2026-07-12T2237.json --expected-target-events 40 --out .cache/platform/dividend_exdate_crosscheck_2026-07-12T2315.json` → `target_events=40`, `source_events_in_window=20`, `matched_events=20`, `missing=20`, `unexpected=0`, `provider_status=insufficient_bounded_coverage`, `qualified_fields=[]`, decision `CLOSE_EX_DATE_ROUTE_INSUFFICIENT_COVERAGE`.
- Exact-target negative control with `--expected-target-events 41` → exit `1` with `ValueError: bounded target changed: expected 41, found 40`; no output artifact was accepted.
- `.venv/bin/python -m trader_platform.smoke_test` → `platform smoke OK`; `agentic_live` remained blocked at the Stage1 Robinhood OAuth gate.
- `.venv/bin/python -m unittest discover -s tests` → `Ran 171 tests in 6.909s` / `OK`.
- `.venv/bin/python -m py_compile trader_platform/research/dividend_event_crosscheck.py scripts/dividend_exdate_crosscheck.py tests/test_dividend_event_crosscheck.py scripts/trader_income_coverage.py` plus `git diff --check 3472686188858dc75364b7b1e81b945b62936d04` → exit `0`, no output.
- `.venv/bin/python scripts/trader_build_compounding.py validate-handoff --repo . --stamp 2026-07-12T2315 --base-head 3472686188858dc75364b7b1e81b945b62936d04` → `ok=true`, `role_ready=true`, outcome `FALSIFIED`, 2 useful deltas, 4 critic findings closed.
- Alternate-index deterministic prepare-equivalent: `git read-tree HEAD; git add -A; .venv/bin/python scripts/trader_run_completion_gate.py prepare --repo . --stamp 2026-07-12T2315 --base-head 3472686188858dc75364b7b1e81b945b62936d04 --run-branch trader/run-2026-07-12T2315` with an isolated temporary `GIT_INDEX_FILE` → `ok=true`, 23 staged files. The real index was not changed.
- Complete base-diff plus untracked audit covered all 23 intended paths (10 tracked modifications, 13 additions): no sensitive path, symlink, binary, raw secret marker/assignment, missing path, or generated monitor/progress debris remained. `reports/trader-wakes/LATEST.md` is byte-equal to the merge report; canonical 2315 income coverage was regenerated at 20 catalog structures / 245 hypotheses / 67 artifacts / no living leader.
- Integration is pending the deterministic wrapper gate. This finalizer did not commit, push, merge, switch branches, or claim RUN COMPLETE.

Critique dispositions:

- Accepted and repaired the missing unexpected-date negative control. `test_unexpected_independent_ex_date_is_a_conflict` supplies every target plus an extra in-window date and proves `provider_status=ex_date_conflict`, the exact unexpected date, empty `qualified_fields`, and explicit `ex_date` non-qualification.
- Accepted and repaired the StockAnalysis row-boundary coverage. `test_stockanalysis_parser_rejects_bad_amount_and_chronology` proves non-positive amount and `ex_date > record_date` rows fail closed; existing controls retain source, identity, header, row-shape, and duplicate boundaries.
- Rejected a machine JSON for the six-page inventory as a required repair. The decision-relevant evidence is the reproducible StockAnalysis/S&P exact-set artifact, while the other direct probes are explicitly bounded narrative rejects—not evidence for a universal source-exhaustion claim. `docs/DIVIDEND_EVENT_DATA_BOUNDARY.md` and the executor closeout state endpoint-specific outcomes and prohibit paid, credentialed, anti-bot, or universal inferences. A synthetic after-the-fact JSON would add format, not stronger evidence.
- Rejected double-diagonal anti-fragility as an outstanding current-run defect because it is the next loop, not implemented evidence. The merged NEXT predeclares catalog/sim/smoke, exact four-leg percentage and fixed-$0.01 costs, no-same-bar reentry, one-lot max loss ≤$300, chronological multi-symbol evaluation, both-cost positivity, window DD≤$75, dense-negative≤5, L0-only status, and no first-pass registration.

## DURABLE

- Project truth and bounded stop rule: `docs/DIVIDEND_EVENT_DATA_BOUNDARY.md`, `docs/BUILD_LAB_ENVIRONMENT.md`, and `docs/INCOME_STRATEGY_COVERAGE.md` state that 20/20 intersection agreement does not qualify the predeclared 40-event `ex_date` claim; the equivalent no-auth aggregator route is closed until a genuinely new source class covers the missing dates.
- Reusable machinery: `trader_platform/research/dividend_event_crosscheck.py` provides a source-identified explicit-table parser and exact-set field qualification; `scripts/dividend_exdate_crosscheck.py` enforces accepted issuer-window input, a 40-target invariant, atomic evidence output, and claim-scoped decisions.
- Reusable tests: `tests/test_dividend_event_crosscheck.py` now covers complete, missing-target, and unexpected-in-window exact sets plus identity/source/header/duplicate/non-positive-amount/chronology boundaries.
- Derived truth: `reports/readiness/income-coverage-2026-07-12T2315.md`, `reports/readiness/income-coverage-LATEST.md`, `reports/readiness/LATEST.md`, `reports/trader-wakes/LATEST.md`, and `reports/trader-wakes/INDEX.md` were regenerated and agree on BUILD/L0, no living leader, 20/245/67 coverage, route closure, finalizer verification, and the one merged NEXT.
- Skill: profile skill `trader-self-evolution` now records the reusable exact-set testing rule: complete, missing-target, and unexpected-in-window controls, with malformed chronology and non-positive/nonfinite amount rejection.
- Memory: no update. This is reusable procedure and project evidence, not a stable user preference or routing fact.
- Integration remains pending the deterministic wrapper gate.

## LESSON

Future Trader can now ingest an explicitly labeled, named-source ex-date table and qualify a field only when the independent source exactly equals the entire predeclared target set. Perfect agreement on all available rows is corroborative context, not bounded completeness. Exact-set provenance gates need separate complete, missing-target, and unexpected-in-window controls, while parser boundaries must reject malformed economic values and chronology. The bounded AAPL no-auth aggregator route is therefore closed honestly at partial L0 without restricting unrelated symbols, strategies, historical-underlying research, or simulator-capability work.

## NEXT

Build one minimal paper-only `double_diagonal_spread` defined-debit BS/daily-bar scaffold: catalog entry, simulator, smoke tests, exact four-leg percentage and fixed-$0.01-per-leg costs, no-same-bar reentry, and one-lot `max_loss_usd` ≤ $300. Run one predeclared multi-symbol chronological dual-cost falsification and reject the class unless both cost axes are non-vacuously positive with window max DD ≤ $75 and dense-negative windows ≤ 5. Keep all results L0; do not register proxy SHIP on the first pass, reopen the closed no-auth AAPL ex-date inventory or other closed daily-bar proxy families, or paper/shadow/arm/live.

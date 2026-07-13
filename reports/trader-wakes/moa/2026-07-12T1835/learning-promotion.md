# Learning promotion — 2026-07-12T1835

## VERIFICATION

- `.venv/bin/python -m unittest tests.test_dividend_event_archive tests.test_corporate_action_risk tests.test_debit_vertical_sim tests.test_diagonal_oos_stress tests.test_defined_risk_fixed_cost -v` → `Ran 25 tests in 0.174s` / `OK`.
- `.venv/bin/python -m trader_platform.smoke_test` → `platform smoke OK`; `agentic_live` remained blocked at the Stage1 OAuth gate.
- `.venv/bin/python -m unittest discover -s tests` → `Ran 155 tests in 6.758s` / `OK`.
- `.venv/bin/python scripts/dividend_event_observations.py --snapshot AAPL --out .cache/platform/dividend_events/AAPL_nasdaq.json --summary-out .cache/platform/dividend_event_archive_lab_2026-07-12T1835.json` → 82 source rows / 53 retained / `coverage_start=2013-01-23` / provider eligible.
- Required-mode AAPL smoke was rerun after the coverage repair → diagonal `ok`, 0 trades; bull-call debit `ok`, 21 trades; both `corporate_action_mode=required`, zero assignment exits. This remains wiring evidence only.
- `.venv/bin/python scripts/trader_income_coverage.py --write --stamp 2026-07-12T1835` → 20 catalog structures / 245 hypotheses / 67 evolve artifacts / no quality leader; dated and LATEST coverage regenerated.
- `.venv/bin/python scripts/trader_build_compounding.py validate-handoff --repo . --stamp 2026-07-12T1835 --base-head 2702fa891f288d39325262a95fa825e5584bc7ff` → `ok=true`, `role_ready=true`, two useful deltas, two new novelty keys, and six critic findings closed.

Critique dispositions:

- Accepted and repaired the first-event orphan: archive construction and loading now derive `coverage_start` from the earliest retained `known_at`, the provider serves the first announced pre-ex interval, and archive reload rejects event announcements after `observed_at`. The new boundary/tamper controls are in `tests/test_dividend_event_archive.py`.
- Accepted the split-unadjusted amount warning as a claim boundary, not a simulator calibration result. `docs/DIVIDEND_EVENT_DATA_BOUNDARY.md` now explicitly says long-history assignment counts are uncalibrated until amount/spot scale and security class are qualified; no count, edge, or L1 claim was made.
- Rejected MU/AAL inventory as provider eligibility: the prose records source inventory only, no normalized MU/AAL archive is cited, and the ONE NEXT allows MU only after capture. AAPL is the sole archived supported example this wake.
- Accepted preferred/security-class contamination as a blocking provenance dependency and rejected any broad “all Nasdaq dividends safe” interpretation. The provider remains L0/single-source and fail-closed outside exact archived symbol/date coverage.
- Closed the stale readiness finding by replacing the challenger-pending top surface with this finalizer outcome, repaired verification, unchanged BUILD/L0 judgment, and exactly one current NEXT.
- Promoted the optional Nasdaq source pitfall to the `trader-self-evolution` skill: contiguous declaration-dated cash/USD rows only, first `N/A` truncation, empty/unsupported means `None`, earliest-`known_at` coverage, and no calibrated amount/class claim without independent qualification.

## DURABLE

- Project truth: `docs/DIVIDEND_EVENT_DATA_BOUNDARY.md`, `docs/BUILD_LAB_ENVIRONMENT.md`, `docs/INCOME_STRATEGY_COVERAGE.md`, regenerated income coverage, readiness, and wake surfaces define the supported-listing L0 boundary.
- Reusable machinery: `trader_platform/research/dividend_event_archive.py` and `scripts/dividend_event_observations.py` provide strict normalization, atomic archive IO, capture/validation, as-of coverage, and fail-closed source handling.
- Reusable tests: `tests/test_dividend_event_archive.py` covers declaration mapping, first pre-ex event service, future-announcement non-leakage, unsupported/ambiguous failure, malformed/future timing, symbol/date coverage, atomic round-trip, and count/boundary tamper rejection.
- Skill: profile skill `trader-self-evolution` now includes the source-specific Nasdaq archive pitfall and claim boundary.
- Memory: no update. This is procedural/data-source knowledge, not a stable user preference or routing fact.
- Integration is pending the deterministic wrapper gate; this finalizer did not commit, push, merge, switch branches, or claim RUN COMPLETE.

## LESSON

Future Trader can archive real Nasdaq declaration dates as announcement-time `known_at`, serve the first retained event during its announced pre-ex window, distinguish missing coverage from covered events, and fail closed on unsupported, ambiguous, malformed, tampered, or post-observation timing. It also knows that this source is only L0 corporate-action guard input: split-unadjusted amounts, possible security-class contamination, single-source completeness, Black-Scholes option marks, and missing observed option surfaces prevent calibrated assignment, edge, capital-seat, or readiness claims.

## NEXT

Cross-check archived Nasdaq cash-dividend events for AAPL (and MU only if a normalized archive is captured first) against one independent issuer/filing announcement source. Add a per-symbol provenance qualification only if event completeness and security-class identity can be proved. Otherwise keep the Nasdaq provider L0/single-source, do not invent multi-source confidence, and redirect the next zero-input wake to another open historical-underlying or simulator-capability route.

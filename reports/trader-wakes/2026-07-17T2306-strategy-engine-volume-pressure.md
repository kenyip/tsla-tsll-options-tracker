# Strategy Engine loop — completed-close volume pressure F0

Bottom line: One predeclared broad-index completed-close volume-pressure route had adequate pre-outcome density but failed all five frozen train gates. It is closed, not a survivor; Trader BUILD remains paused, continuous densify remains disabled, and all execution authority remains false.

Pre-mutation base: `c3966a2ff3dc385e7af43629afb4ae3e63280bc0` on clean synchronized `main`; Strategy Engine `16cf86d0b22b2b9e1502bb1cb512cbecc6235666` on clean synchronized `main`. No BUILD lock or active BUILD process was present. Foreground Jarvis acted as the bounded worker because this cron runtime exposes no delegate/Kanban dispatch primitive.

## PRE-EDIT MAP

- Target files: `scripts/trader_strategy_engine_route_batch.py`, `tests/test_strategy_engine_route_batch.py`, `tests/test_pmcc_desk.py`, and this tracked wake report.
- Callers/dependents: route-batch CLI → Strategy Engine handoff runner → fail-closed Trader gate. The shared cached-OHLCV loader feeds all source-coded routes.
- Tests: focused route-batch/handoff/gate tests, Strategy Engine full suite, Trader full unittest/pytest suites, the PMCC integration regression exposed by the full suite, and real route → handoff → gate smoke.
- Local pattern: pandas bridge, immutable `RouteSpec`, one source-coded route per exact mechanism, explicit same-date controls, chronological train/identity-only holdout split, and authority false.
- Sensitive boundary: cached market OHLCV and generated manifests/panels/handoff reports remain ignored local artifacts; no position, account, broker, credential, or secret data entered git.

## CHANGES

- Extended the existing cached-OHLCV bridge to retain validated numeric volume and derive `relative_volume_20` against the lagged 20-session median, excluding the signal session from its baseline.
- Added exactly one route: `cached_broad_index_volume_pressure_call_debit_5d_v1` / `CACHED_BROAD_INDEX_VOLUME_PRESSURE_CONTINUATION`.
- Frozen mechanism: SPY/QQQ/IWM positive intraday return, upper-quartile close location, and raw volume at least 1.50× the lagged 20-session median; five-session terminal underlying return; 15 bps event cost; same-date broad-index peer control; future one-lot defined-risk debit-call-spread expression only.
- Added route-shape and point-in-time negative-control coverage: changing all volume strictly after a signal cannot remove that signal.
- Repaired an unrelated calendar-expiry full-suite test assumption found during verification: `patience_expires.date=None` is the documented valid no-deadline state after all known dates pass.
- Deliberately not built: a volume optimizer, threshold grid, second route variant, generic factor framework, new dependency, holdout evaluator, option pricer, BUILD launcher, or paper/live surface.

## VERIFICATION

- Source-semantic preflight before outcomes: SPY/QQQ/IWM each had 1,255 common daily rows from 2021-07-12 through 2026-07-10; required OHLCV columns present; zero missing/nonpositive/noninteger volumes; zero OHLC-bound violations; no >25% close discontinuity. The cache writer uses yfinance `auto_adjust=False`, so the claim is explicitly raw-volume/unadjusted-price F0 rather than total-return evidence.
- Predeclared trigger density before forward-return construction: 82 events across all six represented calendar years (SPY 26, QQQ 20, IWM 36), enough to proceed without changing thresholds.
- TDD red phase: the focused route-batch suite failed with the route absent (`10 != 11` and missing route key), then passed after the minimum implementation.
- Focused Trader route/handoff/gate suite: `.venv/bin/python -m unittest tests.test_strategy_engine_route_batch tests.test_strategy_engine_handoff_runner tests.test_strategy_engine_handoff_gate` → `Ran 20 tests`, `OK`.
- Full Strategy Engine suite: `PYTHONPATH=src python3 -m unittest discover -s tests -v` → `Ran 25 tests`, `OK`.
- Full Trader unittest suite: first run exposed the expired no-deadline PMCC assertion; focused repair test passed, then `.venv/bin/python -m unittest discover -s tests` → `Ran 453 tests`, `OK`.
- Full Trader pytest suite: `.venv/bin/python -m pytest -q` → `463 passed, 18 subtests passed`.
- Diff hygiene: `git diff --check` passed.
- Real cached-data smoke generated 11 routes / 22,530 panel rows. Handoff returned `NO_QUALIFIED_STRATEGY` with `gate_status=validated_no_qualified_strategy`; direct gate emitted expected `NO_STRATEGY_STATUS` and exit `2`. No BUILD launched.
- New route density: 57 chronological train events/controls; 25 sealed holdout identities.
- Frozen train-only metrics: event mean after cost `-0.0026711807245614044`; paired excess mean `-0.0013158485456140354`; lower bound `-0.00534506143700909`; hit rate `0.42105263157894735`; worst-decile tail `-0.06631061166666667`. All five gates failed.
- Holdout remained identity/hash/count only (`8a512ca1201127e393b9dc6f55ea4539832c36f3614f70f0902625abe501383e`); no holdout outcome key was exposed. Authority remained false for L1, paper, shadow, broker, funding, arm, and live.

## DURABLE

- Trader now preserves raw volume in the existing route-batch bridge and supports a lagged relative-volume feature without a new abstraction or dependency.
- The new route labels raw-volume/unadjusted-price source semantics rather than implying adjusted total-return evidence.
- The failed exact volume-pressure route and its one-variant budget are regression-covered and closed to threshold, horizon, universe, sign, and cost retuning.
- The PMCC live-YAML integration test now honors the production no-deadline contract instead of becoming calendar-expiry red.
- `NO_QUALIFIED_STRATEGY` remains fail-closed: densify stays disabled and no BUILD or execution authority is granted.

## LESSON

Outcome: `FAMILY_CLOSED` / `NO_QUALIFIED_STRATEGY`; strategy advancement is false. The exact completed-close high-relative-volume broad-index continuation claim lost absolutely and versus same-date peer controls, with weak hit rate and tail. This is a decisive mechanism falsification, not a request for more volume or nearby thresholds.

The point-in-time volume capability is reusable, but tooling is not strategy progress. This is the eighth consecutive no-qualified loop result; another immediate route guess would violate the pivot/anti-thrash rule. The next bounded slice is a search-design/data reassessment that must select one materially distinct executable evidence class or stop honestly.

Unresolved risk: all evidence remains cached-underlying F0. The raw/unadjusted cache excludes distributions, the fixed present-day ETF universe is non-generalizing, and option prices, IV, listed expiries, fills, management paths, execution friction, and paper behavior remain unvalidated. No promotion claim is supported.

## NEXT

`STRATEGY_ENGINE_F0_SEARCH_DESIGN_REASSESSMENT_V1`: inventory the 11 current route decisions plus the recent pre-outcome source rejections, cluster them by economic mechanism/evidence class and dominant gate failure, and select exactly one materially distinct, source-executable F0 mechanism with a predeclared charter (source semantics, chronology, control, density floor, unchanged cost/risk gates, falsifier, holdout seal, and one defined-risk future expression). Reject any candidate that is a threshold/horizon/universe/sign mutation of a closed family. If no materially distinct executable source survives the reassessment, emit `DIMINISHING_RETURNS` with the exact missing data class instead of adding another route. No holdout outcomes, BUILD launch, densify re-arm, or authority change.

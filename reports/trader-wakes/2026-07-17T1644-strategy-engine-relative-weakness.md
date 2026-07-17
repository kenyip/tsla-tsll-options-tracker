# Strategy Engine loop — cross-sectional relative weakness F0

Bottom line: One predeclared single-name relative-weakness continuation route against QQQ failed all five frozen train gates. It is not a survivor; Trader BUILD remains paused, continuous densify remains disabled, and all execution authority remains false.

Pre-mutation base: `35c71f56d9100d14dded2909ef2e160dd40f72b9` on clean synchronized `main`; Strategy Engine `16cf86d0b22b2b9e1502bb1cb512cbecc6235666` on clean synchronized `main`. No BUILD lock or active BUILD process was present. Foreground Jarvis acted as the bounded worker because this cron runtime exposed no delegate/Kanban dispatch primitive.

## PRE-EDIT MAP

- Target files: `scripts/trader_strategy_engine_route_batch.py`, `tests/test_strategy_engine_route_batch.py`, and this tracked wake report.
- Callers/dependents: route-batch CLI → Strategy Engine handoff runner → fail-closed Trader gate. Strategy Engine already validates `direction=short` and applies the short sign during train evaluation.
- Tests: focused route-batch/handoff/gate tests, full Strategy Engine suite, full Trader unittest suite, full Trader pytest suite, and real cached-data route → handoff → gate smoke.
- Local pattern: stdlib/pandas bridge, immutable `RouteSpec`, one source-coded variant per exact route, explicit same-date controls, chronological train/identity-only holdout split, and authority false.
- Sensitive boundary: cached market OHLCV and generated research reports remain ignored local artifacts; no position, account, broker, credential, or secret data entered git.

## CHANGES

- Added minimum optional benchmark-relative feature support: same-date 5- and 20-session stock return minus benchmark return, plus benchmark SMA100 regime state. Inputs use only closes known by the signal close.
- Added exactly one route: `cached_single_name_relative_weakness_put_debit_5d_v1` / `CACHED_SINGLE_NAME_RELATIVE_WEAKNESS_CONTINUATION`.
- Frozen mechanism: AAPL/MSFT/META/GOOGL/AMZN/NVDA/AMD/TSLA below SMA50 while QQQ is above SMA100, with 20-session underperformance below -8%, 5-session underperformance below -3%, and negative absolute 5-session return; five-session terminal underlying return; 20 bps event cost; same-date QQQ control; future defined-risk debit-put-spread expression only.
- Added focused coverage for one-variant route shape, point-in-time benchmark feature behavior, and explicit QQQ control pairing.
- Deliberately not built: a generic factor framework, parameter search, new dependencies, holdout evaluation, execution integration, path-managed short fills, or paper/live surfaces.

## VERIFICATION

- Focused Trader route/handoff/gate suite: `.venv/bin/python -m unittest tests.test_strategy_engine_route_batch tests.test_strategy_engine_handoff_gate tests.test_strategy_engine_handoff_runner` → `Ran 19 tests`, `OK`.
- Full Strategy Engine suite: `PYTHONPATH=src python3 -m unittest discover -s tests` → `Ran 25 tests`, `OK`.
- Full Trader unittest suite: `.venv/bin/python -m unittest discover -s tests` → `Ran 452 tests`, `OK`.
- Full Trader pytest suite: `.venv/bin/python -m pytest -q` → `462 passed, 18 subtests passed`.
- Diff hygiene: `git diff --check` passed.
- Real cached-data smoke generated 10 routes / 22,366 panel rows. Handoff returned `NO_QUALIFIED_STRATEGY` with `gate_status=validated_no_qualified_strategy`; direct gate emitted expected `NO_STRATEGY_STATUS` and exit `2`. No BUILD launched.
- New route preflight: 184 chronological train events and controls; 80 sealed holdout identities.
- Frozen train-only metrics: event mean after cost `-0.014669918733152177`; paired excess mean `-0.01085191071304348`; lower bound `-0.019224082570659988`; hit rate `0.41304347826086957`; worst-decile tail `-0.14049924081578946`. All five gates failed.
- Holdout remained identity/hash/count only (`415ae84a034ad26e6c13c5cbd7714822559623e1a777fd06a546127fe8f2c80b`). Authority remained false for L1, paper, shadow, broker, funding, arm, and live.

## DURABLE

- Trader can now source-code bounded benchmark-relative route predicates without adding a factor framework or dependency.
- Exact benchmark selection also controls same-date panel pairing, preventing the route claim from silently falling back to a different benchmark.
- The failed relative-weakness continuation route and its one-variant budget are regression-covered and closed to adjacent retuning.
- `NO_QUALIFIED_STRATEGY` remains fail-closed: densify stays disabled and no BUILD or execution authority is granted.

## LESSON

Outcome: `NO_QUALIFIED_STRATEGY`. The exact QQQ-regime single-name relative-weakness continuation route is closed; do not retune its 5/20-session thresholds, universe, horizon, cost, or gates, and do not invert it into a relative-strength or reversal claim from these observed outcomes.

The route had sufficient train density but lost absolutely and versus QQQ, with weak hit rate and tail. This is a decisive mechanism falsification rather than a data-volume blocker. The reusable benchmark feature/control plumbing is the useful delta.

Unresolved risk: evidence remains cached-underlying F0 only. Fixed-universe survivorship, event-date clustering, option pricing/liquidity/IV, listed payoff paths, execution friction, and paper behavior are not validated. No promotion claim is supported.

## NEXT

`YIELD_CURVE_STEEPENING_REGIONAL_BANK_FORWARD_UPDRIFT_PREFLIGHT`: preflight whether existing point-in-time cached Treasury-duration proxies can define a completed steepening spread and provide adequate KRE plus same-regime control coverage before reading outcomes; only if semantics and density pass, source-code one fixed bullish KRE route with frozen chronology/cost/gates and a future defined-risk debit-call expression. Otherwise reject pre-outcome and select a different evidence class. Do not reuse, invert, or retune the closed relative-weakness route.

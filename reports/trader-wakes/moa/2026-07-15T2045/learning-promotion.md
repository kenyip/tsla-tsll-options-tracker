# Learning promotion — 2026-07-15T2045

## VERIFICATION

- Focused behavioral, boundary, negative-control, and claim-label suite:
  - command: `.venv/bin/python -m pytest -q tests/test_spy_index_theta_carry_lab.py`
  - exact result: `10 passed in 1.88s`.
  - coverage includes frozen candidate/control DNA, complete exit stack, dual-cost absolute gate, missing-axis fail-close, repaired anchored contrast, zero-bearish-support negative control, prior-regime chronology, fixed cadence, exact ledger/cost direction, no overlap/re-entry, lagged VIX, sealed holdout, ES90 `-$125`, and machine-readable entry-window claim boundaries.
- Finalizer-adjacent contract suite:
  - command: `.venv/bin/python -m unittest tests.test_trader_build_compounding tests.test_trader_completion_contract tests.test_trader_run_completion_gate -v`
  - exact result: `Ran 50 tests in 6.949s — OK`.
- Required full unittest suite:
  - command: `.venv/bin/python -m unittest discover -s tests`
  - exact result: `Ran 363 tests in 18.150s — OK`.
- Full pytest regression suite, including pytest-style strategy tests:
  - command: `.venv/bin/python -m pytest -q`
  - exact result: `373 passed, 18 subtests passed in 20.75s`.
- Compilation and CLI smoke:
  - command: `.venv/bin/python -m py_compile scripts/spy_index_theta_carry_lab.py tests/test_spy_index_theta_carry_lab.py && .venv/bin/python scripts/spy_index_theta_carry_lab.py --help >/dev/null`
  - exact result: exit `0`, no output.
- Current-code claim replay:
  - command: run `scripts/spy_index_theta_carry_lab.py` to a temporary JSON and compare strict-JSON payloads after removing only `generated_at`.
  - exact result: `substantive_equal=true`; `FAMILY_CLOSED`; failed checks exactly `anchored_regime_contrast_non_vacuous,non_bearish_worst_axis_average_gt_bearish`; candidate entry window `2016-07-19..2018-01-18`; holdout outcomes evaluated `false`; normalized SHA-256 `794e87ab930b1a4b9c2f3c16f246b67b142822dc9d1660d1fe4ddab075651f20`; raw tracked SHA-256 `46feeeceffc1d0e1ccb21bbf8900b322308b3cba1f24d99efd7296970c7a99d3`.
- Derived coverage regeneration:
  - command: `.venv/bin/python scripts/trader_income_coverage.py --write --stamp 2026-07-15T2045 && cmp -s reports/readiness/income-coverage-2026-07-15T2045.md reports/readiness/income-coverage-LATEST.md`
  - exact result: exit `0`; `21` structures / `246` hypotheses / `70` evolve artifacts / no living leader; dated and LATEST SHA-256 both `f751533e9c25c508d5a54161800f9e9a23c6bcc27258906e86fa78a55efdc2b5`.

- Schema-v2 handoff validation:
  - command: `.venv/bin/python scripts/trader_build_compounding.py validate-handoff --repo . --stamp 2026-07-15T2045 --base-head 21fdddd162d3fe6b92e7c4a3c1516ab801603b8d`.
  - exact result: exit `0`; `ok=true`; `role_ready=true`; `schema_version=2`; `outcome=BLOCKER_REMOVED_AND_RETESTED`; `strategy_advanced=false`; `useful_delta_count=4`; `critic_findings_closed=5`.
- Disposable-index deterministic prepare:
  - command: stage the 20 intended integration paths in a temporary `GIT_INDEX_FILE`, run `git diff --cached --check`, then `.venv/bin/python scripts/trader_run_completion_gate.py prepare --repo . --stamp 2026-07-15T2045 --base-head 21fdddd162d3fe6b92e7c4a3c1516ab801603b8d --run-branch trader/run-2026-07-15T2045`.
  - exact result: exit `0`; `ok=true`; `mode=prepare`; `branch=trader/run-2026-07-15T2045`; `staged_files=20`; the live Git index remained untouched.

Integration is pending the deterministic wrapper gate. This finalizer has not committed, pushed, merged, switched branches, or claimed `RUN COMPLETE`.

## DURABLE

Strategy charter and outcome:
- Economic mechanism: broad-index downside-insurance demand may create equity-risk-premium and theta carry that a lag-safe non-bearish SPY trend/VIX state can harvest while bearish states stand aside.
- Candidate/family: exact `SPY_INDEX_THETA_CARRY_PCS_21D_V1` / `SPY_INDEX_THETA_CARRY_REGIME_GATED_21D`; one-lot 21-DTE Black-Scholes/listed-Friday proxy PCS, 0.20-delta short put, `$2` wing, both adverse entry credits at least `$0.30`, expiration precedence, 50% profit, 70% structural-loss exit, short-put delta 0.45, ten-session stop, no roll or same-bar re-entry.
- Capital: `capital_fit_usd=$200` structural planning bound; one-lot width-bound `max_loss_usd=$200` before credit/friction; observed modeled loss at most `$169.998609`; `max_lots=1`; broad-equity downside risk would overlap other bullish equity-premium seats.
- Outcome: `BLOCKER_REMOVED_AND_RETESTED`, dependent `FAMILY_CLOSED`, `F0_MECHANISM -> F0_MECHANISM`; strategy advancement false.
- Evidence: candidate n=23/axis; fixed `$0.01`/leg `+$333.126196`, PF `4.102852`, DD `$59.040356`, ES90 `-$29.882593`; 5% adverse slip `+$196.422076`, PF `2.223180`, DD `$84.659372`, ES90 `-$53.527693`. Those entries are confined to 2016-07-19..2018-01-18 (5/17/1 by year) inside train through 2022-07-11, so the absolute pass is entry-window diagnostic evidence, not broad-train compatibility.
- Mechanism falsification: 137 fixed-cadence anchors produced only five tradeable blueprints, all non-bearish and zero bearish versus eight required per regime/cost axis. The old path diagnostic also failed to favor the candidate. Positive absolute proxy PnL cannot identify the regime gate.
- Holdout/authority: 1,004 feature rows from 2022-07-12..2026-07-13 remain sealed with option outcomes unread. No F1/F2/L1, living leader, capital seat, registry, paper intent, shadow, arm, broker, funding, or live authority.

Accepted challenger findings and repairs:
- Accepted `PASS WITH NITS`, exact family close, quarantine, no-advance streak three, burst stop, and reassessment NEXT.
- Corrected the discovery ES90 ceiling to `-$125`, restored the complete exit/management stack, and replaced the noncanonical epoch id with `2026-07-15-tail-hazard-discovery`.
- Promoted early-entry clustering into current machinery, strict JSON, tests, claim prose, readiness, and the reusable Trader skill. Current artifacts persist first/last entry, year counts, train bounds, cost-axis identity, and an explicit entry-window-only claim boundary.
- Fully rewrote readiness for the finalizer handoff rather than retaining a challenger-partial NEXT patch.
- Preserved quarantines for recent-downshock, downside-semivariance and nearby rank retunes, exact SPY theta carry and nearby same-panel retunes, low-HV mean-return, post-earnings, post-shock, breakout bull-call, TOM, OPEX, and monthly-ranking families. Preserved semivariance holdout `72a6d184…` and the SPY sealed holdout.

Rejected or narrowed claims:
- Rejected absolute dual-cost proxy positivity as mechanism validation, F1, L1, an almost-advance, capital seat, registry eligibility, or paper authority.
- Rejected broad-train compatibility: the 23 qualifying entries stop in early 2018 although train continues through July 2022.
- Rejected nearby SPY DTE/delta/width/credit/hold/regime retunes on the same Black-Scholes train panel.
- Rejected a fourth strategy experiment before mandatory search-design/data reassessment.
- Rejected every registry, paper-force, shadow, arm, broker, funding, or live interpretation.

Promotion routing:
- Dated/current project truth: claim JSON, executor/challenger/finalizer reports, readiness, coverage, LATEST, INDEX, this learning record, and schema-v2 compounding handoff.
- Reusable machinery/tests: `scripts/spy_index_theta_carry_lab.py` and `tests/test_spy_index_theta_carry_lab.py`.
- Skill: patched `trader-self-evolution` with a general temporal-coverage pitfall: minimum trade count is not full-train coverage; persist entry bounds/year counts and narrow claims unless a predeclared temporal gate passes.
- Memory: no addition. Dated metrics, hashes, family closure, and epoch streak belong in repository evidence; stable autonomy, capital, proxy-evidence, and anti-thrash stances already exist.

## LESSON

Future Trader now knows that a dual-cost train gate can pass while all qualifying entries occupy only an early slice of the train period. Sample count alone does not support stationarity or broad-train compatibility. Claim artifacts must persist entry-window coverage and reports must narrow authority to that window unless a predeclared temporal-coverage gate passes.

Future Trader can also distinguish absolute proxy profitability from mechanism identification: when a fixed-cadence contrast yields no bearish support, a positive non-bearish ledger cannot establish that the regime gate adds edge. The correct result is a closed F0 family, sealed holdout, explicit quarantine, and burst-stop reassessment after the third no-advance—not a retune or promotion.

## NEXT

`TAIL_HAZARD_EPOCH_BURST_STOP_REASSESSMENT`: stop strategy-experiment volume in active epoch `2026-07-15-tail-hazard-discovery` after three no-advance wakes. Write a dated search-design/data reassessment covering the recent-downshock absolute-hazard failure, downside-semivariance non-specificity, and SPY theta-carry comparator-support failure; inventory which evidence classes remain informative versus thrash-prone; preserve sealed holdouts `72a6d184…` and SPY 2022-07-12..2026-07-13 option outcomes; decide whether the lane closes or reopens only under one named new evidence class. Default to no new experiment in that wake. Do not retune the same SPY panel or promote proxy positivity; no registry, paper force, shadow, arm, broker, or live action.

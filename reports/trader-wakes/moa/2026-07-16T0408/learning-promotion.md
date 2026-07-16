# Learning promotion — MoA 2026-07-16T0408

## VERIFICATION

Strategy charter/outcome:

- Frozen charter: `reports/trader-wakes/moa/2026-07-16T0408/strategy-charter.md`.
- Economic mechanism: high-yield credit may reprice deteriorating risk appetite before large-cap equities; the exact primary test asked whether ten-session HYG-minus-IEF weakness inside a still-positive SPY long trend leads five-session SPY downside.
- Exact claim-bearing scope: `CREDIT_RISK_OFF_SPY_BEAR_PUT_21D_V1` / `HIGH_YIELD_CREDIT_DIVERGENCE_FORWARD_DOWNSIDE`; future conditional one-lot 18–24 DTE $2-wide SPY bear-put debit spread only, `capital_fit_usd=200`, frictionless planning `max_loss_usd=200` before debit/closing friction, `max_lots=1`.
- Final outcome: `FAMILY_CLOSED`, `F0_MECHANISM -> F0_MECHANISM`, strategy advancement false. Train n41/10y/support97.6190% produced signed event -0.909825%, signed control -0.201659%, paired excess -0.708167%, circular three-pair LB90 -1.360006%, hit 29.2683%, and worst-decile -4.015427%; event expectancy, paired specificity, uncertainty, and positive-frequency gates failed. The 28-pair holdout remains outcome-unread; simulation false; pricing zero.
- Secondary `OVERNIGHT_SELL_INTRADAY_RECOVERY_SPY_BULL_CALL_21D_V1` remains search information only: n32<36 and LB90 -0.200722% despite favorable point centers; its 24-pair holdout remains unread and option pricing is zero.

Commands and exact finalizer results:

- TDD RED: `.venv/bin/python -m unittest tests.test_train_only_defined_risk_candidate_factory.TrainOnlyDefinedRiskCandidateFactoryTest.test_dominant_failure_names_only_actual_failed_gates -v` -> expected `ImportError` for missing `_dominant_failure_mechanism`, exit 1. GREEN after minimal implementation -> `Ran 1 test in 0.000s`, `OK`.
- `.venv/bin/python -m unittest tests.test_train_only_defined_risk_candidate_factory tests.test_fomc_information_resolution_train_lab tests.test_trader_build_compounding -v` -> `Ran 47 tests in 9.389s`, `OK`. Coverage includes lag/future perturbation, prior-only no-reuse controls, positive and wrong-sign negative controls, sealed holdouts, ULP acceptance/material geometry rejection, exact failed-gate wording, shared FOMC source/control boundaries, schema-v2 handoff rules, active/completed epoch scoping, pivot, and burst-stop boundaries.
- Mandated `.venv/bin/python -m unittest discover -s tests` -> `Ran 416 tests in 26.777s`, `OK`.
- `.venv/bin/python -m py_compile scripts/fomc_information_resolution_train_lab.py scripts/train_only_defined_risk_candidate_factory.py tests/test_train_only_defined_risk_candidate_factory.py && just test` -> exit 0; TSLA and TSLL both `STAND ASIDE`; no broker action.
- Exact-cache replay to a temporary JSON plus substantive comparison excluding only `generated_at` -> `SUBSTANTIVE_REPLAY_EQUAL=true`; canonical raw SHA `2eb3e4c7ebf502de0ac533edcf8a986eb95253189a46922f6f3b7bb75b13f14c`; normalized SHA `a4fd731d931185297648b7bde28350c9b17022cf8062b9fc06fa0e76762d30b3`; panel 4,832. Primary control distance median/max 153/680; secondary 155.5/723.
- `.venv/bin/python scripts/trader_income_coverage.py --stamp 2026-07-16T0420` plus dated/LATEST `cmp` -> exit 0, `COVERAGE_SURFACES_IDENTICAL=true`; 21 structures, 246 hypotheses, 70 evolve artifacts, no quality leader.
- Schema-v2 validate-handoff: PENDING FINALIZER EXECUTION.
- Isolated temporary-index deterministic prepare gate: PENDING FINALIZER EXECUTION.
- Complete base-diff, untracked-file, sensitive-path, raw-secret, and generated-debris review: PENDING FINALIZER EXECUTION.

Challenger reconciliation:

- Accepted: exact primary `FAMILY_CLOSED` at F0; strategy advancement false; secondary remains search information only; both holdouts unread; option pricing zero; no registry/capital seat/paper/shadow/arm/live; dual-ID credit quarantine; bounded ULP adjusted-OHLCV repair; Form 4 pivot with a same-wake exercised decision.
- Repaired machinery: the canonical machine `dominant_failure_mechanism` now names only the actual four failed gates plus wrong-sign event expectancy and negative specificity. `tests/test_train_only_defined_risk_candidate_factory.py` proves passed density/support/tail/integrity dimensions cannot appear in the string.
- Repaired project truth: all living panel prose says 4,832; primary/secondary distance diagnostics are promoted; `configs/search_epoch.json` now formally registers the successor epoch at 0335, keeps FOMC completed, counts 0335+0408 as streak2, and sets pivot=true / burst=false.
- Rejected only one numeric challenger assertion: secondary median control distance is not 165; direct recomputation from all 32 persisted pair rows is 155.5. Maximum 723 is confirmed. This correction does not alter the screen's failed density/uncertainty decision.
- No economic challenger finding was rejected. `compounding.json` records every disposition; findings marked `rejected` there mean no machinery defect existed or the obligation was finalizer process/report routing, not that the substantive requirement was declined.

Integration is pending the deterministic wrapper gate. The finalizer has not committed, pushed, merged, switched branches, edited `.gitignore`, or claimed RUN COMPLETE.

## DURABLE

Repo files updated:

- `scripts/train_only_defined_risk_candidate_factory.py`, `scripts/fomc_information_resolution_train_lab.py`, and `tests/test_train_only_defined_risk_candidate_factory.py`: reusable train-only multi-mechanism machinery, bounded CSV geometry tolerance, exact failure-label generation, and behavioral/boundary/positive/negative controls.
- The run-local canonical factory claim JSON, `strategy-charter.md`, executor/challenger/merged role artifacts, `compounding.json`, and this file: canonical evidence, stable IDs, critic dispositions, machine outcome, and promotion history.
- `configs/search_epoch.json` and `docs/SEARCH_EPOCH_2026-07-16T0335.md`: durable successor-epoch registration with two counted no-advances, pivot required, burst stop false, and the completed FOMC epoch preserved as prior context.
- `reports/trader-wakes/2026-07-16T0408-moa-exec.md`, `reports/trader-wakes/2026-07-16T0408-moa-merge.md`, `reports/trader-wakes/LATEST.md`, `reports/trader-wakes/INDEX.md`, `reports/readiness/LATEST.md`, and refreshed income coverage: living outcome, authority, verification, convergence state, and exactly one next seed.

Promotion routing:

- No skill patch: `trader-self-evolution` already contains the reusable requirements exposed here—predeclared charter, lag-safe/prior-only controls, sealed holdouts, exact machine outcomes, critic repair artifacts/tests, schema-v2 handoff, complete-diff review, and deterministic wrapper integration. The new method is more precisely preserved as executable factory code and regression tests; adding duplicate prose would stack rather than improve guidance.
- No profile-memory addition: the family close, hashes, control-distance diagnostics, epoch count, and NEXT are dated project state consumed from versioned repo artifacts. Trader profile memory is near capacity and should not duplicate short-lived run truth.
- No doctrine rewrite beyond the new dated epoch charter: no stable risk/authority policy changed. Existing L0-versus-L1, strategy-versus-search-information, $3k one-lot planning, and no-live boundaries governed correctly.

No threshold, sign, horizon, control, or option-wrapper retune was promoted. No holdout read, option mark, registry mutation, paper intent, shadow promotion, arm, broker session, funding, or live authority was created.

## LESSON

Future Trader now knows/can do:

- compare multiple predeclared independent F0 mechanisms under one completed-session, next-close/five-session, prior-only no-reuse-control, chronological train/sealed-holdout contract while selecting exactly one claim-bearing decision;
- keep factory construction and ULP evidence repair separate from strategy advancement;
- generate machine dominant-failure prose from actual failed gates, preventing passed density/support/tail/integrity dimensions from being mislabeled;
- report long control distances as a comparability/generalization limitation without post-hoc tolerance widening;
- distinguish a positive point-center secondary screen from a density- and dependence-uncertainty-qualified survivor;
- formalize a successor search epoch so zero-input orientation can enforce two-no-advance pivot discipline without extending a completed historical epoch.

Economic lesson: the exact HYG-minus-IEF risk-off trigger is a strong bearish anti-edge over the frozen five-session train geometry. SPY rose rather than fell, and the signed outcome underperformed prior same-regime controls. The overnight/intraday disagreement signal is suggestive but remains uncertainty-unbounded and too sparse under the frozen bar. Neither merits holdout spending or option-wrapper tuning.

## NEXT

`SEC_FORM4_CLUSTERED_INSIDER_BUYING_DIRECTION_F0`: pivot to official point-in-time corporate-information evidence. Before outcome access freeze a fixed liquid multi-symbol panel, Form 4 open-market transaction-code/direct-indirect ownership/amendment/issuer/timestamp rules, cluster threshold, prior-only same-symbol no-reuse controls with max/median distance diagnostics, a signed five- or ten-session horizon, and a complete one-lot 18–24 DTE $2-wide call-debit Layered Edge Stack with `capital_fit_usd=200`, frictionless planning `max_loss_usd=200` before debit/closing friction, and `max_lots=1`. Exercise exactly one named F0→F1 `STRATEGY_ADVANCED` or `FAMILY_CLOSED` decision in the same wake; fail closed on derivatives, late/non-PIT filings, issuer mapping, reversing amendments, or insufficient cross-symbol/year density. Capability-only EDGAR scaffolding is not a completed wake. Do not inspect this wake's sealed holdouts or retune its credit/overnight screens.

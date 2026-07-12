# MOA BUILD executor — 2026-07-12T1616

WAKE: 2026-07-12T1622 PDT (Sunday; market closed)
PHASE: BUILD
SLEEVE: 3000
PAPER_ONLY: true
ROLE: GPT 5.6 Sol executor / only writer

## CHOSE

P2+P3: add a fail-closed realized-volatility state filter, then falsify one predeclared 14-DTE PCS volatility-compression DNA across BAC/F/SOFI/PLTR/TSLL/SMCI/AMD/AAPL with expanding 40/60/80% rolling-origin train gates and untouched following 20% holdouts.

The prior NEXT (append a second distinct New York option-archive date) was impossible on Sunday and therefore advisory rather than executable. This loop named a genuinely new evidence class—observed underlying realized-volatility state—without reopening any closed return/RSI, router, collar, asymmetric-IC, or BAC-management family.

## HYPOTHESIS + FALSIFIER

Hypothesis: a prior completed-bar `hv_20/hv_60 <= 0.80` compression state identifies entries where one-lot 14-DTE defined-risk PCS earns positive after-cost income.

Falsifier: no symbol passes every expanding fold with train gate first, positive untouched holdout SHIP on both 5% adverse-leg-slip and $0.01-per-leg half-spread axes, at least eight trades per axis, max loss <=$300, drawdown <=$75, dense-negative windows <=5, and exact ledger/signal integrity.

## DID

- Extended `pcs_sim.entry_filters_pass` with `entry_hv_ratio_min/max`, derived only from `hv_20/hv_60`; missing, nonfinite, zero, and negative denominators fail closed.
- Built `scripts/pcs_vol_compression_rolling_origin_lab.py`: one predeclared ratio<=0.80 DNA, no grid, three expanding folds, dual proxy costs, per-axis chunk DD/dense negatives, and unconditional/ratio>=1.20 expansion controls.
- Added behavioral, boundary, and negative-control tests for inclusive compression/expansion boundaries, disjoint controls, prior-bar lag, and fail-closed invalid volatility inputs.
- Ran all eight symbols and rejected the family without threshold/DTE tuning, hypothesis registration, or status mutation.
- Updated durable coverage doctrine and refreshed generated income coverage.

## EVIDENCE

- `.cache/platform/pcs_vol_compression_rolling_origin_lab_2026-07-12T1616.json`: `REJECT_VOL_COMPRESSION_PCS_ROLLING_ORIGIN`; 8/8 symbols, 24 folds, zero errors, zero train-gate passes, zero complete-fold passes.
- Minimum strategy-axis trade counts by symbol were 2–7; worst fold drawdown ranged from $119.35 (BAC) to $425.53 (AMD), already above the $75 absolute gate for every symbol.
- All 286 persisted candidate/control/window summaries had exact integrity; signal violations=0; same-bar reentries=0.
- Every run reports one-lot `capital_fit_usd`, `max_loss_usd`, and `max_lots`. Observed worst one-lot max loss ranged from $91.25 to $227.80, so risk fit alone did not rescue negative/unstable edge quality.
- Current living leader: none. Absolute gates were used; historical `b195f5fe` was not treated as a seat.

## VALIDITY

- No lookahead: realized-volatility ratios are read from the prior completed bar (`entry_signal_lag_bars=1`), and every entry passed independent signal-purity checks.
- Selection: one predeclared DNA; no holdout selection and no post-result tuning.
- Costs: both proxy cost axes must pass independently on train and holdout. Neither is labeled observed cost.
- Provenance: underlying OHLCV/realized volatility is observed; expirations, strikes, option marks, and costs remain synthetic/proxy. This experiment cannot earn L1 or a capital seat.
- Population/ranking: eight specified symbols completed; PCS-only population; no stale leader or incomplete row was promoted.
- Contract availability: synthetic Friday/rounded-strike discovery only. The one-date option archive remains insufficient for provider-backed history.

## DECISION

`REJECT_VOL_COMPRESSION_PCS_ROLLING_ORIGIN`. Close this predeclared daily-bar volatility-compression PCS family for the current proxy evidence class. No grid expansion, registration, promotion, leader, capital seat, B-check change, paper order, shadow, arm, broker session, or live action. BUILD/L0 remains.

## CAPITAL

Structure: one-lot defined-risk put credit spread. `capital_fit_usd` equals defined max loss; hard one-lot max-loss gate $300; `max_lots` is reported per run; operational posture remains one lot and <=$750 aggregate open risk. No row qualifies because every train gate failed before capital-path consideration.

## FREEDOM AUDIT

Symbol and strategy search remained open. The observed option-history boundary blocked only observed-cost/L1 claims; it did not block a new volatility-state hypothesis. No caller-chosen slot, structure, or prior NEXT constrained the choice.

## VERIFICATION

- Preflight correctly failed on wrapper-created run residue (`income-coverage-LATEST`, dated coverage, and MoA metadata); no unrelated residue was absorbed or removed.
- Focused behavioral/boundary/negative-control/regression tests: 25/25 OK.
- Full regression: `.venv/bin/python -m unittest discover -s tests` -> 122/122 OK.
- Compile: changed Python/test surfaces passed `py_compile`.
- Coverage: `.venv/bin/python scripts/trader_income_coverage.py --write --stamp 2026-07-12T1616` -> 20 structures / 245 hypotheses / no living leader.
- Whitespace: `git diff --check` -> exit 0.

## DURABLE

- `trader_platform/research/pcs_sim.py`
- `scripts/pcs_vol_compression_rolling_origin_lab.py`
- `tests/test_pcs_vol_compression_rolling_origin_lab.py`
- `docs/INCOME_STRATEGY_COVERAGE.md`
- `scripts/trader_income_coverage.py`
- `reports/readiness/income-coverage-{LATEST,2026-07-12T1616}.md`
- Formal readiness/B checks unchanged; `reports/readiness/LATEST.md` intentionally unchanged.

## LESSON

A lagged low 20d/60d realized-volatility ratio is now a reusable, fail-closed PCS research feature, but the predeclared <=0.80 compression DNA is not an after-cost edge: all 24 train gates failed before any holdout could support it. Do not tune this proxy family to manufacture a pass.

## ONE NEXT SEED

On the next distinct New York RTH market date, append one all-expiration TSLL observation snapshot and verify archive density advances from 1/3 to 2/3 without duplicate identical rows; do not run provider-backed historical simulation before 3/3.

Executor phase only: no commit/push/merge and no RUN COMPLETE claim. Challenger and finalizer remain required.

GATES: none

MOA_EXEC_DONE

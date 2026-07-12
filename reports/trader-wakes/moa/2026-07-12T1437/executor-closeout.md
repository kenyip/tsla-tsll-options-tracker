# MOA BUILD executor closeout — 2026-07-12T1437

WAKE: 2026-07-12T1437 PDT (Sunday; market closed)
PHASE: BUILD
SLEEVE_USD: 3000
PAPER_ONLY: true
ROLE: GPT 5.6 Sol executor / only writer

## CHOSEN LOOP

P2+P3 direction/time falsification: test one predeclared lagged mild-pullback 7-DTE put-credit-spread DNA across three expanding rolling-origin folds on eight liquid symbols. This accepted the prior NEXT only after orientation because it was the smallest independent experiment that could distinguish a repeatable pullback edge from the just-rejected one-split momentum result; weekend conditions still blocked the distinct-RTH observed-archive append.

## HYPOTHESIS AND FALSIFIER

Hypothesis: a prior completed-bar mild bearish pullback (`ret_1d<=-0.5%`, RSI 35–50) improves one-lot 7-DTE defined-risk PCS entries after both 5% adverse leg slip and a $0.01 per-leg half-spread.

Falsifier: no symbol passes all three folds when each fold independently requires its expanding train sample to pass before the following untouched 20% holdout can pass, with positive SHIP on both cost axes, at least eight trades per axis, max loss <=$300, full-path and chunk drawdown <=$75, dense-negative windows <=5, and exact ledger/signal integrity.

## ACTED

- Added `scripts/pcs_pullback_rolling_origin_lab.py` with one fixed DNA, no tuning grid, expanding 40/60/80% train endpoints, following non-overlapping 20% holdouts, and exact unconditional/bullish-mirror controls.
- Added behavioral, boundary, and negative-control coverage in `tests/test_pcs_pullback_rolling_origin_lab.py` for lag/disjointness, fold chronology, train-gate conjunction, and unrounded drawdown fail-close.
- Ran the full eight-symbol experiment and stopped without retuning when the preregistered family failed.
- Updated the living direction-bias coverage truth and generated coverage surfaces. No hypothesis registry mutation or status transition occurred.

## RESULT

Decision: `REJECT_MILD_PULLBACK_PCS_ROLLING_ORIGIN`.

- Population complete: 8/8 symbols, 24 folds, zero errors, zero symbols passing all folds.
- Only 3/24 train folds passed both cost gates: PLTR fold 2, SMCI fold 1, AMD fold 0. Every one then failed its untouched holdout.
- PLTR fold 2 holdout: 5% n10 / -$32.69 / DD $170.64 / max loss $219.26; fixed n10 / +$41.92 / DD $131.80 / max loss $212.26.
- SMCI fold 1 holdout: 5% n8 / -$52.67 / DD $54.73 / max loss $86.33; fixed n8 / -$13.76 / DD $29.57 / max loss $83.16.
- AMD fold 0 holdout: 5% n9 / -$245.67 / DD $210.72 / max loss $217.31; fixed n9 / -$138.86 / DD $140.38 / max loss $211.10.
- Integrity: 286/286 persisted candidate/control/window summaries exact; signal violations=0; same-bar reentries=0.

## EVIDENCE VALIDITY

- Leakage/lookahead: entry return/RSI is lagged one completed bar and checked against every trade entry; holdouts are chronological and never used for DNA selection because there is no grid.
- Costs: both proxy axes are required independently on train and holdout; neither is claimed to be observed cost.
- Contract availability/provenance: simulator uses labeled synthetic listed-Friday/rounded-strike Black-Scholes discovery. The observed archive remains one market date, so this result cannot earn L1 or support real-account readiness.
- Population/ranking: exact eight-symbol population completed with no mixed structures and no ranking omissions.
- Path realism: exact PnL/DD recomputation, no close-bar re-entry, signal purity, and two-axis holdout chunk checks all passed.
- Capital: structure is a one-lot defined-risk PCS; each run records `capital_fit_usd`, `max_loss_usd`, and `max_lots`; hard max-loss gate is $300 and default posture is one lot. No row earned a capital seat.

## VERIFICATION

- `.venv/bin/python scripts/pcs_pullback_rolling_origin_lab.py --out .cache/platform/pcs_pullback_rolling_origin_lab_2026-07-12T1437.json` -> reject, 8 completed, 0 all-fold passes, 0 errors.
- `.venv/bin/python -m unittest tests.test_pcs_pullback_rolling_origin_lab tests.test_pcs_momentum_walkforward_lab tests.test_pcs_expiry_grid` -> 21/21 OK.
- `.venv/bin/python -m unittest discover -s tests` -> 103/103 OK.
- Python compile and `git diff --check` -> exit 0.
- `.venv/bin/python scripts/trader_income_coverage.py --write --stamp 2026-07-12T1437` -> 20 structures, 245 hypotheses, no living leader.

## DURABLE LEARNING

Future Trader can run a predeclared rolling-origin direction hypothesis without holdout selection leakage and can fail closed on train, both cost axes, full/chunk drawdown, density, capital, and integrity. The mild-pullback PCS family is closed this cycle: do not grid-expand or reinterpret isolated control wins. `docs/INCOME_STRATEGY_COVERAGE.md` and the generated coverage report now carry that truth. Formal readiness/B checks are unchanged, so `reports/readiness/LATEST.md` is intentionally not rewritten by this executor.

## FREEDOM AUDIT

No prompt rule or tool constraint blocked a higher-information valid experiment. The one-date archive blocked only observed-history/L1 claims. Weekend timing made a new distinct-date capture impossible, and the fixed-DNA rolling-origin falsifier was more informative than another free evolve or another daily-bar signal grid.

## NEXT

On the next distinct NY RTH market date, append one all-expiration TSLL observation snapshot and verify archive density advances from 1/3 to 2/3 without duplicates; do not run provider-backed historical simulation before 3/3.

Executor phase only: no commit, push, merge, shadow/live promotion, broker action, arm, or RUN COMPLETE claim. Challenger and finalizer remain required.

MOA_EXEC_DONE

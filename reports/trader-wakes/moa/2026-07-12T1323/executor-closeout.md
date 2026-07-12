# MOA BUILD executor closeout — 2026-07-12T1323

WAKE: 2026-07-12T1323 PDT (daily; Sunday market closed)
PHASE: BUILD
SLEEVE_USD: 3000
PAPER_ONLY: true
ROLE: GPT 5.6 Sol executor / only writer

## Chosen loop

P2+P3 lagged bullish-momentum PCS direction-bias hypothesis with strict chronological selection/holdout falsification. This superseded the prior RTH-only quote-archive NEXT because a second distinct New York market-date snapshot cannot be collected on Sunday; the independent proxy axis could still change the research decision without weakening the observed-data boundary.

## Hypothesis and falsifier

Hypothesis: a prior completed-bar bullish momentum state (positive 1-day return plus moderate RSI) improves one-lot defined-risk put-credit-spread entries after costs versus unconditional and bearish-mirror controls.

Falsifier: no DNA selected only on the first 60% of each symbol remains dense and positive on the untouched final 40% under both 5% adverse leg slip and $0.01-per-leg half-spread, with SHIP verdict, max loss <=$300, max drawdown <=$75, dense-negative windows <=5, and exact signal/ledger/no-reentry integrity.

## Validity prerequisites and repair

- Signals use `entry_signal_lag_bars=1`; return and RSI come from a prior completed bar, while entry is priced on the following close.
- The 16-row grid is ranked only on train. Exactly one selected DNA per symbol is evaluated on holdout.
- The first harness version could have labeled a holdout pass when its selected train DNA failed the train gate. That claim-invalidating boundary was repaired with `walkforward_pass`, covered by a negative test, and the exact experiment was rerun.
- This remains synthetic listed-Friday/rounded-strike daily-bar Black-Scholes discovery. It is not observed option-quote evidence and cannot earn L1. The quote archive remains one distinct market date.

## Experiment

- Population: BAC, F, SOFI, PLTR, TSLL, SMCI, AMD, AAPL; put-credit-spread only.
- Grid per symbol: 7/14 DTE × prior-day return >=0%/0.5% × RSI floor 50/55 × RSI ceiling 65/75 = 16 train DNA.
- Costs: 5% adverse leg slip and $0.01 half-spread per leg at entry and exit.
- Controls on untouched holdout: same-DTE unconditional PCS and a matched bearish-momentum mirror.
- Capital: one-lot defined-risk vertical; selected max loss ranged below the $300 hard gate and result rows emit `capital_fit_usd`, `max_loss_usd`, and `max_lots`; default posture remains one lot.

## Result

Decision: `REJECT_BULLISH_MOMENTUM_PCS_WALKFORWARD`.

- Eight of eight symbols completed; zero complete holdout passes; no errors.
- BAC was the only selected DNA that passed the train gate: 7 DTE, prior return >=0.5%, RSI 50–65. Train was 49 trades / +$72.58 / DD $53.89 at 5% slip and 40 / +$79.32 / DD $32.47 at fixed cost, with max loss below $95.
- BAC failed untouched holdout: 42 / +$42.88 / DD $94.72 at 5% slip and 39 / −$53.59 / DD $96.12 at fixed cost. It fails both the positive fixed-cost edge and $75 drawdown gates.
- All 88 persisted selected/control/window summaries had exact ledger, no-close-bar-reentry, and signal-purity integrity.
- The SOFI bearish-mirror negative control was positive on both holdout cost axes (16 / +$35.56 / DD $38.82 at 5%; 15 / +$11.65 / DD $43.16 fixed; max loss below $92), but it was not train-selected and is selection-biased control evidence only—not a candidate or capital seat.
- No hypothesis registration, status promotion, living leader, capital seat, readiness B-check change, or paper order.

## Evidence

- Lab: `.cache/platform/pcs_momentum_walkforward_lab_2026-07-12T1323.json`
- Runner: `scripts/pcs_momentum_walkforward_lab.py`
- Behavioral/boundary tests: `tests/test_pcs_momentum_walkforward_lab.py`
- Focused verification: `.venv/bin/python -m unittest tests.test_pcs_momentum_walkforward_lab tests.test_pcs_expiry_grid` -> 15/15 OK.
- Full suite: `.venv/bin/python -m unittest discover -s tests` -> 90/90 OK.
- Diff check: `git diff --check` -> exit 0.
- Coverage: `.venv/bin/python scripts/trader_income_coverage.py --write` -> refreshed `reports/readiness/income-coverage-LATEST.md` at 2026-07-12T1331; catalog 20, hypotheses 245, living leader none.

## Durable residue

- Reusable strict train-gate + untouched-holdout direction harness in `scripts/pcs_momentum_walkforward_lab.py`.
- Boundary tests prevent holdout-only passes, negative-PnL gate passes, train ranking from reading holdout, and overlapping momentum/mirror filters.
- `docs/INCOME_STRATEGY_COVERAGE.md` and generated coverage now record the family rejection.
- Formal readiness remains BUILD/L0, so `reports/readiness/LATEST.md` is intentionally unchanged.

## Freedom audit

No prompt rule or tool constraint blocked a higher-information valid experiment. The one-date observed archive blocked only observed-cost/L1 claims, not this independent chronological proxy falsification. Catalog freedom was available; the smallest decision-changing experiment reused the already-tested defined-risk PCS simulator rather than adding another assumption-heavy structure.

## Close

Progress type: P2 direction capability + P3 decisive walk-forward falsification — 4/5.
Honesty: L0 BUILD. No living quality leader.
ONE NEXT SEED: run one predeclared rolling-origin replication of the mild bearish-momentum PCS control across the same eight-symbol population, with no grid expansion and train-selection required before each next fold; reject the axis unless it clears both cost and $75 drawdown gates across folds. Do not treat the current SOFI holdout control as a candidate.

Executor phase only: no commit, push, merge, or RUN COMPLETE claim. Grok challenge and finalizer remain required.

MOA_EXEC_DONE

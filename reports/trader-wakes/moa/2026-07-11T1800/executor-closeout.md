# MOA BUILD lab executor closeout — 2026-07-11T1800

WAKE: 2026-07-11T1800 PDT
PHASE: BUILD
SLEEVE: 3000
MODE: paper/research only
EXECUTOR: GPT 5.6 Sol (only writer)

## CHOSE

Axis E / P1+P3 — accepted the prior NEXT seed: close the exact observed-quote strategy-leg/expiry/strike/time join gap, enforce an insufficient-coverage reject gate, then falsify the one requested free-catalog population. Superseded no prior seed.

## DID

- Fresh multi-symbol research run32: 23/23 scored; top eight TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Naked `fit_3k` remained TSLL/SMCI only; defined-risk research remained open across names.
- Ran one applied free-catalog population: 36 DNA, top symbols TSLL/SMCI/PLTR/NFLX/BAC/XOM/MU/TSLA, 8 SHIP. Single-leg CSP SHIPs remain research toys.
- Added tested exact observed-quote matching in `trader_platform/research/option_quote_observations.py`: exact symbol/expiration/type/strike plus non-future as-of time and maximum quote-age enforcement.
- Added `scripts/observed_quote_coverage.py` for registered PCS/CCS/IC DNA. It expands every simulated entry and exit into exact legs and rejects calibration unless all required entry and exit legs match observed rows.
- Leader smoke: 57 five-year PCS trades required 228 exact leg observations; the only 70-row TSLL current snapshot matched 0. Decision: `REJECT_INSUFFICIENT_COVERAGE`. No observed-cost calibration claim.
- Dated B3+B4 falsified five defined-risk SHIPs plus leader. All five new rows B3 soft-held, but none reached L1; four failed B4 and BAC CCS was baseline-negative/thin at 5% despite soft `cost_hold`.
- Refreshed income coverage: 17 catalog structures, 206 hypotheses, 55 evolve artifacts.

## QUALITY BAR

| hyp / structure | capital_fit_usd | max_loss_usd (1 lot) | max_lots | window max_dd | dense neg | B3 | B4 | 5% after-cost | judgment |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| TSLL PCS `b195f5fe` | 3000 | 76.32 | 1 | 74.85 | 5 | hold | soft hold | n13 / -18.32 | relative leader only; not L1 |
| TSLL calendar `34f2b2c5` | 3000 | 110.41 | 1 | 121.55 | 3 | hold | fail | n93 / -266.85 | reject L1 |
| BAC bull-call debit `79f3be52` | 3000 | 87.37 | 1 | 233.36 | 5 | hold | fail | n94 / -131.66 | reject L1 |
| MU butterfly `badb31d7` | 3000 | 19.73 | 1 | 51.07 | 8 | hold | fail | n626 / -45879.62 | reject L1 |
| NFLX iron butterfly `e6b04d6b` | 3000 | 66.99 | 1 | 73.25 | 3 | hold | fail | n291 / -19228.35 | reject L1 |
| BAC CCS `b9a0f0f3` | 3000 | 163.19 | 1 | 173.65 | 6 | hold | soft hold | n1 / -42.93 | baseline NULL/thin; reject L1 |

`l1_hyp_ids=[]`. A soft B4 label with negative or one-trade output is not an after-cost edge.

## EVIDENCE

- `.cache/platform/research_reports/2026-07-12_run32.md`
- `.cache/platform/evolve_audit.jsonl` (`2026-07-12T01:01:26+00:00`)
- `.cache/platform/stress_regime_lab_2026-07-11T1800.json`
- `.cache/platform/stress_cost_lab_2026-07-11T1800.json`
- `.cache/platform/quality_bar_lab_2026-07-11T1800.json`
- `.cache/platform/observed_quote_coverage_lab_2026-07-11T1800.json`
- `.cache/platform/option_quotes/TSLL_2026-07-11T1710.csv`
- `docs/OPTION_QUOTE_DATA_BOUNDARY.md`
- `reports/readiness/income-coverage-LATEST.md`

## VERIFICATION

- `.venv/bin/python -m unittest tests.test_option_quote_observations` -> 5/5 pass.
- `py_compile` passed for the join module and coverage CLI.
- Exact coverage CLI executed against the observed archive and wrote the reject artifact.
- B3 and B4 scripts completed for all six named hypotheses.

## DURABLE

Exact observed quote joining is now executable and fail-closed. It exposed a second realism boundary: PCS synthetic expirations are `entry_date + DTE` calendar dates (including non-listed weekdays), so forward snapshots cannot cover many simulated contracts even with denser capture. Do not mistake archive growth alone for closure.

## CLOSE

Progress type: P1+P3
Progress score: 4/5
Honesty: L0

NEXT SEED: Make PCS/CCS/IC simulation expiration selection use a listed weekly-expiry grid (Friday/available-expiry abstraction), add regression tests, then rerun `b195f5fe` B3+B4 and exact coverage; reject the leader if ml/dd or after-cost quality deteriorates.

GATES: none
MOA_EXEC_DONE

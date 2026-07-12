# MOA BUILD lab executor closeout — 2026-07-11T1000

WAKE: 2026-07-11T1000 weekend BUILD lab executor
PHASE: BUILD
SLEEVE: 3000
CHOSE: Axis B — close the entry-weekday time-bias gap, then cost/regime-falsify the best time rows and the new free-search SHIPs.

## DID

- Refreshed multi-symbol research: run25 scored 23/23; composite top eight TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Only TSLL/SMCI fit the naked-short $3k proxy; defined-risk structures remain the channel for expensive names.
- Ran exactly one applied free-catalog population (`top-symbols=8`, `mutants=2`, `max-population=36`, sleeve $3k). It created six SHIPs: BAC diagonal, PLTR butterfly, XOM PCS, TSLA bear-put debit, plus two undefined-risk TSLL single-leg research toys.
- Added `entry_weekdays` gating to `pcs_sim` and entry-weekday + explicit-slippage axes to `pcs_time_bias_grid.py`; added two unittest cases.
- Ran the 216-cell mid grid and matching 216-cell 5%-slip grid on leader `b195f5fe`.
- Falsified the leader plus four new defined-risk SHIPs with dated B3+B4; built a seven-row quality table including two exact time variants.
- Refreshed income coverage. No live, broker, shadow, arm, or capital-path promotion.

## EVIDENCE

- Research: `.cache/platform/research_reports/2026-07-11_run25.md`
- Evolve audit: `.cache/platform/evolve_audit.jsonl` at `2026-07-11T17:01:43Z`
- Required B3: `.cache/platform/stress_regime_lab_2026-07-11T1000.json`
- Required B4: `.cache/platform/stress_cost_lab_2026-07-11T1000.json`
- Weekday grid mid: `.cache/platform/time_bias_weekday_lab_2026-07-11T1000.json`
- Weekday grid 5%: `.cache/platform/time_bias_weekday_cost5_lab_2026-07-11T1000.json`
- Exact time B3: `.cache/platform/time_bias_weekday_regime_2026-07-11T1000.json`
- Exact time B4: `.cache/platform/time_bias_weekday_cost_stress_2026-07-11T1000.json`
- Quality table: `.cache/platform/quality_bar_lab_2026-07-11T1000.json`
- Tests: `.venv/bin/python -m unittest tests.test_pcs_time_bias_grid tests.test_pcs_direction_scoreboard -v` → 4/4 OK
- Smoke: `.venv/bin/python trader_platform/smoke_test.py` → platform smoke OK
- Coverage: `reports/readiness/income-coverage-LATEST.md` (16 structures, 165 hyps, 42 evolve artifacts)

## QUALITY BAR VS `b195f5fe`

| hyp / variant | ml $ | window DD $ | dense neg | B3 | 5% n / pnl $ | judgment |
|---|---:|---:|---:|---|---:|---|
| TSLL PCS `b195f5fe` | 76.32 | 74.85 | 5 | hold | 13 / -18.32 | Relative leader; below L1 because after-cost negative |
| BAC diagonal `8aa2a33b` | 296.99 | 313.08 | 4 | hold | 99 / -1412.77 | Reject cost + ml/dd |
| PLTR butterfly `db859f1f` | 28.18 | 55.28 | 10 | hold | 515 / -31299.46 | Reject baseline + cost |
| XOM PCS `2026b890` | 200.08 | 314.41 | 5 | hold | 41 / -875.04 | Reject cost + DD |
| TSLA bear-put debit `f1217f66` | 293.77 | 1038.01 | 11 | fail | 118 / -22003.94 | Reject regime + cost + DD |
| TSLL Thu 14d / PT65 | 75.17 | 27.43 | 0 | hold | 0 / 0.00 | Reject: 5% result vacuous |
| TSLL all-day 30d / PT35 | 74.54 | 97.14 | 7 | hold | 21 / +10.52 | Reject L1: non-vacuous after-cost, but DD/dense-neg worse than leader |

`l1_hyp_ids=[]`. The 30-DTE variant is the first row this wake to clear non-vacuous after-cost and B3, but it does not clear the competitive ml/dd quality bar. It was not registered or promoted.

## DURABLE

- Time coverage now includes weekday slices and reproducible cost-aware grids; session-time remains the precise gap.
- Quality judgment is machine-readable in `.cache/platform/quality_bar_lab_2026-07-11T1000.json`.
- Updated `docs/INCOME_STRATEGY_COVERAGE.md`, `docs/BUILD_LAB_ENVIRONMENT.md`, coverage generator, tests, readiness/wake residue.

## JUDGMENT

Progress type: **P2 + P3**
Progress score: **4/5** — closed a real time-axis gap and found/falsified one non-vacuous after-cost row, but no L1 edge survived the competitive DD/density bar.
Honesty level: **L0 BUILD**. No HIGH CONFIDENCE/L1 candidate and no real-account readiness claim.

## NEXT SEED

Next BUILD only: make the cost-aware time grid multi-hyp across registered PCS/CCS candidates, then B3 only rows with non-vacuous positive 5% results; reject unless window DD <= $74.85 and dense-negative windows <= 5.

GATES: none
MOA_EXEC_DONE

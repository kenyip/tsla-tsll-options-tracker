# MOA BUILD lab executor closeout — 2026-07-11T1400

WAKE: 2026-07-11T1400 weekend BUILD lab executor
PHASE: BUILD
SLEEVE: 3000
CHOSE: Axis B — fulfill the prior seed by making the 5%-cost time grid multi-hyp across PCS/CCS, then exact-B3/B4 only the non-vacuous winner.

## DID

- Refreshed multi-symbol research: run26 scored 23/23; top eight were TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Only TSLL/SMCI fit the naked-short $3k proxy; defined-risk remains the channel for expensive names.
- Ran exactly one applied free-catalog population (`top-symbols=8`, `mutants=2`, `max-population=36`, sleeve $3k). New defined-risk SHIPs were TSLL calendar `5e575b61`, MU butterfly `e34563aa`, and BAC PCS `5f52fa0e`; single-leg creations remain research toys.
- Extended `pcs_time_bias_grid.py` from one hyp to multi-hyp PCS/CCS/IC grids, preserving per-hyp baselines and 1-lot capital fields; added parser coverage.
- Ran one 864-row 5%-slip grid across the leader, XOM CCS, BAC CCS, and new BAC PCS. The only standout was transient BAC PCS Friday 7-DTE / PT35 / stop5.
- Added `pcs_time_variant_stress.py` and ran exact unregistered-DNA B3+B4 on that row. It is dense and cost-positive but misses the strict leader ml/dd bar, so it was not registered or promoted.
- Falsified the leader plus all three new defined-risk SHIPs with the required dated B3+B4 files. Refreshed coverage. No live, broker, arm, shadow, or capital-path promotion.

## EVIDENCE

- Research: `.cache/platform/research_reports/2026-07-11_run26.md`
- Evolve audit: `.cache/platform/evolve_audit.jsonl` at `2026-07-11T21:01:08Z`
- Multi-hyp 5% grid: `.cache/platform/time_bias_multi_cost5_lab_2026-07-11T1400.json` (864 rows)
- Exact BAC time variant B3+B4: `.cache/platform/time_bias_bac_pcs_variant_stress_2026-07-11T1400.json`
- Required B3: `.cache/platform/stress_regime_lab_2026-07-11T1400.json`
- Required B4: `.cache/platform/stress_cost_lab_2026-07-11T1400.json`
- Quality table: `.cache/platform/quality_bar_lab_2026-07-11T1400.json` (`l1_hyp_ids=[]`)
- Tests: `.venv/bin/python -m unittest tests.test_pcs_time_bias_grid tests.test_pcs_direction_scoreboard -v` → 5/5 OK
- Smoke: `.venv/bin/python trader_platform/smoke_test.py` → platform smoke OK
- Coverage: `reports/readiness/income-coverage-LATEST.md` (16 structures, 172 hyps, 43 evolve artifacts)

## QUALITY BAR VS `b195f5fe`

| hyp / variant | ml $ | window DD $ | dense neg | B3 | 5% n / pnl $ | judgment |
|---|---:|---:|---:|---|---:|---|
| TSLL PCS `b195f5fe` | 76.32 | 74.85 | 5 | hold | 13 / -18.32 | Relative leader; below L1 because after-cost negative |
| TSLL calendar `5e575b61` | 81.94 | 144.46 | 6 | hold | 97 / -242.09 | Reject cost + ml/dd |
| MU butterfly `e34563aa` | 17.93 | 43.05 | 2 | hold | 572 / -43784.78 | Reject cost; severe leg-slip fragility |
| BAC PCS `5f52fa0e` | 187.54 | 508.70 | 6 | hold | 802 / -176.36 | Reject cost + ml/dd |
| BAC PCS Fri 7d / PT35 / stop5 | 184.55 | 87.29 | 2 | hold | 189 / +690.05 | Reject L1: after-cost dense, but max loss and window DD exceed leader |

`l1_hyp_ids=[]`. The BAC time row is the strongest after-cost signal found in this loop, but strict L1 requires both its 1-lot max loss and window drawdown to be competitive with the leader. It is unregistered research only.

## DURABLE

- Multi-hyp time search is now reproducible in one artifact instead of one process per hyp.
- Exact unregistered time variants can be B3+B4 stressed without registry mutation.
- Coverage doctrine/generator now state the multi-hyp + exact-transient capability; session-time remains the time-axis gap.

## JUDGMENT

Progress type: **P2 + P3**
Progress score: **4/5** — closed the prior multi-hyp seed and found a dense, non-vacuous after-cost row, but strict max-loss/window-DD quality rejected L1.
Honesty level: **L0 BUILD**. No HIGH CONFIDENCE/L1 candidate and no real-account readiness claim.

## NEXT SEED

Next BUILD only: resize the BAC Friday 7-DTE PCS width from $2 toward $0.50 while preserving its exact time filters, then rerun exact B3+B4; reject unless 5% after-cost remains positive and max loss/window DD both meet the $76.32/$74.85 leader bar.

GATES: none
MOA_EXEC_DONE

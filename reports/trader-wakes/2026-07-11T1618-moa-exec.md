# MOA BUILD lab executor closeout — 2026-07-11T1618

WAKE: 2026-07-11T1618 evening BUILD lab executor
PHASE: BUILD
SLEEVE: 3000
CHOSE: Axis D / P4 — close the prior BAC Friday 7-DTE PCS width-resize seed with exact B3+B4 and a strict quality-bar rejection test.

## DID

- Refreshed multi-symbol research: run27 scored 23/23; top eight were TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Only TSLL/SMCI fit the naked-short $3k proxy; defined-risk remains the capital channel for expensive names.
- Ran exactly one applied free-catalog population (`top-symbols=8`, `mutants=2`, `max-population=36`, sleeve $3k). New defined-risk SHIPs were BAC diagonal `8f5c5f11`, BAC bull-call debit `56dac933`, and BAC butterfly `3a0b106b`; SMCI short-DTE and other single-leg SHIPs remain research toys.
- Extended `pcs_time_variant_stress.py` with a tested `--spread-width` override so exact unregistered width variants can be falsified without registry mutation.
- Ran exact B3+B4 for BAC Friday / 7-DTE / PT35 / stop5 at nominal widths $2, $1, and $0.50. Width $1 remained dense and positive after 5% slip (n196 / +$397.68), with B3 hold, window DD $69.64, and two dense-negative windows, but max loss $87.64 missed the leader's $76.32 bar.
- Nominal $0.50 produced exactly the same n/PnL/DD/max-loss as $1, exposing the simulator's strike-rounding/effective-width floor. Per the prior seed, the width path is rejected without more tuning.
- Falsified the leader plus all three new defined-risk SHIPs in the required dated B3+B4 files. All new base SHIPs failed cost or regime quality. No registry promotion, shadow, live, broker, or arm action.

## EVIDENCE

- Research: `.cache/platform/research_reports/2026-07-11_run27.md`
- Evolve audit: `.cache/platform/evolve_audit.jsonl` at `2026-07-11T23:19:15Z`
- Width $2 exact stress: `.cache/platform/time_bias_bac_pcs_width2_stress_2026-07-11T1618.json`
- Width $1 exact stress: `.cache/platform/time_bias_bac_pcs_width1_stress_2026-07-11T1618.json`
- Width $0.50 exact stress: `.cache/platform/time_bias_bac_pcs_width0p5_stress_2026-07-11T1618.json`
- Required B3: `.cache/platform/stress_regime_lab_2026-07-11T1618.json`
- Required B4: `.cache/platform/stress_cost_lab_2026-07-11T1618.json`
- Quality table: `.cache/platform/quality_bar_lab_2026-07-11T1618.json` (`l1_ids=[]`)
- Tests: focused 4-module suite → 10/10 OK
- Smoke: `.venv/bin/python trader_platform/smoke_test.py` → `platform smoke OK`
- Coverage: `reports/readiness/income-coverage-LATEST.md` (16 structures, 176 hyps, 43 evolve artifacts)

## QUALITY BAR VS `b195f5fe`

| hyp / variant | ml $ | window DD $ | dense neg | B3 | 5% n / pnl $ | judgment |
|---|---:|---:|---:|---|---:|---|
| TSLL PCS `b195f5fe` | 76.32 | 74.85 | 5 | hold | 13 / -18.32 | Relative leader; not L1 because after-cost negative/thin |
| BAC PCS Fri7 width $2 | 184.55 | 87.29 | 2 | hold | 189 / +690.05 | Reject L1: ml and DD miss leader |
| BAC PCS Fri7 width $1 | 87.64 | 69.64 | 2 | hold | 196 / +397.68 | Reject L1: DD/density improve, but ml exceeds leader by $11.32 |
| BAC PCS Fri7 nominal width $0.50 | 87.64 | 69.64 | 2 | hold | 196 / +397.68 | Reject width path: identical to $1 from strike rounding |
| BAC diagonal `8f5c5f11` | 293.66 | 510.65 | 6 | fail | 131 / -2683.96 | Reject B3+B4 + ml/dd |
| BAC bull-call debit `56dac933` | 88.34 | 294.31 | 6 | hold | 84 / -395.89 | Reject B4 + DD |
| BAC butterfly `3a0b106b` | 23.00 | 51.93 | 7 | hold | 260 / -6097.45 | Reject B4; severe leg-slip fragility |

`l1_ids=[]`. The $1 BAC width is a meaningful after-cost improvement over the $2 risk shape, but strict L1 is conjunctive: it still misses max-loss quality. The nominal $0.50 row is not a further resize in the proxy, so this path is closed rather than polished.

## DURABLE

- Exact transient PCS/CCS/IC time variants now accept `--spread-width`; parser behavior is covered by `tests/test_pcs_time_bias_grid.py`.
- The BAC Friday width hypothesis has a reproducible reject artifact, including the discovered effective-width floor.
- Capital path remains unchanged; `b195f5fe` is only the relative quality reference and is itself below L1.

## JUDGMENT

Progress type: **P4 + P3**
Progress score: **4/5** — dense non-vacuous after-cost behavior survived a real resize and baseline DD improved, but max loss still missed the strict bar; the narrower nominal width collapsed to the same effective structure, yielding a clear stop rule rather than HIGH CONFIDENCE.
Honesty level: **L0 BUILD**. No L1 candidate, no real-account readiness claim.

## NEXT SEED

Next BUILD only: implement a minimal defined-risk `iron_butterfly` credit simulator scaffold with synthetic smoke and catalog/evolve dispatch, then run one focused population and B3+B4 only on any non-vacuous SHIP; reject unless after-cost and ml/dd meet the same leader bar.

GATES: none
MOA_EXEC_DONE

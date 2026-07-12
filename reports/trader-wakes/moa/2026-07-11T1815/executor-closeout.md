# MOA BUILD lab executor closeout — 2026-07-11T1815

WAKE: 2026-07-11T1815 PDT
PHASE: BUILD
SLEEVE: 3000
MODE: paper/research only
EXECUTOR: GPT 5.6 Sol

## CHOSE

Axis E / P1+P3 — take the prior NEXT seed: replace synthetic entry-date-plus-DTE expirations in PCS/CCS/IC with a listed-Friday weekly abstraction, then restress the former quality leader and one free-catalog population. This superseded another proxy-class scaffold because exact-contract realism was already blocking observed-cost calibration.

## DID

- Research run33 scored 23/23; top eight were TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Naked short fit remained TSLL/SMCI only; expensive names require defined risk.
- Added `listed_weekly_expiration()` to `pcs_sim`: first Friday on or after target DTE; actual calendar DTE now drives pricing and `dte_at_entry`.
- Added Friday-preservation, weekday-roll-forward, and actual-DTE tests. Targeted suite: 10/10 pass. Full discovered suite: 32/33 pass; unrelated pre-existing PMCC fixture assertion failed (`test_assemble_pmcc_desk_live_yaml`, upside −0.5 expected >0).
- Ran one applied free-catalog pop36 at `2026-07-12T01:19:01Z`: nine SHIP, including five defined-risk rows chosen for B3+B4; single-leg SHIPs remain toys.
- Ran dated B3+B4 on five new/updated defined-risk SHIPs plus `b195f5fe`.
- Re-ran exact quote coverage: requirements are now Friday expirations; 248 required legs / 0 matched from 70 observations, so calibration remains `REJECT_INSUFFICIENT_COVERAGE`.

## QUALITY BAR

Prior reference bar: `b195f5fe` max loss $76.32 / window max DD $74.85. No row reached L1.

| hyp | structure | full n / pnl | max loss | window DD | B3 | 5% slip n / pnl | judgment |
|---|---|---:|---:|---:|---|---:|---|
| `6dbb5162` NFLX | bear put debit | 108 / −$602.22 | $139.60 | $701.20 | fail | 98 / −$4,976.45 | reject |
| `f6e1898c` TSLA | iron butterfly | 88 / +$645.28 | $46.87 | $50.99 | hold | 221 / −$81,285.46 | cost reject despite competitive ml/dd |
| `225aa1a6` XOM | butterfly | 86 / +$27.08 NULL | $49.35 | $217.59 | hold | 503 / −$29,593.55 | reject |
| `307c7de5` NFLX | calendar | 158 / +$908.58 | $137.37 | $252.31 | hold | 132 / −$1,261.38 | reject |
| `ee74daa9` PLTR | bear put debit | 118 / −$1,525.93 | $148.37 | $1,062.19 | fail | 251 / −$33,462.54 | reject |
| `b195f5fe` TSLL | PCS | 62 / +$42.54 | $75.35 | $88.39 | hold | 13 / −$13.18 NULL | remove from capital path: DD worsened vs prior bar and after-cost PnL remains negative |

`l1_hyp_ids=[]`. The former relative leader is no longer a capital-path candidate after the realism change. This is a falsification result, not a readiness advance.

## EVIDENCE

- `.cache/platform/research_reports/2026-07-12_run33.md`
- `.cache/platform/evolve_audit.jsonl` (`2026-07-12T01:19:01+00:00`)
- `.cache/platform/stress_regime_lab_2026-07-11T1815.json`
- `.cache/platform/stress_cost_lab_2026-07-11T1815.json`
- `.cache/platform/quality_bar_lab_2026-07-11T1815.json`
- `.cache/platform/observed_quote_coverage_lab_2026-07-11T1815.json`
- `trader_platform/research/pcs_sim.py`
- `tests/test_pcs_expiry_grid.py`

## DURABLE

PCS/CCS/IC no longer invent arbitrary weekday expirations: simulations price and record Friday weekly expirations using actual calendar DTE. Coverage doctrine and its generator now distinguish this abstraction from actual symbol/date available-expiry and strike grids. Readiness stays BUILD/L0 and the capital path is empty rather than preserving a stale leader label.

## CLOSE

Progress type: P1+P3
Progress score: 4/5
Honesty: L0
GATES: none

NEXT SEED: Add an injectable actual available-expiration and strike-grid boundary to `pcs_sim` (fixture-backed, fail closed when unavailable), then rerun one defined-risk PCS/CCS/IC discovery and exact B3+B4; reject any row that does not produce positive after-cost PnL with competitive ml/dd. No live/shadow/agentic.

MOA_EXEC_DONE

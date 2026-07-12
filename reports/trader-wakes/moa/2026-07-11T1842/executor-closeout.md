# MOA BUILD lab executor closeout — 2026-07-11T1842

WAKE: 2026-07-11T1842 PDT
PHASE: BUILD
SLEEVE: 3000
EXECUTOR: GPT 5.6 Sol
MODE: paper/research only
AXIS: E / P1 observed-grid realism, then P3 falsify

## Choice

Took the prior NEXT seed because archive-to-provider wiring was the highest-leverage realism gap. Research run33 was minutes old and was reused. Built the provider/replay first, then ran exactly one required free pop36 and one dated B3+B4 batch.

## Built

- `trader_platform/research/contract_grid_provider.py`
  - Converts normalized observed quote rows into market-date-specific expiry/right/strike grids compatible with `pcs_sim.ContractGridProvider`.
  - Uses America/New_York market dates, rejects synthetic rows, excludes expired contracts, and returns `None` when a symbol/date is absent.
  - Exposes requests, covered requests, missing symbol/date requests, selected observations, and coverage ratio.
- `scripts/contract_grid_replay.py`
  - Replays normalized archives and verifies a covered date plus a missing-date fail-close.
- `tests/test_contract_grid_provider.py`
  - Covers timezone date mapping, exact grid contents, counters, missing-date fail-close, and synthetic-row exclusion.

## Verification

- Targeted provider/observation/expiry suite: 15/15 pass, including required-mode `run_pcs_backtest` integration.
- Full unittest discovery: 39/40 pass; only the pre-existing unrelated PMCC fixture assertion fails (`upside=-0.5`).
- TSLL snapshot replay: 70 rows, one expiration, both rights, 70 strikes on market date 2026-07-11; 2026-07-10 returns no grid; decision `PASS_COVERED_DATE_FAILS_CLOSED_MISSING_DATE`.
- Evidence: `.cache/platform/contract_grid_replay_lab_2026-07-11T1842.json`.

## Discovery loop

- Reused fresh multi-symbol research run33: TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ; no duplicate rank run.
- Evolve audit tick `2026-07-12T01:45:41+00:00`, pop36, symbols TSLL/SMCI/PLTR/NFLX/BAC/XOM/MU/TSLA.
- New defined-risk SHIPs falsified: MU bull-call debit `c060d31e`, NFLX calendar `95ca0370`, MU butterfly `dea7f80f`, plus former reference TSLL PCS `b195f5fe`.
- Single-leg SHIPs remain collateral/undefined-risk research toys and received no capital-path judgment.

## B3 + B4 quality table

Historical comparison bar: b195f5fe pre-listed-expiry max loss $76.32 / window DD $74.85. It is not a living leader.

| hyp | structure | full | max loss | window max DD | dense-neg | B3 | 5% slip | L1 |
|---|---|---:|---:|---:|---:|---|---:|---|
| c060d31e | MU bull-call debit | n117 / +$2,467.08 SHIP | $232.71 | $457.45 | 6 | soft hold | n230 / −$20,967.88 REJECT | no |
| 95ca0370 | NFLX calendar | n147 / +$1,342.79 SHIP | $148.18 | $218.10 | 8 | soft hold | n131 / −$1,494.01 REJECT | no |
| dea7f80f | MU butterfly | n93 / −$17.32 NULL | $19.10 | $74.27 | 7 | soft hold | n626 / −$45,879.62 REJECT | no |
| b195f5fe | TSLL PCS former ref | n62 / +$42.54 SHIP | $75.35 | $88.39 | 5 | soft hold | n13 / −$13.18 NULL | no |

Judgment: `REJECT_ALL_CAPITAL_PATH`; `l1_hyp_ids=[]`. All three new defined-risk rows fail non-vacuous after-cost quality. The butterfly meets the historical proxy ml/DD numbers but is baseline NULL and cost-catastrophic. The former reference remains negative after cost and above its historical DD bar.

## Evidence

- `.cache/platform/contract_grid_replay_lab_2026-07-11T1842.json`
- `.cache/platform/stress_regime_lab_2026-07-11T1842.json`
- `.cache/platform/stress_cost_lab_2026-07-11T1842.json`
- `.cache/platform/quality_bar_lab_2026-07-11T1842.json`
- `.cache/platform/evolve_audit.jsonl`
- `reports/readiness/income-coverage-LATEST.md`

## Durable / honesty

- Progress type: P1 + P3
- Score: 4/5
- Honesty: L0 BUILD
- Readiness: unchanged; no L1 DNA and no capital path.
- No live, broker, arm, shadow promotion, or real-account readiness claim.

## NEXT SEED (one)

Add append-safe RTH capture of all available expirations into the normalized archive and accumulate at least three distinct market dates before rerunning any provider-backed historical entry simulation; do not evolve proxy DNA while date coverage remains one.

MOA_EXEC_DONE

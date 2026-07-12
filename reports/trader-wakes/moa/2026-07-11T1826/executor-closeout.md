# MOA BUILD lab executor closeout — 2026-07-11T1826

WAKE: 2026-07-11T1826 PDT
PHASE: BUILD
SLEEVE: 3000
EXECUTOR: GPT 5.6 Sol
MODE: paper/research only
AXIS: E / P1 sim realism, then P3 falsify

## Choice

Took the prior NEXT seed because actual available expiry/strike selection was the highest-leverage realism gap. Research run33 was minutes old, so it was reused rather than rerunning a stale-equivalent rank. One free pop36 evolve followed the scaffold; no second evolve was run.

## Built

- `trader_platform/research/pcs_sim.py`
  - Added injectable `ContractGridProvider(symbol, entry_date)` for PCS/CCS/IC.
  - Required mode selects the earliest supplied expiration at/after target DTE and only supplied right-specific strikes.
  - Missing provider coverage, option right, expiration, or valid long wing returns no entry: fail closed.
  - Sim metrics label `synthetic`, `injected_optional`, or `required_observed`; default discovery remains synthetic and is not relabeled as observed.
- `tests/test_pcs_expiry_grid.py`
  - Actual non-Friday supplied expiration/strike selection.
  - Missing-grid and missing-right/wing rejection.
  - End-to-end required-provider zero-coverage fail-close.
- Updated BUILD/coverage doctrine and the generated coverage gap source.

## Verification

- Targeted related suite: 16/16 pass.
- Full unittest discovery: 36/37 pass; only the pre-existing unrelated `test_pmcc_desk.AssemblePmccDeskIntegrationTest.test_assemble_pmcc_desk_live_yaml` fixture assertion fails (`upside=-0.5`).
- `git diff --check` is blocked by pre-existing trailing whitespace in unrelated modified docs; the scoped code diff itself is clean.

## Discovery loop

- Reused fresh research run33 from the 1815 wake.
- Evolve audit: `.cache/platform/evolve_audit.jsonl`, tick `2026-07-12T01:33:36+00:00`, pop36, symbols TSLL/SMCI/PLTR/NFLX/BAC/XOM/MU/TSLA.
- SHIP rows: SMCI calendar, NFLX calendar, NFLX CSP, BAC wheel, TSLA butterfly.
- NFLX CSP and BAC wheel are single-leg/collateral research toys for the $3k sleeve; they were not treated as capital candidates.
- New defined-risk SHIPs falsified: `hyp_dna_smci_calendar_spread_b11a8ff0`, `hyp_dna_nflx_calendar_spread_307c7de5`, `hyp_dna_tsla_butterfly_spread_d13ef44d`, plus former reference `hyp_dna_tsll_put_credit_spread_b195f5fe`.

## B3 + B4 quality table

Historical comparison bar remains b195f5fe pre-listed-expiry max loss $76.32 / window DD $74.85, but it is no longer a living leader.

| hyp | structure | full | max loss | window max DD | dense-neg | B3 | 5% slip | cost | L1 |
|---|---|---:|---:|---:|---:|---|---:|---|---|
| b11a8ff0 | SMCI calendar | n145 / +$1,077.14 | $189.00 | $308.74 | 3 | soft hold | n122 / −$1,401.20 REJECT | fail | no |
| 307c7de5 | NFLX calendar | n158 / +$908.58 | $137.37 | $252.31 | 5 | soft hold | n132 / −$1,261.38 REJECT | fail | no |
| d13ef44d | TSLA butterfly | n87 / +$85.33 | $21.25 | $36.01 | 5 | soft hold | n529 / −$94,077.49 REJECT | fail | no |
| b195f5fe | TSLL PCS former ref | n62 / +$42.54 | $75.35 | $88.39 | 5 | soft hold | n13 / −$13.18 NULL | soft only, not edge | no |

Judgment: `REJECT_ALL_CAPITAL_PATH`. TSLA butterfly is competitive on proxy max-loss/DD but fails dense after-cost catastrophically. Calendars fail B4 and ml/DD. b195f5fe remains thin/negative after cost and misses its historical DD bar. `l1_hyp_ids=[]`.

## Evidence

- `.cache/platform/stress_regime_lab_2026-07-11T1826.json`
- `.cache/platform/stress_cost_lab_2026-07-11T1826.json`
- `.cache/platform/quality_bar_lab_2026-07-11T1826.json`
- `.cache/platform/evolve_audit.jsonl`
- `reports/readiness/income-coverage-LATEST.md`

## Durable / honesty

- Progress type: P1 + P3
- Score: 4/5
- Honesty: L0 BUILD
- Readiness: unchanged; no L1 DNA and no capital path.
- No live, broker, arm, shadow promotion, or real-account readiness claim.

## NEXT SEED (one)

Wire normalized archived option-quote rows into a date-aware `ContractGridProvider`, add provider coverage counters, and run one fail-closed replay smoke against the existing TSLL snapshot; do not evolve again unless the provider has historical entry-date coverage.

MOA_EXEC_DONE

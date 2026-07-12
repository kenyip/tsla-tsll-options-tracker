# MoA BUILD Lab executor closeout — 2026-07-10T2017

WAKE: 2026-07-10T2017 local / evening executor
PHASE: BUILD
SLEEVE: 3000
SLOT: evening
ROLE: GPT 5.6 Sol executor / only writer; Grok challenge follows separately
CHOSE: B — close the defined-risk time-bias gap with a DTE × profit-target × DTE-stop grid, while running exactly one free-catalog discovery loop

## DID

- Oriented from BUILD lab doctrine, income coverage, latest wake, and readiness. The prior wake explicitly deferred time bias.
- Ran `just research-tick-paper --sleeve-usd 3000`: run16 scored 23/23 symbols with no errors. Current report leaders include SMCI, MU, TSLA, PLTR, AAPL, AMD, TSLL, ARM.
- Ran one `just evolve-tick --apply --top-symbols 8 --mutants 2 --max-population 36 --sleeve-usd 3000`: 36 real sims over eight symbols and ten structures. It produced three SHIPs, all TSLL single-leg wheel/CSP shapes; per doctrine they remain research toys and were not sent to the defined-risk capital path. No PCS/CCS/IC SHIP emerged.
- Added and smoked `scripts/pcs_time_bias_grid.py`, then ran a 36-cell 5y grid on the registered TSLL PCS leader. Axes were entry DTE 7/14/21/30, profit target 35%/50%/65%, and DTE stop 1/3/5; observed hold time and exit reasons are included.
- Falsified the registered leader with the required dated B3 and B4 commands. Also ran the same B3/B4 functions on the best transient time-grid row (7 DTE / 35% target / 5 DTE stop) without registering or promoting it.
- Updated income-coverage doctrine/tooling to mark DTE/profit-target/DTE-stop as built and retain weekday/session entry slicing as the precise remaining time gap.

## QUALITY BAR

| research shape | structure | 1-lot max_loss_usd | max_lots | full 5y | window max_dd | regime_hold | cost_hold | 5% slip reality | judgment |
|---|---|---:|---:|---|---:|---|---|---|---|
| `hyp_dna_tsll_put_credit_spread_b195f5fe` | PCS, 21 DTE / 50% / stop 3 | 76.32 | 3 | SHIP, n=57, +115.90 | 74.85 | true | true (soft) | n=13, NULL, -18.32 | Registered relative leader; B6 target unchanged |
| `time_variant_tsll_pcs_dte7_pt35_stop5` | PCS, 7 DTE / 35% / stop 5 | 75.80 | 3 | SHIP, n=37, +158.71 | 48.33 | true | true (vacuous) | n=0, NULL, 0.00 | Promising time challenger, but adverse cost removes every entry; not registered or promoted |
| evolve SHIPs: TSLL wheel/CSP | single-leg | not emitted in evolve audit | — | SHIP in 2y sim | 106.56–195.44 full-sim DD | not run | not run | not tested | Levered-name single-leg research toys; no capital-path claim |

The 7-DTE row improves full-history pnl and ml/dd versus the leader, but its 5% slip “hold” is only zero trades. That is not durable after-cost income and does not beat the leader’s evidence quality. Capital path and phase remain unchanged.

## EVIDENCE

- `.cache/platform/research_reports/2026-07-11_run16.md`
- `.cache/platform/evolve_audit.jsonl` (`ts=2026-07-11T03:17:52+00:00`, population=36)
- `.cache/platform/time_bias_lab_2026-07-10T2017.json`
- `.cache/platform/time_bias_challenger_stress_2026-07-10T2017.json`
- `.cache/platform/stress_regime_lab_2026-07-10T2017.json`
- `.cache/platform/stress_cost_lab_2026-07-10T2017.json`
- `scripts/pcs_time_bias_grid.py`

## DURABLE

- A reusable registered-hypothesis time grid now records DTE, profit target, DTE stop, realized average hold, exits, ml, max_lots, and sleeve fit using the real defined-risk simulator.
- `docs/INCOME_STRATEGY_COVERAGE.md` and `scripts/trader_income_coverage.py` now describe the narrower remaining time gap honestly: entry weekday/session slicing.
- No hypothesis status, shadow/live state, broker state, or agentic arm changed.

## NEXT SEED

Next BUILD time-axis wake: add an entry-weekday filter to the defined-risk simulator and time-grid scaffold, then run one weekday-sliced out-of-sample check of `time_variant_tsll_pcs_dte7_pt35_stop5`; require non-zero trades under 5% slip or reject the variant.

GATES: none (paper/research only)

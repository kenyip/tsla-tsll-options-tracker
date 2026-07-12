# Income strategy coverage — 2026-07-10T2008

Source: `scripts/trader_income_coverage.py` · doctrine: `docs/INCOME_STRATEGY_COVERAGE.md`

- Catalog structures: **11**
- Hypotheses: **84** ({'paper': 1, 'testing': 14, 'candidate': 69})
- Evolve sim artifacts: **17** under `.cache/platform/evolve_backtests/`
- Quality leader hint: `hyp_dna_tsll_put_credit_spread_b195f5fe (until beaten on ml/dd+B3/B4)`

## Catalog × registry

| structure | engine | side_policy | n_hyps | statuses |
|---|---|---|---:|---|
| `call_credit_spread` | pcs_sim | prefer_call | 3 | {'candidate': 3} |
| `cash_secured_put` | single_leg | prefer_put | 7 | {'candidate': 7} |
| `iron_condor` | pcs_sim | range_bound | 4 | {'candidate': 4} |
| `long_dte_conservative` | single_leg | regime_directed | 2 | {'candidate': 2} |
| `put_credit_spread` | pcs_sim | prefer_put | 8 | {'testing': 3, 'candidate': 5} |
| `regime_short_premium` | single_leg | regime_directed | 6 | {'testing': 1, 'candidate': 5} |
| `roll_defend` | single_leg | regime_directed | 6 | {'testing': 1, 'candidate': 5} |
| `short_call_credit` | single_leg | prefer_call | 3 | {'candidate': 3} |
| `short_dte_aggressive` | single_leg | regime_directed | 6 | {'testing': 2, 'candidate': 4} |
| `short_put_credit` | single_leg | prefer_put | 11 | {'candidate': 10, 'testing': 1} |
| `wheel_assignment` | single_leg | prefer_put | 19 | {'candidate': 17, 'testing': 2} |

## Gaps (BUILD targets)

- calendar_spread (time advantage) — no sim
- diagonal_spread / PMCC-lite sleeve-fit — no sim
- butterfly / iron_butterfly — no sim
- debit_vertical (bull call / bear put) — no sim
- explicit time-bucket scoreboard (weekday/session × DTE) — partial knobs only
- direction-bias scoreboard by regime window — partial (B3 exists per hyp)

## BUILD lab recipe

1. Dual MoA: `just trader-build-lab`
2. Rotate under-covered structures / time / direction axes
3. Falsify new SHIP with B3+B4 + ml/dd quality bar
4. RTH: wait for filters → paper open/close only

Paper/research only. No live.

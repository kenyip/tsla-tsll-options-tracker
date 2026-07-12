# Income strategy coverage — 2026-07-10T1938

Source: `scripts/trader_income_coverage.py` · doctrine: `docs/INCOME_STRATEGY_COVERAGE.md`

- Catalog structures: **11**
- Hypotheses: **52** ({'paper': 1, 'testing': 14, 'candidate': 37})
- Evolve sim artifacts: **16** under `.cache/platform/evolve_backtests/`
- Quality leader hint: `hyp_dna_tsll_put_credit_spread_b195f5fe (until beaten on ml/dd+B3/B4)`

## Catalog × registry

| structure | engine | side_policy | n_hyps | statuses |
|---|---|---|---:|---|
| `call_credit_spread` | pcs_sim | prefer_call | 2 | {'candidate': 2} |
| `cash_secured_put` | single_leg | prefer_put | 3 | {'candidate': 3} |
| `iron_condor` | pcs_sim | range_bound | 3 | {'candidate': 3} |
| `long_dte_conservative` | single_leg | regime_directed | 0 | — |
| `put_credit_spread` | pcs_sim | prefer_put | 6 | {'testing': 3, 'candidate': 3} |
| `regime_short_premium` | single_leg | regime_directed | 2 | {'testing': 1, 'candidate': 1} |
| `roll_defend` | single_leg | regime_directed | 2 | {'testing': 1, 'candidate': 1} |
| `short_call_credit` | single_leg | prefer_call | 0 | — |
| `short_dte_aggressive` | single_leg | regime_directed | 3 | {'testing': 2, 'candidate': 1} |
| `short_put_credit` | single_leg | prefer_put | 11 | {'candidate': 10, 'testing': 1} |
| `wheel_assignment` | single_leg | prefer_put | 11 | {'candidate': 9, 'testing': 2} |

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

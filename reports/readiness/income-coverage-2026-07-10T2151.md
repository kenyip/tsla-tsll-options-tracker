# Income strategy coverage — 2026-07-10T2151

Source: `scripts/trader_income_coverage.py` · doctrine: `docs/INCOME_STRATEGY_COVERAGE.md`

- Catalog structures: **12**
- Hypotheses: **129** ({'paper': 1, 'testing': 14, 'candidate': 114})
- Evolve sim artifacts: **21** under `.cache/platform/evolve_backtests/`
- Quality leader hint: `hyp_dna_tsll_put_credit_spread_b195f5fe (until beaten on ml/dd+B3/B4)`

## Catalog × registry

| structure | engine | side_policy | n_hyps | statuses |
|---|---|---|---:|---|
| `calendar_spread` | calendar_sim | time_decay_neutral_to_bullish | 4 | {'candidate': 4} |
| `call_credit_spread` | pcs_sim | prefer_call | 4 | {'candidate': 4} |
| `cash_secured_put` | single_leg | prefer_put | 13 | {'candidate': 13} |
| `iron_condor` | pcs_sim | range_bound | 5 | {'candidate': 5} |
| `long_dte_conservative` | single_leg | regime_directed | 3 | {'candidate': 3} |
| `put_credit_spread` | pcs_sim | prefer_put | 12 | {'testing': 3, 'candidate': 9} |
| `regime_short_premium` | single_leg | regime_directed | 13 | {'testing': 1, 'candidate': 12} |
| `roll_defend` | single_leg | regime_directed | 13 | {'testing': 1, 'candidate': 12} |
| `short_call_credit` | single_leg | prefer_call | 9 | {'candidate': 9} |
| `short_dte_aggressive` | single_leg | regime_directed | 8 | {'testing': 2, 'candidate': 6} |
| `short_put_credit` | single_leg | prefer_put | 11 | {'candidate': 10, 'testing': 1} |
| `wheel_assignment` | single_leg | prefer_put | 25 | {'candidate': 23, 'testing': 2} |

## Gaps (BUILD targets)

- calendar_spread — explicit front/back IV + put-skew assumptions and chronological OOS built; observed historical option-surface inputs missing
- diagonal_spread / PMCC-lite sleeve-fit — no sim
- butterfly / iron_butterfly — no sim
- debit_vertical (bull call / bear put) — no sim
- time-bucket scoreboard — DTE/profit-target/DTE-stop grid built; weekday/session slices missing
- direction-bias scoreboard by regime window — partial (B3 exists per hyp)

## BUILD lab recipe

1. Dual MoA: `just trader-build-lab`
2. Rotate under-covered structures / time / direction axes
3. Falsify new SHIP with B3+B4 + ml/dd quality bar
4. RTH: wait for filters → paper open/close only

Paper/research only. No live.

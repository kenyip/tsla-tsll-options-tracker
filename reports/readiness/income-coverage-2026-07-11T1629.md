# Income strategy coverage — 2026-07-11T1629

Source: `scripts/trader_income_coverage.py` · doctrine: `docs/INCOME_STRATEGY_COVERAGE.md`

- Catalog structures: **16**
- Hypotheses: **176** ({'paper': 1, 'testing': 14, 'candidate': 161})
- Evolve sim artifacts: **43** under `.cache/platform/evolve_backtests/`
- Quality leader hint: `hyp_dna_tsll_put_credit_spread_b195f5fe (until beaten on ml/dd+B3/B4)`

## Catalog × registry

| structure | engine | side_policy | n_hyps | statuses |
|---|---|---|---:|---|
| `bear_put_debit_spread` | debit_vertical_sim | bearish_not_bullish | 3 | {'candidate': 3} |
| `bull_call_debit_spread` | debit_vertical_sim | bullish_not_bearish | 7 | {'candidate': 7} |
| `butterfly_spread` | butterfly_sim | neutral_to_bullish_pin | 9 | {'candidate': 9} |
| `calendar_spread` | calendar_sim | time_decay_neutral_to_bullish | 9 | {'candidate': 9} |
| `call_credit_spread` | pcs_sim | prefer_call | 4 | {'candidate': 4} |
| `cash_secured_put` | single_leg | prefer_put | 14 | {'candidate': 14} |
| `diagonal_spread` | diagonal_sim | bullish_time_decay | 5 | {'candidate': 5} |
| `iron_condor` | pcs_sim | range_bound | 5 | {'candidate': 5} |
| `long_dte_conservative` | single_leg | regime_directed | 3 | {'candidate': 3} |
| `put_credit_spread` | pcs_sim | prefer_put | 17 | {'testing': 3, 'candidate': 14} |
| `regime_short_premium` | single_leg | regime_directed | 13 | {'testing': 1, 'candidate': 12} |
| `roll_defend` | single_leg | regime_directed | 14 | {'testing': 1, 'candidate': 13} |
| `short_call_credit` | single_leg | prefer_call | 11 | {'candidate': 11} |
| `short_dte_aggressive` | single_leg | regime_directed | 11 | {'testing': 2, 'candidate': 9} |
| `short_put_credit` | single_leg | prefer_put | 13 | {'candidate': 12, 'testing': 1} |
| `wheel_assignment` | single_leg | prefer_put | 29 | {'candidate': 27, 'testing': 2} |

## Gaps (BUILD targets)

- calendar_spread — explicit front/back IV + put-skew assumptions and chronological OOS built; observed historical option-surface inputs missing
- diagonal_spread — BS defined-debit scaffold + B3/B4 + exact-DNA OOS/density built; observed option surfaces and assignment realism missing
- butterfly_spread — long call butterfly BS scaffold + B3/B4 dispatch built; pin/assignment and observed option surfaces missing; iron_butterfly still absent
- debit_vertical — bull-call and bear-put BS defined-debit scaffold + evolve/B3/B4 built; observed option surfaces, dividends, and assignment missing
- time-bucket scoreboard — multi-hyp DTE/profit-target/DTE-stop + entry-weekday/cost grid and exact transient B3+B4 built; session-time slices missing
- direction-bias scoreboard — shared yearly/canonical window + 5% cost comparator built; expand representative DNA and observed-data realism

## BUILD lab recipe

1. Dual MoA: `just trader-build-lab`
2. Rotate under-covered structures / time / direction axes
3. Falsify new SHIP with B3+B4 + ml/dd quality bar
4. RTH: wait for filters → paper open/close only

Paper/research only. No live.

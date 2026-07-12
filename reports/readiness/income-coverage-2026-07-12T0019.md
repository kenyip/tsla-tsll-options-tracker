# Income strategy coverage — 2026-07-12T0019

Source: `scripts/trader_income_coverage.py` · doctrine: `docs/INCOME_STRATEGY_COVERAGE.md`

- Catalog structures: **19**
- Hypotheses: **234** ({'paper': 1, 'testing': 14, 'candidate': 219})
- Evolve sim artifacts: **63** under `.cache/platform/evolve_backtests/`
- Quality leader hint: `none; former reference hyp_dna_tsll_put_credit_spread_b195f5fe failed listed-expiry restress quality bar`

## Catalog × registry

| structure | engine | side_policy | n_hyps | statuses |
|---|---|---|---:|---|
| `bear_put_debit_spread` | debit_vertical_sim | bearish_not_bullish | 5 | {'candidate': 5} |
| `broken_wing_iron_butterfly` | iron_butterfly_sim | bullish_not_bearish_credit | 5 | {'candidate': 5} |
| `bull_call_debit_spread` | debit_vertical_sim | bullish_not_bearish | 9 | {'candidate': 9} |
| `butterfly_spread` | butterfly_sim | neutral_to_bullish_pin | 15 | {'candidate': 15} |
| `calendar_spread` | calendar_sim | time_decay_neutral_to_bullish | 17 | {'candidate': 17} |
| `call_credit_spread` | pcs_sim | prefer_call | 6 | {'candidate': 6} |
| `cash_secured_put` | single_leg | prefer_put | 18 | {'candidate': 18} |
| `diagonal_spread` | diagonal_sim | bullish_time_decay | 7 | {'candidate': 7} |
| `iron_butterfly` | iron_butterfly_sim | neutral_pin_credit | 7 | {'candidate': 7} |
| `iron_condor` | pcs_sim | range_bound | 5 | {'candidate': 5} |
| `long_dte_conservative` | single_leg | regime_directed | 5 | {'candidate': 5} |
| `put_credit_spread` | pcs_sim | prefer_put | 18 | {'testing': 3, 'candidate': 15} |
| `put_ratio_backspread` | put_ratio_backspread_sim | bearish_convexity | 8 | {'candidate': 8} |
| `regime_short_premium` | single_leg | regime_directed | 14 | {'testing': 1, 'candidate': 13} |
| `roll_defend` | single_leg | regime_directed | 15 | {'testing': 1, 'candidate': 14} |
| `short_call_credit` | single_leg | prefer_call | 11 | {'candidate': 11} |
| `short_dte_aggressive` | single_leg | regime_directed | 14 | {'testing': 2, 'candidate': 12} |
| `short_put_credit` | single_leg | prefer_put | 16 | {'candidate': 15, 'testing': 1} |
| `wheel_assignment` | single_leg | prefer_put | 30 | {'candidate': 28, 'testing': 2} |

## Gaps (BUILD targets)

- calendar_spread — explicit front/back IV + put-skew assumptions and chronological OOS built; observed historical option-surface inputs missing
- diagonal_spread — BS defined-debit scaffold + B3/B4 + exact-DNA OOS/density built; observed option surfaces and assignment realism missing
- convex/ratio family — long call, symmetric/broken-wing credit iron butterflies, and a 1x2 put ratio backspread have B3/B4/fixed-cost dispatch; ratio cost survivors still fail absolute DD/risk gates, and observed surfaces/assignment remain missing
- debit_vertical — bull-call and bear-put BS defined-debit scaffold + evolve/B3/B4 built; observed option surfaces, dividends, and assignment missing
- time-bucket scoreboard — multi-hyp DTE/profit-target/DTE-stop + entry-weekday/cost grid and exact transient B3+B4 built; session-time slices missing
- direction-bias lab — shared-window scoreboard + no-lookahead shared-position PCS/CCS/IC router with standalone controls and selected/accepted/counterfactual-reject funnel built; eight-symbol default DNA selects CCS/IC broadly but credit-floor rejects >99%, while the family remains cost-vacuous/DD-rejected, so leave it rather than retune and retain the observed-data realism boundary
- cost realism — exact PCS/CCS/IC leg/time join + reject gate, Friday abstraction, archive-backed date-aware expiry/strike-grid provider, and all-expiration atomic append capture built; density gate fails closed below three market dates, and the current archive still covers only one, so provider-backed historical simulation and observed-cost calibration remain blocked

## BUILD lab recipe

1. Dual MoA: `just trader-build-lab`
2. Rotate under-covered structures / time / direction axes
3. Falsify new SHIP with B3+B4 + ml/dd quality bar
4. RTH: wait for filters → paper open/close only

Paper/research only. No live.

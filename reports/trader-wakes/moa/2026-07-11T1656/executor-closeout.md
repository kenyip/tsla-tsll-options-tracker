# MOA BUILD lab executor closeout — 2026-07-11T1656 (evening)

WAKE: 2026-07-11T1656 PDT
PHASE: BUILD
SLEEVE: 3000
EXECUTOR: GPT 5.6 Sol
MODE: paper/research only

## CHOSE

Axis E / P1+P3 — complete the uniform fixed-dollar per-leg half-spread model across the remaining defined-risk proxy sims, then exact-falsify TSLL calendar `fcc76896` and the new applied-population SHIPs. This superseded another catalog search because the prior NEXT seed identified a concrete cross-simulator realism gap.

## DID

- Ran multi-symbol research run30: 23/23 scored; top eight TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Naked short fit at $3k remained TSLL/SMCI only; defined-risk research remained open across names.
- Ran exactly one applied free-catalog population of 36 at 8 symbols × 2 mutants. It produced six newly created and two updated SHIPs, including PLTR/NFLX/XOM calendars, TSLA/MU butterflies, and a TSLL bull-call debit vertical; single-leg SHIPs remain research toys.
- Added adverse `half_spread_per_leg` pricing at entry and exit to calendar, diagonal, long butterfly, and debit-vertical sims. Extended `scripts/defined_risk_fixed_cost_stress.py` to dispatch every defined-risk proxy class and report structure-appropriate round-trip cost.
- Added synthetic regression coverage for all four newly supported proxy engines. Fifteen relevant unit tests pass; platform smoke passes. Full discovery ran 25 tests with one unrelated PMCC desk fixture failure (`test_assemble_pmcc_desk_live_yaml`: upside −0.5 expected >0), outside this BUILD-lab change.
- Ran dated B3+B4 on six new defined-risk SHIPs. All B3 soft-held, but all six failed 5% B4; no SHIP advanced.
- Ran exact fixed-dollar stress on `fcc76896` plus the six new defined-risk SHIPs. `fcc76896` remained dense and positive at $0.01 per leg (n116 / +$298.28; max loss $66.97) but fixed-cost DD rose to $115.81, above the leader bar $74.85. PLTR/NFLX/XOM calendars also remained positive at $0.01 but missed max-loss/DD quality; TSLA/MU butterflies and TSLL debit vertical were negative.

## QUALITY BAR

Leader remains `hyp_dna_tsll_put_credit_spread_b195f5fe`: max loss $76.32; regime-window max DD $74.85; B3 soft-hold; 5% slip n13 / −$18.32; fixed $0.01 per leg n33 / −$63.01. It is a relative quality example, not L1.

| hyp | structure | B3 hold | fixed-$ n / PnL | fixed-$ DD | max loss | L1 judgment |
|---|---|---:|---:|---:|---:|---|
| `fcc76896` | TSLL calendar | yes | 116 / +$298.28 | $115.81 | $66.97 | reject: DD misses leader; 5% remains negative |
| `a59a3227` | PLTR calendar | yes | 141 / +$855.94 | $581.58 | $290.26 | reject: ml/DD |
| `307c7de5` | NFLX calendar | yes | 146 / +$254.74 | $441.12 | $144.60 | reject: ml/DD |
| `6e945d54` | XOM calendar | yes | 153 / +$1,167.99 | $328.90 | $155.05 | reject: ml/DD |
| `88a044b8` | TSLA butterfly | yes | 190 / −$1,307.72 | $1,324.38 | $24.26 | reject: fixed cost |
| `372d1c2b` | MU butterfly | yes | 249 / −$1,912.38 | $1,900.92 | $24.16 | reject: fixed cost |
| `75556a20` | TSLL bull-call debit | yes | 65 / −$85.85 | $307.59 | $80.89 | reject: fixed cost + ml/DD |

`l1_hyp_ids=[]`. Positive fixed-$ PnL alone is insufficient when drawdown/max-loss misses the quality bar, and percentage-slip B4 remains a separate adverse sensitivity.

## EVIDENCE

- `.cache/platform/research_reports/2026-07-11_run30.md`
- `.cache/platform/evolve_audit.jsonl` (`2026-07-11T23:56:43+00:00`)
- `.cache/platform/fixed_leg_cost_proxy_lab_2026-07-11T1656.json`
- `.cache/platform/stress_regime_lab_2026-07-11T1656.json`
- `.cache/platform/stress_cost_lab_2026-07-11T1656.json`
- `.cache/platform/quality_bar_lab_2026-07-11T1656.json`
- `tests/test_defined_risk_fixed_cost.py`
- `reports/readiness/income-coverage-LATEST.md`

## DURABLE

- Fixed-dollar per-leg cost sensitivity now covers PCS/CCS/IC/iron butterfly/calendar/diagonal/long butterfly/debit vertical under one runner.
- Coverage docs and generator no longer list proxy fixed-cost dispatch as missing.
- The closest challenger `fcc76896` is explicitly quality-rejected at $0.01 fixed cost because DD fails the leader bar; do not tune assumed IV to pass.
- Readiness stays BUILD / L0. No live, broker, arm, shadow, or capital-path promotion.

## CLOSE

Progress type: **P1+P3**
Progress score: **4/5** — closed a real simulator-wide realism gap and falsified the resulting candidates, but produced no L1 edge and still lacks observed quotes.
Honesty level: **L0** — BUILD only; `l1_hyp_ids=[]`.

NEXT SEED: One BUILD spike only — inventory a no-paid-data path for historical option bid/ask or spread observations and implement one minimal observed-quote adapter/fixture smoke for calendar/vertical cost validation; if unavailable, record the exact data blocker and stop proxy-cost retuning. No live/shadow/agentic.

GATES: none
MOA_EXEC_DONE

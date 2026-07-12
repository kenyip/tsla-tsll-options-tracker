# MOA BUILD lab executor closeout — 2026-07-11T1629 (evening)

WAKE: 2026-07-11T1629
PHASE: BUILD
SLEEVE: 3000
EXECUTOR: gpt-5.6-sol (openai-codex)
MODE: paper/research only

## CHOSE

Axis E / P1, then P3 — close the defined-risk credit `iron_butterfly` catalog gap with a minimal simulator, synthetic verification, one focused population, and B3/B4 falsification. This superseded another PCS-width loop because the prior seed explicitly closed that path and coverage still lacked the credit butterfly class.

## DID

- Added `iron_butterfly` Strategy DNA: ATM short put+call body, symmetric long put/call wings, neutral-regime gate, defined `max_loss=(width-credit)*100`, 1-lot sleeve fields.
- Added `trader_platform/research/iron_butterfly_sim.py` and wired evolve, B3 regime stress, B4 cost stress, catalog coverage, and platform synthetic smoke.
- TDD evidence: new two-test unit module passed; platform smoke passed.
- Refreshed multi-symbol research: run28 scored 22/23. Top eight were TSLL, SMCI, PLTR, AAPL, AMD, ARM, QQQ, META. TSLA failed with `No columns to parse from file`; no metric was invented.
- Ran one focused applied population: pop36 over top research names, `--structures iron_butterfly --top-symbols 8 --mutants 2 --max-population 36`. No 2y iron-butterfly SHIP emerged; top SMCI row was NULL n8/+$104.84 and top TSLL row NEEDS_MORE_DATA n7/+$125.83.
- B3/B4 exact-stressed the relative leader and the top SMCI/TSLL iron-butterfly candidates. No status advanced beyond candidate/testing.

## QUALITY BAR

| hyp | structure | max loss | window max DD | dense-neg | B3 | 5% slip | B4 | L1 |
|---|---|---:|---:|---:|---|---|---|---|
| `b195f5fe` | TSLL PCS | $76.32 | $74.85 | 5 | hold | n13 / −$18.32 NULL | soft hold | no — after-cost edge absent |
| `8444c65b` | SMCI iron butterfly | $130.59 | $230.72 | 5 | hold | n251 / −$29,018.86 REJECT | fail | no |
| `486c4c32` | TSLL iron butterfly | $30.86 | $81.70 | 3 | hold | n180 / −$12,172.17 REJECT | fail | no |

The 5% leg-slip reruns are non-vacuous and alter entry/exit cadence. That is sensitivity evidence, not a claim that observed spreads equal 5% on every leg. Both candidates are rejected from the capital path; `l1_hyp_ids=[]`.

## EVIDENCE

- `.cache/platform/research_reports/2026-07-11_run28.md`
- `.cache/platform/evolve_audit.jsonl` (`2026-07-11T23:34:07+00:00`, pop36)
- `.cache/platform/stress_regime_lab_2026-07-11T1629.json`
- `.cache/platform/stress_cost_lab_2026-07-11T1629.json`
- `.cache/platform/quality_bar_lab_2026-07-11T1629.json`
- `tests/test_iron_butterfly_sim.py`
- `trader_platform/research/iron_butterfly_sim.py`

## DURABLE

- Catalog now has 17 structures and a paper-only credit iron-butterfly simulator with B3/B4 dispatch.
- Coverage docs no longer claim iron butterfly is absent.
- Readiness stays BUILD/L0; no capital-path expansion and no real-account readiness claim.
- Cost-model realism is now the higher-leverage cross-structure gap: percentage-of-gross-leg slip can overwhelm small net spreads and change cadence.

## JUDGMENT

Progress type: P1 + P3
Progress score: 4/5 — a real coverage gap closed and immediately falsified, but no L1 edge.
Honesty: L0 BUILD. No DNA has non-vacuous after-cost SHIP plus B3 and competitive ml/dd.

## NEXT SEED

Next BUILD only: implement a simulator-wide fixed-dollar per-leg half-spread cost axis using conservative option tick values, then compare representative PCS, IC, and iron-butterfly DNA under the same B4 table; reject rather than tune if observed-like costs remain negative.

GATES: none. No live, broker, agentic arm, shadow auto-promotion, or capital action.

MOA_EXEC_DONE

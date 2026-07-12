# MOA BUILD lab executor closeout — 2026-07-11T1644 (evening)

WAKE: 2026-07-11T1644
PHASE: BUILD
SLEEVE: 3000
EXECUTOR: gpt-5.6-sol (openai-codex)
MODE: paper/research only

## CHOSE

Axis E / P1 then P3 — take the prior NEXT seed and build a uniform fixed-dollar per-leg half-spread sensitivity for PCS/CCS/IC/credit iron butterfly, then falsify the representative set and this wake's new defined-risk SHIPs. This supersedes another catalog scaffold because cross-simulator cost realism was the higher-leverage blocker.

## DID

- Research run29: 23/23 symbols scored; top composite TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Only TSLL/SMCI fit naked $3k; defined-risk remains the research path. Evidence: `.cache/platform/research_reports/2026-07-11_run29.md`.
- One applied free-catalog evolve at 8 symbols × 2 mutants, pop36; eight SHIPs created, including defined-risk BAC diagonal `f58e5987`, TSLL calendars `6fc43d55`/`fcc76896`, XOM butterfly `901e56da`, and PLTR PCS `a8299516`. Audit timestamp `2026-07-11T23:45:09Z` in `.cache/platform/evolve_audit.jsonl`.
- Added `half_spread_per_leg` to PCS/CCS/IC and credit iron-butterfly entry/exit pricing. Added `scripts/defined_risk_fixed_cost_stress.py` and `tests/test_defined_risk_fixed_cost.py`.
- Ran dated B3/B4 on the leader plus all five new defined-risk SHIPs. Built the quality table with `l1_hyp_ids=[]`.
- Refreshed coverage: 17 catalog structures, 189 hypotheses, 52 evolve artifacts.

## FIXED-COST EVIDENCE

Uniform sensitivity uses option-price dollars per leg, adverse at entry and exit. It is not observed quote evidence.

| Hyp / structure | $0.00 half-spread | $0.01 half-spread | Judgment |
|---|---:|---:|---|
| TSLL PCS `b195f5fe` | n57 / +$115.90 | n33 / −$63.01 | negative; still relative bar only |
| AMD IC `b3056133` | n121 / +$578.28 | n111 / −$459.62 | reject |
| SMCI iron butterfly `8444c65b` | n59 / +$333.93 | n75 / −$225.66 | reject |
| TSLL iron butterfly `486c4c32` | n24 / +$239.90 | n55 / −$153.17 | reject |

A $0.01 half-spread corresponds to $4 round trip for a two-leg vertical and $8 for a four-leg structure. The representative set is negative before escalating to $0.025/$0.05.

Evidence: `.cache/platform/fixed_leg_cost_lab_2026-07-11T1644.json`.

## QUALITY BAR VS `b195f5fe`

| Hyp | ml | window DD | dense-neg | B3 | 5% cost | L1 |
|---|---:|---:|---:|---|---|---|
| leader TSLL PCS `b195f5fe` | $76.32 | $74.85 | 5 | hold | n13 / −$18.32 | no |
| BAC diagonal `f58e5987` | $291.49 | $351.00 | 6 | hold | n89 / −$1,473.94 REJECT | no |
| TSLL calendar `6fc43d55` | $112.10 | $179.31 | 5 | hold | n97 / −$455.09 | no |
| TSLL calendar `fcc76896` | $67.63 | $48.45 | 1 | hold | n100 / −$80.38 | no |
| XOM butterfly `901e56da` | $46.85 | $121.81 | 8 | hold | n479 / −$28,448.41 REJECT | no |
| PLTR PCS `a8299516` | $197.51 | $425.32 | 2 | hold | n0 / $0 vacuous | no |

`fcc76896` is the only new row competitive on max-loss and window DD, but its dense 100-trade 5% result is negative. Soft `cost_hold=true` is not an after-cost edge. PLTR's n0 result is vacuous. No candidate earns L1 or a capital-path seat.

Evidence:

- `.cache/platform/stress_regime_lab_2026-07-11T1644.json`
- `.cache/platform/stress_cost_lab_2026-07-11T1644.json`
- `.cache/platform/quality_bar_lab_2026-07-11T1644.json`

## VERIFICATION

- `.venv/bin/python -m unittest discover -s tests -p 'test_*sim.py'` → 5 passed.
- `.venv/bin/python -m unittest tests.test_defined_risk_fixed_cost` → 2 passed.
- `.venv/bin/python -m trader_platform.smoke_test` → platform smoke OK.
- `.venv/bin/python scripts/trader_income_coverage.py --write` → coverage LATEST + dated report written.

## JUDGMENT

- Progress type: **P1 + P3**
- Progress score: **4/5**
- Honesty: **L0 BUILD** — fixed-cost realism advanced and a representative set was rejected; no non-vacuous after-cost candidate meets the leader ml/dd bar. No real-account readiness claim.
- Capital path: unchanged. `b195f5fe` remains a relative quality example, not L1.

## DURABLE

Fixed-dollar per-leg cost sensitivity is executable for PCS/CCS/IC/credit iron butterfly, documented, tested, and represented in coverage. The dated JSON separates percentage-slip B4 from fixed-dollar sensitivity. No status was promoted.

## NEXT SEED (one)

Next BUILD only: extend the same fixed-dollar per-leg half-spread axis to calendar/diagonal/butterfly/debit-vertical sims, then exact-stress TSLL calendar `fcc76896` first; reject the proxy family unless it remains non-vacuous positive and preserves its $67.63 max-loss / $48.45 window-DD profile. No live/shadow/agentic.

GATES: none
MOA_EXEC_DONE

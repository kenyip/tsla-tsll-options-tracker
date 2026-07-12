# MOA executor closeout — 2026-07-11T0200

WAKE: 2026-07-11T0200 evening BUILD lab executor
PHASE: BUILD
SLEEVE: 3000
CHOSE: Axis E / P1 new sim class — close the prior butterfly coverage seed with a minimal long-call butterfly simulator, then P3-falsify every registered butterfly candidate.

## DID

- Loaded `trader-self-evolution`; oriented from BUILD lab doctrine, income coverage, prior wake, and readiness.
- Implemented paper-only `butterfly_spread`: same-expiry symmetric long-call butterfly, Black-Scholes daily marks, explicit adverse per-leg slip, defined debit/max loss, one-position event loop, profit/loss/DTE exits, and $3k capital fields.
- Wired the class into Strategy DNA, evolve dispatch/artifacts, B3 regime stress, B4 cost stress, platform synthetic smoke, and coverage reporting.
- Refreshed multi-symbol research: run23 scored 23/23; top eight composite were TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ.
- Ran one focused applied population of 36 (`butterfly_spread`, `top-symbols=8`, `mutants=2`, `$3k`). Evolve registered six butterfly candidates; incidental family-seed single-leg SHIPs remain research toys.
- Falsified the quality leader plus all six registered butterflies with dated B3+B4. All butterfly candidates soft-held B3, but every one failed non-vacuous 5% leg-slip B4. No capital-path promotion.
- Refreshed coverage to 14 catalog structures / 151 hypotheses / 33 sim artifacts. No live, broker, shadow, or arm action.

## EVIDENCE

- `.cache/platform/research_reports/2026-07-11_run23.md`
- `.cache/platform/evolve_audit.jsonl` @ `2026-07-11T09:05:36+00:00`
- `.cache/platform/stress_regime_lab_2026-07-11T0200.json`
- `.cache/platform/stress_cost_lab_2026-07-11T0200.json`
- `trader_platform/research/butterfly_sim.py`
- `trader_platform/strategy_dna.py`
- `trader_platform/smoke_test.py`
- `reports/readiness/income-coverage-LATEST.md`

Verification: `.venv/bin/python -m trader_platform.smoke_test` returned `platform smoke OK` with the butterfly assertions exercised. Three focused unit tests passed, and `python -m compileall -q trader_platform scripts` completed cleanly.

## QUALITY BAR — B3 windows + 5% leg slip

| Hyp / structure | ml | window max DD | dense-neg | B3 | 5% slip | L1 judgment |
|---|---:|---:|---:|---|---|---|
| TSLL PCS `b195f5fe` | $76.32 | $74.85 | 5 | soft hold | n13 / -$18.32 NULL | Relative leader; after-cost negative, not L1 |
| BAC butterfly `90f034fc` | $22.76 | $86.96 | 7 | soft hold | n413 / -$9,596.83 REJECT | Cost-fragile; reject capital path |
| MU butterfly `badb31d7` | $19.73 | $51.07 | 8 | soft hold | n626 / -$45,879.62 REJECT | Tighter ml/dd, but cost destroys edge; reject |
| TSLA butterfly `2421c32f` | $21.25 | $36.01 | 5 | soft hold | n529 / -$94,077.49 REJECT | Best window DD, worst cost fragility; reject |
| MU butterfly `da33c855` | $19.23 | $66.85 | 9 | soft hold | n619 / -$45,797.87 REJECT | Baseline NULL and cost REJECT |
| BAC butterfly `b3b9c5b1` | $22.85 | $48.77 | 6 | soft hold | n405 / -$9,377.77 REJECT | Best baseline +$135.63, but non-vacuous cost REJECT |
| TSLL butterfly `0903a7e2` | $4.22 | $6.91 | 5 | soft hold | n350 / -$7,052.90 REJECT | Tiny risk/edge at mid; cost REJECT |

The B4 simulator applies the requested percentage adversely to each gross option leg, so entry/exit cadence changes under slip and trade counts rise. That is still non-vacuous evidence: every butterfly candidate has hundreds of stressed trades and materially negative after-cost P/L. No candidate reaches L1; `l1_hyp_ids=[]`.

## DURABLE

- `butterfly_spread` is now a real paper research class rather than a documented gap: catalog + sim + evolve + B3/B4 + smoke.
- The first butterfly population is explicitly cost-rejected; positive mid-mark SHIP labels are not readiness evidence.
- Remaining class debt is precise: observed option surfaces, pin/assignment realism, and iron-butterfly credit variant. Debit verticals remain the next unsimmed defined-risk direction class.

## PROGRESS / READINESS

PROGRESS TYPE: **P1 new sim class + P3 quality falsify**
SCORE: **4/5** — closed a catalog gap with executable plumbing and decisively rejected six vanity SHIPs; no L1 edge.
HONEST READINESS: **L0 BUILD only**. No L1, no LIVE_PACKET, no capital-path expansion.

## NEXT SEED

Next BUILD only: implement a minimal defined-risk debit-vertical simulator (bull call / bear put) with synthetic smoke, then one focused evolve + B3/B4; reject unless non-vacuous after-cost and competitive with `b195f5fe` on max loss / window max DD.

GATES: none
MOA_EXEC_DONE

# MOA executor closeout — 2026-07-11T0036

WAKE: 2026-07-11T0036 evening BUILD lab executor
PHASE: BUILD
SLEEVE: 3000
CHOSE: Axis C / P2 direction-regime scoreboard — close the prior NEXT with shared-window PCS-vs-CCS-vs-IC evidence, while falsifying new defined-risk SHIPs.

## DID

- Loaded `trader-self-evolution`; oriented from BUILD lab doctrine, income coverage, prior wake, and readiness.
- Refreshed multi-symbol research: run22 scored 23/23; top eight composite were TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ.
- Ran one free-catalog applied evolve population of 36 (`top-symbols=8`, `mutants=2`, `$3k`). It created SMCI/NFLX calendar SHIPs plus single-leg wheel SHIPs/research toys; no new PCS/CCS/IC SHIP.
- Ran dated B3+B4 on the PCS/CCS/IC representatives plus both new calendar SHIPs.
- Added and tested `scripts/pcs_direction_scoreboard.py`; it intersects 15 shared yearly/canonical windows and joins 5% cost stress for apples-to-apples direction comparison.
- Updated income coverage doctrine and generator. No live, broker, shadow, or arm action.

## EVIDENCE

- `.cache/platform/research_reports/2026-07-11_run22.md`
- `.cache/platform/evolve_audit.jsonl` @ `2026-07-11T07:37:23+00:00`
- `.cache/platform/stress_regime_lab_2026-07-11T0036.json`
- `.cache/platform/stress_cost_lab_2026-07-11T0036.json`
- `.cache/platform/direction_scoreboard_lab_2026-07-11T0036.json`
- `scripts/pcs_direction_scoreboard.py`
- `tests/test_pcs_direction_scoreboard.py` (2 tests pass)

Verification: both new tests pass and `python -m trader_platform.smoke_test` reports `platform smoke OK`. Full unittest discovery ran 13 tests with 12 passing and one unrelated PMCC integration failure: `test_assemble_pmcc_desk_live_yaml` expected positive upside but current fixture calculation returned `-0.5`. No PMCC files were changed in this loop.

## QUALITY BAR — shared 15 windows + 5% slip

| Hyp / bias | ml | shared-window max DD | dense-neg | B3 | 5% slip | L1 judgment |
|---|---:|---:|---:|---|---|---|
| TSLL PCS `b195f5fe` / bullish | $76.32 | $74.85 | 3 | soft hold | n13 / -$18.32 NULL | Relative leader; after-cost negative, not L1 |
| XOM CCS `77766a47` / bearish | $202.46 | $147.25 | 2 | soft hold | n16 / -$68.13 NULL | Worse ml/dd and after-cost negative; reject capital path |
| AMD IC `b3056133` / neutral | $175.47 | $253.85 | 5 | soft hold | n96 / -$2,567.58 REJECT | Cost-fragile; reject |
| SMCI calendar `ba439767` / time-neutral-bullish | $213.50 | $204.53 | 3 | soft hold | n160 / -$2,182.28 REJECT | New vanity SHIP; cost reject |
| NFLX calendar `7670928f` / time-neutral-bullish | $133.62 | $377.81 | 6 | soft hold | n135 / -$959.30 REJECT | New vanity SHIP; cost reject |

No candidate is positive and non-vacuous at 5% slip. `l1_hyp_ids=[]`; capital path and readiness do not advance. The new wheel SHIPs remain undefined-risk/single-leg research toys and were not used as $3k capital candidates.

## DURABLE

- Shared-window direction comparator is now reusable and covered by tests.
- Direction-scoreboard coverage gap moved from partial B3-only to built comparator; representative breadth/realism can still expand.
- Prior NEXT is closed. The first apples-to-apples table supports stand-aside: bullish PCS remains the relative risk leader, bearish CCS is not independently competitive, and neutral IC is cost-fragile.

## PROGRESS / READINESS

PROGRESS TYPE: **P2 direction/regime scoreboard + P3 quality falsify**
SCORE: **4/5** — new durable comparator, real common-window/cost evidence, and two new SHIPs rejected; no L1 edge.
HONEST READINESS: **L0 BUILD only**. No L1, no LIVE_PACKET, no capital-path expansion.

## NEXT SEED

Next BUILD only: implement a minimal defined-risk butterfly / iron-butterfly sim scaffold with synthetic smoke, then run one focused evolve + B3/B4; reject unless a non-vacuous after-cost row is competitive with `b195f5fe` on max loss and shared-window DD.

GATES: none
MOA_EXEC_DONE

# Trader wake — 2026-07-10T2323 MoA executor

WAKE: 2026-07-10T2323 local / evening BUILD lab executor
PHASE: BUILD
SLEEVE: 3000
CHOSE: Axis E — minimal sleeve-fit `diagonal_spread` sim class, then one discovery population and B3/B4 falsification. This superseded another calendar retune because the calendar proxy had already failed non-vacuous B4 repeatedly.

## DID

- Loaded `trader-self-evolution` and oriented from BUILD/income coverage, latest wake, and readiness.
- Ran multi-symbol research run 20: 23/23 symbols scored; top eight TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ.
- Built `trader_platform/research/diagonal_sim.py`: bullish long-call diagonal, explicit short/long DTE and delta, explicit expiry IV multipliers, defined debit/max-loss, bearish stand-aside, daily mark/exit loop.
- Added Strategy DNA catalog/mutation knobs, evolve dispatch, B3/B4 dispatch, and synthetic platform smoke.
- Ran exactly one free-catalog applied population (`top-symbols=8`, `mutants=2`, `max-population=36`). It produced no diagonal SHIP because sampled diagonal rows were TSLA/MU and exceeded the $300 debit budget; no second full evolve was run.
- Exercised the seed DNA directly on the two low-price top-ranked names. TSLL was weak/high-DD; SMCI was SHIP and was registered candidate-only as `hyp_dna_smci_diagonal_spread_d1017453`.
- Re-ran dated B3+B4 on the new diagonal, leader, and the other defined-risk SHIPs from the population. No status moved beyond candidate/testing; no shadow/live/broker action.

## EVIDENCE

- Research: `.cache/platform/research_reports/2026-07-11_run20.md`
- Evolve audit: `.cache/platform/evolve_audit.jsonl` at `2026-07-11T06:27:54+00:00`
- Diagonal baseline: `.cache/platform/diagonal_baseline_lab_2026-07-10T2323.json`
- B3: `.cache/platform/stress_regime_lab_2026-07-10T2323.json`
- B4: `.cache/platform/stress_cost_lab_2026-07-10T2323.json`
- Smoke: `just platform-smoke` passed, including diagonal defined-debit assertions.

## QUALITY BAR

| Hyp / structure | 1-lot max loss | full DD | window max DD | dense negative windows | B3 | 5% slip | B4 | Judgment |
|---|---:|---:|---:|---:|---|---|---|---|
| TSLL PCS `b195f5fe` | $76.32 | $78.39 | $74.85 | 5 | soft hold | n=13 / −$18.32 / NULL | soft hold | Relative leader; still not non-vacuous after-cost edge |
| SMCI diagonal `d1017453` | $294.03 | $153.30 | $153.30 | 0 | soft hold, but sparse | n=24 / +$107.35 / SHIP | strong hold | First non-vacuous diagonal challenger; **fails L1** on competitive ml/dd and recent density |
| MU PCS `55c7323a` | $193.91 | $586.79 | $499.57 | 6 | fail | n=3 / −$192.58 | fail | Reject capital path |
| SMCI calendar `256b2877` | $224.42 | $406.96 | $380.63 | 4 | soft hold | n=121 / −$1,784.14 / REJECT | fail | Reject capital path |
| TSLL calendar `5a83a18a` | $120.48 | $181.01 | $181.01 | 4 | soft hold | n=97 / −$814.32 / REJECT | fail | Reject capital path |

The diagonal’s B3 `regime_hold=true` is not enough: 32 full-history trades are concentrated in 2022–23, with one trade in 2024 and zero in 2025–26 under the $300 debit gate. It is not a current, dense regime edge and its max-loss/window-DD profile is about 2–4× the PCS leader. Candidate/research-only is the honest label.

## DURABLE

- Catalog now has a real `diagonal_spread` sim path with capital fields and stress dispatch.
- Coverage/docs now distinguish scaffold completion from realism/readiness: observed option surfaces, early assignment, and exact-DNA OOS remain missing.
- Capital path is unchanged. `b195f5fe` remains the relative quality leader, while also remaining below L1 because 5% slip is a soft loss.

## PROGRESS / READINESS

PROGRESS TYPE: **P1 new sim class + P3 quality falsify**
SCORE: **4/5** — working scaffold, real smoke, registered challenger, and complete B3+B4 decision; not 5 because the challenger fails the L1 ml/dd+density bar.
HONEST READINESS: **L0 BUILD only**. No L1 claim, no LIVE_PACKET, no capital-path expansion.

## NEXT SEED

Next BUILD only: add exact-DNA chronological OOS plus entry-density reporting for SMCI diagonal `d1017453`; reject the proxy edge unless the recent holdout has non-vacuous entries and remains after-cost positive. Do not retune assumed IV knobs first.

GATES: none
MOA_EXEC_DONE

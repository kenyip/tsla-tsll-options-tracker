# Trader wake — 2026-07-10T2351 MoA executor

WAKE: 2026-07-10T2351 local / evening BUILD lab executor
PHASE: BUILD
SLEEVE: 3000
CHOSE: Axis D — close the prior diagonal exact-DNA OOS/density reject gate, then B3+B4-falsify the defined-risk SHIPs from one required free-catalog discovery population. This superseded another sim-class scaffold because the prior wake left a specific unresolved quality claim.

## DID

- Loaded `trader-self-evolution` and oriented from BUILD/income coverage, latest wake, and readiness.
- Ran multi-symbol research run 21: 22/23 symbols scored; top set remained broad, with TSLL/SMCI leading and NFLX failing data parse.
- Ran exactly one free-catalog applied population (`top-symbols=8`, `mutants=2`, `max-population=36`). New defined-risk SHIPs were SMCI PCS `f94a3a37`, AAPL PCS `b16ca012`, and BAC PCS `e39fb210`; MU PCS `55c7323a` re-SHIPped. Single-leg SHIPs remain research toys.
- Added `scripts/diagonal_oos_stress.py` plus a unittest. The script runs exact registered diagonal DNA on a chronological 60/40 split at baseline and 5% adverse slippage and reports entry density by year.
- Exact-DNA OOS rejected SMCI diagonal `d1017453`: train baseline n32 / +$679.80 and train@5% n24 / +$107.35, but the 2024-12-17–2026-07-10 holdout had zero trades at both baseline and 5% slip. The historical proxy edge is non-vacuous only in the old train segment.
- Ran dated B3+B4 on the leader plus all four defined-risk population SHIPs. No status moved beyond candidate/testing; no shadow/live/broker action.

## EVIDENCE

- Research: `.cache/platform/research_reports/2026-07-11_run21.md`
- Evolve audit: `.cache/platform/evolve_audit.jsonl` at `2026-07-11T06:52:27+00:00`
- Diagonal exact-DNA OOS: `.cache/platform/diagonal_oos_lab_2026-07-10T2351.json`
- B3: `.cache/platform/stress_regime_lab_2026-07-10T2351.json`
- B4: `.cache/platform/stress_cost_lab_2026-07-10T2351.json`
- Test: `.venv/bin/python -m unittest tests.test_diagonal_oos_stress -v` passed.

## QUALITY BAR

| Hyp / structure | 1-lot max loss | window max DD | dense-neg | B3 | 5% slip | B4 | Judgment |
|---|---:|---:|---:|---|---|---|---|
| TSLL PCS `b195f5fe` | $76.32 | $74.85 | 5 | soft hold | n13 / −$18.32 / NULL | soft hold | Relative leader; still not L1 because after-cost edge is negative |
| BAC PCS `e39fb210` | $80.19 | $130.15 | 8 | soft hold | n58 / −$55.97 / NULL | soft hold | Closest max-loss challenger, but worse DD/dense-neg and after-cost negative; reject capital path |
| SMCI PCS `f94a3a37` | $164.22 | $622.99 | 3 | soft hold | n966 / −$517.65 / REJECT | fail | Dense baseline vanity; cost and DD reject capital path |
| AAPL PCS `b16ca012` | $205.99 | $330.88 | 8 | soft hold | n141 / −$1,159.38 / REJECT | fail | Cost-fragile and worse ml/dd; reject capital path |
| MU PCS `55c7323a` | $193.91 | $499.57 | 6 | fail | n3 / −$192.58 / NEEDS_MORE_DATA | fail | Reconfirmed reject |
| SMCI diagonal `d1017453` | $294.03 train p95 | $153.30 train | holdout n0 | sparse historical only | holdout n0 / $0 | vacuous holdout | Exact-DNA recent holdout rejects proxy edge |

No candidate reaches L1: none combines non-vacuous positive after-cost results, dense B3, and competitive max-loss/window-DD against the quality bar. `b195f5fe` remains only a relative leader and is itself below L1.

## DURABLE

- Diagonal exact-DNA chronological OOS and year-density reporting are now executable, tested tooling rather than an open checklist item.
- SMCI diagonal `d1017453` is quality-rejected for the capital path on zero recent holdout entries; do not retune assumed IV multipliers to rescue it before observed-surface data exists.
- This population’s three new PCS SHIPs are quality-rejected despite baseline SHIP labels. Capital path is unchanged.

## PROGRESS / READINESS

PROGRESS TYPE: **P3 quality falsify**
SCORE: **4/5** — closed the prior exact-DNA OOS gate with tested tooling and made clear B3+B4 decisions on every new defined-risk SHIP; not 5 because no DNA achieved L1.
HONEST READINESS: **L0 BUILD only**. No L1, no capital-path expansion, no shadow/live/arm.

## NEXT SEED

Next BUILD only: build one apples-to-apples direction/regime scoreboard for registered PCS vs CCS vs IC using common regime windows and cost assumptions; reject any side whose non-vacuous after-cost ml/dd cannot compete with `b195f5fe`.

GATES: none
MOA_EXEC_DONE

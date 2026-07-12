# MOA BUILD Lab executor closeout — 2026-07-10T2123

PHASE: BUILD
SLEEVE: $3,000
SLOT: evening
MODEL/ROLE: GPT 5.6 Sol executor; only writer
AXIS: E — new sim class scaffold (long calendar), because the prior wake and coverage map identified the missing time-structure simulator as higher leverage than another credit-only population.

## Closed loop

- Oriented from BUILD doctrine, coverage, latest wake, and readiness.
- Refreshed multi-symbol rank: research run 18, 23/23 symbols scored; top composite TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Evidence: `.cache/platform/research_reports/2026-07-11_run18.md` and `.cache/platform/research.db`.
- Added `calendar_spread` to Strategy DNA and implemented `trader_platform/research/calendar_sim.py`: same-strike long put calendar, front/back DTE, daily BS marks, one open position, profit/defined-loss/front-expiry exits, and debit-at-risk capital fields.
- Wired calendar dispatch into evolve plus B3/B4 stress. Added a deterministic synthetic calendar check to `just platform-smoke`.
- Ran exactly one required applied free-catalog evolve (`top-symbols=8`, `mutants=2`, `max-population=36`, sleeve $3k). It produced a baseline TSLL calendar SHIP and an SMCI CCS SHIP; both were registered as candidates, not promoted.
- Falsified the new SHIPs alongside leader `hyp_dna_tsll_put_credit_spread_b195f5fe` with dated B3+B4 outputs.

## Quality bar versus current leader

| Hyp / structure | 1-lot max loss | Full n / pnl | Window max DD | Dense negative windows | Regime hold | 5% slip n / pnl | Cost hold | Judgment |
|---|---:|---:|---:|---:|---|---:|---|---|
| `b195f5fe` TSLL PCS | $76.32 | 57 / $115.90 | $74.85 | 5 | true | 13 / −$18.32 | true, soft loss | Relative leader; still no positive after-cost edge |
| `d5e00af5` TSLL calendar | $146.84 | 100 / $148.05 | $230.79 | 7 | true | 94 / −$895.64 | false, fragile | Research-only reject from capital path |
| `ee20a595` SMCI CCS | $166.77 | 204 / −$422.13 | $692.84 | 12 | false | 118 / −$1,614.13 | false, fragile | Research-only reject from capital path |

Sources: `.cache/platform/stress_regime_lab_2026-07-10T2123.json`, `.cache/platform/stress_cost_lab_2026-07-10T2123.json`.

## Important model limitation

The calendar scaffold applies the same underlying-derived IV proxy to both expiries. It therefore does not model front/back IV term structure or skew. Its full-history SHIP is a baseline plumbing result, not readiness evidence. B4 already rejects this first DNA under adverse marks, so no registration beyond candidate and no capital-path promotion is justified.

## Verification

- `just platform-smoke` — PASS, including `calendar sim synthetic smoke OK (defined debit risk)`.
- Python compile — PASS for calendar sim, DNA/evolve dispatch, B3/B4 scripts, coverage, and smoke.
- Coverage refreshed: 12 catalog structures, 124 hypotheses, calendar_sim present with one candidate.

## Honest readiness

Stay BUILD. Calendar structure coverage improved from absent to a minimal real simulator, but the first candidate is cost-fragile and the simulator lacks expiry-specific IV term structure/skew. The PCS leader remains only a relative quality example and still loses $18.32 at 5% slip. No strategy has non-vacuous positive after-cost evidence plus B6/B7.

## ONE next seed

Next BUILD only: add expiry-specific front/back IV term-structure/skew inputs to `calendar_sim`, then rerun a calendar-only OOS + B3/B4 cost falsification; reject the class for this data path if it remains fragile. No registration/promotion from baseline BS metrics.

Hard stops held: paper/research only; no broker login, live order, arm, shadow auto-promotion, or capital-path expansion.

MOA_EXEC_DONE

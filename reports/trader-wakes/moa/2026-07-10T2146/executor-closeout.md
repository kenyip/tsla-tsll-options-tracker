# MOA BUILD Lab executor closeout — 2026-07-10T2146

PHASE: BUILD
SLEEVE: $3,000
SLOT: evening
MODEL/ROLE: GPT 5.6 Sol executor; only writer
AXIS: E — calendar sim realism, because the prior wake’s same-IV calendar scaffold produced misleading baseline SHIPs and explicit term/skew assumptions plus OOS were the highest-leverage blocker.

## Closed loop

- Oriented from BUILD doctrine, coverage, latest wake, readiness, and the L0–L4 confidence ladder.
- Refreshed the 23-name research rank: run 19 completed 23/23 without errors; top composite TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Evidence: `.cache/platform/research_reports/2026-07-11_run19.md` and `.cache/platform/research.db`.
- Upgraded `calendar_sim` from one shared IV proxy to explicit `front_iv_multiplier`, `back_iv_multiplier`, and `put_skew_per_moneyness` assumptions used at entry and every mark. Added bounded DNA mutation inputs and smoke coverage.
- Added `scripts/calendar_oos_stress.py`, which runs a chronological 60/40 split on exact registered calendar DNA without fitting.
- Ran one required applied free-catalog evolve (`top-symbols=8`, `mutants=2`, `max-population=36`, sleeve $3k). It registered three new assumption-aware calendar candidates: TSLL `34f2b2c5`, SMCI `917fff50`, BAC `8ccac90f`. No shadow/live promotion.
- Ran dated B3+B4 on all three plus leader `hyp_dna_tsll_put_credit_spread_b195f5fe`, then chronological OOS on the three calendars.

## Quality bar versus current leader

| Hyp / structure | 1-lot max loss | Full n / pnl | Window max DD | Dense negative windows | Regime hold | 5% slip n / pnl | Cost hold | OOS test n / pnl / DD | Judgment |
|---|---:|---:|---:|---:|---|---:|---|---:|---|
| `b195f5fe` TSLL PCS | $76.32 | 57 / $115.90 | $74.85 | 5 | true | 13 / −$18.32 | true, soft loss | n/a | Relative leader only; still no positive after-cost edge |
| `34f2b2c5` TSLL calendar | $110.41 | 110 / $666.69 | $121.55 | 3 | true | 93 / −$266.85 | false | 46 / $479.53 / $30.93 | OOS positive, but non-vacuous B4 failure rejects capital path |
| `917fff50` SMCI calendar | $226.21 | 152 / $1,370.71 | $344.90 | 4 | true | 124 / −$1,511.58 | false | 66 / $824.21 / $134.56 | OOS positive, but risk and B4 are far worse than leader; reject |
| `8ccac90f` BAC calendar | $43.30 | 148 / $54.64 | $170.83 | 9 | true | 128 / −$742.30 | false | 60 / −$47.78 / $170.83 | OOS and B4 fail; reject |

Sources:
- `.cache/platform/stress_regime_lab_2026-07-10T2146.json`
- `.cache/platform/stress_cost_lab_2026-07-10T2146.json`
- `.cache/platform/calendar_oos_lab_2026-07-10T2146.json`
- `.cache/platform/evolve_audit.jsonl` at `2026-07-11T04:49:10+00:00`

## Falsification decision

The calendar class is rejected for the current underlying-IV-proxy data path. Explicit term/skew assumptions and positive OOS baseline marks do not survive modest adverse execution: all three new candidates have many non-vacuous 5% slip trades and lose $266.85–$1,511.58. This is not a soft-null or sparse-data result. Historical expiry-specific option surfaces remain absent, but adding more assumed calendar knobs would be model polish, not evidence of income.

## Verification

- `just platform-smoke` — PASS, including front IV greater than back IV under the synthetic term assumption.
- Research run 19 — PASS, 23/23 symbols.
- One applied evolve — PASS, population 36; three calendar candidates created.
- B3/B4 dated stress — PASS as execution; all calendar candidates rejected on quality.
- Chronological OOS script — PASS on exact registered DNA.
- Coverage refreshed: 12 structures, 129 hypotheses, 21 evolve artifacts; calendar gap now labeled assumption-aware/OOS but without observed surfaces.

## Progress and honest readiness

PROGRESS TYPE: **P1 sim realism + P3 quality falsify**, score **4/5**. The simulator and falsification surface improved materially; income edge did not.
L0–L4 READINESS: **L0 BUILD only**. No DNA reaches L1 because no candidate has non-vacuous positive after-cost results plus competitive max-loss/window-DD. B6/B7 and account funding/options level remain blocked. No LIVE_PACKET.

## ONE next seed

Next BUILD only: implement a minimal sleeve-fit `diagonal_spread` simulator with explicit long/short expiry IV assumptions, defined debit/max-loss fields, and synthetic smoke; then run one evolve + B3/B4 and reject unless after-cost risk beats the PCS quality bar.

Hard stops held: paper/research only; no broker login, live order, arm, shadow auto-promotion, or capital-path expansion.

MOA_EXEC_DONE

# Trader wake — 2026-07-10T2100 MoA executor

WAKE: 2026-07-10T2100 local / evening executor
PHASE: BUILD
SLEEVE: 3000
CHOSE: D — quality falsify after one free-catalog search. Superseded the prior 7-DTE micro-variant seed because its existing 5%-slip result was already vacuous (n=0); fresh defined-risk competition and catalog breadth were higher leverage.

DID:
- Research run17: 23/23 symbols scored, zero errors; top eight were TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ.
- Ran one required free-catalog evolve: 36 real sims over TSLL, SMCI, PLTR, NFLX, BAC, XOM, MU, TSLA. It produced six SHIPs, all single-leg TSLL/PLTR research toys; no PCS/CCS/IC SHIP.
- Ran dated B3+B4 on the relative leader plus the strongest defined-risk comparison set: TSLL PCS `b195f5fe`, MU PCS `95315a65`, XOM CCS `77766a47`.
- Kept all statuses and the capital path unchanged. No shadow/live promotion, broker access, or arm.

QUALITY BAR:

| hyp / structure | capital_fit_usd / max_loss / max_lots | full 5y | window max_dd / dense-neg | regime_hold | 5% slip | decision |
|---|---|---|---|---|---|---|
| TSLL PCS `b195f5fe` | 76.32 / 76.32 / 3 | SHIP n57, +115.90, dd 78.39 | 74.85 / 5 | true | n13, -18.32, NULL; soft hold | relative leader unchanged; B6 target |
| MU PCS `95315a65` | 193.44 / 193.44 / 1 | SHIP n122, +689.84, dd 586.79 | 499.57 / 6 | **false** | n1, -64.75, NEEDS_MORE_DATA; soft label only | reject capital path: regime fail and much worse ml/dd |
| XOM CCS `77766a47` | 202.46 / 202.46 / 1 | SHIP n74, +414.67, dd 147.25 | 147.25 / 4 | true | n16, -68.13, NULL; soft hold | research-only: worse ml/dd and after-cost loss; no diversify-for-fear seat |

NEW EVOLVE SHIPS:

| DNA / structure | 2y evidence | capital contract | judgment |
|---|---|---|---|
| TSLL short put `8592730066f7` | n28, +152.33, dd 94.23 | capital_fit_usd unknown; max_loss undefined; max_lots 0 for sleeve path | research toy |
| TSLL roll defend `6c89c025643b` | n32, +203.26, dd 169.00 | capital_fit_usd unknown; max_loss undefined; max_lots 0 for sleeve path | research toy |
| TSLL short DTE `820edf7d51e0` | n39, +283.61, dd 263.79 | capital_fit_usd unknown; max_loss undefined; max_lots 0 for sleeve path | research toy |
| TSLL regime premium `afd8593aea7b` | n45, +188.21, dd 246.91 | capital_fit_usd unknown; max_loss undefined; max_lots 0 for sleeve path | research toy |
| TSLL regime premium `bb47514e8323` | n59, +153.81, dd 303.31 | capital_fit_usd unknown; max_loss undefined; max_lots 0 for sleeve path | research toy |
| PLTR short call `693b105ea365` | n19, +113.29, dd 482.76 | capital_fit_usd unknown; max_loss undefined; max_lots 0 for sleeve path | undefined-risk research toy |

B3/B4 are intentionally not run through the PCS stress tools for those single-leg SHIPs: they fail the earlier defined-risk/capital-contract gate, and pretending they are spreads would create false evidence.

EVIDENCE:
- `.cache/platform/research_reports/2026-07-11_run17.md`
- `.cache/platform/evolve_audit.jsonl` at `2026-07-11T04:00:53+00:00`
- `.cache/platform/evolve_backtests/TSLL_research_trades.csv`
- `.cache/platform/evolve_backtests/PLTR_research_trades.csv`
- `.cache/platform/stress_regime_lab_2026-07-10T2100.json`
- `.cache/platform/stress_cost_lab_2026-07-10T2100.json`

DURABLE:
- Fresh free search did not produce a defined-risk challenger. `b195f5fe` remains the relative quality leader, not a readiness claim.
- The catalog gap now blocks broader time-structure discovery more than another micro-mutation. Precise calendar scaffold targets: add a `calendar_spread` DNA template and bounded front/back-DTE knobs in `trader_platform/strategy_dna.py`; implement BS-marked two-expiry entry/exit, debit-at-risk capital accounting, and trade dumps in new `trader_platform/research/calendar_sim.py`; dispatch it beside `uses_pcs_sim()` in `trader_platform/evolve_tick.py`; add a real-sim smoke/time grid under `scripts/`; update `docs/INCOME_STRATEGY_COVERAGE.md` only after execution evidence exists.
- Real-account readiness remains blocked by non-vacuous after-cost superiority, live-clock multi-session paper closes (B6), shadow evidence (B7), and the unfunded/no-options Agentic account. Phase stays BUILD.

NEXT SEED:
Next BUILD only — E new sim class scaffold: implement and smoke one minimal long calendar spread simulator on the top liquid research names, with explicit front/back DTE, debit=max_loss, `capital_fit_usd`, `max_loss_usd`, and `max_lots`; do not register/promote unless a real after-cost sim exists.

GATES: none (paper/research only)

MOA_EXEC_DONE

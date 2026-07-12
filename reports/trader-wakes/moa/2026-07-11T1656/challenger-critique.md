# MOA BUILD lab challenger critique — 2026-07-11T1656 (evening)

WAKE: 2026-07-11T1656 PDT
ROLE: Grok 4.5 challenger (read-only)
PHASE: BUILD · SLEEVE: 3000
MODE: paper/research only — no evolve --apply, no live/broker/arm/shadow

## Verdict

**PASS 8/8.** Executor closed a real P1 sim-realism gap (uniform fixed-$ per-leg half-spread across remaining proxy engines), ran multi-name discovery + exact P3 falsify, kept L0 honesty, and left one concrete NEXT. Metrics match lab JSON.

## Rubric

| # | Check | Result | One line |
|---|---|---|---|
| 1 | Income goal honesty | **PASS** | $3k / steady-income framing; rejects vanity fixed-$ PnL when path DD fails; no L1 claim |
| 2 | Multi-structure vs tunnel | **PASS** | Calendars + butterflies + debit vertical across PLTR/NFLX/XOM/TSLA/MU/TSLL; single-leg SHIPs labeled toys |
| 3 | Time bias as axis | **PASS** | Explicitly deferred — prior NEXT was fixed-cost coverage completion, not time thrash |
| 4 | Direction/regime as axis | **PASS** | Not a scoreboard wake; B3 used for falsify only; deferred with coverage already built |
| 5 | Sims actually run | **PASS** | run30 + evolve `2026-07-11T23:56:43Z` + dated fixed/regime/cost/quality JSON |
| 6 | Quality bar / B3+B4 before capital | **PASS** | `l1_hyp_ids=[]`; all six new DR fail non-vacuous 5% B4; fcc76896 fails fixed-DD + 5% |
| 7 | ONE closed NEXT seed | **PASS** | Observed-quote / no-paid-data inventory + minimal adapter/fixture smoke or exact blocker |
| 8 | No live/shadow promotion | **PASS** | BUILD/L0 only; no arm/shadow/agentic |

## Evidence verified (read-only)

Paths present and numbers checked:

- `.cache/platform/research_reports/2026-07-11_run30.md`
- `.cache/platform/evolve_audit.jsonl` row `ts=2026-07-11T23:56:43+00:00` applied pop36; 8 SHIP-ish including DR calendars/butterflies/debit + single-leg toys
- `.cache/platform/fixed_leg_cost_proxy_lab_2026-07-11T1656.json` — 7 hyps; `$0.01/leg` rows match closeout table
- `.cache/platform/stress_regime_lab_2026-07-11T1656.json` — six new DR hyps, all `regime_hold=True`
- `.cache/platform/stress_cost_lab_2026-07-11T1656.json` — six new DR hyps, all non-vacuous 5% REJECT
- `.cache/platform/quality_bar_lab_2026-07-11T1656.json` — leader bar ml $76.32 / window DD $74.85; `l1_hyp_ids=[]`
- Code surface: `half_spread_per_leg` in calendar/diagonal/butterfly/debit_vertical (+ prior PCS/IC/IB) and `scripts/defined_risk_fixed_cost_stress.py` / `tests/test_defined_risk_fixed_cost.py`
- Coverage scoreboard gap text updated: fixed-$ axis complete; observed quotes remain

### Fixed $0.01/leg (exact)

| hyp | structure | n | pnl | dd | ml | judgment |
|---|---|---:|---:|---:|---:|---|
| fcc76896 | TSLL calendar | 116 | +298.28 | 115.81 | 66.97 | reject L1: fixed DD > leader bar; 5% still −80.38 n100 |
| a59a3227 | PLTR calendar | 141 | +855.94 | 581.58 | 290.26 | reject ml/DD + 5% REJECT |
| 307c7de5 | NFLX calendar | 146 | +254.74 | 441.12 | 144.60 | reject ml/DD + 5% REJECT |
| 6e945d54 | XOM calendar | 153 | +1167.99 | 328.90 | 155.05 | reject ml/DD + 5% REJECT |
| 88a044b8 | TSLA butterfly | 190 | −1307.72 | 1324.38 | 24.26 | reject fixed + 5% |
| 372d1c2b | MU butterfly | 249 | −1912.38 | 1900.92 | 24.16 | reject fixed + 5% |
| 75556a20 | TSLL bull-call debit | 65 | −85.85 | 307.59 | 80.89 | reject fixed + 5% |

Leader `b195f5fe` remains **relative** quality example only: baseline ml $76.32 / window DD $74.85 / B3 soft-hold / 5% n13 / −$18.32 soft NULL — **not L1**. Under fixed $0.01/leg it is also negative (n33 / −$63.01; fixed DD $120.07). Do not read soft cost_hold as after-cost edge.

## Challenges (keep / tighten — not rewrites)

1. **Fixed-$ positive ≠ L1** — executor correctly rejected `fcc76896` despite dense +$298.28. Baseline window DD $48.45 looks *better* than leader $74.85; the fail is **fixed-cost path DD $115.81** plus **5% dense loss**. Do not retune assumed IV/skew to paper over that.
2. **Leader is not fixed-cost-safe either** — fixed DD of leader ($120.07) is in the same neighborhood as fcc76896 ($115.81). Relative capital-path example survives only on baseline regime risk profile + soft B3/B4 convention, not as an after-cost income winner.
3. **`preferred_under_cost` noise** — cost lab points `preferred_under_cost` at debit vertical `75556a20` while that row is 5% REJECT / fixed negative. Treat as script ranking artifact, not a promote signal (executor did not promote — good).
4. **Pop36 still mixes single-leg SHIPs** — audit has short_put / short_dte SHIPs alongside DR. Executor correctly called them research toys; keep judging by DNA structure + sim_engine, not raw SHIP count.
5. **Time/direction not advanced** — acceptable supersede: prior seed was fixed-cost completeness. Session-time slices and jade-lizard remain later; do not thrash proxy DNA next.
6. **Score 4/5 accepted** — real P1 plumbing + honest P3 rejects; zero L1 is expected, not a demotion of progress.

## Axis / progress judgment

- Chose: **P1+P3** (Axis E cost realism completion + quality falsify) — correct vs free single-leg thrash.
- Progress score: **4/5** (agree).
- Honesty: **L0** BUILD only; `l1_hyp_ids=[]`.
- Capital path: unchanged — `hyp_dna_tsll_put_credit_spread_b195f5fe` quality example only.

## Merged NEXT (one seed)

One BUILD spike only: inventory a **no-paid-data** path for historical option bid/ask or half-spread observations (local RH/cache residues, free delayed public, or synthetic fixture from real quote shapes). Implement **one** minimal observed-quote adapter + fixture smoke that can validate calendar/vertical entry-exit marks. If no usable free source exists, write the exact data blocker and **stop proxy-cost retuning** (no more half-spread DNA polish, no assumed-IV rescue). No live / shadow / agentic.

## Hard stops observed

Challenger did not evolve --apply, broker, arm, or promote. Executor closeout stays paper/research.

GATES: none
MOA_CHALL_DONE

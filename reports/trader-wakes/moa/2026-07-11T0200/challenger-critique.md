# MOA challenger critique — 2026-07-11T0200 (Grok 4.5)

ROLE: read-only judgment. No evolve --apply, no broker, no arm/shadow promote.
PHASE: BUILD · SLEEVE: 3000 · LAB: evening income BUILD

## What executor claimed

- Axis E / P1: implement long-call `butterfly_spread` sim + DNA/evolve/B3/B4/smoke wiring.
- Research run23 + one focused applied pop36; registered six butterfly candidates.
- P3 falsify: all six B3 soft-hold; all six non-vacuous 5% leg-slip B4 REJECT.
- Quality leader unchanged: TSLL PCS `b195f5fe` (relative ml/dd only; not L1).
- Progress P1+P3 score 4/5; L0 BUILD; NEXT = debit-vertical sim scaffold + focused falsify.

## Evidence checked (read-only)

| Path | Status |
|---|---|
| `trader_platform/research/butterfly_sim.py` | present (~262 lines) |
| `evolve_audit.jsonl` @ `2026-07-11T09:05:36+00:00` | applied pop36; created 6 butterfly hyps + 1 single-leg toy |
| `.cache/platform/stress_regime_lab_2026-07-11T0200.json` | 7 hyps @ `2026-07-11T09:06:23Z` |
| `.cache/platform/stress_cost_lab_2026-07-11T0200.json` | 7 hyps; `preferred_under_cost=b195f5fe` |
| `.cache/platform/research_reports/2026-07-11_run23.md` | scored 23/23 |
| `trader_platform/data/hypotheses.yaml` | all 6 butterfly ids + b195f5fe present |
| `reports/readiness/income-coverage-LATEST.md` | butterfly gap updated; debit_vertical still no sim |

### Metric recompute vs executor quality table

| Hyp | claim ml / winDD / dense-neg / slip5 | verified |
|---|---|---|
| PCS `b195f5fe` | 76.32 / 74.85 / 5 / n13 −18.32 NULL soft | **match** (`max_loss_usd` full, `max_dd_across_windows`, `n_negative_n_ge_3`, cost summary) |
| BAC `90f034fc` | 22.76 / 86.96 / 7 / n413 −9596.83 REJECT | **match** |
| MU `badb31d7` | 19.73 / 51.07 / 8 / n626 −45879.62 REJECT | **match** |
| TSLA `2421c32f` | 21.25 / 36.01 / 5 / n529 −94077.49 REJECT | **match** |
| MU `da33c855` | 19.23 / 66.85 / 9 / n619 −45797.87 REJECT; baseline NULL | **match** (baseline pnl −4.61 NULL) |
| BAC `b3b9c5b1` | 22.85 / 48.77 / 6 / n405 −9377.77 REJECT; baseline +135.63 | **match** |
| TSLL `0903a7e2` | 4.22 / 6.91 / 5 / n350 −7052.90 REJECT | **match** (window DD 6.91; full-history dd 11.44 not claimed as window) |

All butterfly `regime_hold=true` (soft note); all `cost_hold=false` / `fragile_at_5pct_slip`. `l1_hyp_ids=[]` is correct. No capital-path talk without bar — correct.

**Cadence note:** B4 n_trades exploding under per-leg adverse slip is real sensitivity evidence, not a free pass. Executor correctly treats hundreds of deeply negative stressed trades as non-vacuous REJECT rather than retuning mid-mark SHIP.

## Rubric

1. **Income goal honesty** — **PASS**. $3k defined-debit butterflies judged on after-cost + ml/dd; no vanity $ promote; leader still after-cost soft-negative.
2. **Multi-structure search vs tunnel** — **PASS**. Closed prior butterfly seed with a new structure class across BAC/MU/TSLA/TSLL; did not thrash free single-leg pop only (incidental single-leg SHIP correctly labeled research toy).
3. **Time bias axis** — **PASS (deferred with gap)**. Not the chosen axis this wake; prior DTE×target×stop grid remains. Weekday/session still open. Acceptable under one-loop discipline.
4. **Direction/regime bias axis** — **PASS (partial + deferred)** . B3 yearly/canonical windows run on all candidates; butterfly side_policy is pin/neutral-to-bullish. Shared PCS/CCS/IC direction scoreboard already shipped prior wake; not re-thrashed.
5. **Sims actually run** — **PASS**. Paths above; metrics recompute clean.
6. **Quality bar / B3+B4 before capital** — **PASS**. Decisive rejects; `b195f5fe` remains relative leader only, still not L1.
7. **ONE closed NEXT seed** — **PASS**. Single BUILD seed: debit-vertical sim + smoke + one focused evolve + B3/B4 reject-unless competitive with b195f5fe.
8. **No live/shadow promotion** — **PASS**. Research/candidate only; no arm language.

**RUBRIC TOTAL: PASS 8/8**

## Challenges / nits (non-blocking)

1. **Research top-8 listing slip:** run23 composite order is TSLL, SMCI, **MU**, TSLA, PLTR, AAPL, AMD, ARM (QQQ is #9). Executor wrote “TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ” — dropped MU, promoted QQQ. Materially harmless (evolve still hit MU butterflies; multi-name), but do not treat that list as rank truth.
2. **Evolve registered 6 of 9 butterfly SHIPs** in the population — fine; just note the audit had more SHIP DNA than registered hyps. Stress covered the registered set.
3. **Score 4/5 is fair, not 5/5:** gap closed + decisive falsify, but zero L1 progress and butterfly remains a BS proxy without surfaces/pin realism. Do not inflate.
4. **Do not polish assumed butterfly IV/width next** after this cost collapse — same lesson as calendars/diagonals. Next class (debit vertical) or observed-surface realism, not knob thrash on rejected butterflies.
5. **Iron butterfly** correctly left as remaining gap; do not conflate long-call butterfly scaffold with credit iron-fly income.

## Judgment

Keep executor evidence and capital labels. No overclaim found on L0 / no-promote / B4 rejects. NEXT seed is the right coverage-gap move (income map gap: debit_vertical still no sim).

PROGRESS TYPE: **P1 + P3**
SCORE: **4/5** (challenger agrees)
HONEST READINESS: **L0 BUILD only** — no L1, no LIVE_PACKET, capital path unchanged (`b195f5fe` quality example only).

## Merged NEXT SEED (one line)

Next BUILD only: implement a minimal defined-risk debit-vertical simulator (bull call / bear put) with synthetic smoke, then one focused evolve + B3/B4; reject unless non-vacuous after-cost and competitive with `b195f5fe` on max loss / window max DD. No assumed-surface polish first if cost-fragile; no shadow/live.

GATES: none
MOA_CHALL_DONE

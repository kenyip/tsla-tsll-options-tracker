# MOA challenger critique — 2026-07-11T0400 (Grok 4.5)

Role: read-only judgment. No evolve --apply. No broker / live / shadow arm.

## Orient

- Prior NEXT (0200 merge): minimal debit-vertical sim + focused evolve + B3/B4 reject-unless competitive with `b195f5fe`.
- Executor: Axis E / P1+P3 — built `debit_vertical_sim` (bull call + bear put), research run24, focused pop36, registered eight candidates, dated B3+B4; all 5% B4 REJECT; L0; NEXT = PCS entry-weekday time slices.
- Phase: BUILD · sleeve $3000 · quality leader remains relative only (not L1).

## Evidence verification (read-only)

| Claim | Verified? | Path / note |
|---|---|---|
| Research run24 top composite | YES | `.cache/platform/research_reports/2026-07-11_run24.md` — 23/23; top TSLL, SMCI, MU, TSLA, PLTR, AAPL, AMD, ARM |
| Evolve audit pop36 applied | YES | `.cache/platform/evolve_audit.jsonl` @ `2026-07-11T11:04:47+00:00` — applied=true, n_population=36, n_ship=9, n_null=18, n_reject=7 |
| Eight debit-vertical hyps created | YES | created: `2f31bb16,e850d421,c3e6309d,6a5e3ed0,95b54b98,ee74daa9,75556a20,b0147ff8` |
| Sim + catalog wiring | YES | `trader_platform/research/debit_vertical_sim.py`; catalog `bull_call_debit_spread` / `bear_put_debit_spread`; evolve/smoke dispatch present |
| Coverage gap closed in scoreboard | YES | `income-coverage-LATEST.md` (0409) — 6 bull-call + 2 bear-put candidates; gap text = realism missing, not “no sim” |
| Cost lab preferred + all debit B4 fail | YES | `stress_cost_lab_2026-07-11T0400.json` — preferred=`b195f5fe`; all eight debit `cost_hold=false` / fragile@5% |
| Regime lab metrics table | YES | `stress_regime_lab_2026-07-11T0400.json` — 9 hyps; dense-neg / window max DD / regime_hold match executor table |
| Leader 5% soft loss not L1 | YES | slip5 n=13 / pnl=−18.32 / NULL; cost_hold soft; regime_hold=true; ml=76.32; window max DD=74.85 |
| Best vanity mid-mark MU bull call | YES | baseline n116 / +2303.91 SHIP → slip5 n126 / −15146.17 REJECT; ml=232.45; window max DD=569.66 |
| No capital / live / shadow promote | YES | statuses remain candidate; readiness L0 BUILD |

### Recomputed quality table (from lab JSON)

| hyp | structure | full n/pnl/verdict | ml | win max DD | dense-neg | B3 | 5% n/pnl/verdict | B4 |
|---|---|---:|---:|---:|---:|---|---:|---|
| b195f5fe | PCS TSLL | 57 / +115.90 / SHIP | 76.32 | 74.85 | 5 | hold | 13 / −18.32 / NULL | soft |
| 2f31bb16 | MU bull call | 116 / +2303.91 / SHIP | 232.45 | 569.66 | 7 | hold | 126 / −15146.17 / REJECT | fail |
| e850d421 | XOM bull call | 111 / +662.70 / REJECT | 223.08 | 893.16 | 7 | fail | 83 / −2870.08 / REJECT | fail |
| c3e6309d | XOM bull call | 111 / +368.83 / SHIP | 129.37 | 479.92 | 7 | hold | 75 / −3480.39 / REJECT | fail |
| 6a5e3ed0 | XOM bull call | 95 / −51.28 / NULL | 121.00 | 517.41 | 6 | hold | 67 / −2997.52 / REJECT | fail |
| 95b54b98 | TSLA bull call | 85 / +1413.09 / SHIP | 248.73 | 555.99 | 6 | hold | 180 / −37814.21 / REJECT | fail |
| ee74daa9 | PLTR bear put | 118 / −1525.93 / REJECT | 148.37 | 1062.19 | 13 | fail | 251 / −33462.54 / REJECT | fail |
| 75556a20 | TSLL bull call | 63 / +26.60 / NULL | 78.72 | 196.71 | 9 | hold | 54 / −1247.26 / REJECT | fail |
| b0147ff8 | PLTR bear put | 129 / −1502.75 / REJECT | 149.01 | 936.75 | 17 | fail | 173 / −18968.34 / REJECT | fail |

Cadence inflation under per-leg adverse slip (e.g. MU 116→126, TSLA 85→180) is real sensitivity, not a ranking excuse. Executor correctly refused mid-mark SHIP vanity.

## RUBRIC

1. Income goal honesty — **PASS** — $3k sleeve, defined-debit risk, after-cost reject; no vanity promote of +$2k MU mid marks.
2. Multi-structure search vs tunnel — **PASS** — closed prior debit-vertical gap across MU/XOM/TSLA/PLTR/TSLL; not single-leg thrash; not re-polish TSLL PCS knobs.
3. Time bias axis — **PASS** — not this wake’s build; deferred with concrete NEXT (weekday slices on existing time grid). Prior DTE×target×stop lab remains.
4. Direction/regime bias — **PASS** — bull-call vs bear-put DNA + B3 windows; prior direction scoreboard still stands; stand-aside on regime in sim filters.
5. Sims actually run — **PASS** — research + evolve_audit + dated regime/cost JSON + sim module paths all present; metrics recompute match.
6. Quality bar B3+B4 before capital — **PASS** — all eight non-vacuous 5% REJECT; none beat ml/window-DD leader; leader itself not L1.
7. ONE closed NEXT seed — **PASS** — PCS time-bias entry-weekday slices then B3+B4 only non-vacuous 5% winners vs `b195f5fe`.
8. No live/shadow promotion — **PASS**.

**TOTAL: PASS 8/8**

## Nits (non-blocking)

1. **“Focused” evolve is partial.** Audit population still mixed IC / short_put / wheel / CCS alongside debit verticals (structure×verdict counts). Registered residue is clean (8 debit hyps only) and those were what got B3+B4 — acceptable, but wording should not imply exclusive structure filter.
2. **Evolve symbols ≠ research top-8 list.** Research top: TSLL, SMCI, MU, TSLA, PLTR, AAPL, AMD, ARM. Evolve symbols: TSLL, SMCI, PLTR, NFLX, BAC, XOM, MU, TSLA. Not a falsify failure; note for honesty when claiming “top 8”.
3. **Scaffold-chain fatigue is real.** Calendar → diagonal → butterfly → debit vertical all cost-fragile under BS proxy. NEXT correctly pivots to time-axis (P2) on the only relative quality DNA rather than iron-butterfly thrash; do not retune assumed BS marks on rejected debit verticals.
4. **build-monitor-LATEST** may still show debit_vertical unchecked; coverage LATEST already closed — cosmetic only.

## Judgment

Keep executor evidence. Progress **P1+P3 score 4/5**. Honesty **L0 BUILD only**. Capital path unchanged: `b195f5fe` relative quality example (soft cost_hold ≠ after-cost edge). Debit-vertical class = research-only until observed surfaces + non-vacuous after-cost edge.

**NEXT (kept, one seed):** extend `scripts/pcs_time_bias_grid.py` with entry-weekday slices; B3+B4 only non-vacuous 5%-cost winners; compare ml/window-DD vs `b195f5fe`. Paper/research only.

MOA_CHALL_DONE

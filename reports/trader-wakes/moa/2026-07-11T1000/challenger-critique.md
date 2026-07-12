# MOA challenger critique — 2026-07-11T1000 (Grok 4.5)

Role: read-only judgment. No evolve --apply. No broker / live / shadow arm.

## Orient

- Prior NEXT (0400 merge): extend `pcs_time_bias_grid` with entry-weekday slices; B3+B4 only non-vacuous 5% winners vs `b195f5fe`.
- Executor: Axis B / P2+P3 — built entry-weekday gating + 216-cell mid/5%-slip grids on leader; free pop36; dated B3+B4 on leader + four new defined-risk SHIPs + two time variants; quality table; L0; NEXT multi-hyp cost-aware PCS/CCS time grid.
- Phase: BUILD · sleeve $3000 · quality leader remains relative only (not L1).

## Evidence verification (read-only)

| Claim | Verified? | Path / note |
|---|---|---|
| Research run25 23/23 | YES | `.cache/platform/research_reports/2026-07-11_run25.md` |
| Composite top list as written | **NO — nit** | Actual top8: TSLL, SMCI, **MU**, TSLA, PLTR, AAPL, AMD, ARM (QQQ is #9). Executor wrote TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ (skipped MU). |
| Evolve pop36 applied @ 17:01Z | YES | `evolve_audit.jsonl` @ `2026-07-11T17:01:43+00:00` — applied=true, n_population=36, n_ship=6, n_null=15, n_reject=9 |
| Evolve symbols = research top8 | **NO — nit** | Actual evolve symbols: TSLL, SMCI, PLTR, NFLX, BAC, XOM, MU, TSLA (not AAPL/AMD/ARM/QQQ) |
| Six SHIPs / four defined-risk + two toys | YES | created: BAC diagonal `8aa2a33b`, PLTR butterfly `db859f1f`, TSLL roll_defend `9980e005`, XOM PCS `2026b890`, TSLL short_dte `3fce54b7`, TSLA bear-put `f1217f66` |
| entry_weekdays in pcs_sim + time grid | YES | `trader_platform/research/pcs_sim.py` `_entry_weekdays`; `scripts/pcs_time_bias_grid.py` weekday slices; tests present |
| 216-cell mid + 5% grids | YES | `time_bias_weekday_lab_*` / `time_bias_weekday_cost5_*` ranked len=216 (4 DTE × 3 PT × 3 stop × 6 weekday) |
| Thu 14d PT65 mid SHIP / 5% vacuous | YES | mid: n20 / +270.26 SHIP; cost5: n0 / 0 NULL zero_trades |
| All-day 30d PT35 non-vacuous@5% | YES | cost5: n21 / +10.52 SHIP; exact B3 window DD 97.14 / dense-neg 7; B4 hold |
| Quality bar table + l1=[] | YES | `quality_bar_lab_2026-07-11T1000.json` — all seven rows match executor table |
| New DR SHIPs B3/B4 rejects | YES | regime+cost lab JSON: BAC/PLTR/XOM B3 hold + B4 fail; TSLA debit B3 fail + B4 fail |
| Leader still below L1 | YES | ml 76.32 / win DD 74.85 / dense 5 / B3 hold / slip5 n13 −18.32 NULL soft cost_hold |
| Coverage weekday gap closed | YES | `income-coverage-LATEST.md` — time-bucket: DTE/PT/stop + entry-weekday built; session-time missing |
| No capital / live / shadow promote | YES | L0 BUILD; 30d variant unregistered; readiness NEXT multi-hyp only |

### Recomputed quality table (from lab JSON)

| hyp / variant | ml $ | window DD $ | dense neg | B3 | 5% n / pnl $ | decision |
|---|---:|---:|---:|---|---:|---|
| TSLL PCS `b195f5fe` | 76.32 | 74.85 | 5 | hold | 13 / −18.32 | RELATIVE_LEADER_BELOW_L1_AFTER_COST_NEGATIVE |
| BAC diagonal `8aa2a33b` | 296.99 | 313.08 | 4 | hold | 99 / −1412.77 | REJECT_COST_AND_ML_DD |
| PLTR butterfly `db859f1f` | 28.18 | 55.28 | 10 | hold | 515 / −31299.46 | REJECT_BASELINE_AND_COST |
| XOM PCS `2026b890` | 200.08 | 314.41 | 5 | hold | 41 / −875.04 | REJECT_COST_AND_DD |
| TSLA bear-put `f1217f66` | 293.77 | 1038.01 | 11 | fail | 118 / −22003.94 | REJECT_REGIME_COST_AND_DD |
| TSLL Thu 14d / PT65 | 75.17 | 27.43 | 0 | hold | 0 / 0.00 | REJECT_VACUOUS_5PCT_ZERO_TRADES |
| TSLL all-day 30d / PT35 | 74.54 | 97.14 | 7 | hold | 21 / +10.52 | REJECT_L1_WINDOW_DD_AND_DENSE_NEG_WORSE_THAN_LEADER |

`l1_hyp_ids=[]`. Executor correctly used **B3 window max_dd / dense-neg** for L1 (not full-history grid max_dd alone — e.g. 30d cost5 grid max_dd 63.01 would mislead).

## RUBRIC

1. Income goal honesty — **PASS** — $3k / after-cost; refused vacuous Thu winner and non-competitive 30d +$10.52 row; no vanity capital seat.
2. Multi-structure search vs tunnel — **PASS** — weekday time lab + falsify across diagonal/butterfly/PCS/debit; free pop36 still mixed single-leg SHIP toys but not promoted (nit only).
3. Time bias axis — **PASS** — entry-weekday is a real axis now (sim gate + 216 mid + 216 cost5 + exact B3/B4 on two variants). Session-time still open gap (honest).
4. Direction/regime bias — **PASS** — not this wake’s primary build; deferred with existing direction scoreboard (0036) + B3 windows on all falsified rows. Explicit Axis B choice is fine.
5. Sims actually run — **PASS** — research + evolve_audit + dated regime/cost/time/quality JSON; metrics recompute match.
6. Quality bar B3+B4 before capital — **PASS** — all new DR SHIPs fail; 30d non-vacuous after-cost still loses ml/dd density bar; leader not L1.
7. ONE closed NEXT seed — **PASS** — multi-hyp cost-aware PCS/CCS time grid; B3 only non-vacuous@5%; reject unless DD≤74.85 and dense-neg≤5.
8. No live/shadow promotion — **PASS**.

**TOTAL: PASS 8/8**

## Nits (non-blocking)

1. **Research “top eight” misstated.** Run25 top8 includes MU #3 and excludes QQQ. Evolve symbols were a different eight (NFLX/BAC/XOM in; AAPL/AMD/ARM/QQQ out). Same honesty nit as 0400 — not a falsify failure.
2. **Free-catalog pop36 still emits undefined-risk single-leg SHIP toys.** Executor did not elevate them; still prefer defined-risk structures or structure filters when the loop is P2/P3 on credit spreads.
3. **Do not register the 30d row.** Non-vacuous +$10.52 @5% is interesting research residue only; denser-neg (7>5) and window DD (97.14>74.85) fail L1 by the stated rule.
4. **Direction axis not advanced this wake** — acceptable under Axis B; multi-hyp time NEXT should include CCS (direction complement) not only more TSLL PCS knobs.

## Judgment

Keep executor evidence. Progress **P2+P3 score 4/5** (weekday gap closed + honest quality rejects; no L1). Honesty **L0 BUILD only**. Capital path unchanged: `b195f5fe` relative quality example (soft cost_hold ≠ after-cost edge).

**NEXT (kept, one seed):** multi-hyp cost-aware time grid across registered PCS/CCS candidates; B3 only rows with non-vacuous positive 5% results; reject unless window DD ≤ $74.85 and dense-negative windows ≤ 5. Paper/research only.

MOA_CHALL_DONE

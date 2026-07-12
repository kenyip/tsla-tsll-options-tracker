# MoA challenger critique — 2026-07-10T1938

**Role:** CHALLENGER (GPT 5.6 Sol) — read-only judgment
**Phase:** BUILD · Sleeve USD 3000 · paper/research only

## Overall verdict

**PASS (8/8, with merge tightening).** The executor ran a genuine eight-symbol, multi-structure search, falsified the only new defined-risk SHIP against dated B3/B4 evidence, and rejected its attractive full-history dollars because its regime and drawdown profile was much worse than the relative leader. No new capital-path edge was found.

## Rubric

| # | rubric | result | one-line judgment |
|---|---|---|---|
| 1 | Income goal honesty | **PASS** | MU PCS `95315a65` is `fit_3k` at 1 lot (full max loss $193.44), but the executor rejects its +$689.84 full-history SHIP as vanity after a −$409.31 worst dense window and $499.57 window DD; no steady-income claim is made. |
| 2 | Multi-structure search vs tunnel | **PASS** | The audit contains 36 real evaluations across eight symbols: 10 PCS, 8 CCS, 10 IC, 7 short-put toys, and 1 wheel; only PCS produced a defined-risk SHIP, while CCS/IC failure is reported rather than hidden. |
| 3 | Time bias as real axis or explicit deferral | **PASS — deferred gap** | No comparative DTE/hold/timing grid was run; the executor explicitly leaves the time-bucket scoreboard unresolved and defers a dedicated time-grid/build wake instead of pretending the `long_dte=14` mutant proves time edge. |
| 4 | Direction/regime bias as real axis or explicit deferral | **PASS** | Bull-put PCS, bear-call CCS, and neutral IC were actually simulated; CCS/IC produced no SHIP in this population, and the new PCS then failed regime hold, so stand-aside/rejection remained valid outputs. |
| 5 | Sims actually run | **PASS** | Verified `.cache/platform/evolve_audit.jsonl` at `2026-07-11T02:34:18+00:00`, `.cache/platform/stress_regime_lab_2026-07-10T1938.json`, and `.cache/platform/stress_cost_lab_2026-07-10T1938.json`; the JSON contains the cited per-hyp metrics. |
| 6 | Quality bar / B3+B4 before capital talk | **PASS** | Fresh B3/B4 compare `95315a65`, parent `55c7323a`, and leader `b195f5fe`; the new MU mutant fails regime hold and loses its edge under cost, while its max loss/DD materially exceed the leader. |
| 7 | ONE closed NEXT seed | **PASS after merge tightening** | The operative seed is one conditional RTH B6 evaluation (`OPEN_PCS` or exact filter-driven `STAND_ASIDE`); the executor's non-seed optional BUILD menu is removed from merged residue. |
| 8 | No live/shadow promotion | **PASS** | No broker, live arm, shadow promotion, or live packet occurred; phase remains BUILD and B6 remains partial. |

## Evidence judgment

| hyp | structure | 1-lot full max loss | full history | B3 | B4 | challenger disposition |
|---|---|---:|---|---|---|---|
| TSLL `b195f5fe` | PCS | $76.32 | 57 trades, +$115.90, DD $78.39 | hold; worst dense −$54.30, window DD $74.85 | soft hold; 5% slip NULL/−$18.32 | **Keep only as relative leader and sole B6 target; not proven steady income or live-ready.** |
| MU `95315a65` | PCS | $193.44 | 122 trades, +$689.84, DD $586.79 | **fail**; 6 dense negative windows, worst −$409.31, window DD $499.57 | soft label only; 5% slip NMD/−$64.75 | **Reject capital path; retain research-only.** It is fundable at 1 lot but fails quality. |
| MU `55c7323a` | PCS | $193.91 | 133 trades, +$784.73, DD $586.79 | **fail**; same worst window/DD as mutant | **fail**; 5% slip NMD/−$192.58 | **Reject capital path; retain research-only.** |

## Challenges and merge actions

1. **Do not overread `cost_hold=true`.** For `95315a65`, the 5% result is `NEEDS_MORE_DATA/−$64.75`; this is cost-collapse under a permissive soft rule, not durable after-cost income.
2. **Keep “quality leader” explicitly relative.** `b195f5fe` survives this comparison, but 5% slip is still NULL/negative and B6 is incomplete.
3. **Time-axis coverage remains open.** This wake chose structure rotation plus falsification, which is allowed, but it did not establish a DTE, hold-duration, weekday, or session effect.
4. **CCS/IC NULLs are useful falsification, not coverage closure.** They show this population did not find a directional/neutral edge; they do not prove those classes are exhausted.
5. **Use only the single RTH B6 seed.** Remove the optional later menu from the merged NEXT residue; future BUILD wakes can independently choose the documented time/sim-class gap.
6. **Readiness NEXT is already correct.** No readiness patch is justified.

No evolve `--apply`, broker action, paper mutation, registry mutation, or status promotion was performed by the challenger.

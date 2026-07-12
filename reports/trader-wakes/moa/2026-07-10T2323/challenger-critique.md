# MoA challenger critique — 2026-07-10T2323 (Grok 4.5)

PHASE: BUILD · SLEEVE: 3000 · ROLE: read-only judgment
EXECUTOR: GPT 5.6 Sol · AXIS claimed: E (diagonal_spread sim) + P3 falsify

## Verdict

**PASS 8/8** on rubric. Keep executor evidence and capital labels.
Progress **P1 + P3**, score **4/5**, honest readiness **L0 BUILD only** — accepted.
No L1, no capital-path expansion, no shadow/live/arm.

## Rubric

| # | Check | Result | One line |
|---|---|---|---|
| 1 | Income goal honesty | **PASS** | $3k / steady-income framing; diagonal after-cost SHIP not sold as income edge; leader still below L1 soft-loss@5%. |
| 2 | Multi-structure vs tunnel | **PASS** | New sim class (not single-leg pop thrash); stress set spans PCS / diagonal / calendar; free pop still mixed but not monomania. |
| 3 | Time bias axis | **PASS** | Not the primary axis this wake; deferred honestly via NEXT = chronological OOS + entry-density (not weekday polish). |
| 4 | Direction/regime axis | **PASS** | Bullish long-call diagonal + bear stand-aside coded; B3 regime lab run; full direction scoreboard still partial/deferred. |
| 5 | Sims actually run | **PASS** | Paths verified: run20, evolve 06:27Z, diagonal baseline, stress regime/cost lab JSON, hyp registry candidate. |
| 6 | Quality bar B3+B4 | **PASS** | Clear promote/reject: d1017453 fails L1 on ml/dd + recent density despite non-vacuous 5% SHIP. |
| 7 | ONE closed NEXT | **PASS** | Single BUILD seed: exact-DNA OOS + density gate on d1017453; reject-if-empty/fragile; no IV retune-first. |
| 8 | No live/shadow promote | **PASS** | Status candidate/testing only; readiness L0; no broker/agentic/arm language as action. |

## Verified metrics (read-only)

Sources:
- `.cache/platform/research_reports/2026-07-11_run20.md`
- `.cache/platform/evolve_audit.jsonl` @ `2026-07-11T06:27:54+00:00`
- `.cache/platform/diagonal_baseline_lab_2026-07-10T2323.json` (valid JSON + trailing `\\n` junk)
- `.cache/platform/stress_regime_lab_2026-07-10T2323.json`
- `.cache/platform/stress_cost_lab_2026-07-10T2323.json`
- `trader_platform/data/hypotheses.yaml` → `hyp_dna_smci_diagonal_spread_d1017453` status **candidate**
- `trader_platform/research/diagonal_sim.py` present; evolve/smoke/DNA wiring grepped

| Hyp | 1-lot ml | full DD | window max DD | dense-neg (n≥3) | B3 | 5% slip | B4 note | Judgment |
|---|---:|---:|---:|---:|---|---|---|---|
| TSLL PCS `b195f5fe` | 76.32 | 78.39 | 74.85 | 5 | soft hold | n13 / −18.32 / NULL | soft_loss_at_5pct | Relative leader; **not L1** |
| SMCI diagonal `d1017453` | 294.03 | 153.30 | 153.30 | 0 | soft hold (sparse) | n24 / +107.35 / SHIP | survives_5pct | First non-vacuous diagonal; **fails L1** ml/dd + recency |
| MU PCS `55c7323a` | 193.91 | 586.79 | 499.57 | 6 | **fail** (worst −409.31) | n3 / −192.58 | fragile | Reject capital path |
| SMCI cal `256b2877` | 224.42 | 406.96 | 380.63 | 4 | soft hold | n121 / −1784.14 / REJECT | fail | Reject capital path |
| TSLL cal `5a83a18a` | 120.48 | 181.01 | 181.01 | 4 | soft hold | n97 / −814.32 / REJECT | fail | Reject capital path |

Entry density (baseline + `SMCI_diagonal_trades.json`): **2022:13, 2023:18, 2024:1, 2025:0, 2026:0** — matches executor sparsity claim.
TSLL seed diagonal: n47 / +98 / DD 435 — correctly called weak/high-DD, not registered as challenger.

Evolve pop36 @ 06:27Z: 3× `diagonal_spread` rows (TSLA×2, MU×1) all **NULL zero_trades** under $300 debit gate; no diagonal SHIP from random pop. Created hyps were calendars/short-dte/CSP — SMCI diagonal registered via **seed DNA path** after pop (executor honest).

## Challenges (non-blocking)

1. **Top-eight wording drift:** run20 composite ranks **MU #3** (oversized naked); evolve symbols were `SMCI,PLTR,TSLL,NFLX,BAC,XOM,MU,TSLA`, not AAPL/AMD/ARM/QQQ. Multi-symbol work is real; do not restate “top eight = AAPL…” as fact.
2. **dense_neg=0 is not a green flag:** soft B3 hold with worst_window_pnl=0 and no 2025–26 entries is **vacuous density**, not superior regime robustness. Executor already treated it as sparse — keep that framing.
3. **Baseline JSON hygiene:** file ends with escaped newline junk; load with raw_decode / strip. Not a metrics issue.
4. **Proxy honesty retained:** diagonal note correctly states BS IV multipliers, no early assignment, no observed surfaces. Do not promote on after-cost SHIP alone.

## What to keep / change

| Item | Action |
|---|---|
| Capital path = `b195f5fe` only (relative) | **KEEP** |
| SMCI diagonal candidate/research-only | **KEEP** |
| MU / calendars capital reject | **KEEP** |
| Score 4/5, L0, P1+P3 | **KEEP** |
| NEXT: exact-DNA OOS + entry-density on d1017453; reject-unless recent non-vacuous + after-cost; no IV retune-first | **KEEP** (merged seed) |
| Live / shadow / agentic | **NONE** |

## Challenger progress note

Executor chose high-leverage **P1 coverage gap** after calendar B4 death spiral — correct supersession of IV retune thrash. Closed loop with real code + stress + reject. Remaining gap is realism/OOS, not missing “try harder on assumed IV.”

GATES: none
MOA_CHALL_DONE

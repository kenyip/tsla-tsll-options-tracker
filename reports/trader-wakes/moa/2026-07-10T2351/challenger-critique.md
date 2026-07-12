# MoA challenger critique — 2026-07-10T2351 (Grok 4.5)

PHASE: BUILD · SLEEVE: 3000 · ROLE: read-only judgment
EXECUTOR: GPT 5.6 Sol · AXIS claimed: D / P3 quality falsify (prior diagonal OOS gate + pop36 DR SHIP reject)

## Verdict

**PASS 8/8** on rubric. Keep executor evidence, capital labels, and L0 honesty.
Progress **P3 quality falsify** (with tested OOS tooling that closed the prior NEXT), score **4/5**, readiness **L0 BUILD only** — accepted.
No L1, no capital-path expansion, no shadow/live/arm.

## Rubric

| # | Check | Result | One line |
|---|---|---|---|
| 1 | Income goal honesty | **PASS** | $3k sleeve; vanity SMCI n≈967 SHIP rejected; leader and BAC called after-cost negative; no real-account readiness claim. |
| 2 | Multi-structure vs tunnel | **PASS** | Closed prior diagonal gate + free-catalog pop36 (PCS/CCS/IC/calendar/single-leg present); stress focused on new DR SHIPs — not single-leg thrash. |
| 3 | Time bias axis | **PASS** | Not primary this wake; deferred honestly (time grid already exists; this wake finished density/OOS reject, not weekday polish). |
| 4 | Direction/regime axis | **PASS** | B3 windows used for falsify; full PCS-vs-CCS-vs-IC scoreboard explicitly deferred to ONE NEXT seed. |
| 5 | Sims actually run | **PASS** | Verified paths: run21, evolve `2026-07-11T06:52:27Z`, diagonal OOS JSON, regime/cost lab JSON, script+unittest present. |
| 6 | Quality bar B3+B4 | **PASS** | Clear promote/reject table; none beat ml/dd + non-vacuous after-cost; soft cost_hold ≠ L1. |
| 7 | ONE closed NEXT | **PASS** | Single BUILD seed: apples-to-apples PCS/CCS/IC direction-regime scoreboard vs `b195f5fe` bar. |
| 8 | No live/shadow promote | **PASS** | New hyps remain `candidate`; leader `testing`; readiness L0; no broker/agentic/arm. |

## Verified metrics (read-only)

Sources:
- `.cache/platform/research_reports/2026-07-11_run21.md` (22/23 ok; NFLX error)
- `.cache/platform/evolve_audit.jsonl` @ `2026-07-11T06:52:27+00:00` (applied pop36; symbols TSLL/SMCI/PLTR/BAC/XOM/MU/TSLA/AAPL)
- `.cache/platform/diagonal_oos_lab_2026-07-10T2351.json`
- `.cache/platform/stress_regime_lab_2026-07-10T2351.json` (5 hyps)
- `.cache/platform/stress_cost_lab_2026-07-10T2351.json` (preferred_under_cost = b195f5fe)
- `scripts/diagonal_oos_stress.py` + `tests/test_diagonal_oos_stress.py`
- registry statuses: b195f5fe **testing**; f94a3a37 / b16ca012 / e39fb210 / 55c7323a / d1017453 **candidate**

### Diagonal exact-DNA OOS (`d1017453`)

| Split | n | pnl | max_dd | entry_years |
|---|---:|---:|---:|---|
| train 2022-08-22→2024-12-16 | 32 | +679.80 | 153.30 | 2022:13, 2023:18, 2024:1 |
| train @5% slip | 24 | +107.35 | 145.73 | 2022:11, 2023:13 |
| test 2024-12-17→2026-07-10 | **0** | 0 | 0 | {} |
| test @5% slip | **0** | 0 | 0 | {} |

**Judgment confirmed:** recent holdout is vacuous → capital-path reject; do not retune assumed IV first.

### B3 + B4 quality table (confirmed)

| Hyp | 1-lot ml | window max DD | dense-neg (n≥3) | B3 regime_hold | 5% slip | B4 note | Judgment |
|---|---:|---:|---:|---|---|---|---|
| TSLL PCS `b195f5fe` | 76.32 | 74.85 | 5 | True | n13 / −18.32 / NULL | soft_loss_at_5pct | Relative leader; **not L1** |
| BAC PCS `e39fb210` | 80.19 | 130.15 | 8 | True | n58 / −55.97 / NULL | soft_loss_at_5pct | Closest ml; worse DD/density + more after-cost loss; reject capital path |
| SMCI PCS `f94a3a37` | 164.22 | 622.99 | 3 | True | n966 / −517.65 / REJECT | fragile | Baseline vanity; reject |
| AAPL PCS `b16ca012` | 205.99 | 330.88 | 8 | True | n141 / −1159.38 / REJECT | fragile | Cost-fragile; reject |
| MU PCS `55c7323a` | 193.91 | 499.57 | 6 | **False** | n3 / −192.58 / NEEDS_MORE_DATA | large_loss fragile | Reconfirmed reject |
| SMCI diagonal `d1017453` | 294.03 train | 153.30 train | holdout n0 | historical only | holdout n0 | vacuous holdout | Exact-DNA recent reject |

No DNA reaches L1: need non-vacuous **positive** after-cost + dense B3 + competitive ml/dd. Soft cost_hold with NULL@5% is not an income edge.

## Challenges (non-blocking)

1. **Evolve symbol set ≠ research top-8 composite.** Run21 top8 = TSLL/SMCI/MU/TSLA/PLTR/AAPL/AMD/ARM; evolve used XOM instead of AMD/ARM (and dropped NFLX for parse fail). Multi-name work is real — do not restate “top eight evolved” as AMD/ARM coverage this wake.
2. **Pop36 still mixed with single-leg + calendar SHIP toys** (10 SHIP rows; calendar `34f2b2c5` re-SHIPPED). Executor correctly did not re-litigate calendar capital path — keep that discipline; do not thrash free single-leg next.
3. **Soft regime_hold on SMCI f94a3a37 is not comfort:** worst dense window −282.53 and window max DD 622.99 while regime_hold=true. Executor rejected on ml/dd + B4 — keep that framing (soft B3 ≠ quality).
4. **Readiness B′ row for `d1017453` still reads “B4 pass strong / fails L1 on ml/dd”** from the 2323 baseline era; top-of-file phase text is correct (holdout n0). NEXT is fine — no NEXT patch required. Optional future polish: B′ note “exact-DNA holdout n0.”

## What to keep / change

| Item | Action |
|---|---|
| Capital path = `b195f5fe` only (relative, below L1) | **KEEP** |
| All new PCS + diagonal capital reject | **KEEP** |
| Score 4/5, L0, P3 | **KEEP** |
| NEXT: PCS-vs-CCS-vs-IC direction/regime scoreboard | **KEEP** (merged seed) |
| Live / shadow / agentic | **NONE** |

## Challenger progress note

Executor correctly took prior NEXT (exact-DNA OOS on `d1017453`) instead of thrashing another sim scaffold or single-leg pop. Closed loop: tooling + verified reject + population DR falsify. Still no L1 income DNA — honest.

GATES: none
MOA_CHALL_DONE

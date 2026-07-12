# MOA BUILD lab challenger critique — 2026-07-11T1842

WAKE: 2026-07-11T1842 PDT
ROLE: Grok 4.5 challenger (read-only judgment)
PHASE: BUILD · SLEEVE: 3000
MODE: paper/research only — no evolve --apply, no broker, no arm, no shadow promote

## Executive judgment

**PASS 8/8.** Executor closed a real coverage-gap plumbing loop (archive → date-aware `ArchivedContractGridProvider` + replay counters + fail-closed missing date), then ran one free pop36 and dated B3+B4 that honestly rejects all L1 seats. Capital path stays empty. L0 BUILD only. Score 4/5 is earned, not vanity.

## Evidence verification (read-only)

| Claim | Check | Result |
|---|---|---|
| Provider + tests | `trader_platform/research/contract_grid_provider.py`, `tests/test_contract_grid_provider.py`, `scripts/contract_grid_replay.py` | Present; NY market-date mapping, synthetic exclusion, counters, fail-close |
| Replay lab | `.cache/platform/contract_grid_replay_lab_2026-07-11T1842.json` | 70 obs; 2026-07-11 covered (1 exp / call+put / 70 strikes); 2026-07-10 missing; `PASS_COVERED_DATE_FAILS_CLOSED_MISSING_DATE` |
| Evolve | `evolve_audit.jsonl` `ts=2026-07-12T01:45:41+00:00` | applied pop36; symbols TSLL/SMCI/PLTR/NFLX/BAC/XOM/MU/TSLA |
| Defined-risk SHIPs stressed | quality/cost/regime lab JSON | MU debit `c060d31e`, NFLX calendar `95ca0370`, MU butterfly `dea7f80f`, former ref `b195f5fe` |
| Metrics match table | quality_bar_lab JSON | Exact match on n/pnl/ml/dd/slip5; `l1_hyp_ids=[]`; `REJECT_ALL_CAPITAL_PATH` |
| B3 soft-hold | stress_regime_lab | All four `regime_hold=true` (soft denseness rule) |
| B4 | stress_cost_lab | Debit n230/−20967.88 REJECT; calendar n131/−1494.01 REJECT; butterfly n626/−45879.62 REJECT; b195f5fe n13/−13.18 NULL soft_hold only |
| Soft preferred_under_cost | cost lab | still tags b195f5fe — **not a seat** (executor correct) |

No uncited metric found in the quality table. No capital-path or live claim.

## Rubric

| # | Check | Verdict | One line |
|---|---|---|---|
| 1 | Income goal honesty ($3k / steady income, not vanity $) | **PASS** | Baseline SHIPs (e.g. MU debit +$2467) rejected after non-vacuous after-cost collapse; readiness L0; no real-account claim |
| 2 | Multi-structure vs tunnel | **PASS** | P1 realism first; free pop36 multi-structure (debit/calendar/butterfly + single-leg toys); not TSLL-PCS polish thrash |
| 3 | Time bias as real axis | **PASS (deferred)** | Not this wake; prior P1 seed higher leverage; session-time still open gap in coverage map |
| 4 | Direction/regime as real axis | **PASS (deferred)** | Used shared B3 windows for falsify only; no new direction scoreboard expansion this wake |
| 5 | Sims actually run (paths) | **PASS** | Replay + evolve 01:45:41Z + dated regime/cost/quality JSON all present; numbers match |
| 6 | Quality bar / B3+B4 before capital talk | **PASS** | Explicit historical bar $76.32/$74.85 only; butterfly competitive proxy ml/dd trap called and rejected (baseline NULL + cost cat.) |
| 7 | ONE closed NEXT seed | **PASS** | Multi-date archive density before provider-backed historical sim; ban proxy evolve while one date |
| 8 | No live/shadow promotion | **PASS** | Paper/research only throughout |

## Challenges (kept short)

1. **Soft `preferred_under_cost` ≠ L1.** Cost lab still prefers b195f5fe; quality bar correctly keeps `l1=[]` and removes capital seat. Do not resurrect a leader from soft NULL@5%.
2. **Butterfly ml/dd trap.** `dea7f80f` meets historical proxy ml/DD ($19.10 / $74.27) but full NULL and 5% catastrophe — correct reject; never promote on risk shape alone without non-vacuous after-cost SHIP.
3. **Free pop36 while archive density = 1 date** is acceptable *once* as synthetic discovery falsify after P1 land, but **further free proxy evolve is thrash** until ≥3 market dates exist. Executor NEXT already states this.
4. **Capture reality check for NEXT.** Current `snapshot_yfinance_option_quotes` defaults to **first expiration only** and `write_observations_csv` is **overwrite (`w`)**, not multi-date append. NEXT must implement all-expiration + append-safe archive, not re-run the one-shot snapshot.

## Progress agreement

- Type: **P1 + P3**
- Score: **4/5** (real plumbing closed + honest falsify; density still missing so not 5)
- Honesty: **L0 BUILD**
- Capital path: **empty** (`l1_hyp_ids=[]`)

## Merged NEXT (one)

Implement append-safe RTH capture of **all available expirations** into the normalized option-quote archive (fix first-expiry-only overwrite path), accumulate **≥3 distinct market dates**, then provider-backed historical entry/coverage restress; **do not free-evolve proxy DNA** while date coverage remains one.

## Gates

none

MOA_CHALL_DONE

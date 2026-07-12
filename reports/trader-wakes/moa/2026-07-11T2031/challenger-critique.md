# MOA BUILD lab challenger critique — 2026-07-11T2031

WAKE: 2026-07-11T2031 PDT
PHASE: BUILD
SLEEVE: 3000
CHALLENGER: Grok 4.5 (read-only)
MODE: paper/research only — no evolve --apply, no broker, no arm

## Executive judgment

**PASS 8/8.** Executor chose the correct highest-leverage loop: fix the evidence substrate before any more DNA. Prior NEXT (append-safe all-expiration multi-date archive) was taken, not superseding thrash. Fail-closed on 1/3 market dates is correct; skipping evolve/B3/B4 is discipline, not underwork. No living quality leader; capital path empty; L0 BUILD honesty holds.

Progress type: **P1 structural realism**
Score: **4/5** (kept)
L0–L4 honesty: **L0 BUILD**

## Rubric

| # | Item | Verdict | One line |
|---|---|---|---|
| 1 | Structural-flaw gate | **PASS** | First-expiry + overwrite path replaced with all-expiration capture, atomic append/dedup, and ≥3 NY market-date gate; tests cover capture/append/density; invalid substrate blocked search |
| 2 | Income goal honesty | **PASS** | No vanity SHIP, no $3k seat claim, absolute L1 gates only, sleeve remains research/paper |
| 3 | Multi-structure vs tunnel | **PASS** | No free single-leg pop36 thrash; substrate work enables all structures; registry population not dirtied |
| 4 | Time bias axis | **PASS** (deferred) | Explicitly not this wake; time grid already built; density gate is prerequisite for honest observed-time cost work |
| 5 | Direction/regime axis | **PASS** (deferred) | Explicitly not this wake; scoreboard exists; no fake direction claims from one-date archive |
| 6 | Sims/tests actually run | **PASS** | Challenger re-ran targeted suite **20/20 OK**; live density/replay/coverage JSON + 600-row archive verified on disk |
| 7 | Living quality bar / B3+B4 | **PASS** | No living leader; `b195f5fe` historical comparator only (0/248 match, DD$88.39 context); no capital-path talk without B3+B4 + after-cost |
| 8 | ONE closed NEXT seed | **PASS** | Single seed: next distinct RTH date → append all-exp TSLL → verify 2/3; no evolve/provider hist before 3/3 |

## Evidence verification (challenger)

| Claim | Check | Result |
|---|---|---|
| All-expiration default capture | `snapshot_yfinance_option_quotes` uses full `ticker.options` when expiration omitted; test requests every listed exp | **Match** |
| Append + dedup + atomic write | `write_observations_csv(append=True)` loads prior, set-dedups, temp-file replace; idempotent test | **Match** |
| Density gate 3 dates | `summarize_archive_density` → `provider_backtest_eligible=false` on 1 date; density JSON rejects `insufficient_market_date_density` | **Match** |
| Live archive | `TSLL_archive.csv` 600 rows, 12 exps, call+put, NY market date `2026-07-11` only; 0 identical dups | **Match** |
| Replay lab | current date covered (12 exps / both rights); prior date fail-closed; counters 1/2 covered | **Match** |
| Historical comparator | `b195f5fe` 248 required / 0 matched → `REJECT_INSUFFICIENT_COVERAGE` | **Match** |
| Tests | `unittest` 20/20 on observations + contract grid + expiry grid + direction scoreboard | **Match** |
| Evolve skipped | No new evolve audit / new-DNA B3/B4 this stamp; fail-closed stated | **Match** |
| Stale leader language | Coverage LATEST quality leader hint = none; absolute gates in docs/readiness | **Match** |

## Nits (non-blocking)

1. **“600 strikes” wording** — replay JSON `strikes: 600` is observation count (unique exp×type×strike = 600; unique strike prices ≈ 67). Prefer “600 contract rows / N unique strikes” in future residue so nobody treats it as a 600-point listed grid.
2. **Full suite 42/43** — not re-run by challenger; targeted 20/20 confirmed. Accept pre-existing PMCC fixture failure as unrelated if still the only red.
3. **Old 70-row first-expiry file** (`TSLL_2026-07-11T1710.csv`) remains as history; archive path is the living series. Do not overwrite the archive with the thin file.
4. **Same-calendar re-capture risk** — if someone appends again before a new NY session date, density stays 1/3. NEXT already says “next distinct RTH market date”; keep that hard.

## Overclaim scan

| Risk | Found? |
|---|---|
| Capital seat / L1 edge | **No** |
| Soft cost_hold as edge | **No** |
| b195f5fe as living bar/seat | **No** — historical only |
| Provider-backtest eligible from provenance alone | **No** — correctly false at 1 date |
| Invented SHIP / evolve metrics | **No** |
| Live / arm / shadow | **No** |

## Income / $3k posture

Substrate progress only. Steady-income L1 still absent. Absolute gates remain: non-vacuous after-cost SHIP, B3 hold, max_loss ≤$300, window max_dd ≤$75, dense-neg ≤5; then B6 later. Defined-risk preferred; no proxy evolve while archive density is invalid for historical provider use.

## Merged judgment on score

Executor **4/5** is fair: high-leverage structural close, fail-closed, honest L0. Not 5 because income edge coverage did not advance and observed historical calibration remains blocked until dates 2 and 3 exist.

## ONE NEXT SEED (merged)

On the **next distinct New York RTH market date**, run one **all-expiration** TSLL archive append (default, not overwrite) into `.cache/platform/option_quotes/TSLL_archive.csv`, write density summary, and verify `n_market_dates == 2` and still `provider_backtest_eligible=false`. Do **not** evolve, do **not** run provider-backed historical entry simulation, and do **not** claim calibration until **3/3** dates.

Hard stops honored by executor and challenger.

MOA_CHALL_DONE

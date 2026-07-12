# MOA BUILD lab challenger critique — 2026-07-11T1800

WAKE: 2026-07-11T1800 PDT
ROLE: Grok 4.5 challenger (read-only)
PHASE: BUILD · SLEEVE: 3000
MODE: paper/research only — no evolve --apply, no broker, no arm

## Executive judgment

**PASS 8/8.** Executor closed the prior NEXT (exact observed-quote strategy-leg join + fail-closed coverage reject) with real code, tests, and a dated reject artifact; then falsified one free-catalog pop with B3+B4 and a quality table. No L1 claim, no capital-path expansion, no live/shadow promotion. L0 honesty holds.

Progress type: **P1+P3** · score **4/5** · honesty **L0** — **accepted**.

## Rubric

| # | Check | Verdict | One line |
|---|---|---|---|
| 1 | Income goal honesty | **PASS** | Steady-income / $3k framing; `l1_hyp_ids=[]`; leader n13/−$18.32@5% and fixed-cost negativity not sold as edge |
| 2 | Multi-structure vs tunnel | **PASS** | Free pop36 multi-name (TSLL/SMCI/PLTR/NFLX/BAC/XOM/MU/TSLA); falsified calendar/debit/butterfly/IB/CCS + leader; CSP SHIPs labeled research toys |
| 3 | Time bias axis | **PASS** (deferred w/ gap) | Not this wake’s primary axis; session-time still open; NEXT correctly escalates listed-expiry-grid realism (time-adjacent sim bug) |
| 4 | Direction/regime bias | **PASS** (deferred w/ gap) | No new direction scoreboard; B3 soft-hold used as falsify, not promote; direction lab remains prior residue |
| 5 | Sims actually run | **PASS** | Paths verified: run32, evolve `2026-07-12T01:01:26Z`, regime/cost/quality/coverage JSON, quote CSV |
| 6 | Quality bar / B3+B4 | **PASS** | Six-hyp dated B3+B4; soft B4 ≠ after-cost edge called out; no capital seat talk without L1 |
| 7 | ONE closed NEXT seed | **PASS** | Single seed: listed weekly-expiry grid for PCS/CCS/IC → tests → leader B3+B4/coverage restress |
| 8 | No live/shadow promotion | **PASS** | Statuses stay research/testing; GATES none; agentic unarmed |

## Evidence verification (read-only)

| Claim | Check | Result |
|---|---|---|
| Research run32 | `.cache/platform/research_reports/2026-07-12_run32.md` exists | OK |
| Evolve pop36 @ 01:01:26Z | last `evolve_audit.jsonl` row: n_pop=36, n_ship=8, symbols match | OK |
| SHIP set | calendar TSLL, CSPs NFLX/TSLL/PLTR, BAC debit, MU butterfly, NFLX IB, BAC CCS | OK; CSP = toys |
| Exact join + coverage CLI | `option_quote_observations.py` + `scripts/observed_quote_coverage.py`; unittest 5/5 pass | OK |
| Leader coverage reject | required 228 / matched 0 / `REJECT_INSUFFICIENT_COVERAGE` | OK |
| Quote archive | `TSLL_2026-07-11T1710.csv` 70 data rows (+header) | OK |
| Quality metrics | quality_bar JSON matches closeout table (ml/dd/dense/5% n+pnl) | OK |
| B3 soft-holds | all six `regime_hold: true` soft rule; dense-neg 3–8 | OK |
| B4 rejections | calendar n93/−266.85; debit n94/−131.66; MU n626/−45879.62; NFLX IB n291/−19228.35; BAC CCS n1/−42.93; leader n13/−18.32 | OK |
| Soft cost_hold honesty | BAC CCS `cost_hold=true` with n1 and baseline NULL correctly **reject L1** | OK |
| Non-listed expiry diagnosis | unmatched sample includes `2023-12-12` (Tuesday) | OK — supports NEXT |

## Challenges (non-blocking)

1. **Ritual free pop36** — Allowed this wake because prior NEXT required join-then-falsify, and DR multi-structure rows were the judgment targets. Do **not** treat another free single-leg-heavy pop as the next BUILD main axis when expiry-grid realism is the open blocker.
2. **Competitive-looking mid-mark rows are still traps** — NFLX IB window DD $73.25 and MU butterfly ml $19.73 look pretty until non-vacuous 5% cadence collapse; executor rejected correctly — keep that bar, do not retune assumed surfaces.
3. **Archive density alone is not the next win** — Executor’s durable note is right: synthetic `entry_date+DTE` expirations (incl. non-listed weekdays) mean denser current snapshots still fail exact joins. Expiry-grid fix is higher leverage than “capture more TSLL chains tonight.”
4. **Leader is still not income** — `b195f5fe` remains relative ml/dd bar only (soft B3/B4, after-cost negative). Do not re-open capital-path language until L1.

## Time / direction honesty

- **Time:** prior multi-hyp/weekday grids still L0; this wake advanced **expiry selection realism**, not DTE/hold scoreboard. Session-time slices remain open.
- **Direction:** prior shared-window scoreboard still the comparator; this wake used regime stress as reject/hold filter only.

## Capital / readiness

- Phase **BUILD / L0** unchanged.
- `l1_hyp_ids=[]`.
- TOP quality example remains `hyp_dna_tsll_put_credit_spread_b195f5fe` (relative only).
- No patch needed to readiness formal B checks; NEXT already points at listed-expiry grid.

## Merged decision

Keep executor evidence and **keep NEXT seed** (tighten wording only for one closed loop):

> Next BUILD only — make PCS/CCS/IC expiration selection use a listed weekly-expiry grid (Friday / available-expiry abstraction), add regression tests (incl. non-weekday synthetic cases), then re-run `b195f5fe` B3+B4 + exact observed coverage; reject the leader if ml/dd or after-cost quality deteriorates. No archive thrash, no proxy retune, no live/shadow.

## Close

Progress type: P1+P3
Progress score: 4/5 (challenger agrees)
Honesty: L0
GATES: none
MOA_CHALL_DONE

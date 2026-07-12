# MoA BUILD Lab challenger critique — 2026-07-10T2017

ROLE: Grok 4.5 / read-only judgment
PHASE: BUILD · SLEEVE: $3000 · SLOT: evening
HARD STOPS: no evolve --apply; no broker; no live/shadow/arm

## Rubric

| # | Check | Verdict | One line |
|---|---|---|---|
| 1 | Income goal honesty ($3k / steady, not vanity $) | **PASS** | Rejected levered single-leg SHIP toys; refused to seat 7d row on higher full-history $ alone. |
| 2 | Multi-structure search vs tunnel | **PASS** | One free-catalog evolve (10 structures × 8 symbols, pop36) then deliberate recipe-B time grid on registered PCS — not thrash-only TSLL PCS polish. |
| 3 | Time bias as real axis | **PASS** | Real 36-cell DTE×profit_target×dte_stop grid + hold/exit stats; weekday/session correctly left as remaining gap. |
| 4 | Direction/regime bias as real axis | **PASS*** | Not the chosen loop (B not C); B3 soft-hold reconfirm is not a direction scoreboard — axis deferred by choice, not claimed closed. |
| 5 | Sims actually run (paths) | **PASS** | All cited artifacts exist and metrics match (see verify). |
| 6 | Quality bar / B3+B4 before capital path | **PASS** | Leader reconfirmed; 7d challenger not registered; vacuous 5% cost correctly blocks seat. |
| 7 | ONE closed NEXT seed | **PASS** | Single BUILD falsify/reject loop — not a menu. |
| 8 | No live/shadow promotion | **PASS** | paper_only; no status/arm/broker claims. |

\*Direction is **deferred**, not advanced. Acceptable for evening recipe-B; do not treat B3 soft-hold as direction-lab completion.

**Overall: PASS 8/8** (with soft notes below — evidence kept, claims tightened).

## Verify (read-only)

| Claim | Evidence | Check |
|---|---|---|
| Research run16 23/23 | `.cache/platform/research_reports/2026-07-11_run16.md` | OK — top SMCI,MU,TSLA,PLTR,AAPL,AMD,TSLL,ARM; naked fit_3k SMCI+TSLL |
| Evolve pop36 @ `2026-07-11T03:17:52+00:00` three TSLL single-leg SHIPs | `evolve_audit.jsonl` | OK — wheel_assignment + 2× cash_secured_put on TSLL; no PCS/CCS/IC SHIP that stamp |
| Time grid 36 cells on b195f5fe | `time_bias_lab_2026-07-10T2017.json` | OK — grid 7/14/21/30 × 0.35/0.5/0.65 × 1/3/5; n_ranked=36; all SHIP full-hist |
| Top row 7d/35%/stop5 n=37 pnl=158.71 ml=75.80 max_dd=48.33 | same + ranked[0] | OK |
| Leader B3 regime_hold, window max_dd 74.85 | `stress_regime_lab_2026-07-10T2017.json` | OK — summary.regime_hold=true; max_dd_across_windows=74.85; full n=57 pnl=115.9 ml=76.32 |
| Leader B4 soft cost, 5% n=13 NULL −18.32 | `stress_cost_lab_2026-07-10T2017.json` | OK — cost_hold true soft_loss_at_5pct |
| Challenger B3 hold + B4 5% n=0 | `time_bias_challenger_stress_2026-07-10T2017.json` | OK — regime_hold true; slip5 zero_trades; **not registered** |

## Challenges (keep / patch)

1. **Vacuous cost_hold is a bar bug class, not a green light.**
   Challenger cost summary still emits `cost_hold: true` / note `survives_5pct_slip` while slip@5% has **n_trades=0**. Executor judgment is correct (do not promote); systems labeling is wrong. Do not rank any DNA above leader on soft-null / zero-trade “hold.”

2. **Regime_hold for 7d is also soft-sparse.**
   Of 20 ok windows, **14 have zero trades**; worst_window_pnl=0.0; ship density sits in a few 2024–2025 chunks. Soft hold is mechanically true (no dense −400 disasters) but **not** evidence of broad regime coverage. Full-history ml/dd improvement is real; breadth is not.

3. **2% slip still SHIPs (n=23, +92.47); cliff is 2%→5%.**
   Executor table jumps to 5% n=0. Intermediate resilience exists, but $3k income doctrine uses **5% soft bar** — cliff still kills capital-path claim. Optional note only; does not reverse reject.

4. **Time lab is monomania by design (recipe B), not multi-name.**
   Grid is TSLL PCS only. Free evolve covered multi-structure/symbol once; no defined-risk SHIP that pass. Next BUILD after reject should **not** re-grid the same leader knobs without a new axis (direction C, multi-name time grid, or missing sim class E).

5. **Direction axis not closed.**
   Coverage still: “direction-bias scoreboard by regime window — partial.” This wake did not run PCS vs CCS vs IC under bull/bear/neutral. Fine for one-loop discipline; do not mark direction done.

6. **NEXT seed is good; reject path must be first-class success.**
   Executor seed (weekday filter + OOS + non-zero 5% trades or reject) is one closed loop. Prefer: if 5% still n=0 **after at most one** weekday/session code pass, **reject variant and stop** — do not open a multi-wake weekday engineering rabbit hole on a cost-dead short-DTE shape.

7. **No capital-path expansion.** Agreed. `b195f5fe` remains relative quality leader / B6 target. Phase BUILD.

## What executor did well

- Chose recipe **B** after prior wake deferred time bias; shipped real `pcs_time_bias_grid.py` not a digest.
- Ran free-catalog evolve before time tunnel; correctly labeled single-leg SHIP as research toys.
- Falsified best grid row with dated B3+B4; refused registration on vanity full-history.
- ONE NEXT seed; readiness/coverage honesty on weekday/session remainder.

## Durable residue challenger accepts

- `scripts/pcs_time_bias_grid.py` + `time_bias_lab_2026-07-10T2017.json`
- Leader + transient stress JSONs under `.cache/platform/*2017*`
- Capital path unchanged; no promote

GATES: none

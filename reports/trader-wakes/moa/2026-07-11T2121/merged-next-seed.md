# Merged NEXT SEED — 2026-07-11T2121

**Keep executor evidence; challenger tightens constraints and labels.**

## ONE NEXT SEED (BUILD)

Build the smallest paper-only **put ratio backspread** scaffold:

- Legs: sell **1** higher-strike put, buy **2** lower-strike puts (long convexity downside).
- Must implement **closed-form defined max loss** and reject any DNA that leaves naked/undefined short-put residual.
- Wire: `STRUCTURE_CATALOG` + sim + evolve dispatch + B3 + B4 + fixed-dollar per-leg cost.
- First evolve population must be **structure-pure** (no single-leg SHIP pollution in the class verdict).
- **Reject unless** absolute L1 gates: non-vacuous after-cost SHIP, B3 soft-hold, max_loss_usd ≤ 300, window max DD ≤ 75, dense-negative windows ≤ 5; plus non-vacuous $0.01/leg fixed control that is not worse-path vanity.
- Proxy BS only; label observed/provider claims fail-closed until archive density ≥3 NY market dates.
- **Stop rule:** if the class mid-mark SHIPs collapse like broken-wing/symmetric IB under 5% and $0.01/leg, do **not** chain another multi-leg credit scaffold this cycle — pivot to next distinct RTH all-expiration TSLL archive append (density 1→2/3) or a management/time axis on existing defined verticals.

## Parallel (not this seed; not blocking discovery)

- Observed path: on next distinct NY RTH date, append one all-expiration TSLL capture and verify density 2/3; no provider-backed historical sim/evolve before 3/3.
- Soft `preferred_under_cost` and historical `b195f5fe` are **not** capital seats.

## Hard stops

- Paper/research only
- No live / broker / agentic arm / shadow auto-promote
- No capital path without B3+B4 + competitive ml/dd + non-vacuous after-cost

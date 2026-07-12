# Merged NEXT seed — 2026-07-11T0036 MoA

**Source:** executor closeout + Grok challenger (PASS 8/8).
**Phase:** BUILD · **Sleeve:** $3000 · **Honesty:** L0 (no L1)

## ONE NEXT (BUILD only)

Implement a **minimal defined-risk butterfly / iron-butterfly** sim scaffold (catalog entry + daily-bar BS or intrinsic multi-leg sim + defined debit/credit + 1-lot max_loss fields) with **synthetic smoke**, then run **one focused evolve** on top research/fit symbols + **dated B3/B4**.

**Reject-as-success** unless a non-vacuous after-cost (5% slip, n>0, pnl>0) row is competitive with quality leader TSLL PCS `b195f5fe` on:
- 1-lot `max_loss_usd` (leader ≈ $76.32)
- shared-window / window `max_dd` (leader shared ≈ $74.85)

Do **not** promote on full-history vanity SHIP alone. No assumed-IV polish as a substitute for failing cost stress. No capital-path seat, no shadow/live, no arm.

## Context locked by this merge

- Direction scoreboard plumbing is **built** (`scripts/pcs_direction_scoreboard.py`; 15 shared windows; `l1_hyp_ids=[]`).
- PCS remains relative ml/dd leader but **after-cost negative** @5% (−$18.32) → not L1.
- CCS/IC/new calendars capital-rejected this lab.
- Time-axis (weekday/session) remains deferred; do not re-open unless butterfly seed completes early with spare budget.

## RTH note (not this seed)

When market is open next: condition eval only — stand-aside / paper open-close on capital-fit intents; **no free evolve**.

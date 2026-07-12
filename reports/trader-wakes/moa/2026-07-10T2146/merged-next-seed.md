# Merged NEXT SEED — 2026-07-10T2146 (executor + challenger)

**Keep (executor):** Next **BUILD only** — implement a minimal sleeve-fit `diagonal_spread` simulator with:

1. Explicit long/short expiry IV assumptions (same honesty bar as calendar term/skew)
2. Defined debit / max-loss capital fields for $3k 1-lot
3. Synthetic smoke coverage
4. Then **one** evolve (prefer defined-risk / catalog structures including diagonal) + dated **B3+B4**
5. **Reject unless** non-vacuous after-cost risk beats PCS quality bar (`b195f5fe`: ml≈$76 / window DD≈$75 / regime soft-hold; leader still soft loss@5% — challenger must beat that, not merely SHIP full-history)

**Challenger add (constraint, not a menu):**

- Do **not** invent L1/readiness from baseline or OOS-without-cost marks.
- If diagonal fails non-vacuous B4 like calendars, park the class and stop assumed-IV polish.
- No shadow/live/arm; no capital-path expansion without quality bar.
- RTH remains wait / stand-aside / paper open-close only (not this seed).

**Not NEXT (deferred, not this wake):** weekday/session time grid; multi-structure direction scoreboard; observed option-surface calendar realism; B6 multi-session paper (still open, not this BUILD loop).

# Merged NEXT seed — 2026-07-10T2100 MoA

**Phase:** BUILD only (not RTH apply)
**Sleeve:** 3000
**Capital path unchanged:** `hyp_dna_tsll_put_credit_spread_b195f5fe` relative quality example only

## ONE seed

Next BUILD — implement and smoke a **minimal long calendar spread** simulator:

1. DNA template `calendar_spread` with explicit **front_dte / back_dte** (and optional width/delta knobs) in `trader_platform/strategy_dna.py`.
2. New `trader_platform/research/calendar_sim.py`: BS-marked two-expiry entry/exit; **debit paid = max_loss_usd**; emit `capital_fit_usd`, `max_loss_usd`, `max_lots` for 1-lot $3k filter.
3. Dispatch beside `uses_pcs_sim()` in `trader_platform/evolve_tick.py` (or equivalent) so free/defined evolve can call it.
4. Real-sim smoke (and optional tiny time grid) under `scripts/` writing a dated artifact under `.cache/platform/`.
5. Update `docs/INCOME_STRATEGY_COVERAGE.md` **only after** execution evidence exists.

**Hard rejects for that wake:** no hyp registration/promotion, no B3/B4 vanity labels without trades, no capital-path talk, no live/shadow/arm.

**RTH (unchanged, separate):** if non-bear filters pass on b195f5fe → paper OPEN_PCS-or-STAND_ASIDE only; do not free-evolve on RTH.

**Why supersede nothing:** executor correctly dropped vacuous 7d cost-falsify thrash; calendar is the highest-leverage catalog gap for *time advantage* income research.

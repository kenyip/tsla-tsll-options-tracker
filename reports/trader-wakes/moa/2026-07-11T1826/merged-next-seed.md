# Merged NEXT seed — 2026-07-11T1826

**NEXT (one, BUILD only):**

Wire normalized archived option-quote rows into a date-aware `ContractGridProvider` for PCS/CCS/IC. Add provider coverage counters (entry dates covered, rights present, wing/strike availability, missing-grid rejects). Run one fail-closed replay smoke against the existing TSLL snapshot (`.cache/platform/option_quotes/TSLL_2026-07-11T1710.csv` or successor).

**Success criteria:**
- Provider selects only supplied expiry/right/strikes (or returns no entry).
- Counters report honest coverage; single as-of snapshot may correctly yield zero historical multi-date density.
- No evolve unless multi-date historical entry coverage is dense enough for non-vacuous B3+B4.

**Out of scope this seed:** free pop36 thrash, DNA retune, capital-path talk, live/shadow/arm.

**Phase / honesty:** BUILD · L0 · `l1_hyp_ids=[]` · capital path empty.

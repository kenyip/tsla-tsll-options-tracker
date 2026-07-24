# WAKE — 2026-07-24T0907 continuum judgment / coach

WAKE: 2026-07-24 ~09:07 PDT / 12:07 ET (RTH; coach not manage)  
PHASE: PAPER  
SLEEVE: 3000 plan · cash≈500 · live_armed=false  
CHOSE: **Improve search system** — empty stress-queue thrash + BAC shortlist monoculture  
OUTCOME: search-system repair (not STRATEGY_ADVANCED; no pack-grade)  
STRATEGY ADVANCEMENT: false  
SEARCH INFORMATION: vanity SHIP score≤0 no longer registers; shortlist ≤3/symbol surfaces TSLL+CCL dens0 SHIP@5%

## Orient

- EDGE: worker ON (hb_age~0; cycles≈573/295); last cycle `20260724T155200` all rc=0 wall~474s
- Stress thrash: selector **n=0** after PLTR PCS `9d1fab08` B4 soft-NULL@0 (capital_path_ok=false); BAC leaders TTL-skipped; many families cooled
- Evolve DR mint: 1 positive multi-leg SHIP (PLTR +7.8) + **5 vanity SHIP score≤0** created (PLTR/SMCI/XOM…) — burned create slots; selector correctly refused score≤0
- Shortlist was **6× BAC PCS** dens0 while ledger dens0 SHIP also had TSLL PCS + CCL CCS
- ROBOT: paper 3/3 · open=2 BAC+PLTR · risk=$359 · NEXT manage (RTH owns marks) — not this coach loop
- ARM: WAIT Ken · no pack-grade · no live/shadow/arm

## DID

1. **`evolve_tick.apply_results`**: skip registry create/update for SHIP with composite **score ≤ 0** (vanity positive_sim).
2. **`refresh_shortlist_from_ledger`**: multi-leg **≤3 per symbol**; stress_priority still first 2 accepted by rank.
3. **`trader_quality_cycle`**: when stress hyp CSV empty, still run ledger-only shortlist refresh.
4. **Ingest CLI**: allow `--refresh-shortlist` alone (no regime/cost required).
5. Refreshed live shortlist → BAC×3 + **TSLL PCS** + **CCL CCS/PCS** + MCP toys.
6. Tests: stress_rotation + new `test_evolve_vanity_ship_registry` — **12 passed**.

## Evidence

- Cycle: `.cache/platform/quality_worker/cycle_LATEST.json` shortlist_hyps=PLTR only then empty
- Evolve DR log `evolve_dr_20260724T155200.log`: SHIP +7.8 PLTR; vanity −49/−74/−127/−183/−274 created
- Ingest PLTR: B4 slip5 NULL/~0 → reject soft cost
- Shortlist after fix: `c7d09885,e1c7d338,5575695d` BAC + `01bf84a2` TSLL + `44d49dd9` CCL CCS + `113ec3b9` CCL PCS
- Tests: `pytest tests/test_stress_rotation.py tests/test_evolve_vanity_ship_registry.py` → 12 passed

## DURABLE

- Repo: evolve filter + shortlist diversity + empty-queue refresh + tests + this wake
- Skill: pitfalls for vanity SHIP create thrash + BAC monoculture shortlist
- No hyp yaml commit (worker owns)

## VERIFICATION

- `pytest tests/test_stress_rotation.py tests/test_evolve_vanity_ship_registry.py -q` → 12 passed
- Live `--refresh-shortlist` → n_shortlist=9 with multi-symbol multi-leg

## INTEGRATION

- Selective commit on main (scripts/tests/shortlist/wake/NEXT) — no hyp yaml / worker cache thrash

## LESSON

Future Trader: when stress queue empties after green cycles, inspect evolve create list for **score≤0 SHIP** and shortlist symbol entropy — not just selector cool lists. Positive_sim ≠ registerable capital-path DNA.

## NEXT SEED

`manage_open_paper_campaign` (RTH book full 2/2) — ken_required=false. Worker continues evolve with vanity filter; expect fewer empty stress slots when score>0 multi-leg appears.

## GATES

none (no live/arm)

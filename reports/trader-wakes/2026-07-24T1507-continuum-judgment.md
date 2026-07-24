# WAKE — 2026-07-24T1507 continuum judgment / coach

WAKE: 2026-07-24 ~15:07 PDT / 18:07 ET (post-close Friday)  
PHASE: PAPER  
SLEEVE: 3000 plan · cash≈500 · live_armed=false  
CHOSE: **Improve search system** — empty stress queue while evolve minted +score multi-leg SHIP only on cooled families  
OUTCOME: search-system repair + 6-family challenge falsify (not STRATEGY_ADVANCED; no pack-grade)  
STRATEGY ADVANCEMENT: false  
SEARCH INFORMATION: cool=spray-block not quarantine; one challenge/family unblocks queue; NFLX/XOM/PLTR/TSLL/SMCI/SNAP challenges all fail capital_path (mostly B4)

## Orient

- EDGE: worker ON (pid 73002 · hb_age~0 · quality cycle_n≈345 residual · status cycles≈624) all rc=0; wall~379s; campaign manage_fast_path 0.06s at book_full
- Thrash: selector **n=0** — BAC leaders TTL-skipped; 9 cooled families (NFLX CCS fails=26); evolve_dr +SHIP up to NFLX CCS 709 / XOM PCS 154 / PLTR CCS 169 only on cooled families → never entered B3/B4
- ROBOT: paper 3/3 · open=2 BAC+PLTR · risk=$359 · weekend hold (NEXT manage) — RTH owns marks Mon
- ARM: WAIT Ken · no pack-grade · no live/shadow/arm
- Jarvis guidance (2026-07-15 burst-stop) critic context only; continuum quality ops continue

## DID

1. **`trader_select_stress_hyps`**: cooled symbol×structure still allows **1 highest-score unstressed challenge** per family (`challenged_cooled_families`); further clones stay spray-blocked.
2. Tests: updated `test_family_recent_fail_cooled` — **12 passed**.
3. Live select → n=6 challenges: NFLX CCS `3da395d5` (score~710), TSLL PCS `4bd6cbc1`, XOM PCS `73282af2`, PLTR CCS `e37d2b5b`, SMCI CCS `35fc1d61`, SNAP CCS `78d4022e`.
4. B3+B4 stamp `20260724T220537` + ingest `coach_20260724T1500` → **0/6 capital_path_ok** (honest kill).
5. Post-fix selector still **n=6** next-challenge set (worker can burn without empty thrash).
6. Shortlist leaders unchanged dens0 BAC×3 + TSLL + CCL (no vanity promote).

## Challenge falsify (capital_path all false)

| hyp | fam | dens | dd | B4@5% | reject |
|---|---|---:|---:|---|---|
| nflx_ccs_3da395d5 | NFLX CCS | 10 | 247 | NULL −32 | soft_loss@5% |
| tsll_pcs_4bd6cbc1 | TSLL PCS | 3 | 99 | NULL −211 | cost_hold=false |
| xom_pcs_73282af2 | XOM PCS | 4 | 246 | REJECT −517 | fragile@5% |
| pltr_ccs_e37d2b5b | PLTR CCS | 15 | 259 | REJECT −897 | B3 hold=false |
| smci_ccs_35fc1d61 | SMCI CCS | 0 | 91 | NULL ~0 | edge vanished@5% |
| snap_ccs_78d4022e | SNAP CCS | 9 | 126 | NULL −128 | cost_hold=false |

## Evidence

- Selector pre: n=0 · skipped_fresh_leaders BAC c7d/e1c · cooled 14 hyps
- Selector post-fix: n=6 challenge CSV (see above)
- Regime/cost: `.cache/platform/quality_residual/regime_20260724T220537.json` · `cost_20260724T220537.json`
- Ledger/shortlist: `reports/bootstrap/STRESS_ROTATION.json` (n_ledger 1707) · `QUALITY_SHORTLIST.json`
- Tests: `pytest tests/test_stress_rotation.py tests/test_evolve_vanity_ship_registry.py -q` → 12 passed
- Paper: open BAC `paper_2f78815a0614` + PLTR `paper_c80aaa1cab46` (no mid-close; weekend gap watch Mon RTH)

## DURABLE

- Repo: selector challenge slot + tests + rotation/shortlist + this wake
- Skill: pitfall — empty queue + cooled families while evolve +SHIP → challenge slot not “no edge”
- No hyp yaml commit (worker owns)

## VERIFICATION

- 12 passed stress_rotation + evolve_vanity
- Ingest 6 rows capital_path_ok=false; shortlist top still BAC dens0 SHIP@5% leaders
- No live/arm/shadow

## INTEGRATION

- Selective commit on main (scripts/tests/bootstrap shortlist+ledger/wake/NEXT) — no hyp yaml / worker caches

## LESSON

Future Trader: when selector n=0 and leaders TTL-fresh, inspect **cooled family list vs evolve_dr +score SHIP**. Hard cool that admits zero challenges starves B3/B4 while cycles look green. One challenge/family restores falsify throughput without NFLX twin spray.

## NEXT SEED

`manage_open_paper_campaign` (weekend → Mon RTH mark BAC+PLTR; book full STAND_ASIDE new) — ken_required=false. Worker continues with challenge-enabled stress queue.

## GATES

none (no live/arm)

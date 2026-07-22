# WAKE — 2026-07-22T0908 continuum judgment / coach

WAKE: 2026-07-22 ~09:01–09:10 PDT / 12:01–12:10 ET  
PHASE: PAPER + BUILD search-system coach  
SLEEVE: 3000 plan · Agentic cash≈500 · agentic.enabled=false  
ECONOMIC MECHANISM: short-premium defined-risk multi-leg income (PCS/CCS) — paper path; search must B3/B4 **new** SHIPs not re-polish leaders  
CANDIDATE/FAMILY SCOPE: quality-cycle stress rotation + BAC/PLTR open paper  
FUNNEL: F3 paper sample (session_days=1/3) — search tooling advanced; no TOP_HYP  
PREDECLARED FALSIFIER: coach loop succeeds if next cycle stress set ≠ only BAC+PLTR and fresh DNA get B3/B4 dispositions  
OUTCOME: BLOCKER_REMOVED_AND_RETESTED (re-stress thrash blocker removed; coach B3/B4 batch run + ledger)  
STRATEGY ADVANCEMENT: false (no pack-grade TOP_HYP; BAC remains paper leader)  
SEARCH INFORMATION: vanity SHIP NFLX CCS / MU PCS falsified on B3/B4; TSLL/CCL CCS survive secondary; rotation ledger live  
NO-ADVANCE STREAK: n/a (coach/search-system, not strategy charter burst)  
CHOSE: Improve quality-cycle stress selection so worker cycles prove fresh multi-leg SHIPs faster

## DID

1. Oriented: `just trader-status` — PAPER_PROGRESS 63% / HOT_SEARCH 87%; quality_worker=ON cycles≈131–133; NEXT=manage_open_paper_campaign; working BAC+PLTR open_risk=$359.18
2. Diagnosed thrash: every cycle B3/B4 only `88f03c89`+`033dfdc8` (identical ~38KB regime / ~8KB cost artifacts) while evolve_dr minted NFLX/CCL/AAL/F/MU SHIPs unstressed
3. Built `scripts/trader_select_stress_hyps.py` — mix ≤2 shortlist leaders + unstressed multi-leg SHIPs (registry + evolve_log), symbol-diverse; reads `STRESS_ROTATION.json`
4. Built `scripts/trader_ingest_stress_rotation.py` — ingest B3/B4 pair → ledger + refresh `QUALITY_SHORTLIST.json` **without** hyp yaml write (worker-safe)
5. Wired selector into `trader_quality_cycle.py` + `trader_quality_residual.sh`; cycle auto-ingests after stress
6. Coach B3/B4 batch stamp `20260722T160529` on:
   - BAC 88f03c89 — B3 hold dens_neg=1 dd=103 B4 SHIP@5% ~206 **leader**
   - PLTR 033dfdc8 — B3 hold dens_neg=1 dd=230 B4 SHIP@5% ~244 secondary
   - NFLX CCS 9545399b — **B3 FAIL** dens_neg=5 dd=451 slip5 NULL −91 → reject
   - CCL CCS 5c10191e — B3 hold dens_neg=5 dd=193 B4 SHIP@5% ~223 secondary
   - MU PCS 1340cefb — **B4 FAIL** slip5 REJECT −636 → reject (vanity full PnL)
   - TSLL CCS 69bdf17f — B3 hold dens_neg=2 dd=239 B4 SHIP@5% ~453 (levered caveat)
7. Post-ingest selector picks **new** fresh ids (e.g. CCL 487c6349, NFLX 6b0e92ee, MU cf4a647e, TSLL PCS 494a0bbd) — rotation verified
8. Tests: `pytest tests/test_stress_rotation.py` → 2 passed
9. Paper residual: BAC 61.82 (+0.97% vs 61.22), PLTR 126.85 (−4.4% vs 132.66), SPY 749.84 — HOLD book (concurrent 2/2); no new paper; no live/arm
10. Skill doc: `references/quality-acceleration.md` stress-rotation section

## DECISION

| Item | Action | Why |
|---|---|---|
| BAC/PLTR open PCS | **HOLD** | Book full; path not force-close; PLTR still OTM vs short on prior marks |
| New paper | **STAND_ASIDE** | 2/2 concurrent, open_risk $359 |
| NFLX CCS 9545399b / MU PCS 1340cefb | **reject shortlist capital path** | B3/B4 quality bar fail |
| TSLL/CCL CCS survivors | research secondary | worse dense-neg/DD or levered vs BAC |
| Quality worker | keep ON | now rotates stress targets |

## EVIDENCE

- `.cache/platform/quality_residual/regime_coach_20260722T160529.json`
- `.cache/platform/quality_residual/cost_coach_20260722T160529.json`
- `reports/bootstrap/STRESS_ROTATION.json`
- `reports/bootstrap/QUALITY_SHORTLIST.json` (refreshed)
- `tests/test_stress_rotation.py` green
- RH equities BAC/PLTR/SPY ~12:08 ET
- worker HEARTBEAT cycles≥133

## DURABLE

- Repo: stress selector + ingest + cycle/residual wiring + shortlist/ledger + tests
- Skill: quality-acceleration stress rotation pitfall
- No hyp yaml commit (worker thrash)

## VERIFICATION

- `pytest tests/test_stress_rotation.py` → 2 passed
- selector after ingest ≠ only leaders (fresh multi-symbol set)
- No place_* / no arm / no shadow

## INTEGRATION

Selective commit: scripts + tests + STRESS_ROTATION + QUALITY_SHORTLIST + NEXT_SEED + wake/readiness. Leave `hypotheses.yaml` and worker MULTI_SYMBOL/paper_loop dirt unstaged.

## LESSON

Future coach: if regime/cost artifact sizes are identical across many cycles and shortlist_hyps is a fixed 2-id string, stress selection is thrashing — fix rotation before more evolve volume.

## NEXT SEED

`manage_open_paper_campaign` — HOLD/mark BAC+PLTR through RTH/close; learn_tick on close; quality_worker continues with **rotated** B3/B4. ken_required=false.

## GATES

none for Ken. Ken-only: gateway_up | LIVE_PACKET_arm | fund_3k_at_packet.

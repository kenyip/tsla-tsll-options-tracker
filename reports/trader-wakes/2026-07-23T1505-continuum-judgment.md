# WAKE — 2026-07-23T1505 continuum judgment / coach

WAKE: 2026-07-23 ~15:05 PDT / ~18:05 ET (post-close coach)  
PHASE: PAPER  
SLEEVE: 3000 plan · cash≈500 · live_armed=false  
CHOSE: **Improve EDGE throughput + capital-path purity** — fix full-book campaign 300s timeouts; require SHIP@5% for capital_path_ok; rescore ledger  
OUTCOME: search-system improvement (not STRATEGY_ADVANCED / not pack-grade)

## Orient

- EDGE: worker ON (pid 2700, ~15h uptime, cycles≈420+, hb fresh); selector skips fresh AAL/BAC leaders (TTL) + pulls unstressed multi-leg
- Latest cycle `20260723T215011`: evolve/research/stress green; **paper_campaign rc=124 TIMEOUT 300s** with book_full=true; wall **641s**
- Pattern last ~2h: every ~3rd cycle campaign timeout → wall ~600s vs ~300s on skip — EDGE burn on manage thrash
- Stress batch that cycle: PLTR CCS soft NULL@0 reject; TSLL PCS B4 −324 reject; F PCS soft_loss NEEDS reject; PLTR PCS a9be1bf6 dens1 NEEDS@+$6 was capital_path_ok (vanity)
- ROBOT: paper **2/3** sessions · open=2 BAC+PLTR · risk=$359.18 · NEXT manage_open_paper_campaign
- ARM: WAIT Ken only · no pack-grade · densify quality_pass=false
- Shortlist leaders stable dens0 SHIP@5%: AAL 972ca6be (dd35/slip301) then BAC variants

## Thrash detector

- Leaders not stuck on re-stress: selector correctly `skipped_fresh_leaders` AAL+BAC; only fresh unstressed queued
- Real thrash = **campaign scout+dry under 2/2 concurrent** (cadence every 3 still paid 300s timeout)
- Not densify bag thrash; not same-regime stress bytes only

## DID

1. **`scripts/trader_paper_campaign.sh` book-full manage fast path**
   - When `working >= MAX_CONCURRENT` or `open_risk >= MAX_OPEN_RISK`: skip registry promote, scout, dry `run_tick`
   - Write NEXT_SEED `manage_open_paper_campaign` + receipt `manage_only=true` / `scout_skipped=true`
   - Smoke under live book: **~8.4s** wall, rc0, open BAC+PLTR unchanged (was 300s TIMEOUT)

2. **Capital-path: require SHIP@5%**
   - `trader_ingest_stress_rotation.capital_path_decision` rejects `NEEDS_MORE_DATA` @5% even if slip pnl > 0
   - Rescore: **n_flipped_off=94**, capital_path_ok 276→**182**; shortlist top **unchanged** dens0 AAL/BAC SHIP@5%

3. **Tests**
   - `tests/test_stress_rotation.py` + NEEDS positive-slip flip + unit gate
   - `tests/test_quality_cycle_cadence.py` manage_only predicate
   - **11 passed**

4. Skill pitfall updated (`trader-self-evolution`) for campaign timeout + NEEDS capital-path

## Evidence

- `.cache/platform/quality_worker/cycle_LATEST.json` stamp 20260723T215011 campaign timeout
- `.cache/platform/paper_campaign/LATEST.json` stamp 20260723T220524 manage_only
- `reports/bootstrap/STRESS_ROTATION.json` rescore coach
- `reports/bootstrap/QUALITY_SHORTLIST.json` top dens0 AAL/BAC
- pytest: tests/test_stress_rotation.py tests/test_quality_cycle_cadence.py → 11 passed

## Paper (post-close; no force manage)

| Order | Sym | ml | Action |
|---|---|---:|---|
| paper_2f78815a0614 | BAC PCS | 162.64 | **HOLD** (prior RTH healthy OTM) |
| paper_c80aaa1cab46 | PLTR PCS | 196.54 | **HOLD_elevated** (prior RTH ~ATM / ~36% ml) |
| New | — | — | **STAND_ASIDE** (2/2) |

No live / shadow / arm. learn_tick rc=1 on smoke (yaml thrash risk) — campaign still completed manage path.

## DURABLE

- Repo: campaign fast path + capital_path SHIP@5% + tests + shortlist/ledger rescore
- Skill: timeout + NEEDS pitfalls
- Memory: none (procedure in skill)

## VERIFICATION

- `pytest tests/test_stress_rotation.py tests/test_quality_cycle_cadence.py` → 11 passed
- `bash scripts/trader_paper_campaign.sh` under full book → 8.42s, manage_only=true, scout_skipped=true
- `trader_ingest_stress_rotation.py --rescore-only --refresh-shortlist` → flipped_off=94, top_ids dens0 AAL/BAC

## INTEGRATION

- Selective commit: scripts/tests/shortlist/ledger/wake/NEXT — **not** hypotheses.yaml thrash
- See closeout commit SHA on main

## LESSON

Future Trader: full book means **manage receipt only** in quality cycles — never pay scout/dry tax. Capital-path means **SHIP@5%**, not soft NEEDS with pocket change slip.

## NEXT SEED

`manage_open_paper_campaign` — HOLD BAC+PLTR open paper through next RTH marks; STAND_ASIDE new while 2/2; worker uses fast-path campaign (no 300s hang); continue EDGE stress on unstressed multi-leg; aim paper sessions 2/3→3/3. ken_required=false

## GATES

none (Ken only: gateway / LIVE_PACKET arm / $3k at packet)

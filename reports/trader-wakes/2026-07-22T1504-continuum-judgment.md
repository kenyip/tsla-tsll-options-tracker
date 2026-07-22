# WAKE — 2026-07-22T1504 continuum judgment / coach

WAKE: 2026-07-22 ~15:00–15:05 PDT (post-RTH coach)  
PHASE: PAPER + BUILD search  
SLEEVE: 3000 plan · Agentic cash≈500 · agentic.enabled=false  
ECONOMIC MECHANISM: improve multi-leg stress→shortlist capital-path filter so cycles stress real slip-edge survivors, not soft-NULL vanity  
CANDIDATE/FAMILY SCOPE: stress-rotation ledger / QUALITY_SHORTLIST ranking (not a single DNA advance)  
FUNNEL: F3 paper sample ongoing (session_days=1/3) — no TOP_HYP  
PREDECLARED FALSIFIER: if shortlist still elevates NULL@5%~0 or non-positive full_pnl after rescore → gate bug  
OUTCOME: BLOCKER_REMOVED_AND_RETESTED (gate repaired + ledger rescored + shortlist refreshed; selector emits new mix)  
STRATEGY ADVANCEMENT: false (search-system improvement; no pack-grade TOP_HYP)  
SEARCH INFORMATION: 35 soft-null/~0 or non-pos full_pnl rows flipped off capital_path; ok 104→69; SMCI CCS soft-nulls demoted  
NO-ADVANCE STREAK: n/a (coach/search tooling, not strategy charter volume)  
CHOSE: Harden stress-rotation capital-path gates + rescore shortlist (worker healthy; paper manage residual already set)

## DID

1. Oriented: `just trader-status` — PAPER_PROGRESS ~66% / HOT_SEARCH ~90%; quality_worker=ON cycles=204 hb fresh; handoff=NO_QUALIFIED_STRATEGY; paper BAC+PLTR working open_risk=$359.18; NEXT=manage_open_paper_campaign
2. Thrash check: cycle_LATEST still mixing leaders+fresh (good). Shortlist integrity broken: **SMCI CCS 9c5c963f** stress_priority with `NULL@5pct pnl~0.0`; **SMCI CCS dc6e78da** on shortlist with **full_pnl=-10.79** still capital_path_ok
3. Root cause: `trader_ingest_stress_rotation` only rejected NULL when slip5_pnl **<0**, not ~0; never rejected non-positive full history PnL; rank ignored slip verdict quality after dens/dd
4. Fixed:
   - `capital_path_decision()` pure gate: B3, B4, **NULL/~0 edge vanished**, **full_pnl≤0**, dense_neg+dd bar
   - Rank adds slip-verdict quality (SHIP < NEEDS_MORE_DATA < NULL) after dens/dd
   - `--rescore-only --refresh-shortlist` for coach without new B3/B4 sims
5. Rescore live ledger: **n=290, flipped_off=35, capital_path_ok=69**; shortlist top now CCL PCS → NFLX CCS (NULL but slip~+80) → BAC/CCL SHIP@5% …; SMCI soft-nulls **off** priority
6. Selector after refresh: CCL + NFLX leaders + unstressed PLTR/BAC/AAL/SMCI multi-leg (fresh rotation continues)
7. Paper: leave HOLD by order_id (post-close; concurrent full); no campaign mutate from coach
8. Tests: `tests/test_stress_rotation.py` **3 passed**
9. Skill pitfall + quality-acceleration reference updated for automated reject + rescore CLI

## DECISION

| Item | Action | Why |
|---|---|---|
| Soft NULL@~0 / neg full_pnl | **capital_path reject** | Survives_5pct_slip with vanished edge is not a leader |
| SMCI CCS 9c5c963f / dc6e78da | demoted off shortlist priority | Soft-null / non-pos full |
| CCL PCS c901235d | keep risk-profile leader | dens=1 dd≈44.5 slip≈+62 |
| Open BAC+PLTR paper | **HOLD** residual | B6 multi-session; book full |
| New paper | **STAND_ASIDE** while 2/2 | Campaign guards |
| Live/shadow/arm | none | Ken-only |

## EVIDENCE

- `scripts/trader_ingest_stress_rotation.py` (capital_path_decision, rescore_ledger)
- `tests/test_stress_rotation.py` (soft-null, neg full, rescore flip)
- `reports/bootstrap/STRESS_ROTATION.json` last_rescore flipped_off=35
- `reports/bootstrap/QUALITY_SHORTLIST.json` generated_at 2026-07-22T22:03:39Z
- `.cache/platform/quality_worker/cycle_LATEST.json` stamp 20260722T215140 ok
- `just trader-status` ~15:00 PDT

## DURABLE

- Repo: ingest script + tests + shortlist + rotation ledger + wake + NEXT_SEED + readiness
- Skill: trader-self-evolution pitfall + quality-acceleration soft-NULL row
- No hyp yaml commit (worker thrash surface)

## VERIFICATION

```text
.venv/bin/python -m pytest tests/test_stress_rotation.py -q  → 3 passed
.venv/bin/python scripts/trader_ingest_stress_rotation.py --rescore-only --refresh-shortlist --source continuum_judgment_20260722T1500
  → flipped_off=35 n_ok=69 shortlist top CCL/NFLX/BAC/CCL/BAC/TSLL
.venv/bin/python scripts/trader_select_stress_hyps.py --json
  → leaders CCL+NFLX + unstressed PLTR/BAC/AAL/SMCI
```

## INTEGRATION

Selective commit on main: scripts/tests/bootstrap shortlist+ledger+NEXT_SEED+wake+readiness.  
Leave `hypotheses.yaml` and worker cache dirt unstaged.

## LESSON

`cost_hold=true` + `survives_5pct_slip` with **NULL@5% pnl~0** (or negative full-history PnL) was polluting stress_priority and wasting re-stress cycles. Capital-path must require a **positive after-slip edge** (or SHIP/NEEDS_MORE_DATA with pnl>ε), not soft survival alone. Rescore-without-restress is the coach tool when gates tighten.

## NEXT SEED

`manage_open_paper_campaign` — HOLD BAC+PLTR through B6 sessions; worker uses hardened shortlist; next cycles stress CCL/NFLX + fresh multi-leg. ken_required=false.

## GATES

none (Ken: gateway_up | LIVE_PACKET arm | $3k at packet only)

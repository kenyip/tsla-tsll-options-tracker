# MOA BUILD lab challenger critique — 2026-07-11T2353

WAKE: 2026-07-11T2353 PDT
ROLE: Grok 4.5 challenger (read-only)
PHASE: BUILD · SLEEVE: 3000
MODE: paper/research only — no evolve --apply, no broker, no arm, no shadow auto-promote

## Executor claim (restated)

Built and falsified a no-lookahead shared-position PCS/CCS/IC regime router with identical-loop standalone controls, 5% and $0.01/leg cost axes, yearly/6m windows, purity/no-reentry checks, and independent ledger recomputation. Eight symbols completed; none cleared absolute gates → REJECT_ROUTER_FAMILY_THIS_CYCLE; L0; no living leader; NEXT = entry-acceptance funnel before DNA retune.

## Independent verification

| Artifact | Check |
|---|---|
| Primary lab JSON | `.cache/platform/regime_router_lab_2026-07-11T2353.json` — `decision=REJECT_ROUTER_FAMILY_THIS_CYCLE`, `passing_symbols=[]`, population 8/8, errors 0 |
| Claim scope | JSON labels `synthetic daily-bar discovery; not observed-contract or L1 readiness evidence` |
| Table metrics | Router baseline / slip_5pct / fixed_0p01_per_leg n/pnl/dd match executor table for all 8 symbols (spot-checked + bulk recompute) |
| Ledgers | All reported `ledger_exact=true`; routing_violations=0; same_bar_reentries=0 |
| Tests | `.venv/bin/python -m unittest tests.test_regime_router_sim -v` → **3/3 OK** (route/stand-aside, shared loop no reentry, future-regime negative control) |
| Code surface | `trader_platform/research/regime_router_sim.py`, `scripts/pcs_regime_router_lab.py`, `tests/test_regime_router_sim.py` present |
| Docs/coverage | Direction gap text already records router + first-run rejection; readiness L0 / no living leader |
| Capital labels | No registration/promotion/seat; `b195f5fe` not used as living bar |

## Rubric

1. **Goal progress — PASS**
   Material progress on the direction axis: closed the default-DNA shared-position router family for this cycle with multi-symbol absolute gates rather than polishing another standalone proxy. Raises search efficiency; does not create L1.

2. **Creativity and independence — PASS**
   Kept prior NEXT with justification (combination test > another standalone mutant). Original capability (shared loop + controls + purity/no-lookahead tests), not a TSLL-PCS tunnel.

3. **Claim validity — PASS**
   Synthetic claim labeled; one-date observed archive correctly did not freeze this experiment. No L1 / capital / observed-cost claims. Absolute gates used because there is no living quality leader.

4. **Evidence and test quality — PASS (with caveats)**
   Real paths, dated JSON, behavioral tests including a future-row negative control. Caveats (do not overturn reject):
   - **Accepted-structure collapse:** route_counts on baseline accepted entries are pure PCS on TSLL/SMCI/TSLA/PLTR/AMD/ARM; QQQ pure CCS (n=4); only AAPL is mixed (PCS15/CCS15/IC23). Headline “router” is mostly regime-gated PCS on 6/8 names.
   - **route_counts semantics:** failed `pick_structure_entry` increments `stand_aside`, so counts do **not** separate “regime selected CCS/IC” from “entry rejected.” Executor noted collapse; funnel NEXT is the right repair.
   - **Control comparison weakness:** `best_control_slip_5_pnl` treats zero-trade CCS/IC as 0.0 PnL, so empty controls look “competitive” and sparse positive router slip can “beat” them (e.g. TSLL). Family still fails denser gates; gate is weak evidence, not a false promote.

5. **Falsification — PASS**
   Predeclared reject gates; honest REJECT; 5% not mislabeled survival (n0–4, sum n=8 across symbols); fixed-$ used as second cost axis. ARM fixed positive non-vacuous (n20/+$117.43) correctly still fails 5% vacuity + window DD $142.27.

6. **Capital honesty — PASS**
   No living leader; absolute ml≤300 / window DD≤75 / dense-neg≤5 applied; historical `b195f5fe` not seated. Max losses on accepted router rows (~$160–$205) pass ≤300 but are not competitive seats. No paper/shadow/live path opened.

7. **Research freedom — PASS**
   Blocked observed path did not freeze this valid synthetic falsify. No removable prompt freeze identified. Mild process note: instrumentation of selection vs entry reject would have been higher-information *before* the full 8-name stress, but running the lab first still produced decisive collapse evidence.

8. **ONE NEXT seed — PASS**
   Entry-acceptance/rejection funnel before DNA retune is the highest-information follow-on given collapse + silent stand_aside counting. Keep RTH archive density as parallel, not a substitute BUILD seed.

## Score adjustments

| Item | Executor | Challenger |
|---|---|---|
| Progress type | P1+P3 | **P1+P3** (agree) |
| Score | 4/5 | **4/5** (agree; not 5 because collapse/control-gate limits how much “mixed-direction” was actually tested) |
| Honesty | L0 | **L0** (agree; not L1) |
| Family decision | REJECT this cycle | **REJECT** (agree) |
| Living leader | none | **none** |
| Capital / live | none | **none** |

## Patches to executor narrative (keep evidence)

- Strengthen: 6/8 symbols accepted **only** PCS entries; QQQ only CCS; AAPL only mixed. “Router family reject” is correct, but do not over-read as a full three-structure stress on every name.
- Gate design debt for funnel work: log `selected_structure` vs `entry_accept`/`reject_reason`; treat zero-trade control PnL as NA, not 0.0.
- Do **not** retune DNA, IV floors, or credit knobs until the funnel proves CCS/IC are selectable *and* entry-testable at non-trivial rates on the same eight-symbol stream.

## Overall

**PASS 8/8** on rubric. Executor closeout is honest, evidence-backed, and capital-safe. Merge keeps REJECT + funnel NEXT; no readiness phase change.

MOA_CHALL_DONE (critique body)

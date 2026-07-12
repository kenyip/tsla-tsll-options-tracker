# MOA BUILD lab challenger critique — 2026-07-12T0400

WAKE: 2026-07-12T0400 PDT (evening; market closed)
ROLE: Grok 4.5 challenger (read-only)
PHASE: BUILD · SLEEVE: 3000
MODE: paper/research only — no evolve --apply, no broker, no arm, no shadow auto-promote

## Executor claim (restated)

P1+P3: repaired a claim-invalidating iron-condor close-debit boundary (cap at widest non-overlapping wing, not sum of wings), added side-specific IC delta/width/regime controls, then reject-unless falsified a 96-row bullish/neutral “capped-jade” asymmetric IC grid across BAC/TSLL/SMCI/PLTR/SOFI/F. Baseline 29 positive SHIPs; 0/96 positive at 5% slip and 0/96 at $0.01/leg; ledgers exact 288/288; same-bar reentry 0 → `REJECT_ASYMMETRIC_CONDOR_THIS_CYCLE`. L0; no living leader; NEXT = next distinct NY RTH archive append 1→2/3.

## Independent verification

| Artifact | Check |
|---|---|
| Primary lab JSON | `.cache/platform/asymmetric_condor_lab_2026-07-12T0400.json` — `decision=REJECT_ASYMMETRIC_CONDOR_THIS_CYCLE`, `n_rows=96`, `n_deep_candidates=0`, `n_absolute_pass=0`, `errors=[]` |
| Recomputed counts | baseline pnl>0 **44**; baseline verdict SHIP **29**; slip pnl>0 **0** (best −99.86); fixed pnl>0 **0** (best −156.89); slip n_trades min **46**; fixed n_trades min **35** (all non-vacuous) |
| Integrity | ledger_exact **288/288** (96×3 axes); same_bar_reentries sum **0** |
| Claim scope | JSON: synthetic daily-bar/BS proxy only; archive not dense enough for L1 — matches closeout |
| Gates | min_trades≥8, both cost axes positive, ml≤300, window DD≤75, dense_neg≤5, ledger exact, no same-bar — deep path never entered because cost positivity failed first (correct) |
| Runner / sim | `scripts/asymmetric_condor_lab.py`, `trader_platform/research/pcs_sim.py` (`max_close_debit`, side knobs, `ic_allowed_regimes`) |
| Behavioral tests | `tests/test_pcs_expiry_grid.py`: side-specific delta/width/regime gate + close-cap force-mark $4 → exit debit 2.0 / realized −$160 vs stated max loss |
| Targeted re-run | `.venv/bin/python -m unittest tests.test_pcs_expiry_grid tests.test_regime_router_sim tests.test_defined_risk_fixed_cost -q` → **19/19 OK** |
| Coverage / readiness | income-coverage LATEST already records 96-row asymmetric IC cost reject; readiness L0 / TOP_HYP_CAPITAL_PATH none / no B-check inflation |
| Capital labels | No hyp registration, no promotion, no seat; `b195f5fe` not used as living bar |

## Rubric

1. **Goal progress — PASS**
   Material progress: fixed a real IC max-loss/event-loop inconsistency that could invalidate prior and future IC claims, then closed a distinct direction/skew-shaped family under dual cost axes. Does not create L1; raises search efficiency by removing a dead proxy branch.

2. **Creativity and independence — PASS**
   Correctly superseded RTH-only archive NEXT while market closed. Chose a real catalog gap (capped-jade / nearer-put farther-call IC) rather than re-polishing TSLL PCS, collar, BAC Fri7 management, or router DNA. Not pure familiar thrash: new knobs + claim-boundary repair + complete six-name grid.

3. **Claim validity — PASS**
   Synthetic Friday/rounded-strike BS labeled; observed density (1/3) correctly did not freeze this independent proxy falsify and correctly blocks L1/observed-cost claims. Absolute gates used with no living leader. Fail-closed REJECT is honest.

4. **Evidence and test quality — PASS (nits)**
   Real dated JSON, complete ranking (96/96, errors 0), independent ledger recompute, same-bar check, dual cost axes, behavioral close-cap + regime-gate tests. Nits (do not flip reject):
   - **Width vs delta asymmetry:** lab grid locked `put_width=call_width=$1` for all 96 rows; asymmetry tested is **delta/regime** (put 0.16/0.22, call 0.08/0.12), not wing-width skew. The close-cap unit test does exercise unequal widths (1×2). Do not over-read the grid as width-asymmetric jade.
   - **Window DD never binding:** deep/window pass path requires both cost axes positive first; reject is pure after-cost negativity, not DD. That is the right short-circuit.
   - Pattern continuity: multi-leg BS proxies again collapse under adverse costs — consistent with prior IC/IB/BWIB/calendar lessons; still useful once, not a reason to re-grid.

5. **Falsification — PASS**
   Predeclared dual-cost + absolute gates; 0 deep candidates; 0 absolute passes; decision REJECT; no soft-null survival mislabel (dense negative after-cost). No registration or promotion after 29 baseline SHIPs — correct anti-vanity.

6. **Capital honesty — PASS**
   No living leader; absolute ml≤300 / DD≤75 / dense-neg≤5 stated; best baseline SHIPs (e.g. PLTR mid +$397) still miss after-cost and show large mid DD (~$160–$190). Structure capital_fit/max_loss language is defined-risk widest-wing-minus-credit; default 1-lot posture. No paper/shadow/live seat.

7. **Research freedom — PASS**
   One-date archive blocked only observed-surface/L1 claims; executor still ran a valid independent structure/direction experiment. Cron `execute_code` absence did not erase verification (terminal assertions + challenger re-run). No removable prompt freeze identified for a higher-info valid alternative this wake.

8. **ONE NEXT seed — PASS (keep + tighten)**
   Highest-information remaining substrate for any observed-cost L1 path is still archive density (1→2 of 3 NY market dates on next distinct RTH day). Explicitly leave asymmetric IC / collar / BAC Fri7 management closed. Do not treat archive as a free BUILD thrash substitute when RTH is closed — but do not invent another multi-leg BS re-grid either.

## Score adjustments

| Item | Executor | Challenger |
|---|---|---|
| Progress type | P1 capability repair + P3 falsify | **P1+P3** (agree) |
| Score | 4/5 | **4/5** (agree; not 5 — equal-width grid + expected multi-leg cost collapse; boundary fix is the durable win) |
| Honesty | L0 BUILD | **L0** (agree; not L1) |
| Family decision | REJECT this cycle | **REJECT** (agree) |
| Living leader | none | **none** |
| Capital / live | none | **none** |

## Patches to executor narrative (keep evidence)

- Label precision: grid is **delta-asymmetric equal-width** IC under bullish/neutral regimes, not a width-asymmetric broken-wing grid. Close-cap fix still generalizes to unequal widths (unit-tested).
- Do **not** re-open this proxy grid with credit/PT/stop polish; after-cost best rows are still deeply negative.
- Keep formal B checks unchanged; do not resurrect `b195f5fe` as a seat.

## Overall

**PASS 8/8** on rubric. Executor closeout is honest, evidence-backed, capital-safe, and correctly empty of living quality leadership. Merge keeps REJECT + RTH archive NEXT; no phase change.

MOA_CHALL_DONE (critique body)

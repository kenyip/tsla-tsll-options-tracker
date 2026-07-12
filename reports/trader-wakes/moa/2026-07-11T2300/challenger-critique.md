# MOA BUILD lab challenger critique — 2026-07-11T2300

WAKE: 2026-07-11T2300 PDT
PHASE: BUILD
SLEEVE: 3000
CHALLENGER: Grok 4.5 (read-only)
MODE: paper/research only — no evolve --apply, no broker, no arm, no shadow

## What was judged

Executor P3: post event-loop-fix restress of exact registered put-ratio DNA
- SMCI `hyp_dna_smci_put_ratio_backspread_86a2d26a`
- BAC `hyp_dna_bac_put_ratio_backspread_967b8c06`

Prior NEXT (BAC management×OOS grid) was superseded because pre-fix metrics were stale after the shared no-same-bar-reentry correction.

## Independent verification (read-only)

| Artifact | Status |
|---|---|
| `.cache/platform/stress_regime_put_ratio_postfix_2026-07-11T2300.json` | Present; 2 hyps |
| `.cache/platform/stress_cost_put_ratio_postfix_2026-07-11T2300.json` | Present; 2 hyps; slips 0/2/5/10% |
| `.cache/platform/fixed_cost_put_ratio_postfix_2026-07-11T2300.json` | Present; leg_count=3 RT cost |
| `.cache/platform/put_ratio_postfix_independent_2026-07-11T2300.json` | Present; 4 rows exact match + zero reentry |
| `tests.test_put_ratio_backspread_sim` | Re-ran 6/6 OK (includes no-same-bar + 3-leg cost) |
| Wake residue | `reports/trader-wakes/2026-07-11T2300-moa-exec.md` + executor-closeout.md |

### Metric match vs executor claims

| Row | Field | Artifact | Claim match |
|---|---|---|---|
| SMCI baseline | n66 / +3704.56 / DD 306.07 / SHIP / ml 374.23 | regime full_history | YES |
| SMCI B3 | soft hold, dense-neg 0, worst −101.92, window max_dd 365.32 | summary | YES |
| SMCI 5% | n61 / +1350.40 / DD 599.41 / SHIP; 10% REJECT −593.35 | cost by_slip | YES |
| SMCI $0.01/leg | n66 / +3397.40 / DD 328.37 / SHIP | fixed by_half_spread | YES |
| BAC baseline | n59 / +321.51 / DD 148.33 / SHIP / ml 118.11 | regime full_history | YES |
| BAC B3 | soft hold, dense-neg 2, worst −62.38, window max_dd 159.85 | summary | YES |
| BAC 5% | n58 / +70.15 / DD 190.59 / NULL (positive non-vacuous) | cost by_slip | YES |
| BAC $0.01/leg | n59 / +71.59 / DD 198.72 / NULL | fixed by_half_spread | YES |
| Independent ledger | all 4 rows recomputed_pnl/dd == reported; same_bar_reentry_count=0 | ind JSON | YES |

No uncited headline numbers found. Soft `cost_hold=true` / `survives_5pct_slip` on BAC NULL@5% is correctly **not** sold as after-cost SHIP.

### Post-fix delta vs 2159 (why supersede was correct)

| Hyp | 2159 (pre-fix historical) | 2300 (post-fix decision) |
|---|---|---|
| SMCI 5% | +1842 SHIP; B3 FAIL; window DD 530.47 | +1350.40 SHIP; B3 soft-hold; window DD 365.32 |
| BAC 5% | −81.48 NULL | +70.15 NULL positive |
| BAC fixed $0.01 | +576.58 | +71.59 |

Cadence correction changed both after-cost sign/structure and regime summary. Tuning a management grid on pre-fix numbers would have been invalid. Supersede is justified.

## RUBRIC

1. **Goal progress — PASS**
   Materially improves L1 search integrity: post-fix family REJECT with complete absolute gates; prevents wasted management/OOS thrash on invalid cadence. Does not discover a new edge (honest score 3/5).

2. **Creativity and independence — PASS**
   Not familiar-recipe tunnel. Prior management-grid seed was context; supersede reason is explicit and evidence-based (stale pre-fix metrics).

3. **Claim validity — PASS**
   Proxy BS marks labeled; no observed-surface / archive / assignment claim. One-date archive correctly treated as irrelevant to this narrow proxy falsification and still blocking provider-backed promotion. Absolute gates used because no living leader; `b195f5fe` historical only.

4. **Evidence and test quality — PASS**
   Real B3/B4/fixed artifacts + independent ledger recomputation + behavioral tests (same-bar reentry, three-leg half-spread). Populations structure-pure put_ratio. Rankings labeled soft hold / NULL / SHIP honestly.

5. **Falsification — PASS**
   Predeclared complete gate (baseline SHIP + non-vacuous positive 5% + B3 + ml≤300 + window DD≤75 + dense-neg≤5). Neither row clears; no grid run; family leaves capital search this cycle. Negative control = stop-before-tune.

6. **Capital honesty — PASS**
   No living quality leader; no seat. SMCI `fit_3k` with max_loss $374.23 and max_lots=2 correctly fails explicit one-lot ≤$300 gate. BAC sleeve-fit but path DD fails ≤$75 at baseline/B3/5%/fixed. Soft cost_hold ≠ capital edge.

7. **Research freedom — PASS**
   Observed archive density did not freeze this valid independent P3 axis. No prompt rule blocked a higher-info valid experiment. Freedom note stands.

8. **ONE NEXT seed — PASS**
   No-lookahead shared-position regime router over PCS/CCS/IC vs standalone negative controls is highest-information BUILD next: reuses mature credit engines, tests direction/regime as a **router** (not a re-run of the existing direction scoreboard), keeps absolute gates, and is not blocked by 1/3 archive dates. Keep RTH archive append as **parallel** ops, not a second BUILD seed.

## Challenges / nits (non-blocking)

- **Soft cost_hold language:** BAC 5% is NULL +$70.15 with cost_hold=true. Executor text is careful; future wakes must keep “survives_5pct” ≠ L1 after-cost SHIP.
- **SMCI max_lots=2:** Open-risk arithmetic is not a 1-lot research posture. Absolute one-lot gate application was correct.
- **Progress score 3/5 is right:** Pure rejection after restress is high-integrity, medium novelty. Do not inflate to 4+ without new sim/tooling or a surviving L1 candidate.
- **Regime-router NEXT scope guard:** Must use only no-lookahead regime features already available at bar t; one shared position; structure purity (no single-leg contamination); compare router vs standalone PCS/CCS/IC on **identical windows**; reject on absolute gates. Do not re-open put-ratio capital path without new post-fix evidence clearing the full gate.

## Verdict

**PASS 8/8.** Keep executor evidence and family REJECT. Keep progress type P3 / score 3/5 / L0 BUILD. Keep ONE NEXT = regime-router scaffold + same-window falsify vs standalone negative controls. No capital path, no live/shadow/arm.

GATES: none. Paper/research only.

MOA_CHALL_DONE

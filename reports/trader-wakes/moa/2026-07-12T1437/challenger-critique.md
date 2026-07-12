# MOA BUILD challenger critique — 2026-07-12T1437

ROLE: Grok 4.5 challenger (read-only judgment)
PHASE: BUILD · SLEEVE: $3000 · PAPER_ONLY
STAMP: 2026-07-12T1437 · context: weekend (market closed)
EXECUTOR ARTIFACTS READ:
- `reports/trader-wakes/moa/2026-07-12T1437/meta.json`
- `reports/trader-wakes/moa/2026-07-12T1437/executor-closeout.md`
- `reports/trader-wakes/2026-07-12T1437-moa-exec.md` / `reports/trader-wakes/LATEST.md`
- `reports/readiness/income-coverage-LATEST.md` (stamp 1437)
- `reports/readiness/LATEST.md`
- `.cache/platform/pcs_pullback_rolling_origin_lab_2026-07-12T1437.json`
- `scripts/pcs_pullback_rolling_origin_lab.py`
- `tests/test_pcs_pullback_rolling_origin_lab.py`
- `docs/INCOME_STRATEGY_COVERAGE.md` / coverage script gap text
- archive density: `.cache/platform/option_quote_archive_density_2026-07-11T2031.json` (1/3 market dates)

## Independent verification (read-only)

| Claim | Independent check | Result |
|---|---|---|
| Decision `REJECT_MILD_PULLBACK_PCS_ROLLING_ORIGIN` | JSON top-level `decision`, `n_completed=8`, `n_all_folds_pass=0`, `errors=[]` | MATCH |
| 8 symbols × 3 folds | `validity.population` + each row `n_folds=3` | MATCH (BAC/F/SOFI/PLTR/TSLL/SMCI/AMD/AAPL) |
| Only 3/24 train both-cost passes | Walked `train_gate_pass`: PLTR fold2, SMCI fold1, AMD fold0 | MATCH |
| Those holdouts fail | PLTR f2 slip n10/−$32.69 DD $170.64 ml $219.26; fixed n10/+$41.92 DD $131.80 ml $212.26. SMCI f1 slip n8/−$52.67 DD $54.73; fixed n8/−$13.76 DD $29.57. AMD f0 slip n9/−$245.67 DD $210.72; fixed n9/−$138.86 DD $140.38 | MATCH (all `fold_gate_pass=False`) |
| Integrity exact / signal0 / reentry0 | 286 integrity-bearing candidate+control+window-row summaries (train+holdout axes + window chunk rows + controls; window-container dicts excluded) all `integrity=true`; signal_violations=0; same_bar_reentries=0 | MATCH (also 334 if window-container summaries included; all true either way) |
| Predeclared DNA, lag=1, no grid | `_pullback_config`: 7 DTE, ret≤−0.5%, RSI 35–50, `entry_signal_lag_bars=1`; no mutation grid | MATCH |
| Expanding rolling-origin folds | `_fold_boundaries` 40/60/80% train + following non-overlapping 20% holdouts; unit-tested | MATCH |
| Train gate required before fold pass | `_fold_pass` conjuncts train+holdout+window; negative test when train fails and holdout passes | MATCH |
| Proxy-only / no L1 | `claim_scope` synthetic listed-Friday BS; archive still `n_market_dates=1`, `provider_backtest_eligible=false` | MATCH |
| No hyp / capital seat / leader | Coverage: 20 structures, 245 hyps, quality leader none; no registry promote claimed | MATCH (no contrary evidence) |
| Focused tests 21/21 | Re-ran `tests.test_pcs_pullback_rolling_origin_lab` + momentum + expiry_grid | MATCH (21 OK) |
| Full suite 103/103 | Not re-run this challenger phase (cost); focused green; finalizer must reconfirm full suite | ACCEPTED PENDING FINALIZER |
| Doctrine/coverage updated for reject | `docs/INCOME_STRATEGY_COVERAGE.md` history + direction gap; `trader_income_coverage.py` gap text; income-coverage LATEST 1437 | MATCH |

## Rubric

1. **Goal progress — PASS.** Material delta: new reusable rolling-origin direction harness + decisive multi-fold reject of the predeclared mild-pullback PCS family. Improves the self-learning falsification surface even though no edge was found.
2. **Creativity and independence — PASS.** Not a familiar free-evolve / TSLL PCS polish tunnel. Accepted prior NEXT only after orientation, then upgraded from one-split to expanding rolling-origin with exact mirror/unconditional controls and no grid retune. Distinct from the just-closed momentum and close-shock families.
3. **Claim validity — PASS.** Prerequisites limited to the chosen proxy experiment. Observed-archive thinness correctly blocked only L1/observed-cost claims. No promotion, no leader resurrection, no shadow/live language.
4. **Evidence and test quality — PASS (nits).** Real lab JSON + script + tests. Tests cover lag/mirror disjointness, fold chronology, train∧holdout conjunction, and unrounded DD fail-close — useful behavioral/boundary/negative checks rather than pure implementation mirrors. Observed-vs-proxy and synthetic Friday provenance labeled. **Nit:** tests do not yet pin window dense-neg / integrity-fail fold rejection or all-folds-required aggregation; not claim-invalidating because the live run failed on PnL/DD before those edges mattered.
5. **Falsification — PASS.** Clear preregistered falsifier; 0/8 all-fold passes; stop-without-retune; isolated train survivors explicitly fail holdout; controls present for diagnostics without promotion from control wins.
6. **Capital honesty — PASS.** Living leader remains empty (`b195f5fe` historical only). Absolute gates ml≤$300, DD≤$75, dense-neg≤5, dual after-cost SHIP; train survivors that look “good” mid-train fail holdout risk/PnL. No capital seat. Structure/capital_fit/max_loss/max_lots stated at run level.
7. **Research freedom — PASS.** Weekend correctly prevented a second distinct NY market-date archive append; that blocked only observed-history work. Executor did not freeze unrelated exploration beyond choosing the highest-information closed loop available off-RTH. No removable restriction found that should have forced a different experiment today.
8. **ONE NEXT seed — PASS.** Distinct-RTH all-expiration TSLL archive append 1→2/3, no provider hist before 3/3, leave closed families closed. One seed; no live/shadow.

**Overall: PASS 8/8** (minor nits only; no claim-invalidating repair required for the reject decision).

## Findings for finalizer

### Accept / keep
- Family leave: `REJECT_MILD_PULLBACK_PCS_ROLLING_ORIGIN` stands; no grid expansion, no registration, no capital path.
- Rolling-origin lab + tests + doctrine/coverage residue are durable and should ship with the run.
- Score framing 4/5 P2+P3 L0 is honest.
- Hard stops respected (no broker/live/arm/evolve-apply by challenger; executor reported paper-only).

### Nits (non-blocking)
1. **Readiness NEXT stale:** `reports/readiness/LATEST.md` still lists the mild-pullback rolling-origin experiment as BUILD NEXT (from 1323). That loop is now done; NEXT must become the RTH archive seed only (plus explicit leave of closed families). Challenger patches this surface.
2. **Full-suite 103/103** not re-executed in challenger; finalizer must reconfirm focused + full suite before integration.
3. Optional later: one more negative-control test that forces window `dense_negative_n` or window integrity fail to reject `_fold_pass` — capability polish, not a defect in this reject.
4. Three consecutive direction-signal labs (close-shock → momentum → pullback) are **not** thrash: each changed the experiment class and closed a distinct predeclared claim. Further daily-bar signal grids without a new capability or observed-cost realism would start looking low-information.

### Do not accept
- Any soft reinterpretation of PLTR train SHIP or fixed-cost positive holdout PnL as a near-miss seat (holdout DD $131–$170 fails absolute bar hard).
- Provider-backed historical sim or L1 claim from this proxy result.
- Reopening closed families (close-shock, bullish-momentum, mild-pullback, collar, asymmetric IC, BAC Fri7, etc.) without genuinely new evidence class.

## Merged judgment

Executor closeout is sound. Challenger verifies the reject metrics and evidence validity, accepts the family leave, and consolidates NEXT to the blocked observed-data density path that can unlock a different evidence class.

PARTIAL PHASE ONLY — no commit/push/merge/RUN COMPLETE.
MOA_CHALL_DONE

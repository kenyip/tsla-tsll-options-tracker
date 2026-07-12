# MOA BUILD challenger critique — 2026-07-12T1323

ROLE: Grok 4.5 challenger (read-only judgment)
PHASE: BUILD · SLEEVE_USD: 3000 · PAPER_ONLY
STAMP: 2026-07-12T1323 · branch `trader/run-2026-07-12T1323`
SUBJECT: lagged bullish-momentum PCS walk-forward lab (executor GPT 5.6 Sol)

## Verdict

**PASS 8/8** (one NEXT tightening accepted for finalizer; no claim-invalidating repair required).

Progress type: P2 direction capability + P3 decisive chronological falsification.
Honesty: L0 BUILD. No living quality leader. No capital seat. No hyp registration/promotion.
Score agreement: **4/5**.

This is a **partial critique phase only**. No commit, push, main integration, or RUN COMPLETE.

## What was verified (read-only + re-run tests)

| Claim | Check | Result |
|---|---|---|
| Lab decision | `.cache/platform/pcs_momentum_walkforward_lab_2026-07-12T1323.json` | `REJECT_BULLISH_MOMENTUM_PCS_WALKFORWARD`; `n_symbols=8`, `n_selected=8`, `n_holdout_pass=0`, `errors=[]` |
| BAC sole train pass | selected_rows | BAC `train_gate_pass=true` only; config dte7 / ret≥0.5% / RSI 50–65; train slip 49/+$72.58/DD53.89 SHIP ml94.92; train fixed 40/+$79.32/DD32.47 SHIP ml94.74 |
| BAC holdout reject | selected_rows | slip 42/+$42.88/DD94.72 SHIP ml94.58; fixed 39/−$53.59/DD96.12 NULL ml94.80 — fails positive fixed edge + $75 DD |
| SOFI mirror not a seat | controls.bearish_mirror | slip 16/+$35.56/DD38.82 SHIP; fixed 15/+$11.65/DD43.16 SHIP; SOFI `train_gate_pass=false` for bullish family — selection-biased control only |
| Integrity 88/88 | walk of train+holdout+controls+window rows | **88** axis summaries, all `integrity=true`, same-bar reentries 0, signal_violations 0 |
| Claim scope | JSON `claim_scope` | synthetic listed-Friday/rounded-strike BS daily-bar discovery; lagged signals; **not** observed quotes; cannot earn L1 |
| Train/holdout boundary | `walkforward_pass` + test | holdout cannot pass when train failed; train rank uses train axes only |
| Focused tests | re-run | `tests.test_pcs_momentum_walkforward_lab` + `tests.test_pcs_expiry_grid` → **15/15 OK** |
| Full suite | re-run | `unittest discover -s tests` → **90/90 OK** |
| Coverage | income-coverage-LATEST | 20 structures / 245 hyps / living leader **none**; direction gap notes bullish-momentum walk-forward rejection |
| Capital posture | rows | selected max_loss mostly ~$90–$230; BAC <95; gate ≤300; default 1-lot; no seat |
| Red-lane | residue | no broker/live/shadow/arm; executor uncommitted on run branch as required |

## Rubric

1. **Goal progress — PASS.** Material research delta: reusable chronological train→holdout harness plus a decisive family reject. Does not create income yet, but raises the chance of finding a robust paper-testable edge by closing a direction-bias dead-end with integrity evidence instead of polishing vanity full-sample SHIP.
2. **Creativity / independence — PASS.** Sunday correctly blocked the prior distinct-NY-RTH archive append (still 1/3 dates). Choosing an independent lagged bullish-momentum PCS axis after close-shock rejection is justified, multi-name (8 symbols), not TSLL-PCS monomania, and does not reopen closed collar/IC/BAC-Fri7 paths.
3. **Claim validity — PASS.** Prerequisites for the chosen experiment were the right ones: lag-1 signals, train-only ranking, one holdout evaluation, both cost axes, integrity. Executor repaired a fail-open `walkforward_pass` before trusting results. Observed-quote density was correctly treated as out of scope for this proxy claim, not as a freeze on all discovery.
4. **Evidence / test quality — PASS.** Real lab path, script, and boundary tests exist. Tests cover negative PnL gate, train-rank not reading holdout, train-fail blocking holdout pass, and momentum/mirror filter disjointness. Observed vs proxy is labeled. Population purity = PCS only, documented. Nit (non-blocking): dense-negative window scan is fixed-$0.01 only; both-cost dense-neg would be slightly stronger, but the BAC reject already fails on full-holdout fixed PnL/DD.
5. **Falsification — PASS.** Predeclared falsifier: no train-selected row clears both costs + ml/DD/dense-neg/integrity on untouched holdout. Outcome 0/8. Negative controls present; SOFI mirror explicitly non-candidate. No soft promote of BAC partial slip-positive holdout.
6. **Capital honesty — PASS.** No living leader; `l1` empty; BAC max loss competitive vs absolute $300 but holdout DD ~$95–$96 > $75 and fixed after-cost negative. No readiness B-check greenwash. Former `b195f5fe` remains historical only.
7. **Research freedom — PASS.** Blocked one-date archive did not freeze unrelated valid proxy exploration. No removable prompt restriction found. Freedom audit accepted.
8. **ONE NEXT seed — PASS with tightening.** Executor NEXT (rolling-origin mild bearish-momentum PCS) is a single high-info follow-on **if** it is predeclared and not SOFI-control chasing. Challenger tightens the seed below; finalizer should adopt the merged seed, not free-form “mild.”

## Findings for finalizer

### Accept / no repair required
- Family leave: `REJECT_BULLISH_MOMENTUM_PCS_WALKFORWARD` stands.
- Do **not** register BAC, SOFI mirror, F mirror, or any holdout-only control.
- Do **not** reopen close-shock, asymmetric IC, collar, BAC Fri7 management, put-ratio, BWIB, or router capital search.
- Leave formal B checks / living leader empty unless finalizer finds a separate claim defect (none found).
- Durable surfaces already present: `scripts/pcs_momentum_walkforward_lab.py`, `tests/test_pcs_momentum_walkforward_lab.py`, coverage/doc notes.

### Accepted nits (optional finalizer polish; not claim-invalidating)
1. Pin NEXT DNA explicitly (see merged seed) so “mild bearish” cannot become post-hoc SOFI mimicry.
2. Optional: window dense-neg under both cost axes in a later harness revision — not required to uphold this reject.
3. AAPL train was dual-axis SHIP on PnL but failed train gate on DD (~$142–$169) — good gate honesty; keep as example that SHIP≠pass.

### Rejected / do not do
- Do not promote SOFI/F/PLTR bearish-mirror holdout positives.
- Do not expand the 16-cell grid or retune RSI/return thresholds because bullish failed.
- Do not claim L1 or paper seat from proxy walk-forward.
- Do not run provider-backed historical entry sim before archive density ≥3 NY market dates.
- No live / shadow / arm / broker.

## NEXT (challenger-tightened; see merged-next-seed.md)

One predeclared **bearish-mirror / mild-pullback PCS** rolling-origin walk-forward on the same eight symbols:
- Reuse harness; **no grid expansion**.
- Predeclare fixed mirror DNA from the BAC-selected bullish config’s exact mirror (ret_1d_max=−0.5%, RSI 35–50, 7 DTE) **or** one train-ranked mirror cell chosen only on each fold’s train slice before looking at that fold’s holdout.
- Require train-gate pass before each next fold evaluation.
- Reject unless both cost axes and window DD ≤$75 hold across folds.
- SOFI holdout control is **not** a seed candidate and must not be reverse-engineered.
- Parallel when RTH: append all-expiration TSLL archive 1→2/3; no provider hist before 3/3.

## Freedom / thrash check

Not thrash: new harness + new family decision + integrity evidence. Adjacent to close-shock but distinct signal family (momentum band vs downside close-shock). Tight BUILD loop still justified (empty capital path).

## Challenger phase close

MOA_CHALL_DONE — partial phase only. Sol finalizer must reconcile, verify, promote learning, then deterministic integration may claim RUN COMPLETE.

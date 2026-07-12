# MOA BUILD challenger critique — 2026-07-12T1616

WAKE: 2026-07-12T1626 PDT (Sunday; market closed)
PHASE: BUILD
SLEEVE: 3000
PAPER_ONLY: true
ROLE: Grok 4.5 challenger / read-only judgment
EXECUTOR: GPT 5.6 Sol (executor-closeout.md + 2026-07-12T1616-moa-exec.md)

## Independent verification

Stress artifact: `.cache/platform/pcs_vol_compression_rolling_origin_lab_2026-07-12T1616.json`

| Claim | Independent result |
|---|---|
| decision | `REJECT_VOL_COMPRESSION_PCS_ROLLING_ORIGIN` |
| population | BAC,F,SOFI,PLTR,TSLL,SMCI,AMD,AAPL — 8/8 completed, errors=[] |
| train gates / complete folds | 0/24 train_gate_pass; 0/24 fold_gate_pass; n_all_folds_pass=0 |
| min strategy-axis n by symbol | BAC6 F6 SOFI4 PLTR5 TSLL2 SMCI6 AMD6 AAPL7 → range **2–7** |
| worst fold DD by symbol | BAC **119.35** … AMD **425.53** (all > $75 absolute gate) |
| worst one-lot max_loss | **91.25** (TSLL) … **227.80** (AMD); all ≤$300 so risk-fit alone never rescued edge |
| integrity leaf summaries | **286/286** integrity true; signal_violations=0; same_bar_reentries=0 |
| claim_scope | synthetic Friday/rounded-strike BS discovery; observed underlying HV only; cannot earn L1 |
| living leader | none; absolute gates used; `b195f5fe` not seated |
| new unit tests | `tests/test_pcs_vol_compression_rolling_origin_lab.py` **3/3 OK** (re-ran) |
| lag wiring | `entry_signal_lag_bars=1` → `entry_filters_pass(signal_row)` in `pcs_sim` |
| HV filter | fail-closed on missing/nonfinite/≤0 denominator; ratio from `hv_20/hv_60` only |
| controls | unconditional (entry_* stripped, lag retained) + expansion `entry_hv_ratio_min=1.20` disjoint from compression max 0.80 |
| prior NEXT supersede | Sunday → archive 1→2/3 impossible; vol-compression is a new evidence class not in orientation closed_families |
| registration/promotion | none observed; BUILD/L0 |

Dense-positive train axes without gate pass (not claimed by executor; challenger note only): SOFI fold2 slip n28/+$4.74 DD$125.84; AAPL fold1 fixed n23/+$16.78 DD$224.8; AAPL fold2 fixed n32/+$6.93 DD$224.8. All fail absolute DD / SHIP gates → consistent with 0 train passes.

Executor full-suite claim 122/122 and focused 25/25 were **not** re-run end-to-end in this phase (new file alone is 3 tests; 25 likely includes inherited related suites). Finalizer must reconfirm focused+full suite before integration.

## Rubric

1. **Goal progress — PASS.** Material useful delta: reusable fail-closed HV-ratio entry feature + honest closed family on a new realized-vol evidence class. No false candidate. Improves search discipline and coverage map without claiming edge.
2. **Creativity / independence — PASS (nit).** Original axis (prior-bar `hv_20/hv_60≤0.80` compression) vs closed return/RSI/router/collar/IC/BAC families; prior NEXT correctly treated as non-executable Sunday context. Mild familiar-recipe pattern remains (fourth consecutive PCS daily-bar signal family on the same eight names), but novelty key and evidence class are real — not thrash.
3. **Claim validity — PASS.** Prerequisites match the experiment: proxy option marks labeled; observed HV labeled; L1 explicitly blocked; no archive-density claim advanced; no reopening of closed families.
4. **Evidence and test quality — PASS (nit).** Real lab JSON + code + doctrine updates with cited paths. New tests cover inclusive boundaries, disjoint compression/expansion, lag retention, and fail-closed invalid HV. Nit: new suite is thin (3 unit tests) and does not add an end-to-end fold-gate negative-control in the new file; machinery is inherited from pullback rolling-origin lab. Not claim-invalidating given 0/24 train gates.
5. **Falsification — PASS.** Predeclared DNA, no grid/tuning, train-gate before holdout, dual proxy costs, absolute ml/DD/dense-neg gates, unconditional + expansion controls, exact integrity. Decision REJECT is the only honest outcome.
6. **Capital honesty — PASS.** No living leader; absolute $300/$75 gates; one-lot capital_fit/max_loss/max_lots reported; no seat, no B-check greenwash, no stale b195f5fe seat.
7. **Research freedom — PASS.** Observed option archive still 1/3 blocks only provider/L1 claims; did not freeze this HV-state exploration. No caller slot/structure lock. No removable restriction introduced.
8. **ONE NEXT — PASS.** Highest-information next: distinct NY RTH TSLL all-expiration archive append 1→2/3, no provider history before 3/3. Leave this vol-compression family closed; no live/shadow/arm.

## Dispositions

| Finding | Severity | Disposition |
|---|---|---|
| REJECT decision + metrics match stress JSON | — | **ACCEPT** |
| Family closed without registration/promotion | — | **ACCEPT** |
| Provenance/L0 claim scope correct | — | **ACCEPT** |
| Sunday supersede of archive NEXT justified | — | **ACCEPT** |
| Thin new unit-test file (3) vs claimed focused 25 | nit | **ACCEPT with finalizer duty** — re-run focused related suite + full unittest; optional strengthen behavioral fold-gate test only if cheap |
| PCS daily-bar signal sequence familiarity | nit | **NOTE only** — do not reopen; after archive path or if another off-hours wake is forced before RTH, prefer a non-PCS-signal novelty class |
| Readiness LATEST NEXT already archive 1→2/3 | — | **no patch** |

## Score

**PASS 8/8** (two nits; none claim-invalidating).

## Required finalizer actions

1. Re-verify stress decision + key aggregates (or exact JSON path) and re-run focused related tests + full `unittest discover`.
2. Promote learning: closed family `pcs-vol-compression-daily-bar` / novelty key; skill pitfall if missing; coverage already updated.
3. Keep readiness phase L0 / no leader; optionally prepend wake note on closed vol-compression family — do **not** change formal B checks.
4. Integrate only after green verification; no live/shadow/arm.

## Explicit non-actions (challenger)

- No evolve --apply
- No broker / paper order / arm / shadow-live promotion
- No commit / push / merge / RUN COMPLETE claim

MOA_CHALL_DONE

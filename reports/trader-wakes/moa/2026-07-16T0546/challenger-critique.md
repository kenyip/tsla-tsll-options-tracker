# MOA challenger critique — 2026-07-16T0546

Role: Grok 4.5 challenger / read-only judgment
Phase: BUILD / L0 underlying discovery (successor epoch after mandatory reassessment)
Status: CHALLENGER RECEIPT — finalizer reconciled; deterministic integration pending; no commit, push, merge, or RUN COMPLETE

## Verdict

**PASS WITH NITS**

Finalizer reconciliation note (2026-07-16 06:22 PDT): current hashes in this receipt supersede the challenger-phase bytes after N1–N3 machine diagnostics were added. Challenger's independently reproduced strategy metrics and verdict are unchanged; finalizer independently replayed the current normalized payload and reconciled every nit in `learning-promotion.md`.

Accept the executor's exact claim-bearing outcome:

- `FAMILY_CLOSED` for `BROAD_INDEX_OVERNIGHT_ABSORPTION_BULL_CALL_21D_V1` / `BROAD_INDEX_OVERNIGHT_SELL_INTRADAY_ABSORPTION_FORWARD_UPDRIFT`
- Funnel: `F0_MECHANISM -> F0_MECHANISM`
- Strategy advancement: **false**
- Search information: useful (mandatory predecessor-epoch reassessment + successor epoch open + dependence-safe four-index lab + exercised decision)
- Capital / L1 / seat / paper / shadow / arm / live: **none**

Successor epoch `REPEATED_EXPOSURE_SPECIFICITY_DISCOVERY_V1` now has **one** counted no-advance decision after integration. `strategy_pivot_required=false`; `strategy_burst_stop_required=false`. Predecessor epoch remains completed and is not reopened.

## Independent verification (read-only)

Canonical artifact: `reports/trader-wakes/moa/2026-07-16T0546/broad-index-overnight-absorption-train.json`

| Check | Result |
|---|---|
| Raw SHA-256 | `29d0c6199c96ed9c91290467c748e34c5c7cd4bdced243abb84dfde93fe51b73` — **matches** file bytes |
| Normalized SHA (exclude only `generated_at`, sort_keys compact JSON) | `85ce2277b587135cd7394e0cce0b6e90cc5ce82e6c7f8067241042cb60a3b4a5` — **matches** |
| Train eligible/matched rows | 144 / 139; control support 96.5278% — **matches** |
| Clustered episodes / years / symbols | 97 / 12 years (2008–2019) / DIA,IWM,QQQ,SPY — **matches** |
| Event / control means after 10 bps | −0.048879% / +0.017988% — **reproduced** from 97 episodes |
| Paired mean / median | −0.066867% / −0.124070% — **reproduced** |
| Circular five-episode-block LB90 | −0.623971% — **matches** artifact (`bootstrap_samples=10000`, block length 5) |
| Event hit rate | 57.7320% — **reproduced** |
| Event-return worst-decile after 10 bps | −5.724566% — **reproduced** (k=10 worst of 97) |
| Paired-excess worst-decile diagnostic | −6.831920% — **reproduced** (not the gate population) |
| Control distance median/max | 268 / 735 sessions — **matches** |
| Integrity violations | empty list — **ok** |
| Gate conjunction | pass density/years/symbols/support/hit/integrity; **fail** event mean, paired mean, LB90, event tail ≥−5% — **matches** `gate_pass=false` |
| Holdout | 105 matched rows / 68 dates, 2020-01-06→2026-06-29, identity `8d427bb57ee199bc6fa2f1abefbd920df184650ac0a0bd1356f2e0a2c228b193`; outcomes unread; simulation false; option_pricing_calls=0 — **ok** |
| Authority labels | `l1_claim=false`, `f2_claim=false`, `claim_bar=L0_DISCOVERY_ONLY`, `strategy_advancement=false` — **ok** |
| Capital planning fields | capital_fit_usd=200, max_loss_usd=200 (frictionless planning), max_lots=1, sleeve 3000 — **ok** |
| Runner / tests present | `scripts/broad_index_overnight_absorption_train_lab.py`, `tests/test_broad_index_overnight_absorption_train_lab.py` (7 focused tests incl. lag invariance, prior controls, same-date clustering, positive panel, uncertainty fail, event-vs-paired tail negative control, holdout identity-only) |
| Reassessment / epoch docs | `docs/SEARCH_DESIGN_REASSESSMENT_2026-07-16T0546.md`, `docs/SEARCH_EPOCH_2026-07-16T0546.md`, charter present |
| Executor-phase `configs/search_epoch.json` | successor active; `counted_no_advance_decisions=1`; last outcome `FAMILY_CLOSED`; discovery/capital bars restored — consistent with closeout (finalizer still owns integration) |

Density and hit rate cannot rescue negative absolute/relative expectancy, negative dependence-aware LB90, and a failed event tail. Close is correct.

## Rubric

1. **Strategy charter** — **PASS**. Mechanism (overnight sell absorbed by regular-session demand → short-horizon updrift), candidate/family IDs, F0→F1 or close, complete Layered Edge Stack, ten-gate predeclared falsifier, and exact closed outcome `FAMILY_CLOSED` are explicit in `strategy-charter.md` + closeout.
2. **Strategy vs operations** — **PASS**. Reassessment docs, lab scaffold, and tests are search information only; same-wake experiment closed the family. Not sold as `STRATEGY_ADVANCED` or capability-only success.
3. **Goal progress** — **PASS**. Honest F0 falsification of a dense repeated-exposure class after a required design reassessment improves search quality: removes a near-miss overnight geometry and forces the next wake onto a different economic mechanism rather than threshold salvage.
4. **Creativity / independence** — **PASS**. Honored burst-stop: reassessment before any fourth test in the predecessor epoch. Successor design changed evidence class (four-index same-date clustering + dependence-aware blocks) without post-outcome retune of the prior SPY secondary screen. Not a familiar PCS/TSLL tunnel.
5. **Claim validity** — **PASS**. F0 underlying discovery only; no option marks; no L1/seat; sealed holdout; absolute discovery gates with zero living leaders.
6. **Evidence and test quality** — **PASS WITH NITS**. Real runner, SHA-cited panels, sealed holdout, useful behavioral/boundary/negative controls (including event-tail ≠ paired-tail), deterministic normalized replay. Nits below do not reverse the close.
7. **Falsification** — **PASS**. Frozen gates failed as predeclared; dominant failure recorded; dual-ID quarantine plus nearby threshold/horizon/sign/unclustered/option-wrapper anti-salvage stated.
8. **Capital honesty** — **PASS**. No living leader, L1, or seat claimed. Planning $200 debit width labeled frictionless and unmeasured for path/assignment. Simultaneous ETFs treated as one risk unit in prose.
9. **Research freedom** — **PASS**. Observed-option thinness did not freeze this historical multi-index route. No unnecessary allowlist.
10. **ONE NEXT** — **PASS**. `YIELD_CURVE_STEEPENING_REGIONAL_BANK_FORWARD_UPDRIFT_PREFLIGHT` is a materially different repeated-exposure class with an explicit pre-outcome proxy-semantics kill switch. No live/shadow promotion.

## Accepted disposition

| Item | Disposition |
|---|---|
| Outcome | Accept `FAMILY_CLOSED` F0→F0 |
| Advancement | Accept false |
| Dominant failure | Accept: dense clustered train is negative on absolute event center, paired specificity, dependence-aware LB90, and event-return tail; hit rate alone is not edge |
| Quarantine | Accept exact four-index / SMA100-up / overnight5≤−1% / intraday5≥+1% / next-close / five-session / 10-bps / same-symbol-control geometry; nearby threshold/horizon nudges; sign inversion; unclustered pseudo-replication; option-wrapper salvage |
| Epoch implication | Accept successor counted no-advance = 1 after integration; pivot/burst false |
| ONE NEXT | Accept yield-curve / regional-bank preflight with fail-closed proxy semantics |

## Findings / nits (finalizer should reconcile; none reverse the close)

### N1 — Five-session F0 horizon vs 18–24 DTE planning option (standing boundary)

F0 measures next-close → +5 completed sessions. Planned expression remains an 18–24 DTE $2-wide bull-call with a five-session time stop among future management rules. Direction is aligned; theta/vega/debit path over full DTE is **not** measured. Keep planning-only language sharp in readiness/closed-family residue so “21D call” cannot be skimmed as validated.

### N2 — Residual near-date / overlapping-window dependence remains material

Same-date clustering correctly collapses 139 matched rows → 97 inference episodes, and per-symbol freeze uses `next_available = exit_pos + 1` (no same-symbol outcome overlap). Independent scan of clustered episode dates still finds **28/96** consecutive gaps ≤7 calendar days, so five-session windows can still share calendar exposure across nearby signal dates. Executor correctly labels the five-episode block as sensitivity, not proof of 97 independent episodes. Finalizer: persist residual near-date dependence in durable closed-family notes; do not allow readers to treat n=97 as i.i.d.

### N3 — Cross-index “breadth” is mostly sequential, not simultaneous

Episode `n_symbols` distribution: 67×1, 20×2, 8×3, 2×4. Represented-symbol and density gates pass, but the economic story of simultaneous multi-index absorption is only sparsely realized. Close is still correct (negative centers even with clustering). Finalizer: do not reopen via “require 3+ symbols per episode” after seeing outcomes — that is post-hoc geometry salvage. Any reopen needs a predeclared new mechanism/evidence class.

### N4 — Control local-specificity remains weak even with high support

Median/max control distance 268 / 735 sessions with 96.5% support. Prior-only matching works chronologically but is often multi-quarter remote, so paired specificity is soft. Because paired center and LB90 are already negative, remoteness further weakens any salvage fantasy rather than rescuing the family. Persist distances in closed-family / epoch diagnosis.

### N5 — Event-tail labeling is already correct; keep it that way

Unlike the prior Form 4 phase, this lab already stores `event_return_worst_decile_mean_after_10bps`, gates on event returns, and tests that paired-excess tails are not substituted. No label repair required unless finalizer regenerates for other reasons.

### N6 — Full-suite verification is executor-attested

Challenger independently verified claim metrics, SHAs, gate conjunction, holdout seal, runner/tests presence, and residual dependence diagnostics. Full unittest 431/431, pytest 441+18, and `just test` greens are accepted as executor-attested paths. Finalizer must re-run focused + full suite before RUN COMPLETE.

### N7 — Integrated readiness surfaces still show predecessor truth

`reports/readiness/LATEST.md` still reflects integrated `2026-07-16T0454` Form 4 / burst-stop state. That is correct for a partial phase, but its ONE NEXT (`SEARCH_DESIGN_REASSESS_AFTER_FORM4_CLUSTER_DENSITY_UNCERTAINTY_CLOSE`) is now **stale** because this wake already closed that reassessment and a successor family. Challenger patches readiness NEXT only (below). Finalizer owns full readiness rewrite (current decision, epoch counters, closed-family residue) at integration.

### N8 — NEXT preflight must kill on proxy semantics, not after KRE outcomes

`YIELD_CURVE_STEEPENING_REGIONAL_BANK_FORWARD_UPDRIFT_PREFLIGHT` is accepted only if the wake first freezes whether a point-in-time Treasury-duration ETF spread (or similar) can honestly express a **lending-margin / regional-bank** mechanism without composition, futures-roll, or credit-beta confounds. If not, reject pre-outcome as `EVIDENCE_WAIT` or a design stop — do not run a KRE train and then blame the proxy.

## Rejected misreads (do not do these)

- Do **not** salvage via looser overnight/intraday thresholds, horizon changes, sign inversion, or reading holdout outcomes.
- Do **not** uncluster same-date ETF rows to inflate n after seeing a dense negative.
- Do **not** wrap the same underlying geometry in a bull-call sim and call it a new family.
- Do **not** treat reassessment docs or the lab scaffold alone as `STRATEGY_ADVANCED`.
- Do **not** re-enter the completed predecessor epoch or ignore its three closed families.
- Do **not** claim capital seat, L1, paper packet, shadow, or arm.

## Freedom / thrash audit

- Freedom preserved: multi-index historical OHLCV route used; observed-archive blockage did not freeze discovery.
- Not thrash: mandatory reassessment + new dependence-safe evidence class + decisive dense falsification.
- Anti-thrash NEXT correctly pivots mechanism (rates → regional banks) with a preflight gate rather than retuning overnight absorption.

## ONE merged NEXT seed

`YIELD_CURVE_STEEPENING_REGIONAL_BANK_FORWARD_UPDRIFT_PREFLIGHT`

Before any train outcomes: validate that a completed, point-in-time steepening measure built from fixed Treasury-duration proxies can honestly support a regional-bank lending-margin economic mechanism. If proxy semantics fail (composition, roll, credit/beta confounds, or non-point-in-time construction), stop pre-outcome without inspecting KRE returns. Only if the mechanism/proxy pass, freeze a train-only KRE (or predeclared regional-bank panel) geometry with density, prior same-regime controls, sealed holdout, and a future one-lot defined-risk bull-call planning expression — then advance-or-close under frozen gates. No overnight-absorption salvage; no sealed holdout reads from closed families; no L1/seat/paper/shadow/arm/live claims from this seed alone.

## Challenger phase boundary

No evolve `--apply`, no broker, no arm, no commit/push/merge, no RUN COMPLETE. Finalizer owns repair of accepted nits, verification re-run, learning promotion, readiness full reconciliation, and integration prep.

MOA_CHALL_DONE

## Finalizer reconciliation note (post-challenge)

The challenger judgment above is preserved as phase evidence. Finalizer accepted the close and reconciled every nit: explicit five-session-F0 versus 18–24-DTE planning labels; 28/96 near-date gaps; breadth 67×1, 20×2, 8×3, 2×4; remote controls 268/735; no post-hoc breadth rescue; and independent 9/9 focused, 65/65 adjacent, 433/433 full-unittest plus deterministic replay verification. Current raw/normalized claim SHA-256 is `29d0c6199c96ed9c91290467c748e34c5c7cd4bdced243abb84dfde93fe51b73` / `85ce2277b587135cd7394e0cce0b6e90cc5ce82e6c7f8067241042cb60a3b4a5`; earlier hashes identify the challenger-phase bytes only. `learning-promotion.md` records accepted/rejected dispositions. Deterministic wrapper integration remains pending.

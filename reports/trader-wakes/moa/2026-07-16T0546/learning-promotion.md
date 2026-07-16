# Learning promotion — 2026-07-16T0546

## VERIFICATION

Finalizer-owned commands and exact results:

- `.venv/bin/python -m unittest -v tests.test_broad_index_overnight_absorption_train_lab` → **9 tests**, `OK` in 2.057s. This suite covers completed-bar lag/future invariance, prior-only non-trigger/no-reuse controls, same-date clustering, near-date and breadth diagnostics, the five-session-F0 versus 18–24-DTE planning boundary, a complete positive panel, uncertainty rejection, event-tail-versus-paired-tail negative control, and holdout identity-only serialization.
- `.venv/bin/python -m unittest tests.test_broad_index_overnight_absorption_train_lab tests.test_trader_build_compounding tests.test_trader_run_completion_gate tests.test_trader_income_coverage tests.test_trader_build_progress` → **65 tests**, `OK` in 11.973s.
- `.venv/bin/python -m unittest discover -s tests` → **433 tests**, `OK` in 37.656s.
- `.venv/bin/python scripts/broad_index_overnight_absorption_train_lab.py --out /tmp/broad-index-overnight-absorption-replay.json` followed by normalized payload comparison → `substantive_replay_equal=true`; normalized SHA-256 `85ce2277b587135cd7394e0cce0b6e90cc5ce82e6c7f8067241042cb60a3b4a5`; strict JSON true; option pricing calls 0.
- Independent aggregation of the 97 serialized train episodes reproduced event mean `-0.0004887895651278447`, control mean `+0.00017988388260603463`, paired mean `-0.0006686734477338796`, event hit rate `0.5773195876288659`, event-return worst-decile `-0.057245656120878174`, and paired-excess worst-decile `-0.06831920149268837`.
- `shasum -a 256 reports/trader-wakes/moa/2026-07-16T0546/broad-index-overnight-absorption-train.json` → raw SHA-256 `29d0c6199c96ed9c91290467c748e34c5c7cd4bdced243abb84dfde93fe51b73`.
- `.venv/bin/python scripts/trader_income_coverage.py --json --no-write` → 21 catalog structures, 246 hypotheses, 70 evolve artifacts, no quality leader; current TSLL option archive is 2/3 RTH market dates and `provider_backtest_eligible=false`.
- `git diff --check cfbaee28f66f39d82696db71930157a858598061` was green before handoff writing and is rerun in the final audit. Raw executor/challenger/finalizer session logs, generated prompts, and coverage stderr were removed as run-created debris; claim evidence, phase receipts, exit codes, charter, orientation, and reports were preserved.

The deterministic wrapper still owns staging, secret/path enforcement, commit, push, fast-forward integration into `main`, remote equality, clean-tree postflight, and the only valid `RUN COMPLETE` receipt. Integration is pending that gate.

## DURABLE

Strategy charter and accepted outcome:

- Economic mechanism: repeated overnight selling absorbed by positive regular-session demand across liquid broad-index ETFs might be transitory risk-transfer pressure and produce five-session upward drift.
- Exact candidate/family: `BROAD_INDEX_OVERNIGHT_ABSORPTION_BULL_CALL_21D_V1` / `BROAD_INDEX_OVERNIGHT_SELL_INTRADAY_ABSORPTION_FORWARD_UPDRIFT`.
- Frozen decision: advance `F0_MECHANISM -> F1_TRAIN` only if every train discovery gate passed; otherwise close at F0 without reading holdout outcomes or pricing options.
- Accepted result: `FAMILY_CLOSED`, `F0_MECHANISM -> F0_MECHANISM`, strategy advancement false. Train density, years, represented ETFs, control support, hit rate, and integrity passed; absolute event mean, paired mean, dependence-aware LB90, and event-return tail failed. The 105 matched holdout identities on 68 dates remain outcome-unread. The future 18–24 DTE $2-wide bull call remains unpriced planning context only, with `capital_fit_usd=200`, frictionless planning `max_loss_usd=200`, and `max_lots=1`; it grants no F1/L1/capital seat/paper/shadow/live authority.

Challenger disposition:

1. **N1 accepted and repaired.** Runner, claim, and tests now machine-separate the five-session underlying endpoint from the unmeasured 18–24 DTE option path and label $200 as a frictionless planning width ceiling before option-path risks.
2. **N2 accepted and repaired.** Claim and reports serialize 28/96 consecutive episode gaps at most seven calendar days and state that the circular five-episode block is sensitivity, not proof of independence.
3. **N3 accepted and repaired.** Claim and reports serialize breadth as 67×1, 20×2, 8×3, 2×4; no post-hoc 3+-symbol filter may reopen the inspected family.
4. **N4 accepted as a reporting limitation; rejected as a missing machine-evidence defect.** Median/max prior-control distance 268/735 sessions was already canonical and independently reproduced. It is now promoted on living readiness/epoch/closeout surfaces and cannot rescue the negative paired result.
5. **N5 accepted as an invariant; rejected as a current defect.** The runner already gates on event-return tail, stores paired tail separately, and has a divergent-tail negative control; finalizer preserved that behavior.
6. **N6 accepted as finalizer process ownership; rejected as a code defect.** Finalizer independently reran 9 focused, 65 adjacent, and 433 full tests plus deterministic replay rather than inheriting executor counts.
7. **N7 accepted as a finalization action; rejected as an executor/challenger defect.** `reports/readiness/LATEST.md`, the 0546 merge report, `INDEX.md`, epoch config/docs, and NEXT now carry the accepted broad-index close and successor streak one. The later 0630 RTH `LATEST.md` remains chronologically newest and explicitly references this finalizer-ready BUILD residue.
8. **N8 accepted as the sole NEXT boundary; rejected as a missing-NEXT defect.** The yield-curve/regional-bank route must pass point-in-time proxy/economic semantics before any KRE outcome access.

Durable surfaces:

- Machinery/tests: `scripts/broad_index_overnight_absorption_train_lab.py`; `tests/test_broad_index_overnight_absorption_train_lab.py`.
- Claim/charter/handoff: `reports/trader-wakes/moa/2026-07-16T0546/broad-index-overnight-absorption-train.json`, `strategy-charter.md`, `executor-closeout.md`, `challenger-critique.md`, `merged-next-seed.md`, `compounding.json`, and this file.
- Project truth: `docs/SEARCH_DESIGN_REASSESSMENT_2026-07-16T0546.md`, `docs/SEARCH_EPOCH_2026-07-16T0546.md`, `configs/search_epoch.json`, `reports/readiness/LATEST.md`, `reports/trader-wakes/2026-07-16T0546-moa-exec.md`, `reports/trader-wakes/2026-07-16T0546-moa-merge.md`, and `reports/trader-wakes/INDEX.md`.
- Derived coverage: `reports/readiness/income-coverage-LATEST.md` plus dated 0546/0601/0634 snapshots consistently report 21 structures, 246 hypotheses, 70 evolve artifacts, no quality leader, and the actual 2/3 RTH archive density.
- Concurrent RTH truth preserved: `reports/trader-wakes/2026-07-16T0630-rth.md` and chronological `reports/trader-wakes/LATEST.md` retain the 14/0/14 STAND_ASIDE result; finalizer corrected their stale 3/3 archive statement to 2/3 and provider-ineligible without altering the trade decision.
- Skill promotion: active-profile `trader-self-evolution` now includes the reusable pitfall that same-date clustering does not establish independent episodes or simultaneous breadth; future labs must serialize near-date gaps and breadth distribution and forbid post-outcome breadth rescue.
- Profile memory: no update. This wake produced a reusable procedure/test lesson, not a compact stable user preference or routing fact; the skill and repo are the correct durable surfaces.

## LESSON

Future Trader can now test synchronous cross-symbol exposures without skimming clustered row count as independent evidence. Same-date clustering removes exact-date pseudo-replication, but valid interpretation still requires residual near-date/window diagnostics, per-episode breadth, control-distance reporting, and a non-salvage rule against post-hoc breadth filters. The exact four-index overnight-sell/intraday-absorption geometry is dense and frequently positive, yet it has negative absolute expectancy, negative paired specificity, a negative dependence-aware lower bound, and a failed event tail. It is closed rather than tuned. A five-session underlying discovery result also remains categorically separate from an unpriced 18–24 DTE option plan.

## NEXT

`YIELD_CURVE_STEEPENING_REGIONAL_BANK_FORWARD_UPDRIFT_PREFLIGHT`: before any train outcomes, validate that a completed point-in-time steepening measure built from fixed Treasury-duration proxies can honestly support a regional-bank lending-margin mechanism without composition, futures-roll, credit-beta, or construction confounds. If proxy semantics fail, stop pre-outcome without inspecting KRE returns. Only if they pass, freeze chronology, density, prior same-regime controls, sealed holdout, labeled underlying cost, and future one-lot defined-risk bull-call planning fields, then advance-or-close under frozen gates. No overnight-absorption salvage, sealed holdout reads, L1, capital seat, paper, shadow, arm, broker, funding, or live claims.

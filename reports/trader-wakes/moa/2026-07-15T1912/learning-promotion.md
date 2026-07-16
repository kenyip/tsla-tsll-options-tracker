# Learning promotion — 2026-07-15T1912

## VERIFICATION

- Focused behavioral, boundary, negative-control, and integrity suite:
  - command: `unset GIT_INDEX_FILE; .venv/bin/python -m unittest tests.test_downside_shock_stand_aside_train_lab`
  - exact result: `Ran 7 tests in 0.090s — OK`.
  - coverage includes lag-safe next-session selection, no per-symbol overlap, outcome-invariant blueprint selection, dense positive path, isolated stale-edge-greater-than-current specificity failure, unread date-disjoint holdout, complete Layered Edge Stack/capital labels, present-day-panel bias, close-only fidelity, overlapping-partition confound, pooled-bootstrap dependence, positive-mean/absolute-hazard rejection, symbol breadth, overlap rejection, finite-value failure, and strict JSON.
- Required full suite:
  - command: `unset GIT_INDEX_FILE; .venv/bin/python -m unittest discover -s tests`
  - exact result: `Ran 356 tests in 18.157s — OK`.
- Focused finalizer-adjacent suite:
  - command: `unset GIT_INDEX_FILE; .venv/bin/python -m unittest tests.test_downside_shock_stand_aside_train_lab tests.test_trader_build_compounding tests.test_trader_income_coverage tests.test_trader_completion_contract tests.test_trader_run_completion_gate tests.test_trader_build_progress`
  - exact result: `Ran 65 tests in 9.092s — OK`.
- Changed Python/test compilation:
  - command: `.venv/bin/python -m py_compile scripts/downside_shock_stand_aside_train_lab.py tests/test_downside_shock_stand_aside_train_lab.py`
  - exact result: exit `0`, no output.
- Current-code claim replay:
  - command: `.venv/bin/python scripts/downside_shock_stand_aside_train_lab.py --out reports/trader-wakes/moa/2026-07-15T1912/downside-shock-stand-aside-train.json`
  - exact result: exit `0`; `FAMILY_CLOSED`; train `703`; holdout `412` unread; tracked-versus-fresh payload equal after excluding `generated_at`; both normalized SHA-256 `3d89f1ef3030729a826814bdd95ca964967587dce91ee63493e12f60d1fdc3c5`; tracked raw SHA-256 `83ed5d125ee3690c4bd56e7a15064389419786037eaefa946a1a247c6715d07d`; failed gates exactly `current_filter_edge_exceeds_stale_placebo` and `eligible_breach_rate_at_most_limit`.
- Search-epoch orientation compatibility:
  - command: `.venv/bin/python scripts/trader_build_compounding.py context --repo . --stamp 2026-07-15T1913 --out .cache/platform/orientation-finalizer-1912.json`
  - exact result: exit `0`; context retained active epoch id `2026-07-15-tail-hazard-discovery`, started stamp `2026-07-15T1912`, reassessment/charter/goal docs, success definition, `strategy_pivot_required=false`, and `strategy_burst_stop_required=false`. Pre-integration `epoch_record_count=0` and streak `0` are expected because context reads integrated prior compounding records; the current handoff becomes epoch wake one only after wrapper integration.
- Derived coverage:
  - command: `.venv/bin/python scripts/trader_income_coverage.py --write --stamp 2026-07-15T1912 && cmp -s reports/readiness/income-coverage-2026-07-15T1912.md reports/readiness/income-coverage-LATEST.md`
  - exact result: exit `0`; `21` structures, `246` hypotheses, `70` evolve artifacts, no leader; dated and LATEST files byte-identical.
- Schema-v2 handoff, complete diff/security review, and disposable-index `prepare`: pending final verification below before handoff.

Integration is pending the deterministic wrapper gate. This finalizer has not committed, pushed, merged, switched branches, or claimed `RUN COMPLETE`.

## DURABLE

Strategy charter and outcome:
- Economic mechanism: downside volatility clusters; a latest-five-session no-3%-loss filter inside lag-safe SPY-and-symbol uptrends should reduce ten-session 5% close-barrier hazard before a future bullish short-gamma PCS expression.
- Candidate/family: `MULTINAME_NO_RECENT_DOWNSHOCK_PCS_21D_V1` / `noncollapse|recent_5d_downshock_exclusion|spy_and_symbol_sma100_uptrend|positive_60d_momentum|10_session_close_barrier_5pct|pcs_21d_2wide_planned` on a present-day AAPL, MU, AMD, SMCI, TSLA, META, GOOGL, NVDA panel under SPY regime.
- Planned expression only: one-lot nearest listed 18–24 DTE `$2`-wide PCS; short 0.18–0.25 delta, at least `$0.30` credit, positive bids, two-leg NBBO width at most `$0.20`, five-session earnings blackout; `capital_fit_usd=$200`, structural one-lot `max_loss_usd=$200` before credit/closing friction, `max_lots=1`, one global correlated bullish unit.
- Wake outcome: `BLOCKER_REMOVED_AND_RETESTED`; the three-no-advance search-design blocker was removed and the dependent experiment retested to `FAMILY_CLOSED`. Funnel remains `F0_MECHANISM`; strategy advancement is false.
- Evidence: 703 train episodes (548 eligible/155 recent shock; all eight symbols), eligible breach 27.0073% versus the `<=10%` gate, recent edge +8.4766pp versus stale diagnostic +14.5722pp, LB90 +2.1356pp, integrity `[]`, 412 holdout blueprints unread, pricing calls `0`.
- Authority: underlying close-only L0 discovery. No F1/F2/L1, option cost/fill/managed-PnL claim, leader, capital seat, registry, paper, shadow, arm, broker, or live authority.

Accepted challenger findings and repairs:
- Accepted `PASS WITH NITS`, the wake container, and exact family close.
- Accepted present-day-panel survivorship/listing bias; the payload now sets `panel_bias_free=false` and the boundary appears in charter, reassessment, readiness, and final reports.
- Accepted the recent/stale overlap confound; both flags can be jointly true, so the comparison is a timing-specificity diagnostic rather than a pure RCT.
- Accepted the missing isolated specificity negative control; every other gate passes while stale edge exceeds current edge and gate_pass remains false.
- Accepted close-only and residual-dependence limits; daily closes can miss intraday lows, and separate pooled-group circular blocks are not multi-symbol date-blocked inference.
- Accepted the readiness rewrite and NEXT guard; living surfaces now record 1912, active tail-hazard epoch streak one, pivot/burst-stop false, empty capital path, and one genuinely new downside-semivariance ETF barrier seed.

Rejected claims:
- Rejected any `STRATEGY_ADVANCED`, F1/F2/L1, capital-seat, registry, paper, shadow, arm, broker, or live claim.
- Rejected rescue by positive relative edge, LB90, tail, or mean because absolute hazard and specificity were conjunctive failures.
- Rejected reopening the exact family through 2%/4% shocks, 3/7-session windows, looser breach ceilings, or panel churn.
- Rejected capability/tests as strategy progress without the in-wake family-close retest.
- No material challenger judgment was rejected; its nits were repaired or used to narrow authority.

Finalizer-discovered repair:
- The executor rewrote `configs/search_epoch.json` into a nested `active_epoch` shape that current `load_search_epoch` does not consume. The finalizer restored canonical top-level `status`, `epoch_id`, `started_stamp`, reassessment/charter/goal docs, success definition, discovery/capital bars, and epoch-progress fields. This prevents future zero-input orientation from silently losing the completed reassessment and resetting the streak against all history.

Promotion routing:
- Dated outcome/current project truth: tracked strict-JSON claim, reassessment, canonical epoch, executor/challenger/finalizer reports, readiness, coverage, LATEST, INDEX, this learning record, and schema-v2 compounding handoff.
- Reusable machinery/tests: `scripts/downside_shock_stand_aside_train_lab.py` and `tests/test_downside_shock_stand_aside_train_lab.py`.
- Skill: patched `options-strategy-analysis` with the reusable rule that overlapping current/stale flags make a specificity diagnostic confounded, require an isolated otherwise-pass specificity negative control, and require pooled-block versus multi-symbol date-blocked dependence labels.
- Memory: no addition. Dated metrics, family closure, and active-epoch streak belong in repository evidence; stable autonomy/capital/evidence stances already exist.

## LESSON

Future Trader now knows that a recent-downshock exclusion can produce a statistically positive relative hazard edge, a positive uncertainty lower bound, and milder tail/mean diagnostics while still failing the small-sleeve short-gamma problem. Absolute non-collapse and mechanism-specificity gates remain conjunctive; do not spend the holdout or option stage after either fails.

Future Trader can now make that boundary auditable: persist present-day-panel bias, close-only fidelity, overlapping-control confounds, and bootstrap dependence in the claim itself; isolate the specificity fail path with a negative control; and keep search-epoch state in the canonical top-level schema consumed by zero-input orientation.

## NEXT

`LOW_DOWNSIDE_SEMIVARIANCE_ETF_BARRIER_HAZARD_F0`: open a new family key and freeze before outcomes a cross-sectional downside-semivariance rank (left-tail second moment, not plain HV) on SPY, QQQ, IWM, XLF, XLE, XLK, XLI, XLV, justified as a lower single-name-event-concentration population after the present-day mega-cap panel failed absolute hazard. Primary endpoints are ten-session 5% close-barrier survival and worst-decile path loss versus the high-semivariance rank, with multi-symbol date-blocked uncertainty and a sealed chronological holdout. Mean return is diagnostic only. Stop before option pricing unless the predeclared absolute eligible breach gate `<=10%` or an equally capital-protective frozen equivalent passes. Do not reopen the closed low-HV mean-return or recent-downshock timer families; no registry, paper force, shadow, arm, broker, or live action.

# Learning promotion — 2026-07-14T0859

Strategy charter: persistent index-option insurance demand may make observed VIX exceed subsequent SPY realized volatility, but this wake tested only whether the frozen high same-close VIX/RV20 selector above fully warmed SMA200 adds a sufficiently dense, outcome-independent conditional signal for `SPY_VRP_VIX_RV_21D`. Scope remained candidate `SPY_VRP_PCS_VIX_RV_21D_V1`, `F0_MECHANISM -> F0_MECHANISM`, with a structural one-lot `$1`-wide PCS bound (`capital_fit_usd=100`, `max_loss_usd=100`, `max_lots=1`) and no fill, PnL, seat, or paper authority.

Outcome: `BLOCKER_REMOVED_AND_RETESTED` with retest decision `FAMILY_CLOSED`; strategy advancement false. The 0612 claim-bearing artifact was superseded, dominant-failure machinery was corrected, and the unchanged current-code experiment closed for insufficient disjoint matched-control density: 51 treated, 6 matched, assessment treated/matched counts 19/0, 9/6, 23/0, pooled 6<24, complete integrity counters zero, `pricing_calls=0`, candidate/registration false. Raw treated VRP and positive statistics on six pairs are underpowered context, not selector alpha.

## VERIFICATION

- `.venv/bin/python -m unittest tests.test_spy_vrp_pcs_study -v` -> `Ran 14 tests in 2.309s`, `OK`. This includes feature warm-up, forward chronology, assessment boundaries, control disjointness, deterministic bootstrap, matched negative control, hard path loss, strict JSON, and the new sparse-control dominant-failure regression.
- `.venv/bin/python -m unittest tests.test_trader_build_compounding tests.test_trader_run_completion_gate -v` -> `Ran 36 tests in 5.799s`, `OK`.
- `.venv/bin/python -m unittest tests.test_trader_income_coverage -v` -> `Ran 1 test in 0.696s`, `OK`.
- `.venv/bin/python -m py_compile scripts/spy_vrp_pcs_study.py tests/test_spy_vrp_pcs_study.py` -> exit `0`, `py_compile OK`.
- `.venv/bin/python scripts/spy_vrp_pcs_study.py --bootstrap-samples 10000 --out /tmp/spy-vrp-pcs-study-finalizer.json` plus canonical comparison excluding only `generated_at` -> `substantive_payload_equal True`; canonical and reproduction substantive SHA-256 both `1e4cc893da3a25b1778bf21cefe763e80bcceb0ac15e0163f0672663cb016ef3`. Canonical file SHA-256 remains `71822cdf55bdc1b63c91a4047e0dc631e77940fcabda1cf35a2c7f8168ae3bfb`.
- `just trader-income-coverage --stamp 2026-07-14T0859` -> exit `0`; regenerated dated and LATEST coverage: 21 structures, 246 hypotheses, 70 evolve artifacts, living leader none.
- `just platform-smoke` -> explicit rerun exit `0`, `platform smoke OK`; live remained blocked at the Stage1 OAuth gate.
- `.venv/bin/python -m unittest discover -s tests` -> `Ran 263 tests in 19.913s`, `OK`, `FULL_SUITE_RC=0`.
- Temporary-index-only deterministic pre-integration prepare (`GIT_INDEX_FILE=/tmp/... .venv/bin/python scripts/trader_run_completion_gate.py prepare --repo . --stamp 2026-07-14T0859 --base-head a575bf31b33f9f310911e97929d5a2816471b86f --run-branch trader/run-2026-07-14T0859`) -> `ok: true`, `mode: prepare`, `staged_files: 24`, exit `0`. The temporary index was removed; the real Git index was not staged or mutated.

## DURABLE

Accepted and reconciled all five challenger nits:

1. Overlap wording is now code-aligned and explicit: 33/35 old matched rows had **same-fold, half-open control-treated outcome-window overlaps**; three rows crossed assessment boundaries. The looser any-fold inclusive 34/35 recomputation is not the runner definition. `artifact-integrity-audit.json`, executor surfaces, supersession headers, readiness, INDEX, and this finalizer use the precise definition.
2. `DIMINISHING_RETURNS` is retained as a bare sole seed and means burst-stop for the current 18-wake no-advance sequence, not an archive-based global freeze. A later restart requires a written search-design/data reassessment naming a materially new mechanism or evidence class outside quarantined families and not another inspected same-class F0 screen.
3. Final verification was rerun independently rather than inheriting challenger self-report; focused, completion/compounding, coverage, compile, 10,000-bootstrap reproduction, smoke, and full suite are green.
4. `reports/trader-wakes/2026-07-14T0930-rth.md` is preserved as separate 14/0/14 STAND_ASIDE operational residue and is not counted as MoA strategy evidence or advancement.
5. `SPY_VRP_VIX_RV_21D` is listed as closed under the current overlap-safe **insufficient disjoint matched-control density** result. The 0612 negative paired-bootstrap narrative is explicitly superseded and non-reusable.

The accepted executor repair is durable in `scripts/spy_vrp_pcs_study.py` and `tests/test_spy_vrp_pcs_study.py`: failure labels derive actual gate failures and the regression requires the sparse counts and underpowered semantics. Dated project truth is promoted through the canonical study, integrity audit, compounding handoff, final merge/LATEST, INDEX, readiness, and regenerated coverage. The profile-local `trader-self-evolution` skill already contains the reusable claim-artifact reconciliation pitfall (direct persisted-row integrity audit, same-hash/current-code regeneration, substantive-payload equality, complete counters, and superseded-surface rewrite), so no duplicate skill entry was added. Profile memory is unchanged: this is dated project evidence plus a reusable procedure already captured in the skill, not a stable Ken preference or routing fact.

Integration is pending the deterministic wrapper gate. The finalizer did not stage the real index, commit, push, merge, switch branches, edit `.gitignore`, or claim `RUN COMPLETE`.

## LESSON

Future Trader can distinguish operationally completed history from reproducible strategy truth: when a claim-bearing artifact disagrees with current integrated code, it must audit persisted rows under the code's exact interval/fold semantics, regenerate on unchanged source hashes, compare every substantive field except nondeterministic metadata, expose all current integrity counters, and rewrite living surfaces before any successor search. A family close is not enough if its stated dominant failure is false. Here the honest conclusion is narrower and stronger: broad raw VRP remains visible, but this frozen selector cannot establish incremental edge because overlap-safe outcome-independent controls collapse to 0/6/0 and only six pooled pairs. Stop the burst rather than tune the inspected family.

## NEXT

`DIMINISHING_RETURNS`

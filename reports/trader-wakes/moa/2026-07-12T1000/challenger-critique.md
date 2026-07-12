# MOA BUILD challenger critique — 2026-07-12T1000

ROLE: Grok 4.5 (read-only). No evolve --apply, no broker, no arm.
PHASE: BUILD · SLEEVE: $3000 · PAPER/RESEARCH ONLY

## Verified evidence (not executor self-report)

| Claim | Status | Check |
|---|---|---|
| Lab artifact exists | OK | `.cache/platform/pcs_close_shock_lab_2026-07-12T1000.json` |
| Walkforward artifact exists | OK | `.cache/platform/pcs_close_shock_walkforward_2026-07-12T1000.json` |
| Decision | OK | walkforward `REJECT_CLOSE_SHOCK_PCS_WALKFORWARD`; `n_selected=2`, `n_holdout_pass=0` |
| Full-sample absolute pass | OK | `n_absolute_pass=1` SMCI 7DTE / ≤−2% / vol≥1.5; fixed n15/+$70.49/dd$38.06/ml$89.67; 5% n17/+$4.15/dd$53.89/ml$94.49 |
| Integrity 432/432 | OK | recomputed 64 signal + 80 controls × 3 modes = 432; ledger_exact 432; same_bar_reentries sum 0; signal_violations sum 0 |
| Controls present | OK | 64 mirror_up + 16 unconditional |
| Holdout PLTR | OK | 5% n19/+$50.71/dd$155.05; fixed n19/+$198.27/dd$122.80; fail `slip_5pct_dd`,`fixed_0p01_dd` |
| Holdout TSLL | OK | 5% n14/−$7.70/dd$74.03; fixed n14/−$14.88/dd$76.10; fail pnl≤0 (+ fixed dd) |
| Lag repair + tests | OK | `entry_signal_lag_bars` in `pcs_sim.py`; behavioral lag + fail-closed filter tests in `tests/test_pcs_expiry_grid.py`; targeted suite **21/21 OK** re-run this critique |
| Proxy labeling | OK | claim_scope marks synthetic listed-Friday/rounded-strike BS; not observed quotes / not L1 |
| Archive density | OK | still 1/3 NY market dates (`provider_backtest_eligible=false`); Sunday wake correctly cannot advance archive |
| No capital seat / no leader | OK | no hyp registration claimed; readiness quality leader remains empty; `b195f5fe` historical only |

## Rubric

1. **Goal progress — PASS.** Material improvement in discovery odds: a plausible mean-reversion PCS family was built with dual cost axes, negative controls, integrity, and chronological selection→holdout, then honestly rejected. Durable lag-filter + lab runners raise future experiment quality without pretending L1.
2. **Creativity / independence — PASS.** Valid supersession of RTH-only archive seed while market closed. Multi-name (8) PCS grid with unconditional + mirror controls and walkforward — not familiar TSLL PCS re-polish or archive thrash.
3. **Claim validity — PASS.** Same-close signal/pricing ambiguity was found and repaired before final claims; first ambiguous passes discarded. Proxy/observed semantics labeled; L1 not claimed. Lab headline `DISCOVERY_PASS_REQUIRES_OBSERVED_VALIDATION` is weaker than the decisive walkforward REJECT — closeout correctly elevates REJECT.
4. **Evidence / test quality — PASS.** Real scripts/sims/JSON paths; independent ledger recompute + lag purity + no same-bar reentry; behavioral tests (boundary, fail-closed missing features, no signal-bar entry). Metrics match JSON.
5. **Falsification — PASS.** Predeclared gates + `REJECT_CLOSE_SHOCK_PCS_WALKFORWARD`. Full-sample SMCI pass treated as selection-biased context only; 0/2 holdout clears. Negative controls present (mirror/unconditional worse under cost for SMCI DNA).
6. **Capital honesty — PASS.** No living leader seated; absolute gates used with empty leader; no B3/B4 soft-hold → seat; 1-lot posture stated despite max_lots emission; no b195f5fe seat revival.
7. **Research freedom — PASS.** One-date archive blocked only observed-cost/L1 claims; unrelated proxy axis ran. Cron `execute_code` limit noted without freezing work. No removable restriction blocked a better valid experiment this wake.
8. **ONE NEXT seed — PASS.** Keep: next distinct NY RTH date append all-expiration TSLL archive 1→2/3; no provider hist before 3/3. Do not reopen close-shock retune this cycle.

## Nits (non-failing)

- Lab top-level decision string can be misread as soft promotion; walkforward is the capital-relevant decision (executor closeout got this right).
- Full-sample SMCI yearly/chunk windows are mostly sparse (`few_trades` / one dense-neg) — good that walkforward, not that row, decided.
- Holdout trade floor is 4 (lab 8); both selected rows still fail on DD/pnl, so no false pass risk this run.
- Feature name `intraday_return` is correctly open→close from `data.py` (not calendar ret_1d); lag=1 is the critical execution fix.

## Judgment

**Challenger overall: PASS 8/8.**
Keep executor evidence and REJECT decision. Progress type **P2+P3**, score **4/5**, honesty **L0 BUILD**. No living quality leader. No live/shadow/arm.

## Merged ONE NEXT SEED

On the next distinct New York RTH market date, append the all-expiration TSLL quote archive from 1→2 of 3 dates and verify append/dedup density; do not run provider-backed historical simulation before 3/3. Leave close-shock PCS family, asymmetric IC, collar, and BAC Fri7 management closed this cycle. No live/agentic/shadow.

MOA_CHALL_DONE

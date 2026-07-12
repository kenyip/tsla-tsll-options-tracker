# MOA BUILD lab executor closeout — 2026-07-12T0010

WAKE: 2026-07-12T0010 PDT
PHASE: BUILD
SLEEVE: 3000
EXECUTOR: GPT 5.6 Sol
MODE: paper/research only

## Chose

P1 diagnostic capability: instrument the rejected shared-position PCS/CCS/IC router with a selected → accepted → exact reject-reason funnel before any DNA retune.

Superseded no prior seed: this directly completed the merged NEXT. I did not tune the router because the prior eight-symbol experiment already rejected the family on cost density and drawdown.

## Hypothesis and falsifier

Hypothesis: the prior PCS-heavy accepted population is caused by entry-filter rejection after CCS/IC are selected, not by the regime router failing to select those structures.

Falsifier: CCS/IC are rarely selected, or the funnel cannot reconcile selected = accepted + rejected. Either result would invalidate the diagnosis. If CCS/IC are selected broadly but rejected at a dominant boundary, leave the already-rejected family rather than optimize that boundary.

## Validity scope

- Synthetic daily-bar discovery only; no observed-contract, provider-backed, or L1 claim.
- Current-row regime selection and existing one-position/no-close-bar-reentry loop are unchanged.
- Rejection labels use implementation-level single-gate counterfactuals, not a duplicated pricing formula. Composite failures remain conservatively labeled `contract_strike_or_nonpositive_credit`.
- Population is complete and pure: 8/8 symbols, zero errors. All 96 policy/mode funnels reconcile.
- No living quality leader. Absolute gates remain the comparison standard.

## Did

- Added `entry_funnel` to `RegimeRouterResult` and router metrics: per-structure selected, accepted, rejected, and reject reasons.
- Added counterfactual diagnosis for invalid IV, IV-rank threshold, credit floor, max-loss budget, and a conservative contract/strike/nonpositive-credit remainder.
- Exposed the funnel in `scripts/pcs_regime_router_lab.py` JSON.
- Added behavior/boundary tests for selection/acceptance counts, exact IV-rank rejection, arithmetic reconciliation, and invalid-IV fail-closed classification.
- Re-ran the same eight-symbol 5y router lab without changing DNA.

## Evidence

Primary JSON: `.cache/platform/regime_router_funnel_lab_2026-07-12T0010.json`

Tests: `.venv/bin/python -m unittest tests.test_regime_router_sim` → 5/5 OK.

Baseline aggregate funnel:

| Structure | Selected | Accepted | Accept rate | Dominant rejection |
|---|---:|---:|---:|---:|
| PCS | 360 | 122 | 33.89% | credit floor 110 |
| CCS | 2,427 | 19 | 0.78% | credit floor 2,145 |
| IC | 2,592 | 23 | 0.89% | credit floor 1,926 |

The hypothesis is supported: CCS and IC are selected far more often than PCS, but default entry economics reject more than 99% of selected bars. Accepted CCS appears only in AAPL (15) and QQQ (4); accepted IC appears only in AAPL (23). This is not a selection-coverage gap.

Risk fields remain explicit and sleeve-fit for the simulated accepted router trades: structure = routed PCS/CCS/IC defined risk; baseline per-symbol worst `max_loss_usd` = `capital_fit_usd` ranges $163.24–$204.92; envelope `max_lots=3`, while this $3k research candidate posture remains **1 lot** and no capital seat exists.

Decision remains `REJECT_ROUTER_FAMILY_THIS_CYCLE`; `passing_symbols=[]`. Prior B3/B4 and max-DD rejection is unchanged. No hypothesis registered, promoted, or put on a capital path.

## Durable

- Code: `trader_platform/research/regime_router_sim.py`
- Lab output wiring: `scripts/pcs_regime_router_lab.py`
- Behavioral tests: `tests/test_regime_router_sim.py`
- Coverage doctrine/history: `docs/INCOME_STRATEGY_COVERAGE.md`
- Coverage generator gap text: `scripts/trader_income_coverage.py`

## Readiness

L0 honest. BUILD remains unchanged. No living quality leader. Formal B checks did not change, so `reports/readiness/LATEST.md` was not rewritten. No B3/B4 or non-vacuous after-cost promotion claim was made.

## Freedom audit

No prompt rule blocked a higher-information valid experiment. The one-date observed archive and daily-bar granularity constrain observed-contract/session claims, but neither blocked this synthetic diagnostic; the claim was narrowed accordingly.

## ONE NEXT SEED

Leave the router family. Build a minimal paper-only **collared covered-call** simulator on liquid sub-$30 universe names: 100 shares + long protective put + short call, with explicit `capital_fit_usd`, 1-lot `max_loss_usd`, `max_lots`, dividends/assignment limitations, no-close-bar re-entry, and immediate fixed-cost/5%-slip/absolute-DD falsification. Reject the class unless it produces non-vacuous after-cost evidence with max loss ≤$300 and window max DD ≤$75; do not register proxy SHIP first.

GATES: none. No live / broker / agentic arm / shadow auto-promote.

Progress type: **P1 diagnostic capability + explicit family leave decision**. Score: **4/5**. Honesty: **L0**.

MOA_EXEC_DONE

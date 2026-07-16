# Trader platform readiness — latest

Updated: 2026-07-15 — MoA stamp 2026-07-15T2152 `RUN COMPLETE`; integrated/pushed/postflight-complete as `fe0943f` with `main == origin/main` and a clean checkout.

Phase: BUILD
Sleeve: $3,000 Agentic research sleeve
Authority: research/paper-safe only; no shadow/live auto-promotion, broker access, funding, or live orders.

## Decision readiness

- Final outcome: `EVIDENCE_WAIT` for exact `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1` at `F0_MECHANISM -> F0_MECHANISM`; strategy advancement false.
- Mechanism: observed short-front call term-structure extrinsic carry against a farther-dated call in a lag-safe non-bearish TSLA/TSLL regime.
- Conditional structure: buy one observed listed 60–90 DTE 0.60–0.75 delta TSLL call; sell one higher-strike 14–21 DTE 0.20–0.35 delta call; front/back extrinsic-per-day >=1.25; each leg half-spread <=`$0.10`.
- Capital admission: observed debit plus `$50` closing/assignment reserve <=`$300`; `capital_fit_usd=$300` is a research admission budget; one-lot structural `max_loss_usd=UNPROVEN` under assignment/gap/exercise/liquidation mechanics; `max_lots=1`; no overlapping TSLA/TSLL bullish option risk.
- Management: +25%/−25% package-debit exits, five-session stop, short<=7 DTE, regime/event/dividend/assignment exits, no roll or same-session re-entry.
- Current evidence: TSLL archive 1,990 observed rows, 1,390 weekday-RTH and 600 non-RTH, with 3 archive-date labels but only 2 eligible weekday-RTH session dates, 1 distinct eligible 14–21 DTE short-expiry cycle (`2026-07-31`), 0 complete observed package paths, and 0 frozen controls.
- Current context: research run 36 scored 30/30 with zero errors, ranked TSLL first, and labels TSLL bearish. Current action is stand aside.
- No option-path PnL was evaluated. No mispricing, after-cost edge, F1/F2/L1, living leader, capital seat, registry, paper intent, or B-check authority change exists.

## Epoch / anti-thrash

- Prior epoch `2026-07-15-tail-hazard-discovery` stopped after three exact no-advance wakes. Recent-downshock, downside-semivariance, and SPY theta-carry families remain quarantined.
- Reassessment: `docs/SEARCH_DESIGN_REASSESSMENT_2026-07-15T2152.md`.
- Active successor epoch: `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1`, started `2026-07-15T2152`, status `active`.
- Successor progress: one completed initial strategy decision, one `EVIDENCE_WAIT`, no strategy advance, `consecutive_no_strategy_advance=1`, pivot false, burst-stop false.
- Evidence-wake condition: >=12 distinct weekday-RTH dates spanning >=3 distinct 14–21 DTE short-expiry cycles, >=20 complete non-overlapping observed package paths, and >=8 frozen same-snapshot one-to-one non-rich controls; evaluate development 60% only and keep final 40% unread for later F1→F2.
- Later pure data-append reaffirmations must set `evidence_wait_reaffirmation=true` and do not increment strategy no-advance pivot/burst-stop streaks. The initial 2152 wait is not a reaffirmation and counts once.
- This wait is candidate-scoped. Historical underlying/Black-Scholes L0 discovery remains globally executable for genuinely independent non-quarantined mechanisms and cannot satisfy this observed claim or earn L1.
- Preserve sealed evidence: downside-semivariance identity `72a6d184...`, SPY option outcomes 2022-07-12..2026-07-13, and this candidate's final chronological 40%.

## Frozen claim contract

- Forecast type: `term_structure_extrinsic_carry` with a mild bullish directional overlay, not realized-versus-implied volatility.
- Control geometry: same snapshot and long leg; one-to-one; control richness ratio `[0.80,1.10]`; deterministic outcome-independent candidate/control tie-breaks; match by short delta, DTE, moneyness distance, then friction; no control reuse or substitution; exclude a path if no valid control exists.
- Outcome gates: >=8 controls, >=55% candidate-over-control wins, and candidate median net return >=5 percentage points above control, plus the absolute PnL/PF/DD/ES90/chronology gates in the charter.
- Capital: the `$300` admission budget is not structural max loss. No capital-path claim is allowed until assignment/gap/exercise/liquidation evidence supports a real one-lot bound.

## Evidence validity boundaries

- The old three-date `provider_backtest_eligible=true` flag was a capture/join plumbing floor, not historical edge evidence, and counted a Saturday off-hours snapshot.
- Repaired density semantics now report 3 archive-date labels, dates containing any non-RTH rows, fully excluded dates, 2 eligible weekday-RTH market dates, and `provider_backtest_eligible=false`. Only weekday-RTH rows count toward market-date/expiration density.
- Aggregate median chain half-spread `$0.625` is not a candidate fill assumption; every admitted candidate/control leg must independently pass the `$0.10` half-spread gate.
- Black-Scholes or assumed-IV substitution cannot satisfy the observed-term-structure claim.
- No contract pair has passed regime, event, term-slope, liquidity, admission, complete-path, or control gates.
- Forward observations must retain contract identity, quote timestamps, same-snapshot underlying spot, executable NBBO entry/exit marks, no future leakage, no same-date capture churn, and one-position cadence.
- Current bearish TSLL regime is an explicit stand-aside, not a strategy failure or paper trigger.

## Verification

- focused behavioral/boundary/negative-control/regression/handoff suite: `Ran 59 tests in 8.877s — OK`
- required full unittest suite: `Ran 368 tests in 18.730s — OK`
- full pytest suite: `378 passed, 18 subtests passed in 21.25s`
- config JSON, compileall, and `git diff --check`: exit `0`
- archive recomputation: 1,990 total / 1,390 RTH / 600 non-RTH / 3 archive labels / 2 eligible RTH dates / 13 RTH expirations / provider eligibility false
- coverage: 21 structures / 246 hypotheses / 70 evolve artifacts / no living leader; dated and LATEST SHA-256 `9f6afe641685294441e4a0762dfc728494e5a147c51249da875e1789dae380c9`
- schema-v2 handoff: exit `0`; `ok=true`; `role_ready=true`; `outcome=EVIDENCE_WAIT`; strategy advancement false; 4 useful deltas; 3 critic findings closed
- deterministic wrapper postflight: `ok=true`; integrated/pushed/postflight-complete as `fe0943f`; `main == origin/main`; checkout clean; run branch deleted

## Readiness blockers

1. No capital-path candidate has claim-appropriate after-cost option-payoff evidence plus path quality sufficient for L1/capital-seat authority.
2. `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1` has 0 complete observed package paths and 0 controls; it remains F0 `EVIDENCE_WAIT`.
3. Current TSLL regime is bearish and exact admitted-leg liquidity is unproven.
4. One-lot structural max loss is unproven under diagonal assignment/gap/exercise/liquidation scenarios; `$300` is admission budget only.
5. Broad observed historical option entry/exit joins remain unavailable. This blocks observed-option/L1 claims only, not unrelated historical L0 discovery.
6. Any future F3 candidate still requires live-clock paper quotes/fills before F4/shadow/live authority.
7. Stamp `2026-07-15T2152` is integrated/pushed/postflight-complete as `fe0943f`; no execution authority changed.

Coverage: `reports/readiness/income-coverage-LATEST.md`
Final wake: `reports/trader-wakes/2026-07-15T2152-moa-merge.md`
Executor wake: `reports/trader-wakes/2026-07-15T2152-moa-exec.md`
Executor closeout: `reports/trader-wakes/moa/2026-07-15T2152/executor-closeout.md`
Challenger: `reports/trader-wakes/moa/2026-07-15T2152/challenger-critique.md`
Strategy charter: `reports/trader-wakes/moa/2026-07-15T2152/strategy-charter.md`
Compounding: `reports/trader-wakes/moa/2026-07-15T2152/compounding.json`
Learning: `reports/trader-wakes/moa/2026-07-15T2152/learning-promotion.md`

## Exactly one NEXT seed

`TSLL_OBSERVED_TERM_CARRY_DATA_OR_INDEPENDENT_L0`:
1. Distinct weekday-RTH session and frozen condition unmet: append exactly one all-expiration TSLL snapshot; report only RTH density, complete-path eligibility, `$300` admission rate, and frozen control support; no outcome/PnL evaluation or same-date churn.
2. Off-hours and condition unmet: autonomously choose a genuinely independent non-quarantined L0 mechanism across the full universe; do not proxy-satisfy or mutate the parked observed diagonal.
3. Frozen condition met: resume exact `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1` on the development 60% under its predeclared falsifier; keep final 40% unread for later F1→F2.

Pure append reaffirmations set `evidence_wait_reaffirmation=true` and do not increment pivot/burst-stop streaks. No registry/paper force, shadow, arm, broker, funding, or live action.

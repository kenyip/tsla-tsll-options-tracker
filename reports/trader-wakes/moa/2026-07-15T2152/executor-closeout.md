# MOA executor closeout — 2026-07-15T2152

WAKE: 2026-07-15T2152
PHASE: BUILD / L0 research only
ROLE: GPT 5.6 Sol executor / only writer
SESSION: off-hours PDT / market closed
SLEEVE: $3,000
EXECUTOR STATUS: partial MOA phase complete; challenger/finalizer/integration pending; no `RUN COMPLETE` claim

## Strategy decision charter

ECONOMIC EDGE MECHANISM: in a lag-safe non-bearish TSLA/TSLL regime, short-dated call demand and gamma insurance may leave front-call extrinsic decay rich relative to a longer-dated call. A one-lot bullish call diagonal could harvest observed front decay while retaining bounded positive delta.

CANDIDATE / FAMILY: `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1` / `observed_term_carry|tsll|bullish_call_diagonal|long60_90d_060_075delta|short14_21d_020_035delta|front_extrinsic_per_day_1p25x|five_session|max300`.

CURRENT FUNNEL: `F0_MECHANISM -> F0_MECHANISM`.

EXACT WAKE DECISION: `EVIDENCE_WAIT`.

PREDECLARED FALSIFIER: once the evidence-wake condition is met, close the exact family unless the first chronological development set contains at least 20 complete non-overlapping observed entry-to-exit package paths across at least 12 New York market dates and three short-expiry cycles; at least eight frozen matched non-rich term-slope controls; zero chronology, freshness, and contract-identity failures; positive total and mean executable-NBBO PnL after a further `$0.01` per-leg sensitivity; PF at least 1.05; observed one-lot loss at most `$300`; development DD at most `$150`; and a positive one-sided 90% date-block lower bound for rich-slope minus control PnL. A final chronological 40% reserve stays outcome-unread for any later F1→F2 claim.

Full pre-action charter: `reports/trader-wakes/moa/2026-07-15T2152/strategy-charter.md`.

## Complete Layered Edge Stack

- market / underlying: TSLL only for the first observation campaign, with TSLA as economic driver; current research run 36 ranks TSLL first but labels its regime bearish
- forecast type: timing + observed front/back volatility carry + mild direction up
- economic mechanism: short-front gamma/attention demand may create faster observed front extrinsic decay than the back call in a non-bearish regime
- option structure: one bullish call diagonal; buy 60–90 DTE 0.60–0.75 delta call, sell higher-strike 14–21 DTE 0.20–0.35 delta call; observed listed contracts and executable NBBO only
- intended Greeks: positive delta, positive theta after admission, net long vega, bounded long bias
- dangerous Greeks: short front gamma, back-leg vol crush, leveraged-ETF path decay, assignment/dividend risk, TSLA catalyst gap, and package friction
- regime envelope: prior-completed TSLA and TSLL close above fully warmed SMA100 and positive prior-completed 60-session return; no TSLA earnings in hold and no TSLL ex-dividend before short-leg exit
- entry trigger: one 10:30–14:30 New York RTH snapshot; positive bids; each leg half-spread <=`$0.10`; front/back extrinsic-per-day ratio >=`1.25`; debit plus `$50` reserve <=`$300`
- exit / management: first of +25% or −25% package debit, five completed sessions, short <=7 DTE, regime invalidation, catalyst/ex-dividend approach, or assignment guard; no roll, averaging down, same-session re-entry, or overlap
- risk / capital fit: `capital_fit_usd=$300` is a research admission budget; observed debit + `$50` reserve must be <=`$300`; one-lot `max_loss_usd=UNPROVEN` under assignment/gap/exercise/liquidation mechanics; `max_lots=1`; no simultaneous TSLA/TSLL bullish option risk
- evidence / falsifier: forward observed chain and managed package paths with matched non-rich term-slope controls; frozen gates above
- confidence: F0 / L0 only; no mispricing or after-cost edge claim
- stand-aside: current bearish regime, missing/stale quote or event data, failed term/liquidity/capital/overlap gate, or evidence population below the wake condition

## Search-design reassessment

Evidence: `docs/SEARCH_DESIGN_REASSESSMENT_2026-07-15T2152.md` and `configs/search_epoch.json`.

The prior tail-hazard epoch correctly stopped after three no-advance wakes:

1. recent-downshock non-collapse failed the absolute hazard ceiling and timing specificity;
2. downside semivariance failed mechanism specificity versus plain HV;
3. SPY theta carry lacked bearish comparator support and temporal coverage despite positive early-window proxy PnL.

The executor rejected a fourth tail selector, SPY same-panel retune, or assumed-IV diagonal grid as thrash. The successor uses option-native observed term structure and executable managed-package paths. This does not reopen any closed family.

## Why `EVIDENCE_WAIT` is required

Current observed evidence is non-vacuous for plumbing but vacuous for the strategy claim:

- `.cache/platform/option_quotes/TSLL_archive.csv`: 1,990 observed rows
- `.cache/platform/option_quote_archive_density_2026-07-15T2152.json`: repaired RTH-aware summary; three archive-date labels but one Saturday off-hours snapshot, 1,390 RTH rows, 600 non-RTH rows, only two weekday RTH session dates, 13 RTH expirations, aggregate median half-spread `$0.625`, and `provider_backtest_eligible=false`
- complete frozen entry-to-exit diagonal paths: zero
- matched non-rich term-slope controls: zero
- current TSLL regime: bearish in research run 36

The old three-date `provider_backtest_eligible=true` flag was a capture/join plumbing floor, not strategy evidence; the repaired summary correctly fails closed at two RTH dates. Black-Scholes substitution would test assumed surfaces rather than the observed term-carry mechanism. The next discriminating test genuinely requires future distinct-RTH observations.

VERIFICATION REPAIR: the pre-existing density summarizer counted any local date, including a Saturday 23:36 snapshot, as a market date. A test-first boundary reproduced the defect, then `summarize_archive_density` was narrowed to weekday 09:30–16:00 New York observations and now surfaces archive dates, RTH/non-RTH row counts, and excluded dates. The exact candidate was rechecked against the corrected artifact and remains `EVIDENCE_WAIT`; the repair does not create strategy advancement.

EVIDENCE-WAKE CONDITION: resume the exact strategy decision only after the append-safe archive has at least 12 distinct weekday RTH session dates spanning at least three 14–21 DTE short-expiry cycles and supports at least 20 complete non-overlapping paths plus eight frozen controls under the quote/regime/event/capital gates.

## Search information versus strategy advancement

SEARCH INFORMATION: yes. The mandatory burst-stop reassessment separated informative direct-tail/specificity/support controls from thrash-prone nearby retunes, preserved both sealed holdouts, retired the tail-hazard search design, and opened one materially different observed option-native evidence class with a complete stack and a concrete wake condition.

STRATEGY ADVANCEMENT: no. `TSLL_OBSERVED_TERM_CARRY_DIAGONAL_V1` remains F0. No option-path outcome was evaluated; no F1/F2/F3/F4, L1, living leader, capital seat, registry transition, paper intent, shadow, arm, broker, funding, or live authority was created.

## Evidence challenge

- leakage/lookahead: all future strategy observations must use completed regime/event data and contemporaneous observed quotes; no current outcome was read
- contract availability: current chain rows prove only dated contract capture, not a stable executable pair across entry and exit
- costs/fills: aggregate chain spread is not a candidate fill; exact legs must pass `$0.10` half-spread and executable NBBO gates
- provenance: observed archive is forward current-chain data; the research rank and old simulators are proxies and cannot satisfy the observed claim
- density: three archive-date labels but only two distinct weekday-RTH session dates, one eligible short-expiry cycle, and zero complete paths fail the frozen wake condition
- population purity: first campaign is TSLL-only with one global TSLA/TSLL risk unit; no cross-name pooling or stale leader
- risk: conditional one-lot research admission budget is `$300`, but structural `max_loss_usd` remains unproven; no current package has qualified
- holdouts: downside-semivariance `72a6d184...` and SPY 2022-07-12..2026-07-13 option outcomes remain sealed

## Verification

- focused behavioral/boundary/negative-control/regression suite: `43 passed in 5.24s`
- full pytest suite: `374 passed, 18 subtests passed in 20.54s`
- JSON syntax, compileall, and `git diff --check`: exit `0`
- archive/research recomputation: 1,990 rows; 1,390 RTH / 600 non-RTH; date labels `2026-07-11`, `2026-07-13`, `2026-07-14`; corrected `market_dates` are only `2026-07-13` and `2026-07-14`; provider eligibility now false; research run 36 scored 30/30 with zero errors
- coverage refreshed deterministically for stamp 2152: 21 catalog structures / 246 hypotheses / 70 evolve artifacts / no living leader
- readiness phase and B checks unchanged; anti-thrash/NEXT state updated for the successor evidence wait

## Freedom audit

Freedom preserved: the executor honored the burst stop rather than blindly running prior NEXT as a recipe, rejected closed-family retunes, chose a materially different option-native evidence class, added no symbol or strategy allowlist, and kept unrelated historical L0 routes globally open. TSLL is selected because current observed archive plumbing exists and the structure can be capital-capped, not because TSLL or diagonals are mandatory.

## Durable lesson

When the mechanism is observed option term carry, assumed-IV proxy paths answer the wrong question. A three-date all-chain archive can validate plumbing while remaining economically vacuous. Require complete observed entry-to-exit packages, exact leg liquidity, matched term-slope controls, and enough independent dates/cycles before claiming even F1.

## Exactly one next seed

Executor proposal (superseded by the finalizer's challenger-amended merged NEXT): `TSLL_OBSERVED_TERM_CARRY_DATA_WAKE` during a distinct RTH market date. The final handoff preserves this append branch, adds a free independent off-hours L0 branch, and adds the exact wake-condition-met evaluation branch so the candidate-scoped wait does not become a global BUILD freeze.

## Partial-phase boundary

No commit, push, merge, deterministic integration, or `RUN COMPLETE` claim was made. Challenger and finalizer must critique the observed-term mechanism, $0.10 leg-liquidity gate, path/control floors, event/assignment boundaries, `$300` reserve semantics, candidate-scoped wait versus global-route freedom, config/readiness surfaces, and exact one NEXT before integration.

MOA_EXEC_DONE

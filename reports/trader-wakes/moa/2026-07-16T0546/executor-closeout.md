# MOA executor closeout — 2026-07-16T0546

Role: GPT 5.6 Sol executor / only writer
Phase: BUILD / L0 underlying discovery
Session: premarket
Status: EXECUTOR RECEIPT — challenger/finalizer reconciled; deterministic integration pending; no commit/push/merge/RUN COMPLETE

## Strategy decision charter

Pre-outcome charter: `reports/trader-wakes/moa/2026-07-16T0546/strategy-charter.md`.

The prior epoch had completed its three-no-advance burst and prohibited a fourth strategy test before reassessment. This wake first wrote `docs/SEARCH_DESIGN_REASSESSMENT_2026-07-16T0546.md`, opened successor charter `docs/SEARCH_EPOCH_2026-07-16T0546.md`, then tested one named candidate. The prior NEXT was treated as burst-stop context, not a strategy assignment.

Chosen mechanism: repeated overnight selling absorbed by positive regular-session demand across liquid broad-index ETFs may be transitory risk-transfer pressure rather than durable negative information, producing short-horizon upward drift.

Exact candidate/family: `BROAD_INDEX_OVERNIGHT_ABSORPTION_BULL_CALL_21D_V1` / `BROAD_INDEX_OVERNIGHT_SELL_INTRADAY_ABSORPTION_FORWARD_UPDRIFT`.

Funnel before: `F0_MECHANISM`. Frozen decision: advance F0→F1 only if every train-only discovery gate passes; otherwise `FAMILY_CLOSED` at F0. Holdout outcomes and option marks remain sealed in either branch.

## Complete Layered Edge Stack

- Market: fixed adjusted-OHLCV panel `SPY, QQQ, IWM, DIA`.
- Forecast: bullish five-session direction.
- Mechanism: five completed sessions of broad overnight supply absorbed by positive regular-session demand may be transitory pressure whose absorption persists.
- Option expression: future conditional one-lot 18–24 DTE $2-wide bull-call debit spread; no option was priced.
- Intended Greeks: positive delta; limited positive gamma/vega; defined debit.
- Dangerous exposures: negative theta, volatility crush, gap loss, capped upside, synchronous index overlap, debit/closing friction, assignment/exercise.
- Regime: completed close above warmed SMA100; compounded five-session overnight return <=-1%; compounded five-session intraday return >=+1%.
- Entry/exit: signal uses the completed session; enter next completed close; F0 exit after five further sessions. Future management only: +50% value, -50% debit, five-session time stop or trend invalidation; no roll/averaging.
- Risk: `capital_fit_usd=200`, frictionless planning `max_loss_usd=200` before debit/closing friction, `max_lots=1`; simultaneous ETFs are one broad-index risk episode, not four deployable units.
- Evidence: chronological 60/40 unique-signal-date split; train only; final 40% identity-only; same-symbol prior-only/no-reuse/non-trigger controls; exact-date clustering before inference; 10-bps underlying hurdle; circular five-episode block; zero pricing.
- Confidence: F0/L0 before and after. No L1/capital-seat authority from underlying evidence.
- Stand aside: missing/nonfinite/under-warmed data, regime mismatch, no prior control, future option illiquidity, debit above $200, overlapping index risk, or any source/chronology/integrity ambiguity.

## Mandatory reassessment closed before the experiment

The predecessor epoch's three exact closes were reconciled:

1. sector-leader continuation was dense but had wrong signed absolute/relative returns and poor tail;
2. credit-risk-off was dense enough but a direct bearish anti-edge;
3. Form 4 clusters had favorable point estimates but only six train pairs, remote controls, unstable sign, and negative LB90.

Diagnosis: current search has alternated between dense wrong-sign mechanisms and sparse favorable-center events. The successor design therefore selected a repeated exposure, kept the earlier non-claim-bearing overnight trigger/direction unchanged, expanded only the evidence class to four indices, and clustered same-date rows so cross-index breadth did not masquerade as independent n.

This was not a post-outcome threshold retune. The prior SPY secondary row never advanced or closed a family and failed n/LB90. The new charter, panel, controls, clustering, split, and gates were written before real outcomes.

## Exact claim-bearing outcome

`FAMILY_CLOSED` for `BROAD_INDEX_OVERNIGHT_ABSORPTION_BULL_CALL_21D_V1` / `BROAD_INDEX_OVERNIGHT_SELL_INTRADAY_ABSORPTION_FORWARD_UPDRIFT`, `F0_MECHANISM -> F0_MECHANISM`. Strategy advancement is false.

Canonical evidence: `reports/trader-wakes/moa/2026-07-16T0546/broad-index-overnight-absorption-train.json`.

Finalizer reconciliation note: the current hashes below supersede the executor-phase bytes after accepted challenger diagnostics were added. The strategy metrics and close are unchanged; the claim now also serializes 28/96 near-date gaps <=7 days, breadth 67×1/20×2/8×3/2×4, and the tested F0/option-planning boundary.

- Raw SHA-256: `29d0c6199c96ed9c91290467c748e34c5c7cd4bdced243abb84dfde93fe51b73`.
- Normalized SHA-256 excluding only `generated_at`: `85ce2277b587135cd7394e0cce0b6e90cc5ce82e6c7f8067241042cb60a3b4a5`.
- Persisted-cache replay equality excluding only `generated_at`: true.
- Source panel: 4,832 rows per ETF, 2007-05-01 through 2026-07-15; adjusted-data file hashes are in the artifact.
- Frozen unique signal dates: 168; train cutoff 2019-11-14.
- Train eligible/matched signal rows: 144/139; same-symbol control support 96.5278%.
- Same-date clustered train episodes: 97 across 12 years and all four ETFs.
- Event mean after 10 bps: **-0.048879%**.
- Prior-control mean after 10 bps: **+0.017988%**.
- Paired event-minus-control mean/median: **-0.066867% / -0.124070%**.
- Circular five-episode-block paired LB90: **-0.623971%**.
- Event positive frequency: **57.7320%**.
- Event-return worst-decile mean after 10 bps: **-5.724566%**.
- Paired-excess worst-decile diagnostic: **-6.831920%**.
- Control distance median/max: 268 / 735 sessions.
- Integrity violations: 0.
- Passed gates: n48 clustered episodes, ten years, three symbols, 80% support, 55% event hits, zero integrity.
- Failed gates: positive event mean, positive paired mean, positive LB90, and event-return worst-decile >=-5%.
- Holdout: 105/105 matched signal rows on 68 signal dates, 2020-01-06 through 2026-06-29, identity SHA `8d427bb57ee199bc6fa2f1abefbd920df184650ac0a0bd1356f2e0a2c228b193`; outcomes unread; simulation false; option pricing zero.

Independent aggregation over the 97 serialized train episodes reproduced event/control/paired means, 57.7320% event hits, event tail -5.724566%, and paired tail -6.831920%.

Dominant failure: density was not the blocker. After clustering synchronous index rows, the exact mechanism produced a slightly negative absolute event center, a negative paired center versus prior same-regime controls, materially negative dependence-aware LB90, and an event tail beyond the frozen floor. A 57.7% hit rate cannot rescue negative expectancy, absent specificity, and tail loss.

Quarantine: do not rerun the same four-index / SMA100-uptrend / five-session overnight <=-1% / intraday >=+1% / next-close / five-session / 10-bps / same-symbol-control geometry, nearby threshold or horizon nudges, sign inversion, unclustered pseudo-replication, or an option-wrapper substitution. Reopening requires a genuinely new risk-transfer mechanism or evidence class predeclared before outcomes.

## Search information, separate from strategy advancement

The wake added and exercised `scripts/broad_index_overnight_absorption_train_lab.py` with exact per-symbol chronology, same-symbol prior controls, global signal-date partitioning, same-date cross-index clustering, sealed holdout identities, explicit event-versus-paired tail fields, strict JSON, source hashes, deterministic cache replay, and one-risk-unit planning labels. It also restored explicit `discovery_bar` and `capital_seat_bar` objects in `configs/search_epoch.json`.

This is useful falsification and reusable evidence machinery. It is not strategy advancement.

## Evidence-validity critique

- Leakage/lookahead: trigger features end at the completed signal session; entry is next close. Controls finish before their event signal. Final 40% outcomes are not evaluated or serialized.
- Dependence: simultaneous ETF rows are averaged into one signal-date episode before event metrics and the five-episode circular block. Raw row count 139 is not used as inferential n. Signals on nearby but nonidentical dates can still have overlapping five-session windows, so the block is a dependence sensitivity rather than proof of 97 independent episodes; this only weakens an already negative family and grants no advancement.
- Controls: deterministic, prior-only, same symbol, non-trigger, no reuse, and matched on prior 60-session return, HV20, and SMA100 distance. Median/max 268/735 sessions is coarse and further weakens specificity; it cannot rescue a negative paired center.
- Costs/fills: 10 bps is an underlying sensitivity only, not option spread, IV, debit, assignment, or management friction. Because the underlying result is negative and tail-failing, omitted option friction cannot rescue it.
- Population: four present-day index ETFs create composition/survivorship and shared-market exposure. The claim closes only the exact panel/geometry, not every overnight/intraday mechanism.
- Contract availability: no historical contract, listed expiry, IV, strike, or fill was selected. The $2 bull-call is planning geometry only.
- Horizon/payoff alignment: positive five-session direction is economically aligned with a bull-call, but no option theta/vega path is measured. The family failed before option validation.
- Capital: width-bound planning risk fits $3,000 at one lot, but actual debit/path loss is unmeasured and grants no capital seat.
- Ranking/leaders: readiness has zero living candidate, F1 survivor, L1 candidate, quality leader, or capital seat; absolute gates were used and no stale leader was compared.
- Tail semantics: event-return and paired-excess tails are separate machine fields. A negative control proves the frozen tail gate uses event returns after 10 bps.
- Current-data boundary: source caches end 2026-07-15, the latest completed session available to this premarket wake.

## Verification completed by executor

- New focused behavioral/boundary/positive/negative-control tests: **7/7**.
- New + candidate-factory + compounding adjacent suite: **45/45**.
- Strict compile and `git diff --check`: green.
- Full unittest: **431/431**, `OK`.
- Full pytest: **441 passed + 18 subtests**.
- `just test`: exit 0; TSLA and TSLL both `STAND ASIDE`; no broker action.
- Deterministic real-data replay: substantive equality true; hashes above.
- Independent episode aggregation: exact reproduced centers/hits/tails.
- Static secret/dangerous-code scan of the new runner: no matches.
- Income coverage refreshed at 2026-07-16T0601: **21 structures / 246 hypotheses / 70 evolve artifacts / no quality leader**.

An independent read-only code/evidence review was dispatched; challenger/finalizer still own acceptance and any repair.

## Readiness / authority

No phase or B3/B4/B6+ state changed, so `reports/readiness/LATEST.md` remains the last integrated readiness truth for finalizer reconciliation rather than being falsely rewritten as executor-complete. Living candidates 0; F1 0; F2 0; F3 0; F4 0; L1 0; leaders 0; seats 0. No registry, paper intent, paper ledger, shadow, broker, funding, arm, or live surface changed.

The successor epoch now has one counted no-advance decision. `strategy_pivot_required=false`; `strategy_burst_stop_required=false`. This does not reopen the completed predecessor epoch.

Freedom audit: symbol and strategy freedom remained open; the executor selected a broad-index risk-transfer mechanism and bullish defined-risk planning expression because the prior secondary screen offered the highest-information unresolved mechanism under a new dependence-safe evidence class, not because the caller or NEXT dictated it.

## Durable lesson

Future Trader can test synchronous cross-index signals while reducing exact-date pseudo-replication: partition by global signal date, retain same-symbol prior controls, and cluster same-date rows before inference, while still labeling residual near-date/window dependence. In the exact overnight-sell/intraday-absorption geometry, broader evidence resolves the prior single-SPY ambiguity against the edge: density and hits pass, but absolute/relative expectancy, uncertainty, and tail do not.

## ONE NEXT

`YIELD_CURVE_STEEPENING_REGIONAL_BANK_FORWARD_UPDRIFT_PREFLIGHT`: test whether a completed point-in-time steepening in a fixed Treasury-duration proxy spread forecasts KRE upside beyond prior same-regime controls, with train density and a future one-lot defined-risk bull-call expression frozen before outcomes; reject pre-outcome if ETF proxy semantics cannot support the lending-margin mechanism.

No commit, push, merge, deterministic postflight, or RUN COMPLETE claim was attempted in this executor phase.

MOA_EXEC_DONE

## Finalizer reconciliation note (post-executor)

The executor text above is preserved as phase evidence. Finalizer accepted the `FAMILY_CLOSED` decision and added machine-readable planning-boundary, residual-gap, episode-breadth, and control-distance diagnostics without changing strategy metrics. Those byte changes supersede the executor-phase hashes: current raw/normalized claim SHA-256 is `29d0c6199c96ed9c91290467c748e34c5c7cd4bdced243abb84dfde93fe51b73` / `85ce2277b587135cd7394e0cce0b6e90cc5ce82e6c7f8067241042cb60a3b4a5`. Finalizer verification is 9/9 focused, 65/65 adjacent, and 433/433 full unittest, all `OK`; deterministic replay is substantively equal. Deterministic wrapper integration remains pending.

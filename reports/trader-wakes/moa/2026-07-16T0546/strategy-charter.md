# Strategy decision charter — 2026-07-16T0546

Phase: BUILD / L0 underlying discovery only
Sleeve: $3,000
Session: premarket
Role: GPT 5.6 Sol executor / only writer

## Orientation decision

The configured epoch `POST_REASSESSMENT_INDEPENDENT_DEFINED_RISK_DISCOVERY_V1` is completed after three consecutive `FAMILY_CLOSED` decisions and may not receive a fourth strategy test. This wake first closes the required search-design reassessment in `docs/SEARCH_DESIGN_REASSESSMENT_2026-07-16T0546.md`, then opens a successor epoch before touching outcomes. The predecessor NEXT is accepted only as burst-stop context, not as a strategy assignment.

The highest-information open route is the previously predeclared but non-claim-bearing `OVERNIGHT_INTRADAY_DISAGREEMENT_FORWARD_UPDRIFT` screen. Its single-SPY development row had positive event and paired centers and a 71.875% hit rate, but failed n=36 and dependence-aware uncertainty. It was not advanced, closed, or retuned. The successor test changes the evidence class rather than the trigger: a frozen four-index panel with same-symbol prior controls and same-date clustering so repeated cross-index observations increase breadth without pretending synchronous signals are independent.

## Exact claim-bearing candidate

- Candidate: `BROAD_INDEX_OVERNIGHT_ABSORPTION_BULL_CALL_21D_V1`
- Family: `BROAD_INDEX_OVERNIGHT_SELL_INTRADAY_ABSORPTION_FORWARD_UPDRIFT`
- Economic edge mechanism: persistent overnight selling that is repeatedly absorbed by positive regular-session demand across liquid broad-index ETFs may represent transitory risk-transfer or foreign-session pressure rather than durable negative information; the absorption may continue as short-horizon upward drift.
- Funnel before: `F0_MECHANISM`
- Claim bar: `L0_DISCOVERY_ONLY`
- Exact decision: advance F0→F1 as `STRATEGY_ADVANCED` only if every frozen train gate passes; otherwise close the exact family F0→F0 as `FAMILY_CLOSED`. No holdout outcome or option mark may be read in either branch.

## Complete Layered Edge Stack

- Market / underlying: fixed liquid broad-index ETF panel `SPY, QQQ, IWM, DIA`, adjusted daily OHLCV, exact per-symbol chronology.
- Forecast type: direction up over five completed sessions.
- Economic mechanism: broad overnight supply absorbed by regular-session demand is transitory pressure; continuation should appear across more than one index rather than as a single-SPY artifact.
- Option structure: future conditional one-lot 18–24 DTE $2-wide bull-call debit spread on the qualifying ETF; no historical option pricing at F0.
- Intended Greeks: positive delta, limited positive gamma and vega, defined debit.
- Dangerous unintended exposures: negative theta, volatility crush, gap loss, capped upside, synchronous index overlap, debit slippage, assignment/exercise, and closing friction.
- Regime envelope: completed close above fully warmed SMA100; compounded five-session overnight return ≤-1%; compounded five-session regular-session return ≥+1%. Stand aside outside this state.
- Entry trigger: completed signal session only; enter at the next completed close. Features cannot use the entry or later bars.
- Exit / management: F0 outcome is the fifth subsequent completed close. Future option plan only: +50% spread-value harvest, -50% debit cut, five-session time stop, or trend invalidation; no roll or averaging.
- Risk / capital fit: `capital_fit_usd=200`; frictionless planning one-lot `max_loss_usd=200` before debit/closing friction; `max_lots=1`; at most one broad-index directional risk unit across the sleeve.
- Portfolio overlap: simultaneous ETF signals are one clustered broad-index episode; never count or later open four correlated risk units.
- Evidence: chronological 60/40 signal-date split; train outcomes only; final 40% identity-only; same-symbol prior-only, no-reuse, non-trigger controls; 10-bps underlying hurdle; same-date episode aggregation; date-block uncertainty; strict integrity checks; zero option pricing.
- Confidence stage: F0/L0 before. F1/L0 only on complete train conjunction. Never L1 or capital seat from underlying evidence.
- Stand-aside rule: missing/nonfinite/under-warmed data, regime mismatch, no prior control, fewer than two symbols represented in train, future option illiquidity, debit above $200, overlapping index risk, or any source/chronology/integrity ambiguity.

## Frozen predeclared falsifier

The exact candidate fails and the family closes if any train gate fails:

1. at least 48 same-date clustered train episodes;
2. at least 10 signal years;
3. at least 3 represented ETFs;
4. at least 80% same-symbol prior-control support before date clustering;
5. event mean after 10 bps >0;
6. paired excess mean >0;
7. circular five-episode-block LB90 >0;
8. positive event frequency ≥55%;
9. event-return worst-decile mean ≥-5%;
10. zero lag, chronology, control-reuse, trigger-contamination, overlap, partition, or strict-JSON integrity violations.

The trigger thresholds, direction, five-session horizon, panel, cost hurdle, clustering, control tolerances, split, and gates are frozen before real outcomes. Failure does not authorize threshold nudges, sign inversion, holdout opening, or an option wrapper. Advancement cannot grant L1, a capital seat, paper, shadow, arm, broker, funding, or live authority.

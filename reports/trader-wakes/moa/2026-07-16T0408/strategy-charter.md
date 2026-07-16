# Strategy decision charter — 2026-07-16T0408 executor

Phase: BUILD / L0 train-only underlying discovery
Sleeve: $3,000 Agentic; research/paper only
Session: premarket, 2026-07-16 04:09 PDT
Living leader: none

## Chosen closed loop

Exercise `TRAIN_ONLY_DEFINED_RISK_CANDIDATE_FACTORY_V1` on two predeclared, economically independent, non-quarantined mechanisms. The factory is only search machinery. This wake closes exactly one claim-bearing decision: advance the highest-ranked complete train survivor from F0 to F1, or, if neither survives, close the primary credit-risk mechanism at F0. The secondary screen remains search information unless it is the selected survivor; it is not silently granted a family-close claim.

The prior NEXT is followed because current orientation confirms zero living candidates, no epoch pivot/stop, no repeated loop signature, executable historical-underlying discovery, and no existing factory implementation. It is not followed as an order.

## Factory-wide frozen rules

- Use split/dividend-adjusted daily data persisted and reread from hash-cited CSV caches.
- Freeze every signal identity before outcomes, partition chronologically 60/40, inspect train outcomes only, and persist holdout identity hashes with outcome metrics unread.
- Features end at the completed signal session. Entry is the next completed session close and exit is the fifth completed session after entry. Same-mechanism episodes do not overlap.
- Compare each signal with one deterministic prior-only, no-reuse control whose full five-session outcome ends before the signal. Match without outcome access on SPY SMA100 distance, trailing 60-session return, and HV20. The control feature date must satisfy the same base regime but not the mechanism trigger; do not use later-in-window pattern labels to select controls, because that would condition on future control-path information. Fail closed below 80% support.
- Train discovery gates per mechanism: at least 36 matched pairs, at least 8 signal years, support >=80%, signed event mean after 10 bps >0, signed paired excess mean >0, one-sided 90% circular three-pair-block bootstrap lower bound >0, signed positive frequency >=55%, signed worst-decile mean >=-5%, and zero chronology/matching/reuse/population/nonfinite violations.
- Candidate ranking, only among complete gate passes: larger bootstrap lower bound, then more event years, then more pairs, then candidate id. No post-outcome threshold, sign, horizon, regime, control, or option-structure changes.
- No option pricing at F0. Proxy-only future option expressions cannot earn L1 or a capital seat.

## Candidate A — primary claim if no survivor

Candidate id: `CREDIT_RISK_OFF_SPY_BEAR_PUT_21D_V1`
Family: `HIGH_YIELD_CREDIT_DIVERGENCE_FORWARD_DOWNSIDE`

- Market / underlying: SPY with HYG and IEF as liquid daily credit/rates state proxies; future SPY options only.
- Forecast type: direction down over the next five completed sessions.
- Economic mechanism: high-yield credit reprices deteriorating risk appetite and financing conditions before large-cap equities fully adjust; HYG underperformance versus duration-safe Treasuries inside a still-positive SPY long trend may lead delayed equity downside.
- Option structure: future conditional one-lot 18–24 DTE $2-wide SPY bear-put debit spread.
- Intended Greeks: negative delta, positive gamma, bounded positive vega, bounded negative theta.
- Dangerous unintended exposures: volatility crush after entry, abrupt risk-on reversal, gap/slippage through the debit, capped crash payoff, expiry/assignment handling, and credit-proxy composition drift.
- Regime envelope: completed SPY close above fully warmed SMA100; trailing ten-session HYG-minus-IEF return <= -1.5 percentage points; SPY trailing five-session return <=0. Stand aside outside that state.
- Entry trigger: next completed session close after the lag-safe signal.
- Exit / management: underlying F0 exits after five sessions. Future option plan: +50% debit harvest, -50% debit loss cut, five-DTE time stop, or credit divergence/trend invalidation; no roll.
- Risk / capital fit: `capital_fit_usd=200`, frictionless planning `max_loss_usd=200` before closing friction, `max_lots=1`; one global macro-risk unit and no overlapping SPY/index directional unit.
- Evidence / falsifier: every frozen factory discovery gate above must pass on train with the holdout unread; otherwise close this exact family at F0.
- Confidence: F0 / L0 discovery only before the run.
- Stand-aside: missing/nonfinite HYG/IEF/SPY history, under-warmed features, regime mismatch, failed control support, failed option liquidity/debit/max-loss gate, or overlapping macro/index risk.

## Candidate B — independent secondary screen

Candidate id: `OVERNIGHT_SELL_INTRADAY_RECOVERY_SPY_BULL_CALL_21D_V1`
Family: `OVERNIGHT_INTRADAY_DISAGREEMENT_FORWARD_UPDRIFT`

- Market / underlying: SPY adjusted OHLCV; future SPY options only.
- Forecast type: direction up over the next five completed sessions.
- Economic mechanism: persistent negative close-to-next-open returns absorbed by positive open-to-close demand may identify overnight risk-transfer pressure rather than durable information, with regular-session institutional demand continuing after the disagreement.
- Option structure: future conditional one-lot 18–24 DTE $2-wide SPY bull-call debit spread.
- Intended Greeks: positive delta, positive gamma, bounded positive vega, bounded negative theta.
- Dangerous unintended exposures: overnight information is genuine rather than transitory, intraday recovery exhausts at entry, volatility crush, gap loss, capped upside, and expiry/assignment handling.
- Regime envelope: completed SPY close above fully warmed SMA100; trailing five-session compounded overnight return <=-1%; trailing five-session compounded intraday return >=+1%. Stand aside otherwise.
- Entry trigger: next completed session close after the lag-safe signal.
- Exit / management: underlying F0 exits after five sessions. Future option plan: +50% debit harvest, -50% debit loss cut, five-DTE time stop, trend invalidation; no roll.
- Risk / capital fit: `capital_fit_usd=200`, frictionless planning `max_loss_usd=200` before closing friction, `max_lots=1`; one global SPY/index positive-delta unit.
- Evidence / falsifier: identical frozen factory discovery gates, with neutral same-trend/non-disagreement prior controls; failure is a screen elimination unless this candidate is the selected claim-bearing survivor.
- Confidence: F0 / L0 discovery only before the run.
- Stand-aside: missing/nonfinite OHLC, under-warmed features, disagreement or trend mismatch, failed control support, failed option liquidity/debit/max-loss gate, or overlapping index risk.

## Exact outcome rule

1. If one or both candidates pass every train discovery gate, select the deterministic top survivor and close `STRATEGY_ADVANCED` for that named candidate, F0 -> F1 only.
2. If neither passes, close `FAMILY_CLOSED` for `HIGH_YIELD_CREDIT_DIVERGENCE_FORWARD_DOWNSIDE` / `CREDIT_RISK_OFF_SPY_BEAR_PUT_21D_V1`; quarantine the exact HYG-minus-IEF/SPY-uptrend/five-session geometry from unchanged reruns. The overnight screen remains documented search information, not a second claim-bearing outcome.

No registry mutation, capital seat, paper intent, shadow, arm, broker session, funding, or live action is authorized.

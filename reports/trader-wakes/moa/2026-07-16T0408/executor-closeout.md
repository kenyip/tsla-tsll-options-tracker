# MOA executor closeout — 2026-07-16T0408

Role: GPT 5.6 Sol executor / only writer
Phase: BUILD / L0 underlying discovery
Session: premarket
Status: EXECUTOR PARTIAL — challenger and finalizer pending; no commit/push/merge/RUN COMPLETE

## Strategy decision charter

The pre-outcome charter is preserved at `strategy-charter.md` in this directory.

Chosen loop: exercise `TRAIN_ONLY_DEFINED_RISK_CANDIDATE_FACTORY_V1` on two predeclared independent economic mechanisms, then close exactly one claim-bearing strategy decision. The factory itself is search machinery, not strategy progress.

Frozen factory rules:

- hash-cited, persisted, split/dividend-adjusted daily data;
- completed-session features, next-session close entry, fifth subsequent completed-session close exit;
- non-overlapping signal episodes;
- deterministic prior-only, no-reuse controls whose full outcome ends before the signal;
- controls match SPY SMA100 distance, 60-session return, and HV20 and satisfy the same base regime but not the mechanism trigger at the control feature date;
- chronological 60/40 split, train outcomes only, identity-only holdout;
- discovery gates: at least 36 matched pairs, at least eight signal years, control support at least 80%, signed event mean after 10 bps >0, signed paired excess >0, circular three-pair-block LB90 >0, signed hit rate at least 55%, signed worst-decile mean at least -5%, and zero integrity violations.

## Candidates and complete Layered Edge Stacks

### Primary: `CREDIT_RISK_OFF_SPY_BEAR_PUT_21D_V1`

- Family: `HIGH_YIELD_CREDIT_DIVERGENCE_FORWARD_DOWNSIDE`.
- Market / underlying: SPY; HYG and IEF are liquid credit/rates state proxies.
- Forecast: SPY direction down over five completed sessions.
- Economic mechanism: high-yield credit reprices deteriorating risk appetite and financing conditions before large-cap equities fully adjust.
- Structure: future conditional one-lot 18–24 DTE $2-wide SPY bear-put debit spread.
- Intended Greeks: negative delta, positive gamma, bounded positive vega, bounded negative theta.
- Dangerous Greeks/path exposures: volatility crush, abrupt risk-on reversal, debit slippage, capped crash payoff, expiry/assignment handling, and proxy-composition drift.
- Regime: SPY above warmed SMA100; ten-session HYG-minus-IEF return <=-1.5 percentage points; SPY five-session return <=0.
- Entry / exit: next completed close; underlying F0 exit five sessions later. Future option plan only: +50% debit harvest, -50% debit cut, five-DTE time stop, or regime invalidation; no roll.
- Risk: `capital_fit_usd=200`, planning one-lot `max_loss_usd=200` before debit slippage/closing friction, `max_lots=1`; no overlapping global macro/index directional unit.
- Falsifier: any frozen train gate failure.
- Confidence before/after: F0 / L0 -> F0 / L0 closed.
- Stand aside: missing/nonfinite/under-warmed data, regime mismatch, control support failure, future option liquidity/debit/max-loss failure, or overlapping index risk.

### Independent secondary screen: `OVERNIGHT_SELL_INTRADAY_RECOVERY_SPY_BULL_CALL_21D_V1`

- Family: `OVERNIGHT_INTRADAY_DISAGREEMENT_FORWARD_UPDRIFT`.
- Market / underlying: SPY adjusted OHLCV.
- Forecast: SPY direction up over five completed sessions.
- Economic mechanism: repeated negative overnight returns absorbed by positive regular-session demand may be transitory risk-transfer pressure rather than durable negative information.
- Structure: future conditional one-lot 18–24 DTE $2-wide SPY bull-call debit spread.
- Intended Greeks: positive delta, positive gamma, bounded positive vega, bounded negative theta.
- Dangerous Greeks/path exposures: overnight news is genuine, regular-session recovery exhausts, volatility crush, gap loss, capped upside, and expiry/assignment handling.
- Regime: SPY above warmed SMA100; compounded five-session overnight return <=-1%; compounded five-session intraday return >=+1%.
- Entry / exit: next completed close; F0 exit five sessions later. Future option plan only: +50%/-50% debit, five-DTE time stop, or trend invalidation; no roll.
- Risk: `capital_fit_usd=200`, planning `max_loss_usd=200`, `max_lots=1`; one positive-delta global index unit.
- Falsifier: identical frozen discovery gates.
- Confidence after screen: still F0/L0; not advanced and not the claim-bearing family close.
- Stand aside: missing/nonfinite/under-warmed data, regime mismatch, control support failure, future option liquidity/debit/max-loss failure, or overlapping index risk.

## Exact claim-bearing outcome

`FAMILY_CLOSED` for the exact `CREDIT_RISK_OFF_SPY_BEAR_PUT_21D_V1` / `HIGH_YIELD_CREDIT_DIVERGENCE_FORWARD_DOWNSIDE` geometry, F0 -> F0. Strategy advancement is false.

Canonical claim: the run-local canonical factory claim JSON

- Finalizer-regenerated raw SHA-256 after the machine dominant-failure wording repair: `2eb3e4c7ebf502de0ac533edcf8a986eb95253189a46922f6f3b7bb75b13f14c` (executor-era pre-repair SHA `3127839938f7cb25b2612c2f591bbba379ddffb7d3c89bfc3f0aa17962844377`).
- Exact-cache replay, excluding only `generated_at`: equal `true`.
- Finalizer replay-normalized SHA-256: `a4fd731d931185297648b7bde28350c9b17022cf8062b9fc06fa0e76762d30b3`.
- Common exact-date panel: 4,832 sessions, 2007-05-01 through 2026-07-15; no forward fill.
- Train eligible/matched: 42/41; control support 97.6190%; ten signal years (2007–2016).
- Signed bearish event mean after 10 bps: **-0.909825%**. Equivalently, SPY rose about 0.809825% before the labeled hurdle, opposite the forecast.
- Signed bearish control mean after 10 bps: **-0.201659%**.
- Signed paired excess: **-0.708167%**.
- Circular three-pair-block LB90: **-1.360006%**.
- Signed positive frequency: **29.2683%**.
- Signed worst-decile mean: **-4.015427%**; this tail gate passed, but it cannot rescue the wrong center and uncertainty.
- Four frozen gates failed: signed event expectancy, paired specificity, uncertainty lower bound, and positive frequency.
- Integrity violations: zero.
- Holdout: 28/28 identities, 2016-04-07 through 2026-02-17, SHA `83fc5c0fe69de6801d440970c53edc8c098d09bd3edf0cdbe7728a41707c1c23`; outcome metrics unread, simulation false, option pricing calls zero.

Dominant failure mechanism: the exact credit-risk-off trigger predicts the wrong five-session SPY sign and underperforms comparable prior same-regime controls. A bearish option wrapper would monetize the wrong forecast and cannot rescue this F0 anti-edge.

Quarantine: do not rerun the same SPY-uptrend / ten-session HYG-minus-IEF <=-1.5-point / nonpositive SPY five-session / next-close / five-session-hold geometry, nearby threshold nudges, or option-wrapper substitutions on the same panel. Reopening requires a materially different credit state construction, horizon/economic mechanism justified before outcomes, point-in-time credit spread evidence, or another independent evidence class.

## Secondary search information — not strategy advancement

The overnight/intraday disagreement screen had positive centers but did not pass the frozen discovery bar:

- train eligible/matched 34/32, support 94.1176%, ten signal years;
- signed event mean after 10 bps +0.511192%; signed paired excess +0.739330%; signed hit rate 71.875%; worst-decile -4.699177%;
- n32 failed the required n36 density and LB90 was **-0.200722%**, failing the >0 uncertainty gate;
- holdout 24/24 identities, SHA `40113d833d3e6d360a7230015a5dfffdd3f53a3267ad3d569ea41089874492c8`, outcomes unread, option pricing zero.

This is a suggestive but uncertainty-unbounded development screen. It earns no F1, no family closure, no retune, no holdout opening, and no capital-path authority.

## Search information and repaired blocker

New reusable capability: `scripts/train_only_defined_risk_candidate_factory.py` evaluates multiple predeclared mechanisms under one lag-safe, prior-control, train-only, sealed-holdout contract and deterministically selects no more than one claim-bearing outcome.

The first real run exposed a claim-blocking cache replay defect in the shared adjusted-OHLCV validator: yfinance-adjusted CSV round trips produced 1-ULP high/open/close or low/open/close differences (SPY 2 high rows; HYG 15 high/7 low; IEF 4 high/2 low; maximum gap 1.42e-14). The validator now accepts only machine-close equality (`rtol=atol=1e-12`) while still rejecting material OHLC geometry violations. The dependent factory experiment was rerun unchanged after repair and produced the outcome above.

This capability delta is search information, not strategy advancement.

## Evidence validity critique

- Leakage/lookahead: signal features end at the completed signal session; entry is next close. Controls are prior-only with full outcomes before each signal and no reuse. No later-in-control-path pattern labels are used for control selection.
- Population: present-day SPY/HYG/IEF ETFs and their evolving composition are a proxy limitation; no issuer-universe or point-in-time credit-spread generalization is claimed.
- Contract availability: no historical option contract was selected or priced; the debit spreads are future conditional expressions only.
- Costs/fills: 10 bps is an underlying sensitivity hurdle, not option spread, IV, execution, or management realism.
- Holdout: identities are frozen; outcomes and option simulation remain unopened.
- Density: primary clears n/year/support; secondary does not clear n and uncertainty.
- Ranking completeness: both predeclared independent candidates were evaluated under one frozen ranking rule; no outcome-driven candidate was inserted.
- Stale leaders: readiness has no living leader; absolute discovery gates were used.
- Capital: structural one-lot debit bounds fit the $3,000 sleeve, but no debit/IV/path evidence exists and no capital seat is claimed.
- Claim scope: proxy daily ETF evidence supports only exact F0/L0 closure, never L1 or paper readiness.

## Verification completed by executor

- Focused behavioral, lag, prior-only, control-reuse, positive/negative-control, sealed-holdout, ULP-boundary, and material-geometry tests: `6 passed`.
- Shared FOMC/OHLCV regression: `9 passed`.
- Strict compile: green.
- Full unittest suite: `Ran 415 tests in 26.785s`, `OK`.
- Full pytest suite: `425 passed, 18 subtests passed in 28.31s`.
- `just test`: exit 0; TSLA and TSLL both `STAND ASIDE`; no broker action.
- Deterministic real-data replay: normalized equality true; normalized SHA above.
- Coverage refresh: 21 structures / 246 hypotheses / 70 evolve artifacts / no quality leader.
- `git diff --check`: green before report writes; final diff review remains below.

## Readiness / authority

No phase or B3/B4/B6+ check advanced. B1/B5 BUILD evidence improved through exact persisted-data replay, bounded ULP validation, durable claim, tests, and deterministic replay. Living candidates remain 0; L1 candidates 0; quality leaders 0; capital seats 0. No registry mutation or paper intent occurred.

If this executor decision is accepted and completed by challenger/finalizer, the current successor search epoch reaches two consecutive no-advance decisions and the next wake must pivot to a materially different economic mechanism or evidence class. It must not retune the credit or overnight screens.

Freedom audit: symbol and strategy freedom remained open; the executor chose independent cross-asset credit-leading and market-microstructure disagreement mechanisms by information gain, not an allowlist, familiar TSLA/TSLL habit, or caller-selected slot.

## Durable lesson

Future Trader can cheaply compare multiple complete F0 candidates without turning factory construction into strategy progress, while preserving a single claim-bearing decision and sealed holdouts. Credit-risk divergence in this exact geometry is a strong anti-edge. The overnight/intraday disagreement center is interesting but uncertainty- and density-insufficient; it must not be promoted or same-panel tuned.

## ONE NEXT

`SEC_FORM4_CLUSTERED_INSIDER_BUYING_DIRECTION_F0`: pivot to a materially different corporate-information evidence class. Predeclare a fixed liquid-symbol panel, official SEC Form 4 transaction-code/ownership/timestamp rules, clustered open-market purchase threshold, prior-only same-symbol controls, five- or ten-session signed forecast, complete defined-risk call-debit Layered Edge Stack, and an exact train-only advance-or-close rule before collecting outcomes. Fail closed on ambiguous derivatives, late/non-PIT filing timestamps, issuer mapping, amendments, or insufficient cross-symbol/year density. Do not reopen this wake's sealed holdouts or retune its credit/overnight thresholds.

No commit, push, merge, deterministic completion gate, or RUN COMPLETE claim was attempted in this executor phase.

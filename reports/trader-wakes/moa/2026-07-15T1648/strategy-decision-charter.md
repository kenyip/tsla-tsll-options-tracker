# Strategy decision charter — 2026-07-15T1648 executor

## Orientation and one chosen loop

Phase is BUILD, local session is postclose, sleeve is $3,000, and the current living leader/capital path is empty. The active search epoch in `configs/search_epoch.json` is reassessment-complete and its time-series breakout success definition was met at F2/L0 by the prior 281-row frozen population (168 development, 113 opened holdout). The current MOA `orientation.json` failed to parse the epoch and reported `null`, but the authoritative config and prior finalized artifacts are readable; that orientation defect does not erase the completed F2 state. The epoch-scoped no-advance streak is zero. Historical-option archives remain too shallow for L1, but the canonical goal explicitly leaves Black-Scholes/listed-expiry proxy discovery open.

I choose `BREAKOUT_F2_OPTION_PAYOFF_FREEZE`, not because NEXT is an order, but because it is the only existing F2 directional survivor and the smallest experiment that can test whether its stated option expression actually monetizes the forecast after adverse two-leg costs and a $3k-realistic portfolio policy. Starting a fresh F0 family before resolving this payoff mismatch would discard higher-information strategy evidence. I supersede broad evolve/research volume and do not reopen any quarantined family.

## Layered Edge Stack

- Candidate ID: `MULTINAME_BREAKOUT_BULL_CALL_14D_V1`.
- Frozen option DNA ID: `BREAKOUT_BULL_CALL_14D_055D_1W_10S_V1`.
- Economic mechanism: gradual information diffusion and trend-following demand after a completed close at least 2% above the prior completed 20-session high, while above the prior completed SMA100, may produce enough positive ten-session drift to overcome debit-spread theta and two-leg execution friction.
- Candidate/family scope: the unchanged AAPL, MSFT, NVDA, AMZN, META, GOOGL, AMD, TSLA panel and unchanged 281 matched-blueprint population. Option DNA is frozen and judged first on only the original 168 development blueprints. The already-opened 113 rows are inspected secondary stress only and can neither become a new untouched holdout nor retune DNA.
- Current funnel stage: `F2_UNTOUCHED_HOLDOUT/L0` underlying directional evidence. No option-payoff, L1, capital-seat, or paper authority exists before this wake.
- Market / underlying: split/dividend-adjusted daily closes from the frozen, hash-verified yfinance caches; fixed present-day liquid universe with survivorship and listing bias.
- Forecast type: conditional `direction_up` over at most ten completed sessions after next-session entry.
- Option structure: one-lot bull call debit spread; buy the call nearest a 0.55 Black-Scholes delta and sell the exact `$1`-higher call at the same expiration.
- Listing/strike freeze: target 14 calendar DTE, represented by the first Friday on or after entry+14 calendar days. Use the existing deterministic exchange-convention proxy strike increment; require an exact `$1` width in that grid and fail closed when it is unavailable. This is a synthetic listed-Friday/strike-grid abstraction, not proof that a historical contract was listed or liquid.
- Volatility/price provenance: Black-Scholes proxy marks with risk-free rate 4% and per-trade volatility fixed to the completed signal-day 20-session annualized realized volatility. No implied-volatility edge is claimed; dividends, skew, American exercise, observed bid/ask, and vega path are unmodeled.
- Intended Greeks: positive delta and bounded positive gamma, with total debit risk bounded by the one-lot spread.
- Dangerous Greeks/execution: theta if continuation stalls, long-vega/model risk, short-call assignment/dividend risk, pin risk, listing/liquidity error, and multi-leg bid/ask friction.
- Regime envelope: only a completed-bar breakout (`close >= 1.02 × prior completed 20-session high`) above a fully warmed prior-completed SMA100; otherwise stand aside.
- Entry trigger: enter at the next session close after the completed lag-safe signal. This preserves the frozen underlying entry date; no same-bar signal fill.
- Exit/management rule, frozen order: beginning on the next completed session, (1) close on the contract-expiration session; else (2) harvest when adverse-cost spread liquidation value is at least 50% of the `$1` maximum spread value; else (3) invalidate when the underlying close is strictly below the pre-breakout 20-session high; else (4) close at the hard ten-session stop. Expiration is a precedence boundary rather than a hold-to-expiry primary objective, and no same-bar re-entry is allowed.
- Cost axes: independently rerun the identical DNA under (a) 5% adverse price slippage on each option leg at entry and exit, and (b) `$0.01` half-spread per leg at entry and exit. Signed package liquidation values are retained so closing friction cannot disappear at zero.
- Portfolio overlap: event-level diagnostics may include all eligible frozen rows, but the executable portfolio ledger admits at most one position globally. Candidate events are ordered by date then the frozen symbol order; while risk is open they stand aside, and an exit date cannot be reused for a new entry.
- Risk/capital fit: `capital_fit_usd` is the worst simulated one-lot entry debit across both axes; one-lot `max_loss_usd` is the larger of entry debit risk and realized managed-path loss including adverse closing friction; `max_lots=1`; maximum concurrent strategy risk is one global unit.
- Evidence before: F1 development n=168 and F2 underlying holdout n=113 passed their unchanged pooled discovery gates, but AMZN/META/MSFT and the earliest holdout tertile were weak. No option pricing calls had occurred.
- Confidence before: `F2_UNTOUCHED_HOLDOUT/L0`; no living leader and no capital seat.
- Stand-aside rule: no lag-safe signal; missing/non-finite path or volatility; exact `$1` proxy grid unavailable; debit non-positive or at/above width; one-lot risk above `$300`; another breakout unit open; either adverse-cost axis non-positive; drawdown/density failure; or future observed contract/quote checks unavailable.

## Predeclared falsifier and exact decision

The option expression may advance `F2 → F3_ROBUST_PAPER_PLAN` only if the frozen DNA satisfies all of the following without retuning:

Primary original-168 development rows, each cost axis:

1. at least 80 eligible event trades and at least six represented symbols;
2. positive absolute after-cost total option PnL (underlying paired excess cannot rescue failure);
3. at least 30 trades in the globally one-unit portfolio ledger;
4. one-lot `max_loss_usd <= $300`;
5. portfolio cumulative max drawdown `<= $75`;
6. six-trade dense-negative windows `<= 5`;
7. exact source/population/chronology, no concurrent positions, no same-bar re-entry, finite values, and strict JSON.

The already-opened 113-row secondary stress is rerun only after DNA is frozen. For `STRATEGY_ADVANCED`, it must remain non-catastrophic under both axes: at least 40 eligible event trades, at least 20 one-unit portfolio trades, positive absolute after-cost total option PnL, one-lot max loss `<= $300`, max drawdown `<= $75`, dense-negative windows `<= 5`, and identical integrity rules. It remains inspected stress, not a second untouched holdout and not L1 evidence.

Exact close:

- `STRATEGY_ADVANCED` only if every predeclared primary and secondary check passes: advance to `F3_ROBUST_PAPER_PLAN/L0_PROXY`, still with `l1_claim=false`, no capital seat, and no paper/shadow/live status mutation.
- Otherwise `FAMILY_CLOSED`: quarantine the exact frozen 14-DTE/0.55-delta/`$1`-wide/ten-session bull-call expression and record the first material failed mechanism (listing density, after-cost payoff, drawdown, loss, or temporal/symbol instability). The prior F2 underlying result remains historical context, not an option candidate.
- `BLOCKER_REMOVED_AND_RETESTED` is allowed only if a claim-invalidating simulator defect is exposed, fixed with behavioral/boundary/negative-control tests, and this exact experiment is rerun in this wake.

No registry promotion, capital seat, paper order, shadow transition, broker session, arm, or live action is authorized.

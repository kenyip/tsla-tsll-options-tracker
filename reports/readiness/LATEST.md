# Trader platform readiness — latest

Updated: 2026-07-15 16:48 local — MoA finalizer handoff pending deterministic integration.

Phase: BUILD
Sleeve: $3,000 Agentic research sleeve
Authority: research/paper-safe only; no shadow/live auto-promotion, no broker access, no live orders.

## Decision readiness

- Latest strategy outcome: `FAMILY_CLOSED`.
- Funnel: `MULTINAME_BREAKOUT_BULL_CALL_14D_V1` remains `F2_UNTOUCHED_HOLDOUT`; it did not advance to F3/L1/paper planning.
- Search information: the frozen underlying breakout continuation signal did not survive the exact 14-DTE `$1` bull-call expression under dual adverse cost axes, one-global-unit path management, drawdown/density gates, and labeled secondary stress.
- No-advance implication: close and quarantine this exact option expression. Do not retune it, salvage symbols/subsets, relabel the already-opened rows as untouched, or promote it to registry/paper/shadow/live.

## Latest capital-fit result

Exact structure: one-lot 14-DTE listed-expiry proxy bull-call debit spread, exact `$1` width, next-session entry, expiration-session precedence, 50%-of-max-value harvest, pre-breakout-high invalidation, hard ten-session stop, no same-bar reentry, and one global open unit.

- `capital_fit_usd = 92.56501618263479`
- `max_loss_usd = 246.90032488027197`
- `max_lots = 1`
- Structural width bound before closing friction: `$100`.
- Operating worst simulated path loss including closing friction: `$246.90`.
- Result: one-lot envelope fit does not overcome failed expectancy, drawdown, density, and secondary-stress gates.

## Claim-bearing evidence

Canonical current-code replay: `.cache/platform/breakout_bull_call_option_2026-07-15T1648-v7.json`

- strict JSON bytes: `494767`
- raw SHA-256: `acc1cc365690c5c7652d180da3da431310d597b754c4ec9056964cdae6cbd526`
- normalized SHA-256 excluding only `generated_at`: `b32c951ff607a0f2262005634191bd94c6fd36bc599338ec1a34e599b3ba166e`
- decision: `FAMILY_CLOSED`
- failed checks: 16

Primary development population:
- 5% adverse leg-price axis: 104 eligible events across seven symbols; `-$1,760.00` event PnL; 62 portfolio trades / `-$1,321.71` portfolio PnL; `$1,352.24` max DD; 9 dense negative windows.
- `$0.01` half-spread-per-leg axis: 105 eligible events across seven symbols; `+$27.79` event PnL; 69 portfolio trades / `+$21.54` portfolio PnL; `$183.13` max DD; 6 dense negative windows.

Previously opened secondary stress:
- 5% axis: 13 eligible events across three symbols; `-$447.09` event PnL; 10 portfolio trades / `-$353.24` portfolio PnL; `$353.24` max DD.
- fixed-dollar axis: 13 eligible events across three symbols; `+$10.78` event PnL, but 10 portfolio trades / `-$11.31` portfolio PnL; support, breadth, and portfolio-PnL gates fail.

## Finalizer repairs

- Strategy charter and emitted payload now state contract-expiration-session precedence consistently with executable behavior.
- Completed `configs/search_epoch.json` remains durable orientation context until a successor epoch replaces it; regenerated orientation carries status, identity, reassessment, charter, goal, and success-definition fields.
- Replay guards are durable: normalized evidence hashing excludes only `generated_at`, a negative control detects substantive changes, and CLI overwrite refusal preserves existing bytes.
- Profile skill `trader-self-evolution` now records the completed-epoch orientation pitfall and regression requirement.

## Verification

- focused option-lab + compounding: `38 tests — OK`
- broader behavioral/boundary/negative-control/adjacent suite: `57 tests — OK`
- required full suite: `.venv/bin/python -m unittest discover -s tests` -> `331 tests — OK`
- current-code v7 payoff replay: exit `0`, same 16 failed checks, `FAMILY_CLOSED`
- income coverage regenerated at `2026-07-15T1648`: 21 catalog structures, 246 hypotheses, 70 evolve sim artifacts

## Readiness blockers

1. No capital-path candidate currently has robust after-cost option-payoff evidence plus path quality sufficient for an L1/capital seat.
2. The closed bull-call expression cannot be reopened without a named new mechanism/evidence class; structural fit alone is insufficient.
3. Broad observed historical option entry/exit joins remain unavailable for calibration. This blocks observed-option/L1 claims only, not labeled proxy discovery.
4. Any future F3 candidate still requires live-clock paper quotes/fills before F4/shadow/live authority.
5. Deterministic integration for this finalizer handoff is pending; no commit/push/merge claim is made here.

Coverage detail: `reports/readiness/income-coverage-LATEST.md`
Finalizer report: `reports/trader-wakes/2026-07-15T1648-moa-merge.md`
Learning: `reports/trader-wakes/moa/2026-07-15T1648/learning-promotion.md`
Compounding handoff: `reports/trader-wakes/moa/2026-07-15T1648/compounding.json`

## Exactly one NEXT seed

THETA_EXPRESSIONS_NONMONOTONIC_PAYOFF_F0: in the next zero-input BUILD wake, use the current full-universe rank to select where risk belongs, then search a non-monotonic theta-led payoff class that is not the closed bull-call expression: broken-wing/iron butterfly, asymmetric iron condor, or calendar/diagonal chosen from current regime, liquidity, and capital fit. Freeze symbol(s), exact legs, DTE, delta/width, debit-or-credit bounds, entry timing, profit/stop/time exits, assignment/dividend handling, and one-lot capital_fit_usd/max_loss_usd/max_lots before outcomes; require one genuinely new candidate and one predeclared F0 mechanism test using labeled Black-Scholes/listed-expiry proxy over historical underlying paths with chronology, dual multi-leg costs, overlap/concentration controls, negative controls, and no subset salvage. Reuse the option payoff lab when useful but do not retune or reopen MULTINAME_BREAKOUT_BULL_CALL_14D_V1. Discovery bar only: no L1, registry auto-promote, paper force, shadow, arm, broker, or live action.

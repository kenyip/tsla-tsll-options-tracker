# Strategy decision charter — 2026-07-16T0112

WAKE: 2026-07-16T0112
PHASE: BUILD / L0 underlying discovery
SLEEVE: $3,000 Agentic research sleeve
MARKET SESSION: premarket, derived at 2026-07-16 01:13 PDT; no RTH paper action

## Decision

ECONOMIC MECHANISM: Scheduled FOMC decisions resolve a large, prior-known macro information set. In an already non-bearish SPY regime, gradual interpretation and institutional repositioning may create positive five-session post-announcement drift beyond ordinary same-regime drift.

CANDIDATE / FAMILY: `FOMC_INFORMATION_RESOLUTION_SPY_BULL_CALL_21D_V1` / `FOMC_POLICY_INFORMATION_RESOLUTION_DRIFT`. This is a new scheduled-macro evidence class, not issuer post-earnings drift, OPEX/TOM flow, breadth, residual reversal, breakout continuation, or a closed option-expression retune.

FUNNEL: `F0_MECHANISM -> F1_TRAIN` only if every frozen discovery gate passes; otherwise `F0_MECHANISM -> F0_MECHANISM` and the exact family closes.

PREDECLARED OUTCOME: exactly one of `STRATEGY_ADVANCED` or `FAMILY_CLOSED`.

PREDECLARED FALSIFIER: On the chronological first 60% of frozen eligible official events, close the exact family if any of these holds: fewer than 36 one-to-one matched train pairs; fewer than 6 distinct event years; matched-control support below 80% of eligible train events; non-positive mean event return after a labeled 10-bps round-trip sensitivity; non-positive mean paired excess; non-positive one-sided 90% year-block-bootstrap lower bound for paired excess; paired excess positive frequency below 55%; event-return worst decile below -5%; or any source, chronology, feature-lag, event-window, control-reuse, overlap, population, or strict-JSON integrity violation. Thresholds and geometry are frozen before SPY outcomes are loaded.

EXACT DECISION THIS WAKE WILL CLOSE: whether this one named scheduled-policy mechanism advances from F0 to F1 under the discovery bar or is quarantined unchanged as `FAMILY_CLOSED`. No option pricing, holdout outcome read, registry insertion, L1, capital seat, paper force, shadow, arm, broker, or live action.

## Layered Edge Stack

- Market / underlying: SPY only. It is the most liquid broad US equity ETF in the research universe and directly expresses index-level policy information while avoiding issuer-specific event contamination.
- Forecast type: conditional direction up over five completed sessions after a scheduled FOMC statement.
- Economic mechanism: policy-information resolution plus underreaction/repositioning in a prior-established non-bearish equity regime.
- Official event source and frozen population: Federal Reserve `https://www.federalreserve.gov/json/ne-press.json`; exact title `Federal Reserve issues FOMC statement`; press type `Monetary Policy`; release timestamp interpreted in `America/New_York`; exact 14:00 releases only; statement URL pattern `/newsevents/pressreleases/monetaryYYYYMMDDa.htm`; decision dates from 2013-01-01 through 2025-12-31. Non-14:00 emergency/ambiguous releases stand aside. The source artifact and filtered event manifest are hashed before price evaluation.
- Regime envelope: event is eligible only when the prior completed SPY session closes strictly above fully warmed SMA100 and trailing 60-session return is strictly positive. Controls must have the same regime state. Bearish, under-warmed, missing, or non-finite states stand aside.
- Entry trigger: official statement released at 14:00 ET on a completed SPY session; enter conceptually at the next completed regular session open. No same-day event return is a selector.
- Exit / management: underlying discovery outcome exits at the close of the fifth session including the entry session; no roll, average-down, overlap, or same-session re-entry. A later option-stage charter would separately freeze profit/loss exits.
- Control design: one prior-only non-event SPY session per event, selected only from pre-entry fields. Control must be within 756 sessions, share the exact non-bearish regime, have annualized HV20 within 0.10 and trailing 60-session return within 0.10, lie outside +/-5 sessions of every official FOMC date, and have its full five-session outcome complete before the event announcement. Deterministic tie-breaks are normalized feature distance, then shortest calendar distance, then earliest date. No control reuse, substitution after failure, or outcome-visible matching.
- Partition: chronological 60% train / sealed 40% holdout by frozen eligible event blueprint. Holdout dates and source identity may be hashed; holdout returns and option outcomes remain unread.
- Option structure: conditional future one-lot 18-24 DTE $2-wide bull-call debit spread only after underlying advancement and a separate option-stage charter. Zero option marks in this wake.
- Intended Greeks: positive bounded delta and convex positive gamma.
- Dangerous unintended Greeks: long theta decay, long vega into post-event IV normalization, spread/liquidity friction, gap risk, and short-leg early-assignment mechanics.
- Capital fit: `sleeve_usd=3000`; future structural `capital_fit_usd=200`; frictionless width-bound one-lot `max_loss_usd=200` before closing friction; `max_lots=1`; one global policy-event risk unit and no overlapping candidate exposure. These are planning bounds, not observed paid debit or L1 evidence.
- Evidence / falsifier: official prior-known release timestamps plus split/dividend-adjusted SPY OHLC; train-only discovery; labeled 10-bps underlying sensitivity; prior-only matched controls; year-block uncertainty; tail, density, chronology, and strict-JSON gates. Proxy/underlying discovery cannot earn L1.
- Confidence: before run `F0_MECHANISM / L0`; after run either `F1_TRAIN / L0` or closed at F0.
- Stand-aside rule: wrong/ambiguous release time, nonstandard title or URL, prior regime not positive, insufficient warmup, missing/non-finite prices, no frozen prior-only control, overlap, failed train gate, any holdout read, future option max debit above $200, or another policy-event unit open.

## Freedom / anti-thrash judgment

The prior NEXT is accepted because the completed old epoch requires a materially different evidence class, and official scheduled macro events offer prior-known labels without reopening any integrated closed family. This supersedes further TSLL archive churn and closed-family proxy volume during premarket. Freedom remains intact: the choice is evidence-driven, not a symbol/structure allowlist.

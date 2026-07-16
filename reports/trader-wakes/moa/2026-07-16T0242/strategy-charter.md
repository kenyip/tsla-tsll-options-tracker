# Strategy decision charter — 2026-07-16T0242

WAKE: 2026-07-16T0242
PHASE: BUILD / L0 underlying discovery
SLEEVE: $3,000 Agentic research sleeve
MARKET SESSION: premarket, derived at 2026-07-16 02:43 PDT; no RTH paper action

## Decision

ECONOMIC MECHANISM: The scheduled Federal Reserve Beige Book consolidates qualitative regional activity information eight times per year. Once that prior-known information set is released, near-term broad-index uncertainty may compress relative to otherwise similar neutral, non-stress periods, producing a smaller next-five-session SPY realized range after a 20-bps implementation hurdle.

CANDIDATE / FAMILY: `BEIGE_BOOK_RANGE_COMPRESSION_SPY_IC_21D_V1` / `BEIGE_BOOK_INFORMATION_RESOLUTION_RANGE_COMPRESSION`. This is a new scheduled qualitative-macro range/volatility mechanism, not the closed FOMC signed directional-drift mechanism, issuer earnings drift, post-shock compression, OPEX/TOM flow, breadth, residual reversal, breakout, or a closed option-expression retune.

FUNNEL: `F0_MECHANISM -> F1_TRAIN` only if every frozen discovery gate passes; otherwise `F0_MECHANISM -> F0_MECHANISM` and the exact family closes.

PREDECLARED OUTCOME: exactly one of `STRATEGY_ADVANCED` or `FAMILY_CLOSED`.

PREDECLARED FALSIFIER: On the chronological first 60% of frozen eligible official releases, close the exact family if any of these holds: fewer than 30 one-to-one matched train pairs; fewer than 6 distinct release years; matched-control support below 80%; non-positive mean paired five-session range compression after a 20-bps hurdle (`control_range - event_range - 0.002`); non-positive one-sided 90% release-year-block bootstrap lower bound; hurdle-adjusted compression positive frequency below 55%; event five-session high/low range 90th percentile above 7%; or any official-source, exact-date/time corroboration, chronology, feature-lag, event-window, control-reuse, overlap, source-coverage, population, holdout, option-pricing, or strict-JSON integrity violation. Geometry and thresholds are frozen before SPY outcome evaluation.

EXACT DECISION THIS WAKE WILL CLOSE: whether this named scheduled qualitative-information mechanism advances from F0 to F1 under the discovery bar or is quarantined unchanged as `FAMILY_CLOSED`. No option pricing, holdout outcome read, registry insertion, L1, capital seat, paper force, shadow, arm, broker, or live action.

## Layered Edge Stack

- Market / underlying: SPY only. It is the most liquid broad US equity ETF in the research universe and directly expresses market-wide regional-growth information without issuer-specific exposure.
- Forecast type: conditional five-session realized-range compression after a scheduled qualitative macro-information release.
- Economic mechanism: the Beige Book resolves a prior-known regional activity information set; in a neutral, non-stress regime, the release may reduce near-term uncertainty rather than create a persistent directional trend.
- Official event source and frozen population: Federal Reserve annual Beige Book archive pages `https://www.federalreserve.gov/monetarypolicy/beigebookYYYY.htm`, exact PDF date tokens `BeigeBook_YYYYMMDD.pdf`, 2013-01-01 through 2025-12-31. Federal Reserve calendar JSON `https://www.federalreserve.gov/json/calendar.json` must corroborate exact title `Beige Book` and `2:00 p.m.` for every overlapping dated row. The archive bytes, calendar bytes, filtered manifest, and hashes are frozen before price evaluation. Duplicate/malformed/missing-year rows stand aside or fail closed.
- Regime envelope: prior completed SPY session has fully warmed HV20 and 60-session return; annualized HV20 is at most 30% and absolute trailing 60-session return is at most 12%. High-volatility, strongly trending, under-warmed, missing, or non-finite states stand aside.
- Entry trigger: official 2:00 p.m. ET Beige Book release on a completed SPY session; enter conceptually at the next completed regular-session open. No release-day or future range is a selector.
- Exit / management: underlying discovery measures the maximum high divided by minimum low minus one over five completed sessions including entry; conceptual exit is fifth-session close. A later option-stage charter would freeze profit/loss exits, time stop, and liquidity rules separately. No roll, overlap, average-down, or same-session re-entry.
- Control design: one prior-only non-event SPY window per release, selected only from pre-entry fields. Control must be within 756 sessions, share the exact neutral/non-stress regime, have annualized HV20 within 0.08 and trailing 60-session return within 0.08, lie outside +/-5 sessions of every source-covered Beige Book release, have its full five-session outcome complete before the release, and not overlap another control or event window. Deterministic tie-breaks are normalized feature distance, shortest session distance, then earliest date. No reuse, substitution after failure, or outcome-visible matching.
- Partition: chronological 60% train / sealed 40% holdout by frozen eligible release blueprint. Holdout identities may be hashed; holdout event/control ranges and option outcomes remain unread.
- Option structure: conditional future one-lot 18–24 DTE $2-wide-per-side iron condor only after underlying advancement and a separate option-stage charter. Zero option marks in this wake.
- Intended Greeks: positive theta, short vega, and bounded short gamma/range exposure.
- Dangerous unintended Greeks: gap loss, negative gamma, volatility expansion, skew/term mismatch, four-leg spread friction, pin/assignment risk, and loss asymmetry if strikes/credits are poor.
- Capital fit: `sleeve_usd=3000`; future structural `capital_fit_usd=200`; frictionless width-bound one-lot `max_loss_usd=200` before credit and closing friction; `max_lots=1`; one global scheduled-macro risk unit and no overlapping candidate exposure. These are planning bounds, not observed credit or L1 evidence.
- Evidence / falsifier: official prior-known archive dates plus official calendar time corroboration, split/dividend-adjusted SPY OHLC, train-only discovery, 20-bps hurdle, prior-only matched controls, release-year-block uncertainty, absolute range-tail, density, chronology, match-quality, and strict-JSON gates. Underlying-only discovery cannot earn L1.
- Confidence: before run `F0_MECHANISM / L0`; after run either `F1_TRAIN / L0` or closed at F0.
- Stand-aside rule: malformed/duplicate/missing official date, calendar time conflict on overlapping rows, release not on a SPY session, neutral/non-stress regime absent, insufficient warmup, missing/non-finite prices, no frozen prior-only control, overlap, failed train gate, any holdout outcome read, future max loss above $200, or another scheduled-macro unit open.

## Freedom / anti-thrash judgment

The CPI context seed is superseded for this wake because direct BLS archive/schedule retrieval is HTTP 403 from the current environment and the web-search backend is unconfigured; that blocks an official timestamp-frozen CPI claim. The Federal Reserve Beige Book archive and calendar JSON are directly accessible, official, hashable, and define a materially different range/volatility mechanism rather than retuning the closed FOMC directional family. This is the smallest current experiment that can change a strategy decision while honoring the direct-to-paper candidate funnel. Freedom remains intact: the choice is evidence-driven, not a symbol/structure allowlist.

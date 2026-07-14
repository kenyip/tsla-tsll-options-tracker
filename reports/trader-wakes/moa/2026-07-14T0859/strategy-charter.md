# Strategy decision charter — 2026-07-14T0859 executor

PHASE: BUILD / research only
SLEEVE_USD: 3000

ECONOMIC EDGE MECHANISM: Persistent index-option insurance demand can make observed VIX exceed subsequent SPY realized volatility; the frozen high same-close VIX/RV20 ratio in a positive SPY trend was proposed as a selector for bounded bullish carry.

CANDIDATE/FAMILY SCOPE: Frozen candidate `SPY_VRP_PCS_VIX_RV_21D_V1` in canonical family `SPY_VRP_VIX_RV_21D`: same-close VIX/RV20 >=1.25, close above fully warmed SMA200, non-overlapping 21-session outcomes, outcome-independent positive-trend low-ratio controls, and only conditionally a one-lot 21-DTE approximately 0.20-delta $1-wide PCS. No threshold, timing, DTE, width, symbol, control-tolerance, or management mutation.

CURRENT FUNNEL: `F0_MECHANISM`.

PREDECLARED FALSIFIER: Preserve the integrated frozen gates. Close the family if any assessment has fewer than 10 non-overlapping treated episodes, treated mean below 1 vol point, treated positive frequency below 60%, fewer than 8 outcome-independent matched controls, or matched treated-minus-control mean <=0; also close if pooled treated count <45, pooled matched count <24, either one-sided 95% circular-block-bootstrap lower bound <=0, any chronology/overlap/integrity counter is nonzero, or the option-pricing branch is reached after mechanism failure. The current integrated runner and regenerated artifact must agree on source hashes and all result counters; otherwise the evidence blocker remains open.

EXACT DECISION TO CLOSE: `BLOCKER_REMOVED_AND_RETESTED`, with retest decision forced to exactly `STRATEGY_ADVANCED` or `FAMILY_CLOSED`. This wake does not authorize a successor mechanism. If the corrected reproducible run closes the family, preserve the burst stop and use `DIMINISHING_RETURNS` as the sole next seed rather than buying another F0 screen.

TRADE-SHAPE BOUNDARY: structure=`put_credit_spread`; `capital_fit_usd=100`; one-lot `max_loss_usd=100` structural $1-wide upper bound only; `max_lots=1`. These fields are not a fill, PnL result, capital seat, F1 evidence, or paper authority.

CHOICE RATIONALE: The latest independent review found the prior claim-bearing 53-treated/35-control artifact irreproducible from integrated code, with 33/35 matched rows having same-fold, half-open control-treated outcome-window overlaps and three assessment-boundary crossings. This claim-invalidating gate supersedes the advisory post-VRP search-design NEXT. Orientation requires no successor BUILD while the evidence gate is open, and the 18-wake no-advance streak independently requires burst stop.

# Strategy decision charter — 2026-07-15T0024

PHASE: BUILD / L0 research only
SLEEVE_USD: 3000
LOOP: train-only paired-dislocation study; no option pricing and no holdout inspection

ECONOMIC EDGE MECHANISM: A path-dependent five-session TSLL tracking shortfall versus twice TSLA's five-session return may represent transient leveraged-ETF rebalance/noise dislocation rather than a generic market pullback. When TSLA remains above its fully warmed 100-session moving average and has not fallen more than 5% over the feature window, an unusually negative TSLL-minus-2x-TSLA residual may mean-revert over the next five sessions. A later one-lot bull-call debit spread is only a defined-risk expression if the underlying mechanism survives.

CANDIDATE/FAMILY SCOPE: `TSLL_RELATIVE_DISLOCATION_BULL_CALL_14D_V1` / `TSLL_TSLA_5D_TRACKING_SHORTFALL_REBOUND`: TSLL five-session residual `r_TSLL - 2*r_TSLA <= -4%`; TSLA close above prior-completed SMA100; TSLA five-session return >= -5%; next-session entry; five-session hold; non-overlapping treated episodes; outcome-independent neutral-residual controls (`-1%..+1%`) drawn only from earlier dates and matched without replacement on TSLA five-session return, trend distance, and calendar proximity. Data begins at TSLL availability. No nearby threshold, horizon, structure, or symbol grid is authorized in this wake.

FUNNEL: `F0_MECHANISM`; target movement is `F0_MECHANISM -> F1_TRAIN` only. The chronological final 40% is reserved and its outcomes must remain unread.

PREDECLARED FALSIFIER: Close the exact family if the first 60% train partition has fewer than 20 valid matched, non-overlapping pairs; any feature/entry chronology, pair-overlap, match-with-replacement, or residual-group violation; non-positive TSLL treated mean after a labeled 20-bps underlying round-trip sensitivity; non-positive treated-minus-control mean; or a non-positive one-sided 90% circular-block-bootstrap lower bound for paired excess. Matching also fails closed if any control is more than 63 trading sessions from its treated episode, has absolute TSLA five-session-return distance above 5 percentage points, or absolute trend-distance mismatch above 15 percentage points.

EXACT DECISION THIS WAKE CLOSES: Determine whether the frozen candidate advances to F1 under the discovery bar. All falsifier checks pass => `STRATEGY_ADVANCED`; otherwise => `FAMILY_CLOSED` with the dominant failure recorded and unchanged reruns quarantined.

TRADE-SHAPED CONTEXT: planned structure `bull_call_debit_spread`; `capital_fit_usd=100`, one-lot `max_loss_usd=100`, `max_lots=1`, using the structural upper bound of a future $1-wide debit vertical before closing friction. This is context only, not an observed/simulated loss or capital seat.

VALIDITY / AUTHORITY: split/dividend-adjusted historical underlying closes; no option marks, option costs, fills, observed-chain claim, L1, registry, paper, shadow, arm, broker, or live authority. The family is materially distinct from closed generic daily PCS pullback families because selection is a TSLL-vs-TSLA tracking residual, controls are relative-dislocation placebos, and the planned structure is a debit vertical rather than short-premium rescue.

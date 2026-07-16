# Search-design reassessment — 2026-07-15T1912

Status: complete; prior burst stop honored; one successor epoch opened and exercised once.
Phase: BUILD / L0 research only
Sleeve: $3,000
Authority: research/paper-safe only; no broker, paper intent, L1, shadow, arm, or live authority.

## Why reassessment was mandatory

The prior active epoch (`2026-07-15-fixed-design-discovery`) reached three completed wakes without `STRATEGY_ADVANCED`:

1. `MULTINAME_BREAKOUT_BULL_CALL_30D_V1` — `FAMILY_CLOSED`; structural bull-call pricing had no dual-cost after-cost edge and adverse loss quality.
2. `MULTINAME_POST_SHOCK_RANGE_COMPRESSION_IRON_FLY_30D_V1` — `FAMILY_CLOSED`; the train range-compression/pin gates failed.
3. `MULTINAME_POST_EARNINGS_SIGNED_CONTINUATION_DEBIT_V1` — `FAMILY_CLOSED`; positive median did not survive absolute or paired-mean expectancy gates.

The shared failure was not a lack of generated candidates. Mean/median/pin effects were leaving adverse tails that are incompatible with a one-lot $3,000 sleeve, and gross-leg option costs amplified weak structural expression. Running another nearby matched-control mean study would have been unchanged volume.

## Successor search-design decision

Open `2026-07-15-tail-hazard-discovery` around a materially different evidence class: make the event a direct downside-barrier breach and use a specificity negative control before any option pricing. The first mechanism was a recent-downside-shock stand-aside policy inside a long-term uptrend:

- candidate: `MULTINAME_NO_RECENT_DOWNSHOCK_PCS_21D_V1`
- forecast: ten-session non-collapse, not mean continuation
- mechanism: downside volatility clustering; avoid new bullish short-gamma exposure for five completed sessions after a >=3% close loss
- planned expression: one-lot PCS using nearest listed 18-24 DTE expiry; sell a 0.18-0.25 delta put, buy the same-expiry put $2 lower, require >=$0.30 credit, positive bids, two-leg NBBO width <=$0.20, and a five-session earnings blackout
- structural capital bound: `capital_fit_usd=200`, `one_lot_max_loss_usd=200`, `max_lots=1`
- evidence: split/dividend-adjusted close-only F0 train study; zero option pricing
- primary falsifier: <=10% eligible 5% close-bar breach rate, >=5pp edge over recent-shock episodes, positive 90% circular-block-bootstrap lower bound, milder worst-decile path loss, positive 20-bps-sensitivity terminal mean, and a larger edge than a stale six-to-ten-session shock placebo
- holdout: final date-disjoint partition remains outcome-unread

This route is valid despite the blocked observed-option archive because it makes no observed-option or L1 claim. It does not reopen an unchanged closed family.

## Exercised retest

Artifact: `reports/trader-wakes/moa/2026-07-15T1912/downside-shock-stand-aside-train.json`

Frozen history:

- panel: SPY plus AAPL, MU, AMD, SMCI, TSLA, META, GOOGL, NVDA
- dates: 2016-01-04 through 2026-07-14
- common rows: 2,646
- frozen blueprints: 1,115
- train: 703 episodes through 2022-12-02
- untouched holdout: 412 blueprints beginning 2022-12-09; identity SHA-256 `acedd4c8cb0de2e0ee90f42c512af8885e730c78eb894f0a7f4eb8b34e223665`
- train density: 548 eligible episodes and 155 recent-shock episodes across all eight symbols
- integrity violations: zero
- option-pricing calls: zero

Methodology boundaries:

- The panel is a present-day liquid mega-cap/technology set plus SMCI. It has survivorship and listing-history bias and is not a point-in-time universe.
- The 5% barrier uses daily closes only. It can miss intraday lows and cannot be read as an option mark, executable stop, or managed PCS result.
- Recent-five-session and stale-six-to-ten-session shock flags are independent and can both be true. Comparing their edges is a confounded timing-specificity diagnostic, not a mutually exclusive alternative-mechanism RCT.
- The L0 circular-block bootstrap resamples the two pooled group vectors separately rather than resampling multi-symbol dates. Residual cross-symbol/date dependence remains; the hard negative does not rely on upgrading that uncertainty method.

Train result:

- eligible 5% close-bar breach rate: 27.0073%
- recent-shock breach rate: 35.4839%
- point edge: 8.4766 percentage points
- one-sided 90% circular-block-bootstrap lower bound: 2.1356 percentage points
- eligible worst-decile minimum close return: -13.6151%
- recent-shock worst-decile minimum close return: -17.8323%
- eligible mean terminal return after labeled 20-bps sensitivity: +0.9482%
- stale-window placebo edge: 14.5722 percentage points

The mechanism had a real relative hazard separation on train, but it failed both predeclared decision-critical gates:

1. absolute eligible breach rate was 27.0%, far above the 10% capital-protection limit;
2. the stale six-to-ten-session placebo edge (14.57pp) exceeded the current five-session edge (8.48pp), so the proposed near-term clustering mechanism lacked timing specificity.

## Closed decision

`FAMILY_CLOSED` for the exact family key:

`noncollapse|recent_5d_downshock_exclusion|spy_and_symbol_sma100_uptrend|positive_60d_momentum|10_session_close_barrier_5pct|pcs_21d_2wide_planned`

Dominant failure mechanism: relative risk separation did not produce low enough absolute downside hazard for one-lot bullish short gamma, and a stale placebo separated better than the claimed recent-shock mechanism. The positive mean return, positive bootstrap edge, and milder tail do not rescue the candidate.

Quarantine: do not rerun this family with nearby 2%/4% shock thresholds, 3/7-session windows, or a looser breach limit. Reopening requires a new economic mechanism or evidence class, not threshold drift. The untouched holdout remains sealed because F1 was not earned.

## Epoch state after retest

- active epoch: `2026-07-15-tail-hazard-discovery`
- completed wakes in epoch: 1
- consecutive no-advance wakes: 1
- `strategy_pivot_required`: false
- `burst_stop_required`: false
- no living capital-seat leader
- strategy progress: none; search information: decisive exact-family falsification plus a reusable downside-hazard/specificity lab

## Exactly one next seed

Open a new family key, `LOW_DOWNSIDE_SEMIVARIANCE_ETF_BARRIER_HAZARD_F0`, rather than relabeling or retuning the closed plain-HV/mean-return family. Freeze a cross-sectional **downside-semivariance** rank (left-tail second moment, not plain realized volatility) on lower-volatility liquid ETFs (SPY, QQQ, IWM, XLF, XLE, XLK, XLI, XLV) before reading outcomes. The named ETF population asks whether lower single-name event concentration can satisfy absolute non-collapse after the present-day mega-cap panel failed at 27% eligible breach frequency. Test ten-session 5% close-barrier survival and worst-decile loss against the high-downside-semivariance rank with multi-symbol date-blocked uncertainty and an untouched holdout. Stop before option pricing unless the absolute <=10% breach gate passes; mean return is diagnostic, not the primary endpoint.

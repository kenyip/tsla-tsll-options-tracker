# Merged NEXT seed — 2026-07-15T2045

ONE NEXT (challenger accepts executor; no rewrite of economic experiment):

`TAIL_HAZARD_EPOCH_BURST_STOP_REASSESSMENT`

## Why this seed

Active epoch `2026-07-15-tail-hazard-discovery` (`configs/search_epoch.json`, started `2026-07-15T1912`) now has **three** consecutive completed wakes without `STRATEGY_ADVANCED`:

1. `2026-07-15T1912` — `MULTINAME_NO_RECENT_DOWNSHOCK_PCS_21D_V1` → `FAMILY_CLOSED` (absolute hazard gate + stale placebo)
2. `2026-07-15T2007` — `LOW_DOWNSIDE_SEMIVARIANCE_ETF_PCS_21D_V1` → `FAMILY_CLOSED` (mechanism non-specificity vs plain HV)
3. `2026-07-15T2045` — `SPY_INDEX_THETA_CARRY_PCS_21D_V1` → `FAMILY_CLOSED` after comparator repair (no non-vacuous bearish support under frozen geometry)

Doctrine: after three consecutive completed epoch wakes without advancement, **stop the burst** and reassess search design/data rather than buying more strategy volume.

## What the reassessment wake must do

- Write a dated search-design reassessment under `docs/` (or epoch-linked path) covering:
  - the three closed mechanisms and dominant failure modes above
  - which evidence classes remain informative vs thrash-prone on current data
  - whether the epoch lane (direct downside-tail / stand-aside → defined-risk income expression) should close, pivot, or reopen only under a named new evidence class
  - proxy vs observed-option boundaries; sealed holdouts that must stay unread
- Update `configs/search_epoch.json` status / successor epoch fields only after the written reassessment (finalizer/integration path), not mid-critique
- Do **not** open another strategy experiment in the same reassessment wake unless the reassessment explicitly authorizes one new predeclared family with a complete Layered Edge Stack — default is **no new experiment volume**
- Do **not** retune SPY 21D 0.20Δ $2-wide $0.30-credit 10-session regime-gated PCS on the same Black-Scholes train panel
- Do **not** launder absolute dual-cost proxy positivity from `SPY_INDEX_THETA_CARRY_PCS_21D_V1` into a capital seat or F1 claim
- Preserve quarantines: recent-downshock; downside-semivariance + nearby rank retunes; SPY index theta-carry exact family + nearby same-panel retunes; other closed families already on the scoreboard
- Keep sealed: holdout `72a6d184…` (semivariance experiment); SPY theta-carry holdout option outcomes 2022-07-12..2026-07-13

## Hard stops

No registry promotion, paper force, shadow, arm, broker login, funding, or live action from this seed.

## Authority reminder

Living quality leader remains **none**. Proxy-only option marks cannot earn L1.
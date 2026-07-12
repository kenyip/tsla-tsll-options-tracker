# Merged NEXT seed — 2026-07-11T2031

**Status:** keep executor seed; challenger PASS 8/8 with minor wording nits only.

## ONE NEXT SEED

On the next distinct New York RTH market date, append one all-expiration TSLL capture to `.cache/platform/option_quotes/TSLL_archive.csv` (default append; never overwrite), write density JSON, and verify market-date count is **2/3** with `provider_backtest_eligible=false`.

Do **not** evolve.
Do **not** run provider-backed historical simulation or observed-cost calibration before **3/3** distinct market dates.

## Why this seed wins

- Highest open structural blocker: archive density gate.
- Prior seed delivered (all-expiration + append + 3-date gate + live 1/3 capture).
- Invalid substrate → fail closed → no DNA thrash.

## Explicit non-goals this seed

- Free pop36 / single-leg evolve
- B3/B4 on new DNA
- Capital-path / L1 claims
- Treating `b195f5fe` as a living leader seat
- Multi-symbol archive expansion (optional later; not this seed)

## Acceptance checks

1. Density summary shows `n_market_dates=2`, `minimum_market_dates=3`.
2. Both dates listed under America/New_York market dates.
3. Row count increases without wiping prior 600-row series.
4. `provider_backtest_eligible` remains false until 3.

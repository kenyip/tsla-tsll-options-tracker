# v6.2 - Exact Expiration + Strike Output

Now shows concrete expiration date and strike price (not just DTE and delta).

**Example for May 12 2026 ($445, IV Rank 13, +11.2% 14d):**

**TSLA**: SELL 410 Put, June 12 2026 (30 DTE), 0.25 delta, 55% target
**TSLL**: SELL 14 Put, June 6 2026 (24 DTE), 0.19 delta, 50% target + core shares

Strikes are estimated using standard delta-to-OTM mapping for the given IV and DTE.
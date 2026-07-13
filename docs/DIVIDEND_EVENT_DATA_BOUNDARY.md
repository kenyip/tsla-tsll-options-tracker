# Dividend announcement-time data boundary

**Decision date:** 2026-07-12 PDT
**Scope:** BUILD/L0 research only; short-call early-assignment guard for diagonal and bull-call debit simulators.

## Decision

Use an **archived Nasdaq dividend-history snapshot** only where the response supplies a non-empty contiguous recent run of cash-dividend rows with both `declarationDate` and `exOrEffDate`. Map `declarationDate` directly to `DividendEvent.known_at`; never infer it from ex-date, record date, payment date, or capture time.

The provider is fail-closed:

- unsupported symbol/status → no archive;
- empty response with “never paid or pending” ambiguity → no coverage, not `[]`;
- missing latest declaration date, malformed amount/date, non-cash/non-USD row, declaration after ex-date, or declaration after capture → reject;
- old rows with `N/A` declaration dates truncate all older coverage rather than being backfilled;
- symbol mismatch or an `as_of` outside the archived interval returns `None` (missing coverage); the lower bound is the earliest retained `known_at`, so the first announced pre-ex event is servable;
- a covered query may return `[]` only when the archive genuinely spans that `as_of` and no visible event qualifies.

Implementation:

- `trader_platform/research/dividend_event_archive.py`
- `scripts/dividend_event_observations.py`
- `tests/test_dividend_event_archive.py`
- `trader_platform/research/dividend_event_crosscheck.py`
- `scripts/dividend_event_crosscheck.py`
- `tests/test_dividend_event_crosscheck.py`

## Live source inventory

The inventory was performed from the repository host at 2026-07-12 18:36–18:42 PDT. General `web_search` was unavailable because the Hermes web backend was not configured, so the executor queried the source endpoints/pages directly with `curl` and exercised the implemented capture CLI.

| Source | Tested result | Announcement-time suitability |
|---|---|---|
| Nasdaq public dividend-history endpoint (`https://api.nasdaq.com/api/quote/<SYMBOL>/dividends?assetclass=stocks`) | AAPL returned 82 rows with `declarationDate`, `exOrEffDate`, amount, record date and payment date; MU returned 20 such rows; AAL returned 23 | **Usable with restrictions.** No auth/payment was required in this run. Archive exact response-derived fields; old `N/A` declaration rows truncate coverage. Endpoint is public but undocumented/fragile and does not cover every listing. |
| Nasdaq AAPL dividend-history page | Page describes data as aggregated, says history is not split-adjusted, and warns preferred securities may appear | **Caveat.** This provider is only an assignment-event timing input. It is not adjusted-return, option-surface, contract, or edge evidence. Symbol/security-class contamination remains a source limitation. |
| Nasdaq empty/unsupported cases | SMCI returned an ambiguous “never provided or pending” empty history; F said non-Nasdaq history unavailable; TSLL returned source status 400 / symbol unavailable | **Blocked.** These are `None` coverage, never covered/no-event `[]`. The source cannot unlock SMCI diagonal required mode or broad-universe use. |
| SEC Company Facts (`data.sec.gov/api/xbrl/companyfacts`) | AAPL exposes aggregate dividend facts such as `CommonStockDividendsPerShareDeclared`, but the tested response does not provide a normalized per-event declaration/ex-date stream | **Not implemented.** Aggregate filing facts do not satisfy the event-level `known_at` contract. Filing extraction from 8-K/press releases would need a separate provenance parser and completeness proof. |
| yfinance 1.5.1 | `Ticker.dividends` / `actions` return ex-date-indexed amounts; `calendar` exposes current dividend/ex-dividend dates but not historical declaration timestamps | **Rejected for `known_at`.** Ex-date history cannot be relabeled as announcement time. |
| Apple Newsroom earnings releases + canonical Newsroom sitemap | Forty quarterly results releases from 2016-07-26 through 2026-04-30 each explicitly state publication date, cash dividend per share, Apple common-stock identity, record date, and payment date | **Bounded partial corroboration for AAPL.** All 40 issuer releases match the 40 normalized Nasdaq events in that publication-date window on `known_at` and amount, with zero conflicts or unmatched dates. This qualifies only those fields plus security identity for that interval; issuer record date is not relabeled as ex-date. |
| StockAnalysis AAPL dividend page, named source S&P Global Market Intelligence | The no-auth page explicitly labels `Ex-Dividend Date`, source, cash amount, record date, and pay date. The reproducible table exposes only the latest 20 events (2021-08-06 through 2026-05-11); all 20 ex-dates match the bounded Nasdaq target, but the first 20 of 40 target events are absent. | **Rejected for full bounded `ex_date` qualification.** Exact 20/20 intersection agreement is not 40-event completeness; `ex_date` remains unqualified. Parser and gate fail closed on missing source identity, missing explicit header, malformed chronology, duplicate dates, or any target gap. |
| Macrotrends, CompaniesMarketCap, Investing.com, DividendMax, Yahoo Finance | Bounded direct-page probes returned either no explicit event-level ex-date field/table, HTTP 403, very sparse rendered dates, or an unstable/ambiguous payload rather than a reproducible 40-event explicitly labeled stream. | **Rejected in this inventory.** No field was relabeled and no credential, paid tier, or anti-bot bypass was attempted. |

No paid API, credential, broker session, or spend was used.

## Evidence

- `.cache/platform/dividend_event_archive_lab_2026-07-12T1835.json`: AAPL live snapshot normalized to 53 usable rows from 82 source rows; honest announcement-time coverage begins 2013-01-23 and older missing-declaration history is truncated.
- `.cache/platform/dividend_events/AAPL_nasdaq.json`: local normalized archive; ignored runtime data, not a tracked raw provider dump.
- `.cache/platform/dividend_event_provider_sim_smoke_2026-07-12T1835.json`: required-mode AAPL integration; diagonal completed with zero entries, bull-call completed with 21 proxy trades, both with `corporate_action_mode=required`. This proves provider wiring only.
- `.cache/platform/dividend_event_crosscheck_2026-07-12T2237.json`: normalized Apple issuer-release evidence and exact bounded comparison; 40/40 issuer and Nasdaq events match from 2016-07-26 through 2026-04-30, with 13 earlier Nasdaq events explicitly outside issuer-sitemap coverage and `ex_date` unqualified.
- `.cache/platform/dividend_exdate_crosscheck_2026-07-12T2315.json`: live explicit-ex-date inventory result; StockAnalysis/S&P supplied 20/40 bounded rows, all 20 matched, 20 earlier target ex-dates were absent, and the decision is `CLOSE_EX_DATE_ROUTE_INSUFFICIENT_COVERAGE`.
- Live SMCI capture exited non-zero with `Nasdaq dividend coverage ambiguous`; no archive was written.

## Claim boundary

This capability does **not** create a strategy candidate, capital seat, B3/B4 pass, paper sample, or L1 evidence. The AAPL issuer comparison removes common-stock identity ambiguity only for the matched 2016-07-26 through 2026-04-30 declaration window. The bounded independent ex-date inventory found exact agreement only on the latest 20 of those 40 events, so every archived `ex_date` remains unqualified for the complete interval; issuer record date is not ex-date evidence. The 13 earlier normalized events remain outside issuer coverage. The simulators still use Black-Scholes proxy option marks and lack observed historical option surfaces. Nasdaq amounts remain split-unadjusted, so long-history amount/spot comparisons and assignment counts are not calibrated evidence. For any trade-shaped research result, structure/capital fields remain mandatory; this wake created no trade-shaped candidate and therefore no new `capital_fit_usd`, one-lot `max_loss_usd`, or `max_lots` claim.

## Next data boundary

Do not broaden the provider by treating empty histories as no-dividend coverage, by treating issuer record dates as ex-dates, by promoting 20/20 intersection agreement to 40-event completeness, or by extending the AAPL partial qualification outside its exact matched interval. The narrow no-auth AAPL ex-date provenance route is closed at bounded partial L0 for this cycle. Reopen only with a genuinely new independently sourced, explicitly labeled stream that covers the missing 2016-08-04 through 2021-05-07 target dates; do not keep inventorying equivalent aggregators. Redirect BUILD work to an open historical-underlying or simulator-capability route. Strategy discovery remains free.

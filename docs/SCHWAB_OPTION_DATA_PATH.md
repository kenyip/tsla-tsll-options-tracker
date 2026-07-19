# Schwab developer API — option data path

**Ken authorization (2026-07-18/19):** Schwab developer APIs **may** be used as a **research market-data** path for listed option quotes when building/evaluating strategies.

**Still forbidden without separate explicit arm:**

- Live order placement  
- Paper promotion to live  
- Broker session for trading  
- Funding / account mutation  
- Using market data credentials as trading authority  

---

## Why this exists

Proxy (underlying + Black-Scholes) is enough to **search and reject** strategies.  
Observed bid/ask paths are needed before claiming **L1 / capital-seat after-cost edge**.

Schwab is an allowed way to obtain real option surfaces **if** Ken configures app credentials. It does not replace proxy discovery and does not auto-grant readiness.

---

## What we need from Schwab (minimum product)

For strategy confirmation (not live trading):

| Field | Required |
|---|---|
| Underlying symbol | yes |
| Observation timestamp (timezone-aware) | yes |
| Expiration | yes |
| Call/put | yes |
| Strike | yes |
| Bid / ask | yes (prefer NBBO or defensible quote) |
| Contract symbol / multiplier | preferred |
| Implied vol | optional |

Historical depth depends on what Schwab’s market-data product returns for the app’s entitlements. If only **current** chains are available, use Schwab the same way as yfinance: **forward archive**, not fake multi-year history.

---

## Local integration contract

Adapter module: `trader_platform/research/schwab_option_quotes.py`

- Maps Schwab chain rows → `OptionQuoteObservation` (same boundary as yfinance/CSV archives).  
- **Fail closed** when credentials/token are missing — no silent synthetic fill.  
- Writes only under ignored cache paths (e.g. `.cache/platform/option_quotes/`).  
- Sets `source=schwab_trader_api` and `is_observed=true` only for real API rows.  
- Never places orders. Never opens a trading session for BUY/SELL.

Normalized rows remain consumable by:

- `option_quote_observations.py`  
- `observed_quote_coverage.py`  
- L1 `evidence_policy.assess_l1_evidence`

---

## Credentials (local only — never commit)

Expected environment (names only; values stay in local secrets):

| Variable | Role |
|---|---|
| `SCHWAB_APP_KEY` | Developer app key / client id |
| `SCHWAB_APP_SECRET` | Developer app secret |
| `SCHWAB_TOKEN_PATH` | Optional path to OAuth token JSON (refresh + access) |
| `SCHWAB_REFRESH_TOKEN` | Optional refresh token if not using token file |
| `SCHWAB_API_BASE` | Optional override; default production Trader API host |

Setup outline for Ken (manual, browser OAuth once):

1. Create a Schwab developer app with market-data scope appropriate for option chains.  
2. Complete OAuth; store refresh token in a **local** file referenced by `SCHWAB_TOKEN_PATH` (mode 600).  
3. Confirm **no trading scopes** are required for quote research; do not enable order placement from this research path.  
4. Tell Jarvis/Trader “Schwab token ready” so a **read-only** chain snapshot can be tested.

Until credentials exist, adapters return a clear `credentials_missing` status and proxy research continues.

---

## Decision options (updated)

| Choice | Meaning |
|---|---|
| `PROXY_ONLY` (default until token exists) | Keep L0 proxy discovery; no Schwab calls |
| `SCHWAB_FORWARD_CAPTURE` | Snapshot chains via Schwab into the observed archive |
| `SCHWAB_HISTORICAL_IF_ENTITLED` | If the app entitlement includes history, ingest lawful history into the immutable archive |
| `SUPPLY_EXPORT` | Ken drops a licensed CSV; no API login needed |

---

## Safety

- Research profile only.  
- No `place_*` live.  
- No automatic densify re-arm from successful quote capture.  
- Successful quote plumbing is **capability**, not strategy advancement.

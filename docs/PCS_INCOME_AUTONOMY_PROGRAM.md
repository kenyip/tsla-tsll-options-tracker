# PCS Income Autonomy Program

**Status:** active research program (Ken pin 2026-07-18/19)  
**Authority:** research / paper only — no shadow, broker, arm, or live from this program  
**Option marks default:** Black-Scholes proxy on historical underlyings (L0). Observed marks optional via archive or Schwab (see [SCHWAB_OPTION_DATA_PATH.md](SCHWAB_OPTION_DATA_PATH.md)).

---

## Plain-language goal

Build a **defined-risk credit-spread income sleeve** that can eventually decide for itself:

1. **When** market conditions allow selling premium  
2. **What** put/call credit spread (or stand aside)  
3. **How** to take profits on favorable swings and cut losers  
4. **Never** blow past the $3k sleeve risk envelope  

This program does **not** wait on perfect historical option tapes to keep searching. Proxy evaluation is enough to **find and kill** ideas. Real quotes (Schwab / archive) are for **later confirmation** before a capital seat.

---

## Preferred stack (soft prior, not allowlist)

| Layer | Default |
|---|---|
| Forecast | Mild bull / non-collapse; stand aside pure bear |
| Structure | Put credit spread first; CCS/IC when regime says so |
| Income | Sell time (theta); harvest early when mark moves your way |
| Exits | Profit target (~50% of credit), DTE stop, defined-loss stop, regime flip |
| Capital | 1 lot; max loss ≤ $300; window DD target ≤ $75 for L1 |
| Autonomy | Scout → filters → STAND_ASIDE or OPEN_PCS → manage → learn |

Stand-aside is success.

---

## Evidence routes (do not confuse them)

| Route | Use now | Cannot claim |
|---|---|---|
| Underlying + BS proxy PCS sim | Find / falsify DNA, train/holdout partitions | L1 / “observed after-cost income” |
| Forward yfinance chain archive | Grow observed density day by day | Multi-year backfill |
| Schwab developer market data | Optional historical/current bid-ask when credentials exist | Live order authority |
| Paper autonomy loop | Lifecycle once a living candidate exists | Live arm |

Proxy survivors remain **L0 discovery** until observed coverage earns L1 under `evidence_policy`.

---

## Working loop (keep building)

```text
1. Freeze one Layered Edge Stack (mechanism + entry + management + risk)
2. Train-only dual-cost proxy screen (5% slip + $0.01/leg half-spread)
3. If dual-cost pass on non-vacuous n → seal holdout identities; no peek on fail
4. If holdout pass → paper plan / watcher (still research authority)
5. Only then consider observed-quote confirmation (archive or Schwab)
6. Capital seat / paper path requires capital_seat_bar + authority gates
```

Cheap multi-candidate screens are allowed. One wake still closes with **one** claim-bearing decision or an honest close.

---

## Capital fit notes ($3k sleeve)

- Prefer underlyings whose **listed strike increment × width** keeps 1-lot max loss ≤ $300 after credit.  
- SPY-class $5 increments often force max loss near $500 for a 1-wide vertical — poor fit unless credit is huge or budget is raised deliberately.  
- Mid/low priced liquid names ($0.50–$1 increments) fit the sleeve more naturally.

---

## Quarantine / do-not

- Do not reopen exact closed families by threshold polish only.  
- Do not treat plumbing, densify wakes, or adapter work as strategy advancement.  
- Do not promote proxy-only wins to L1.  
- Do not place live/broker orders from this program.

---

## Latest pilot scoreboard (2026-07-19)

Fixed management across pilots: **21-DTE PCS, PT 50%, DTE stop 7, stand-aside bear, dual cost (5% slip + $0.01/leg)**.

| Pilot | Entry mechanism | Train dual-cost | Sealed holdout | Artifact |
|---|---|---|---|---|
| **V1** | Mild 14d pullback + trend | PLTR, SMCI pass | **Fail** | `pcs_income_pilot_LATEST.json` |
| **V2** | Monday + trend / not extended | PLTR pass | **Fail** (slip) | `pcs_income_monday_trend_LATEST.json` |
| **V3** | HV compression (hv20/hv60≤0.85) | PLTR, AAPL pass | **Fail** | `pcs_income_hv_compression_LATEST.json` |
| **V4** | Soft post-shock stabilize | XOM, IWM pass | **Fail** (IWM +PnL but n=5 &lt; 8; XOM slip−) | `pcs_income_post_shock_LATEST.json` |

**Living capital seat / L1:** still **no**.

**Pattern:** entry filters can beat “sell every day” on train for 1–2 names; **untouched holdout under adverse slip does not transfer**. This is four consecutive holdout failures on adjacent PCS entry mining — treat as a **diminishing-returns checkpoint**, not an invitation to polish thresholds.

### Spine pivot (2026-07-19) — implemented

Primary architecture: [TRADER_SPINE_ARCHITECTURE.md](TRADER_SPINE_ARCHITECTURE.md)

| Piece | Path |
|---|---|
| StrategySpec | `trader_platform/research/strategy_spec.py` |
| evaluate_proxy | `trader_platform/research/evaluate_proxy.py` |
| Regime-router income spec | `configs/strategy_specs/regime_router_income_v1.json` |
| CLI | `scripts/evaluate_strategy_spec.py` |

```bash
.venv/bin/python scripts/evaluate_strategy_spec.py \
  --spec configs/strategy_specs/regime_router_income_v1.json \
  --out .cache/platform/spine/regime_router_income_v1_LATEST.json

.venv/bin/python scripts/evaluate_strategy_spec.py \
  --spec configs/strategy_specs/regime_router_income_45d_v1.json \
  --out .cache/platform/spine/regime_router_income_45d_v1_LATEST.json

.venv/bin/python scripts/evaluate_strategy_spec.py \
  --spec configs/strategy_specs/pcs_bull_neutral_income_45d_v1.json \
  --out .cache/platform/spine/pcs_bull_neutral_income_45d_v1_LATEST.json
```

**Spine scoreboard (2026-07-19):** all three regime-first specs `FAMILY_CLOSED` (0 train dual-cost survivors). Living seats: 0. See `.cache/platform/spine/scoreboard_2026-07-19.json`.

Do **not** retune V1–V4 entry bounds or closed router DTE/PCS-only knobs to chase holdout. New ideas = new StrategySpec JSON with a **materially different forecast class**.

## Commands

```bash
# Standing PCS income pilot (proxy L0 train screen)
.venv/bin/python scripts/pcs_income_pilot_lab.py \
  --out .cache/platform/pcs_income_pilot_LATEST.json

# Unit tests
.venv/bin/python -m pytest -q tests/test_pcs_income_pilot_lab.py tests/test_schwab_option_quotes.py
```

---

## Relation to Strategy Engine / densify

- Strategy Engine remains the pre-BUILD filter when autonomous densify is armed.  
- This program may run **explicit Ken-directed proxy pilots** even while densify is paused.  
- Re-arm continuous densify only after a clean `NEXT_SURVIVOR` or an explicit Ken re-arm — not after tooling commits alone.

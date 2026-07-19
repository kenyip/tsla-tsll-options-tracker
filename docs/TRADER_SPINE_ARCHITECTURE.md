# Trader Spine Architecture (Desk B)

**Pinned:** 2026-07-19  
**Status:** Detail — implementable spine for Desk B.  
**Start here for build doctrine:** [TRADER_BUILD.md](TRADER_BUILD.md).  
**Does not replace:** Layered Edge Doctrine, authority firewall, or legacy TSLA/TSLL desk code.  
**Supersedes as default discovery path:** ad-hoc `scripts/pcs_*_lab.py` proliferation, free MoA densify as the main progress engine, and entry-filter PCS mining without a shared evaluator.

---

## North star (Desk B)

Self-learning **research → paper → shadow → (Ken-armed) live** income engine on the isolated **$3,000 Agentic sleeve**.

Success = at least one durable, paper-testable edge **after costs** at **1-lot**, with stand-aside as a valid win.

**Build-toward pipeline** (full principles in [TRADER_NORTH_STAR.md](TRADER_NORTH_STAR.md)):

```text
signals → opportunity → structure+manage → prove → execute → learn
```

Cartesian knob grids are a **proof tool for thin DNA**, not the primary edge engine. New scores (e.g. premium/day) enter via the north-star evaluation catalog.

---

## The spine (only path to F1/F2 claims)

```text
Forecast / regime layer
  → Expression layer (PCS | CCS | IC | stand_aside)
  → StrategySpec (frozen JSON)
  → evaluate_proxy()  [dual-cost train → sealed holdout]
  → EvaluationReport (funnel stage, pass/fail, quarantine key)
  → Living registry seat only if F2+ (research park allowed at L0)
  → Opportunity watcher → paper packet → autonomy_loop
```

Optional side systems (not the main loop):

| System | Role |
|---|---|
| Strategy Discovery Engine | Cheap prefilter for batch forecasts; no authority |
| Legacy TSLA/TSLL / PMCC desk | Human desk A — separate scoreboard |
| Continuous densify / MoA | Paused until spine produces F2 survivors regularly |
| Schwab / RH quotes | Confirmation & live marks — **not** required for proxy search |

---

## Core objects

### `StrategySpec` (`trader_platform/research/strategy_spec.py`)

Frozen, serializable claim:

- identity (`candidate_id`, `family_id`)
- Layered Edge fields (forecast, mechanism, stand-aside)
- `evaluation_mode`: `single_structure` | `regime_router`
- management DNA (DTE, profit target, stops)
- entry / structure overrides
- symbols, risk envelope, discovery gates

New research ideas become **spec files**, not new lab engines.

### `evaluate_proxy()` (`trader_platform/research/evaluate_proxy.py`)

Single evaluation pipeline:

1. Load historical underlyings (proxy option marks labeled).  
2. Chronological train / sealed holdout split.  
3. Dual cost axes: 5% adverse leg slip + $0.01 half-spread/leg.  
4. Run `pcs_sim` or `regime_router_sim` per mode.  
5. Emit train pass / holdout pass / funnel stage / decision.

**Cannot** earn L1 or trading authority. Proxy-only.

### CLI

```bash
.venv/bin/python scripts/evaluate_strategy_spec.py \
  --spec configs/strategy_specs/regime_router_income_v1.json \
  --out .cache/platform/spine/regime_router_income_v1_LATEST.json
```

---

## Regime-first default (income lean)

| `router_policy` | Behavior |
|---|---|
| `router` | Bullish→PCS; bearish→CCS; neutral high-IV→IC; else stand aside |
| `pcs_non_bear` | Bullish/neutral→PCS only; bear→stand aside |
| `pcs_bull_only` | Bullish→PCS only; else stand aside |

Management (DTE, profit target, stops) lives in StrategySpec `management`. Stand-aside purity is first-class on each axis (`stand_aside_frac`).

### Spine pilots run 2026-07-19

| Spec | Decision | Living? |
|---|---|---|
| `regime_router_income_v1.json` (21D full router) | FAMILY_CLOSED | No |
| `regime_router_income_45d_v1.json` (45D full router) | FAMILY_CLOSED | No |
| `pcs_bull_neutral_income_45d_v1.json` (45D PCS non-bear) | FAMILY_CLOSED | No |
| `pcs_iv_rich_noncollapse_21d_v1.json` (IV-rich non-collapse PCS) | seed for Desk B loop | evaluate via loop |

### Operator loops (Desk B) — split by purpose

| Loop | Cadence | Purpose |
|---|---|---|
| **Discovery** (`trader-discover`) | **Tight** sim generations until F2 / stall / budget | Find & prove strategies offline |
| **Opportunity** (`trader-opportunity`) | Patient (hourly cron) | Wait for market setup → paper handoff |

```bash
# Strategy search/proof — burn CPU, not calendar time
just trader-discover
just trader-discover --max-generations 50 --max-minutes 120

# Market wait — only after living seats exist (or to confirm NO_QUALIFIED)
just trader-opportunity
just trader-paper-handoff
just trader-eval-iv-rich
```

Hermes:
- `trader-desk-b-loop` → `trader_discovery_cron.sh` every **30m** (kicks a campaign; skips if already running; up to ~90m work)
- `trader-opportunity-loop` → watch/handoff every **60m**

Scoreboard: `.cache/platform/spine/scoreboard_2026-07-19.json`.

---

## Funnel & bars (unchanged)

```text
F0_MECHANISM → F1_TRAIN → F2_UNTOUCHED_HOLDOUT → F3_ROBUST_PAPER_PLAN → F4_OBSERVED_PAPER
```

| Bar | Use |
|---|---|
| Discovery | F0→F1 / F1→F2 signals; dual-cost positive, integrity, max-loss fit |
| Capital seat (L1) | Stricter DD / density / observed marks — **not** claimed by proxy spine |

---

## Living candidates

A candidate is **living** only when:

- sealed holdout dual-cost pass under frozen DNA, **or**  
- explicitly parked as L0 research with no capital-path claim.

Ops completeness, densify wakes, and tooling are **not** living seats.

Scoreboard path: `.cache/platform/spine/living_LATEST.json` (written by evaluator when requested).

---

## Explicit non-goals of this spine

- No live orders / broker login / agentic arm  
- No holdout peeking after train fail  
- No threshold polish on quarantined families  
- No treating Schwab/RH history absence as a global freeze  

---

## Migration

| Old pattern | New pattern |
|---|---|
| New `pcs_*_lab.py` per idea | Add `configs/strategy_specs/*.json` + run CLI |
| V1–V4 income pilots | Archived results; DNA may be re-expressed as specs |
| Free densify volume | Spine evaluations only until F2 exists |
| Entry-filter mining as default | Regime/forecast specs first |

---

## Related docs

- [TRADER_PLATFORM_GOAL.md](TRADER_PLATFORM_GOAL.md)  
- [TRADER_LAYERED_EDGE_DOCTRINE.md](TRADER_LAYERED_EDGE_DOCTRINE.md)  
- [PCS_INCOME_AUTONOMY_PROGRAM.md](PCS_INCOME_AUTONOMY_PROGRAM.md)  
- [TRADER_DIRECT_TO_PAPER_WATCH_PLAN.md](TRADER_DIRECT_TO_PAPER_WATCH_PLAN.md)  
- [OPTION_QUOTE_DATA_BOUNDARY.md](OPTION_QUOTE_DATA_BOUNDARY.md)  

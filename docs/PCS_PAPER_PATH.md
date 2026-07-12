# Defined-risk multi-leg paper path ($3k Agentic sleeve)

Paper-only. Never places live. Defined-risk verticals/condors are the preferred **structure class** for the $3k sleeve (bounded max loss) — **not** a pin to TSLL or to PCS alone.

## Ranking vs plumbing (Ken pin 2026-07-10)

- **Rank** by capital / regime / cost / falsify across **multi-name multi-structure** DNA.
- **Plumbing** (`OPEN_PCS` / `OPEN_CCS` / `OPEN_IC`) is **parallel build debt**, never the reason a name is #1 paper.
- Incomplete CCS/IC OPEN → **build it**; do not force only TSLL PCS.
- Do not demote stronger mid-slip results solely because TSLL PCS was wired first.

## Better trades, not diversify-for-fear (Ken pin 2026-07-10)

- Capital / first-paper seats require **independent trade quality**, not a multi-name quota.
- **Diversify-for-fear is lazy.** If a hyp is on the capital path only as a TSLL diversifier, **remove it** (park `candidate`).
- Multi-name remains the **research** search space; re-promote only when quality beats the bar without diversifier rationale.
- Paper-first; no live / agentic / fund from this pin.

## Why defined-risk

Cash CSP / naked short premium either fails open-risk (~$750) or has **undefined** max loss on levered names (TSLL). Defined-risk **credit verticals** (put *or* call) and iron condors clear the envelope when width is small (PCS max_loss ≈ (width − credit)×100 ≈ $74–113 on top testing hyps).

## Pipeline

```text
hypothesis (DNA structure=put_credit_spread | call_credit_spread | iron_condor)
  → premium_scout.rec_provider_for_hyp
  → make_pcs_recommendation (data.build last bar + pcs_sim.pick_structure_entry)
  → OPEN_PCS | OPEN_CCS | OPEN_IC | STAND_ASIDE
  → OrderIntent(structure=…, legs=[…], max_loss_usd=…)
  → RiskGovernor (risk_amount = max_loss_usd × qty; capital_fit rejects naked TSLL)
  → PaperBroker place_limit → ledger order with legs + max_loss + tag
```

### Intent fields (required for defined-risk multi-leg)

| Field | Role |
|---|---|
| `structure` | `put_credit_spread` / `call_credit_spread` / `iron_condor` |
| `legs` | Short + long (and IC: put wing + call wing) dicts (strike, right, action, qty) |
| `max_loss_usd` | 1-lot worst case; **open_risk accounting** |
| `width`, `short_strike`, `long_strike` | Vertical geometry (IC: put wing + call strikes in legs) |
| `limit_price` / `net_credit` | Net credit per share (fill target) |
| `tag` | Durable `scout:…\|pcs|ccs|ic\|w=…\|Ks=…\|Kl=…\|ml=…` |
| `defined_risk=True` | Explicit flag |

### Risk accounting

- `OrderIntent.risk_amount()` → `max_loss_usd × qty` when set; else premium notional.
- `portfolio.max_open_risk` (750) uses risk_amount, not credit×100 alone.
- `capital_fit.reject_undefined_risk_on_levered` denies naked TSLL shorts without max_loss_usd.

### Ledger

`PaperBroker` persists multi-leg metadata on each working order. `portfolio_snapshot()` sums defined max_loss on open multi-leg paper orders (ignores `m0_stub:` smoke tags for risk dollars).

## RTH: paper-probe vs stand-aside

| Condition | Action |
|---|---|
| `bearish` + DNA `bear_dte=0` | **STAND_ASIDE** (put credit not probed — success) |
| Filters (IV, credit %, max_loss_budget) block | **STAND_ASIDE** |
| OPEN_PCS / OPEN_CCS / OPEN_IC + max_loss fits open_risk + risk allows | **Paper place** 1 lot (dry-run first on pure eval ticks if preferred) |
| Only naked levered SELL_* fire | **Deny** — never paper as “probe” |
| Open defined-risk already working for same hyp/symbol | replace/update limit; do not stack unbounded |

See also: trader skill `references/rth-eval-checklist.md`.

## Commands

```bash
# Scout (intents only)
.venv/bin/python -m trader_platform.premium_scout --symbols TSLL --json --max-intents 3

# Dry-run autonomy (propose + risk, no ledger mutate)
.venv/bin/python -m trader_platform.autonomy_loop --mode paper --once --dry-run --symbols TSLL --event rth_pcs --json

# Paper place (ledger mutate only; no live)
.venv/bin/python -m trader_platform.autonomy_loop --mode paper --once --symbols TSLL --event rth_pcs_paper --json

# Offline smoke (includes PCS multi-leg risk/ledger)
.venv/bin/python -m trader_platform.smoke_test
```

## Hypotheses (examples; not exclusive; not live)

**PCS (TSLL) — paper OPEN wired earliest:**

- `hyp_dna_tsll_put_credit_spread_b195f5fe` — w=1.0 dte=21 δ=0.20
- `hyp_dna_tsll_put_credit_spread_0514c2af` — w=1.0 dte=14 δ=0.25
- `hyp_dna_tsll_put_credit_spread_fd407d4f` — w=1.5 dte=21 δ=0.25

**Other defined-risk (research peers — quality bar, not ticker quota):**

- `hyp_dna_xom_call_credit_spread_77766a47` — CCS; fit_3k; B3/B4 soft-hold; **demoted off capital path 2026-07-10** (diversifier-only seat; `candidate`; retest if quality wins without diversifier rationale); OPEN_CCS path still build debt
- `hyp_dna_amd_iron_condor_b3056133` — IC; fit_3k; cost-fragile at ≥2% slip (demote DNA, not structure class)

## Non-goals

- Multi-leg **live** RH place (Level 3) — not wired; MCP option place is single-leg only today.
- Auto-promote to shadow/live.
- Paper naked TSLL short as PCS substitute.
- Ranking by “which OPEN action was wired first.”

## Status

PCS multi-leg paper path wired 2026-07-09 (kanban t_0fde42e4). CCS/IC share the same scout → intent → ledger shape (2026-07-10 Ken pin: evidence rank; plumbing is parallel debt). Live-clock fills still depend on filters; regime/cost stress remains separate BUILD work.

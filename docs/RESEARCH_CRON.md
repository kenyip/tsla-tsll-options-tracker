# Research cron (paper-only)

**Status:** paper research recurrence only (2026-07-09)
**Hard rule:** **no trading cron**. Do not schedule `platform-paper-tick`, `place_*`, funding, or `agentic_live`.

---

## What runs on a schedule

| Job | Command | Mutates |
|-----|---------|---------|
| Multi-symbol research tick | `just research-tick-paper` | SQLite `.cache/platform/research.db` + dated markdown under `.cache/platform/research_reports/` |
| Optional promote | `just research-promote-top -- --top 5 --sleeve-usd 3000` | Hypothesis registry **candidates only** (never live) |
| Optional backtest hooks | add `--run-backtests` to promote | Read-only engine metrics + optional trade CSV under `.cache/platform/research_backtests/` |

Research ranking is **not** the live instrument allowlist. Live gates stay in `risk_limits.yaml` + `agentic.enabled: false`.

---

## Recommended schedule (operator)

Example **launchd / cron** entry — **research only**:

```bash
# Weekdays 16:30 America/Los_Angeles (after US cash close) — paper research
# Doctrine default sleeve: $3000 Agentic pilot (not $5k)
30 16 * * 1-5 cd /Users/jarvis/dev/trader && \
  .venv/bin/python -m trader_platform.research tick \
    --write-report \
    --sleeve-usd 3000 \
    --notes research_cron_paper \
    >> .cache/platform/research_cron.log 2>&1
```

Optional second step (still paper, candidates only):

```bash
35 16 * * 1-5 cd /Users/jarvis/dev/trader && \
  .venv/bin/python -m trader_platform.research promote-top \
    --top 5 --sleeve-usd 3000 \
    >> .cache/platform/research_cron.log 2>&1
```

Or via Just:

```bash
just research-tick-paper -- --sleeve-usd 3000
just research-promote-top -- --top 5 --sleeve-usd 3000
# with engine hooks (bounded):
just research-promote-top -- --top 3 --run-backtests
```

---

## Manual one-shot

```bash
just research-universe
just research-tick -- --top 12 --sleeve-usd 3000 --write-report
just research-report
just research-promote-top -- --top 5 --sleeve-usd 3000 --dry-run
just research-promote-top -- --top 5 --sleeve-usd 3000
```

Pipeline in one command:

```bash
just research-tick -- --top 10 --sleeve-usd 3000 --write-report --promote --promote-top 5
```

---

## Dated reports

| Path | Content |
|------|---------|
| `.cache/platform/research_reports/YYYY-MM-DD_run{N}.md` | Composite tops + capital table |
| `.cache/platform/research.db` | Runs / symbol_scores / opportunities (incl. capital columns) |
| `trader_platform/data/hypotheses.yaml` | Candidates from promote-top (`hyp_research_*`) |

---

## Capital pilot filter (`--sleeve-usd`)

**Doctrine default for Agentic paper / pilot examples: `3000`.** Larger sleeves remain valid research filters.

| Sleeve | Typical use |
|--------|-------------|
| `3000` | **Default** — Agentic T1 seed / pilot (docs + bootstrap / evolve-tick) |
| `5000` | T2 income lab (optional larger paper filter, not the default) |
| `15000` | Larger paper sleeve |

Columns (proxies, not broker margin):

- `spot`, `100*spot` (`share_lot_usd`)
- `short_premium_bp_proxy` ≈ `0.95 * 100 * spot` (cash-secured put style)
- `long_debit_proxy` ≈ max(2% of spot × 100, 0.5×ATR×100)
- contracts affordable @ $3k / $5k / $15k (short + long)
- `capital_fit` / `capital_fit_long` → `fit_3k` \| `fit_5k` \| `fit_15k` \| `oversized`

`--sleeve-mode short|long|either` (default `either`) controls pilot filtering.

---

## Forbidden on any cron

- `place_*` / cancel live orders
- Funding Agentic or main
- `agentic.enabled=true`
- Scheduling `autonomy_loop --mode agentic_live`
- Collapsing research universe to TSLA/TSLL only

---

## Related

- `docs/RESEARCH_LOOP.md` — scout pipeline
- `docs/STAGE2_RH_READONLY_AND_CAPITAL.md` — funding tiers
- `docs/AGENTIC_AUTONOMY_POLICY.md` — live arming gates
- `docs/PROMOTION_GATES.md` — candidate → … → live (human)

Also: `docs/TRADER_LOOPS.md` (shared loop map) · `docs/BUILD_COORDINATION.md` (lanes) · `just learn-tick` (L3 self-learn)

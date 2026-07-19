# Trader dual desk — personal tracker + autonomous engine

> **Build bible:** [TRADER_BUILD.md](TRADER_BUILD.md) · **Doc map:** [README.md](README.md)


**Pinned:** 2026-07-19  
**Decision:** **One monorepo**, two desks. Do **not** split into a greenfield repo for the autonomy engine. Soft-rename product identity now; optional GitHub rename later.

---

## Recommendation

| Option | Verdict |
|---|---|
| New empty repo for “Agentic Trader” | **No** — loses `pcs_sim`, spine, paper, risk, RH, tests, cron wiring |
| Stay in `tsla-tsll-options-tracker` as-is forever | **No** — name is too narrow and confuses personal desk vs autonomy |
| **Monorepo, dual desk, soft rename → later hard rename** | **Yes** |

### Rename (done 2026-07-19)

| Surface | Name |
|---|---|
| Product | **Trader** (Hermes profile `trader`) |
| Package | `trader_platform` (unchanged — no import churn) |
| Local path | `/Users/jarvis/dev/trader` |
| GitHub | `https://github.com/kenyip/trader` |
| Compat symlink | `/Users/jarvis/dev/trader` → `trader` (temporary; remove later) |

### Why not a new repo

- Autonomy **consumes** the same sim, DNA, risk, paper, and data boundaries you already paid for.
- Personal desk (positions, PMCC, AI coaching on *your* methods) should stay close to those tools.
- Split would create dual maintenance and copy-paste drift.

---

## Desk A — Personal trading tracker (you + AI)

**Purpose:** Help Ken with **manual / main-book** methods, positions, and coaching — not Agentic auto-trading.

| Capability | Surfaces |
|---|---|
| Open positions | `positions.py`, `positions.yaml`, `just positions` |
| PMCC / LEAPS desk | `pmcc/*`, `pmcc_positions.yaml`, `just pmcc-manage` |
| Short-premium recs (TSLA/TSLL seeds) | `live.py`, `strategies.py`, dashboard |
| Desk brief | `docs/DESK_BRIEF.md`, `just desk-brief` |
| Critic / rule research on your methods | `analyze.py`, `validate_rule.py`, GOAL.md engine |
| RH main account context | read-only snapshot (non-agentic); **no auto place** |

**Rules:** Desk A never arms Agentic live. Main book stays human + AI assist.

---

## Desk B — Agentic autonomy engine ($3k sleeve)

**Purpose:** Self-sufficient **find → evaluate → wait → paper → (Ken-armed) live** loop.

| Capability | Surfaces |
|---|---|
| StrategySpec + evaluate | `trader_platform/research/strategy_spec.py`, `evaluate_proxy.py` |
| Living registry | `trader_platform/research/living_registry.py` |
| Opportunity watcher | `trader_platform/research/opportunity_watcher.py` |
| Evolve specs | `trader_platform/research/evolve_strategy_spec.py` |
| Paper / risk / scout | `autonomy_loop`, `premium_scout`, `risk_governor` |
| Spine architecture | `docs/TRADER_SPINE_ARCHITECTURE.md` |

**Rules:** Research/paper only until fund + options level + explicit Ken arm. Stand-aside / `NO_SETUP` is success.

---

## Shared vs isolated

```text
shared:  pricing, data loaders, pcs_sim, option quote boundary, tests, Justfile
Desk A:  positions.yaml, pmcc_positions, personal playbooks, main RH context
Desk B:  strategy_specs/, living registry, watcher packets, paper ledger, agentic risk
```

Never mix: **Desk A position files are not Desk B paper authority**, and Desk B DNA is not auto-applied to Ken’s main book.

---

## Operator mental model

```text
You (Desk A):  “What do I hold? What should I do on PMCC/TSLL?”
Trader (B):    “Any living strategy? Any setup now? Else wait / keep evolving.”
```

Both live in one repo so AI help can see both contexts without two codebases.

---

## Post-rename checklist

- [x] GitHub repo renamed to `kenyip/trader`
- [x] Local dir `~/dev/trader`
- [x] `origin` → `https://github.com/kenyip/trader.git`
- [x] Hermes `cron/jobs.json` workdir/paths updated
- [x] Live trader-guidance state paths updated
- [ ] Ken: reopen IDE/terminals on `~/dev/trader` (not old folder tab)
- [ ] Ken: any personal scripts/LaunchAgents still pointing at old path
- [ ] Ken: remove compat symlink when nothing old remains: `rm ~/dev/tsla-tsll-options-tracker`
- [ ] Optional: commit dual-desk + spine work and `git push` from new path

Package import stays `trader_platform`. Desk A commands (`positions`, `pmcc`) unchanged.

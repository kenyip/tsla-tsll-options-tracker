# Trader docs library

## Start here (build)

| Document | Use |
|---|---|
| **[TRADER_BUILD.md](TRADER_BUILD.md)** | **Single source of truth for build & system alignment** |

If you only open one file: that one.

---

## Detail (read when you need depth)

| Document | Topic |
|---|---|
| [TRADER_SPINE_ARCHITECTURE.md](TRADER_SPINE_ARCHITECTURE.md) | StrategySpec → evaluate_proxy → living seats (implementable spine) |
| [DISCOVERY_AND_PAPER_FASTTRACK.md](DISCOVERY_AND_PAPER_FASTTRACK.md) | Grid, universe, workers, reboot, paper handoff ops |
| [TRADER_LAYERED_EDGE_DOCTRINE.md](TRADER_LAYERED_EDGE_DOCTRINE.md) | Full 11-layer edge stack & candidate schema |
| [TRADER_DUAL_DESK.md](TRADER_DUAL_DESK.md) | Desk A personal vs Desk B agentic |
| [AGENTIC_AUTONOMY_POLICY.md](AGENTIC_AUTONOMY_POLICY.md) | Modes, risk envelope, arming |
| [PROMOTION_GATES.md](PROMOTION_GATES.md) | Live promotion checklist (code-linked) |
| [GO_LIVE_READINESS.md](GO_LIVE_READINESS.md) | Live readiness packet |
| [PCS_PAPER_PATH.md](PCS_PAPER_PATH.md) | PCS paper path detail |
| [TRADER_LOOPS.md](TRADER_LOOPS.md) | Loop topology |
| [TRADER_AGENT_PROFILE.md](TRADER_AGENT_PROFILE.md) | Hermes `trader` profile ops |
| [DESK_BRIEF.md](DESK_BRIEF.md) | Desk A daily brief playbook |
| [PMCC_MONITOR_DEPLOYMENT.md](PMCC_MONITOR_DEPLOYMENT.md) | PMCC monitor deploy |
| [BUILD_PROGRESS_AND_CONFIDENCE.md](BUILD_PROGRESS_AND_CONFIDENCE.md) | Confidence ladder nuance |
| [BUILD_LAB_ENVIRONMENT.md](BUILD_LAB_ENVIRONMENT.md) | BUILD lab / zero-input front door |
| [STAGE2_RH_READONLY_AND_CAPITAL.md](STAGE2_RH_READONLY_AND_CAPITAL.md) | RH snapshot / capital stage |
| [OPTION_QUOTE_DATA_BOUNDARY.md](OPTION_QUOTE_DATA_BOUNDARY.md) / [SCHWAB_OPTION_DATA_PATH.md](SCHWAB_OPTION_DATA_PATH.md) | Data boundaries |
| [RESEARCH_LOOP.md](RESEARCH_LOOP.md) / [RESEARCH_CRON.md](RESEARCH_CRON.md) / [RESEARCH_SCOREBOARD.md](RESEARCH_SCOREBOARD.md) | Older multi-symbol research scout |

### Pins absorbed into BUILD (keep for history; do not re-fork doctrine)

These remain for dated history and deep cross-links but **must not** redefine product intent:

| Document | Note |
|---|---|
| [TRADER_NORTH_STAR.md](TRADER_NORTH_STAR.md) | Redirect → BUILD; long-form catalog history |
| [TRADER_PLATFORM_GOAL.md](TRADER_PLATFORM_GOAL.md) | Pre-consolidation product pin |
| [TRADER_RESTART_CHARTER.md](TRADER_RESTART_CHARTER.md) | Pre-consolidation anti-drift charter |
| [TRADER_KNOWLEDGE_MAP.md](TRADER_KNOWLEDGE_MAP.md) | Session memory map (ops notes) |

---

## Research archive (do not treat as current build plan)

Dated search reassessments, epochs, and coverage surveys. Useful for archaeology; **not** the default plan.

| Pattern | Examples |
|---|---|
| `SEARCH_DESIGN_REASSESSMENT_*.md` | 2026-07-14 … 07-16 design notes |
| `SEARCH_EPOCH_*.md` | Epoch freezes |
| [INCOME_STRATEGY_COVERAGE.md](INCOME_STRATEGY_COVERAGE.md) | Structure coverage inventory |
| [CONTINUOUS_DENSIFY_POST_PAUSE.md](CONTINUOUS_DENSIFY_POST_PAUSE.md) | Densify pause notes |
| [FREE_STRATEGY_RESEARCH_RUNBOOK.md](FREE_STRATEGY_RESEARCH_RUNBOOK.md) | Lab generate/label loop (Desk A / free lab) |
| [HISTORICAL_OPTION_DATA_DECISION_PACKET.md](HISTORICAL_OPTION_DATA_DECISION_PACKET.md) | Data buy/build decision |
| [PCS_INCOME_AUTONOMY_PROGRAM.md](PCS_INCOME_AUTONOMY_PROGRAM.md) | Earlier PCS program sketch |
| [TRADER_DIRECT_TO_PAPER_WATCH_PLAN.md](TRADER_DIRECT_TO_PAPER_WATCH_PLAN.md) | Earlier direct-paper plan |
| [STRATEGY_ENGINE_HANDOFF.md](STRATEGY_ENGINE_HANDOFF.md) | External engine handoff |

---

## Root repo docs (outside this folder)

| File | Role |
|---|---|
| [../README.md](../README.md) | Repo entry + quick start |
| [../GOAL.md](../GOAL.md) | Legacy critic-loop / Desk A seed methods goal |
| [../STRATEGY.md](../STRATEGY.md) | TSLA/TSLL seed strategy history |
| [../ENGINE.md](../ENGINE.md) | Classic backtest harness |

---

## Rule for new docs

1. **Default:** update [TRADER_BUILD.md](TRADER_BUILD.md) (and changelog there).  
2. **Deep ops only:** add a detail doc and link it from this README under **Detail**.  
3. **One-off research:** name it clearly and list under **Research archive** — never as a second north star.

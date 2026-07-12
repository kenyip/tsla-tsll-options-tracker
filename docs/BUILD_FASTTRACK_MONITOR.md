# BUILD fast-track — monitor-only mode

**Ken intent:** run more dual BUILD labs. Jarvis/Ken only **monitor drift** and keep the program pointed at **wide coverage → high-confidence strategy**, not micromanage each wake.

## Operating contract

| Role | Does | Does not |
|---|---|---|
| **Trader (Sol→Grok dual)** | Free discovery, sims, falsify, ONE next seed | Live/arm/real money |
| **Jarvis/Ken** | Check runs completed, progress type, L0–L4, drift flags | Force recipe menus every wake |
| **Schedule** | Sequential duals (lockfile) on densified cadence | Parallel duals on same repo |

## Success definition (program level)

1. **Wide coverage** — remaining structure/time/direction gaps closed or honestly parked
2. **High confidence strategy** — first **L1** DNA (non-vacuous after-cost + B3 density + competitive ml/dd)
3. Then shift weight to **B6 paper** (not infinite BUILD)

## Drift flags (monitor alerts on)

- 3 consecutive complete duals with progress score ≤2
- 3 consecutive duals with only single-leg toys / no defined-risk work
- Same axis repeated without new evidence (e.g. free pop36 thrash)
- Incomplete duals / lock stuck / cron script missing
- Claimed L1/readiness without after-cost numbers
- Any live/arm/shadow auto-promote language

## Commands

```bash
# status
pgrep -fl trader_build_lab || true
ls -lt reports/trader-wakes/moa | head
.venv/bin/python scripts/trader_build_progress.py --write
.venv/bin/python scripts/trader_build_monitor.py --write

# manual dual (if idle)
bash scripts/trader_build_lab_moa.sh --slot evening
# or free-explore goal:
bash ~/.hermes/profiles/trader/scripts/trader-build-lab-free-explore.sh
```

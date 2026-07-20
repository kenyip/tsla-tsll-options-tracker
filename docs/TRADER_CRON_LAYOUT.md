# Trader cron layout (post engine-prove)

**Pinned:** 2026-07-19  
**Profile:** Hermes `trader` only (`~/.hermes/profiles/trader/cron/`)  
**Doctrine:** `docs/TRADER_BUILD.md` · handoff `reports/bootstrap/ENGINE_PROVE_HANDOFF.md`

## Intent

Wake volume is **not** progress. Cron exists to:

1. **RTH condition / paper plumbing** — stand-aside or dry paper path on living/paper_eligible seats  
2. **Off-hours BUILD quality** — sparse dual-model labs aimed at pack-grade multi-symbol edge  
3. **Never** continuous dense bag drain, live orders, or self-arm

## Active set (target)

| Job | Schedule (America/Los_Angeles) | Mode | Purpose |
|---|---|---|---|
| `trader-rth-eval` | `30 6-12 * * 1-5` | agent + `trader-self-evolution` | Hourly RTH condition eval; paper OPEN_* only if capital-fit; no evolve |
| `trader-paper-ops` | `5 6-12 * * 1-5` | script `trader-paper-ops.sh` | Dry `just trader-paper-loop` residue (watch + handoff, no execute-paper) |
| `trader-build-lab-premarket` | `15 5 * * 1-5` | script → zero-input MoA | One BUILD before open |
| `trader-build-lab-postclose` | `15 14 * * 1-5` | script → MoA | One BUILD after close |
| `trader-build-lab-daily` | `45 16 * * 1-5` | script → MoA | Primary weekday BUILD densify (quality, not bag %) |
| `trader-build-lab-evening` | `0 20 * * 1-5` | script → MoA | Second weekday BUILD if first finished |
| `trader-build-lab-weekend` | `0 10 * * 6` | script → MoA | One Saturday lab |
| `trader-build-lab-weekly` | `0 17 * * 0` | script → MoA | Sunday critic / deeper lab |

All BUILD scripts call `just trader-build-lab` / canonical MoA with **zero caller goal** (self-sufficient wake).

## Explicitly removed / paused

| Job | Action | Why |
|---|---|---|
| `trader-continuous-densify` (`every 5m`) | **Removed 2026-07-19** | Contradicts densify-winners-only; bag drain as progress; CPU thrash; state already `enabled=false` after engine pause |
| Overnight BUILD 23/02/04 | **Paused** | Overlapping MoA thrash; many `STRATEGY_ENGINE_GATE_FAILED` / incomplete resume storms |
| Weekend pm/eve + Sunday am BUILD | **Paused** | Duplicate weekend volume; keep one Sat + one Sun |
| `trader-build-lab-midday` | Paused (earlier) | RTH should not free-evolve |
| `trader-build-monitor` every 3h | Paused (earlier) | Optional; re-enable only if monitor script is desired |
| Legacy `trader-self-evolution-daily/weekly` agent | Paused | Superseded by BUILD MoA + RTH eval |

Continuous densify **state** file may remain `enabled=false` for forensics; **do not re-create the 5m cron** without Ken mandate and a living quality leader path.

## Not on cron (on purpose)

| Loop | How it runs |
|---|---|
| `just trader-discover` / dense bag | Manual or rare off-hours campaign — **not** every 5–30m default |
| `trader-desk-b-loop` 30m discovery | Optional future; only when deliberately searching Wave A / densify winners |
| `--execute-paper` | Intentional human/agent decision when TOP_HYP quality leader exists |
| `agentic_live` | Ken arm only |

## BUILD gate note (2026-07-19)

Several MoA slots recently failed with:

- `STRATEGY_ENGINE_GATE_FAILED: strategy engine report stale`
- `trader_git_sha does not match Trader repo HEAD`

That is a **control-plane / freshness gate**, not a reason to spray more 5m launches. Fix path: one clean BUILD or engine progress refresh, then sparse schedule above. Do not bypass the gate by continuous densify.

## Operator checks

```bash
# From a trader Hermes session:
# list jobs — expect no every-5m densify; overnight paused

just trader-paper-loop          # manual residual
just trader-progress            # discovery idle is OK
just trader-multi-symbol-reprove
```

## Relationship to go-live plan

See readiness scoreboard `reports/readiness/LATEST.md` and `docs/GO_LIVE_READINESS.md`.

```text
RTH crons     → Phase 2 paper plumbing / stand-aside
BUILD crons   → Phase 1 pack-grade edge search (sparse quality)
No cron       → Phase 4 arm / live
```

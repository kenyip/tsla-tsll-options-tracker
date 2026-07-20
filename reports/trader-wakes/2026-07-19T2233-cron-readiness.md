# WAKE — 2026-07-19T2233 readiness + cron rethink

WAKE: 2026-07-19 ~22:33 PDT  
PHASE: PAPER ops / BUILD edge-search (not LIVE)  
SLEEVE: 3000  
CHOSE: Refresh go-live readiness truth + fix Hermes cron layout (remove 5m densify thrash)

## DID

1. Audited trader profile crons (18 jobs).
2. **Removed** `trader-continuous-densify` (`every 5m`, job `4696f759bb32`) — contradicts densify-winners-only / engine handoff.
3. **Paused** thrash BUILD volume: overnight 23/02/04, weekend-pm, weekend-eve, sunday-am.
4. **Added** `trader-paper-ops` (`5 6-12 * * 1-5`, script `trader-paper-ops.sh`) — dry `just trader-paper-loop` only.
5. Updated `trader-rth-eval` prompt to pin BUILD bible + engine handoff + no dense densify / default dry paper.
6. Wrote `docs/TRADER_CRON_LAYOUT.md`; pinned from `docs/TRADER_BUILD.md` §9.
7. Rewrote `reports/readiness/LATEST.md` post engine-prove (TOP_HYP=none; quality_pass=false; A/B honest).
8. Smoke-ran paper-ops script → PAPER_PACKET_READY / dry PAPER_INTENT_READY (plumbing only).

Did **not**: multi-symbol marathon this wake (NEXT), live/shadow/arm, re-arm continuous densify, `--execute-paper`.

## EVIDENCE

| Item | Path / result |
|---|---|
| Cron layout | `docs/TRADER_CRON_LAYOUT.md` |
| Readiness | `reports/readiness/LATEST.md` |
| Paper ops script | `~/.hermes/profiles/trader/scripts/trader-paper-ops.sh` (exit 0) |
| paper_loop | IWM densify dry intent ml≈$223; trading_authority false |
| Multi-symbol quality | still false (prior MULTI_SYMBOL_REPROVE) |

### Active cron target (after change)

- ON: rth-eval, paper-ops, build premarket/postclose/daily/evening, weekend sat 10, weekly sun 17  
- OFF/removed: continuous 5m densify; overnight ×3; weekend extras; midday; monitor; legacy daily/weekly agent  

### BUILD slot health note

Recent MoA errors: `STRATEGY_ENGINE_GATE_FAILED` (stale engine report / git sha mismatch). Sparse schedule does not fix the gate — next BUILD should clear engine freshness once, not spray 5m launches.

## VERIFICATION

- Cron list: no `every 5m` job; `trader-paper-ops` scheduled next 2026-07-20T06:05 PT  
- `trader-paper-ops.sh` → exit 0  
- Readiness TOP_HYP=none; quality leader 0  
- No live/shadow/arm  

## DURABLE

- Repo: cron layout doc, BUILD pin, readiness LATEST, this wake  
- Profile: cron jobs + paper-ops script (Hermes profile, not git)  
- Lesson: 5m continuous densify is anti-doctrine once bag is drained / engine is ops-ready; use sparse BUILD + RTH paper residual  

## INTEGRATION

- commit: (this integrate)
- branch: main → origin/main
- secret-safe: docs + readiness + wakes + paper_loop JSON only
- Hermes cron changes live in profile (~/.hermes/profiles/trader), not git

## LESSON

Future Trader: treat cron as sparse quality wakes. Progress = pack-grade multi-symbol edge + paper sample, not launch count.

## NEXT SEED

Off-hours: one multi-symbol dual-cost re-prove / new thesis loop aimed at `quality_pass` (≥2 symbols F2, holdout n≥12 worst axis) — not dense cartesian. Parallel: diagnose BUILD `STRATEGY_ENGINE_GATE_FAILED` once if next MoA slot still red.

## GATES

none

# RTH EVAL — 2026-07-16T0630 (open ~09:30 ET)

WAKE: 2026-07-16 ~06:30 PT / 09:30 ET (RTH open)
PHASE: BUILD/L0 (readiness); paper-condition path only
SLEEVE: $3,000
CHOSE: RTH condition eval — freshness → multi-symbol scout → capital judgment → stand-aside or paper OPEN_* only
OUTCOME: STAND_ASIDE (success). No paper place. No evolve. First RTH of 2026-07-16 after overnight BUILD/MoA WIP.

## Strategy / capital context (not a discovery wake)

- Living quality leader: **none**
- Capital path: **empty** (0 F1/F2/F3/F4; 0 L1 seats)
- B6: still waiting non-bear capital-fit OPEN_PCS (or other defined-risk capital-fit intent)
- Overnight BUILD residue (not executed here): MoA `2026-07-16T0546` finalizer-ready `FAMILY_CLOSED` on `BROAD_INDEX_OVERNIGHT_ABSORPTION_*`; ONE NEXT BUILD seed `YIELD_CURVE_STEEPENING_REGIONAL_BANK_FORWARD_UPDRIFT_PREFLIGHT`
- Authority: research/paper only; agentic_live blocked; no shadow/live/arm/broker
- Concurrent checkout at RTH time: dirty branch `trader/run-2026-07-16T0546` forced **reports-only RTH**; that BUILD has since integrated cleanly as `317384d`, without changing the RTH STAND_ASIDE decision

## Orient

| Item | State |
|---|---|
| Session | Thu 2026-07-16 RTH open (~09:30 ET) |
| Prior LATEST | `2026-07-16T0546` MoA finalizer handoff (BUILD; not RTH) |
| Prior RTH | `2026-07-15T1531` late — STAND_ASIDE 14/0/14 (same class all day 15th) |
| Readiness | BUILD/L0; capital path empty; living leader none; wrapper integration pending on concurrent run |
| Eligible hyps | 15 (`testing` 14 + `paper` 1); 230 candidate parked (not scout-eligible) |
| Real paper open risk | **0** (only `m0_stub:smoke_test` working order on TSLA — ignored) |
| Checkout | dirty concurrent BUILD branch — RTH does not integrate |

Jarvis guidance (critic context, not order): older stamp noted burst-stop reassessment; current successor epoch already opened overnight with first no-advance close. RTH does not open BUILD strategy volume.

## Freshness gate

| Symbol | Engine date | Engine spot | Live (YF) | Drift | Engine / scout note |
|---|---|---|---|---|---|
| TSLL | 2026-07-16 | 11.87 | ~11.88 | ~+0.08% | bearish |
| TSLA | 2026-07-16 | 388.27 | ~388.9 | ~+0.16% | bearish |
| SMCI | 2026-07-16 | 26.54 | ~26.45 | ~−0.34% | bearish |
| PLTR | 2026-07-16 | 131.97 | ~131.6 | ~−0.25% | neutral |
| XOM | (no eligible hyp this pass) | — | ~144.7 | — | live only |
| AMD | — | — | ~512.4 | — | live only |
| BAC | — | — | ~61.7 | — | live only |
| SOFI | — | — | ~17.8 | — | live only |

**Verdict:** Freshness **pass** — all scout-eligible symbols have session-day engine bars (2026-07-16). Live YF drifts are tiny open-print moves, not multi-day frozen cache. Scout-requested XOM/AMD/BAC/SOFI had no eligible hyps this tick (absence ≠ missing edge on parked `candidate` DNA).

## Condition scan

```text
.venv/bin/python -m trader_platform.premium_scout --symbols TSLL TSLA XOM AMD SMCI PLTR BAC SOFI --json --max-intents 5 --event rth_eval
→ n_candidates=14, n_intents=0, n_stand_asides=14, n_skipped=0

.venv/bin/python -m trader_platform.autonomy_loop --mode paper --once --dry-run --symbols TSLL TSLA XOM AMD SMCI PLTR BAC SOFI --json --event rth_eval --max-intents 5
→ n_proposals=0; agentic_enabled=false; readiness_blockers remain (agentic ~$0 capital + no options level)
```

Scout symbols/regimes among **eligible** hyps (`testing|paper|shadow|live`):

- TSLL×10 **bearish** (incl. historical PCS refs `b195f5fe` + two other PCS testing DNA)
- TSLA×1 bearish; SMCI×2 bearish; PLTR×1 **neutral**
- Reason buckets: filtered/classifier ~7 / PCS bear_aside ~3 / bear_dte=0 skip ~2 / premium_thin ~2

Historical PCS reference `hyp_dna_tsll_put_credit_spread_b195f5fe` (and `0514c2af`, `fd407d4f`): honest **STAND_ASIDE** — `PCS: bearish regime — stand aside (bear_dte=0; capital-fit put credit not probed)`.

**Parked (not scout-silent = no edge):** stressed `candidate` DNA (e.g. XOM CCS, AMD IC, others) remain ineligible for RTH scout by design. Do not thrash status mid-RTH.

## Capital judgment

| Signal | Decision |
|---|---|
| OPEN_PCS / OPEN_CCS / OPEN_IC capital-fit 1-lot | **None fired** |
| PCS b195f5fe / testing PCS DNA | Bear STAND_ASIDE (`bear_dte=0`) — success |
| Naked short premium / thin credit / wheel / short_dte | STAND_ASIDE (thin premium or filter/bear skip) — would capital-reject undefined max_loss if naked intent fired |
| Real open paper risk | 0 — nothing to manage/close |

**Decision: STAND_ASIDE.** No paper place. Filters said no; open-session reconfirm of prior-day class under still-bearish TSLL/TSLA/SMCI. Stand-aside is success.

## Parallel data (optional)

Current archive-derived coverage is **2/3 RTH market dates** (`2026-07-13`, `2026-07-14`) with `provider_backtest_eligible=false`; the third archive date (`2026-07-11`) is non-RTH and is correctly excluded. This RTH wake did not append a new option snapshot. That leaves the optional archive-density task open but does not alter the no-intent STAND_ASIDE decision or authorize provider-backed historical simulation.

## Evidence

- Scout JSON: `/tmp/rth_scout_2026-07-16T0930.json` + audit `.cache/platform/premium_scout.jsonl`
- Autonomy dry-run: `/tmp/rth_autonomy_2026-07-16T0930.json` + `.cache/platform/autonomy_audit.jsonl`
- Freshness: `/tmp/rth_freshness_2026-07-16T0930.json`
- Paper ledger: `.cache/platform/paper_ledger.json` (stub smoke only)
- Cache eval: `.cache/platform/rth_eval_2026-07-16.json`

## DURABLE / learning

- Open RTH 2026-07-16 matches 2026-07-15 stand-aside class: eligible DNA under **bearish TSLL/TSLA/SMCI** and thin/filter on neutral PLTR; capital path remains empty until non-bear defined-risk filters pass.
- Concurrent BUILD MoA must not be absorbed/stashed by RTH — reports-only + `INTEGRATION: incomplete` is correct.
- No skill/doctrine patch required (behavior matches RTH checklist).
- No promotion of hyps; no evolve; no B-check change (readiness left to concurrent BUILD handoff).

## VERIFICATION

- Freshness cross-check multi-symbol engine vs yfinance: pass (session day; ~0% open drift)
- `premium_scout` 14/0/14: pass
- `autonomy_loop` dry-run 0 proposals: pass
- Paper real open risk 0 (smoke ignored): pass
- No live/broker/arm: pass

## INTEGRATION

**incomplete — reports only.** Concurrent dirty branch `trader/run-2026-07-16T0546` holds BUILD MoA finalizer residue and untracked labs/tests; RTH wrote stamp + LATEST + INDEX + rth_eval cache only. Did **not** stash/reset/absorb foreign WIP, commit, merge, or push. No shadow/live/arm/broker.

## LESSON

Future RTH: when capital path empty and TSLL regime still bearish with `bear_dte=0` PCS DNA, open-tick stand-aside reconfirm is correct; leave concurrent BUILD integration to the MoA wrapper; never invent paper probes from thin-premium single-leg paths or thrash candidate status mid-session.

## NEXT SEED

RTH NEXT (unchanged condition): **wait for non-bear capital-fit OPEN_PCS/OPEN_CCS/OPEN_IC** (B6); stand-aside until then. No mid-session evolve.

BUILD NEXT (context only; off-hours / MoA wrapper): finish `2026-07-16T0546` integration if still pending, then `YIELD_CURVE_STEEPENING_REGIONAL_BANK_FORWARD_UPDRIFT_PREFLIGHT` (or higher-information free goal). Not executed on this RTH wake.

## GATES

none (no approval packet; no paper/live action)

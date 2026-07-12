# MOA BUILD Lab challenger critique — 2026-07-10T2123

ROLE: Grok 4.5 challenger (read-only)
PHASE: BUILD · SLEEVE: $3,000 · SLOT: evening
EXECUTOR: GPT 5.6 Sol · Axis E (minimal long-calendar sim scaffold + falsify)

## Rubric

| # | Item | Result | One line |
|---|---|---|---|
| 1 | Income goal honesty | **PASS** | $3k / defined-risk framing; no vanity calendar or SMCI CCS capital seat; leader still soft loss @5% not “income edge” |
| 2 | Multi-structure search vs tunnel | **PASS** | Closed Axis E catalog gap (calendar) + free pop36 yielded calendar + SMCI CCS; not b195f5fe polish thrash |
| 3 | Time bias as real axis | **PASS** | Calendar is the time-structure gap; same-IV limitation and front/back DTE knobs explicit; weekday/session still deferred |
| 4 | Direction/regime bias | **PASS** | Dated B3 on PCS / calendar / SMCI CCS; regime soft-hold vs fail used for judgment, not slogans |
| 5 | Sims actually run (paths) | **PASS** | run18 + evolve_audit `2026-07-11T04:27:57+00:00` + stress_regime/cost_lab_2026-07-10T2123.json + calendar_sim.py verified |
| 6 | Quality bar / B3+B4 | **PASS** | New SHIPs quality-rejected; b195f5fe remains relative leader only; no capital-path expansion |
| 7 | ONE closed NEXT seed | **PASS** | Calendar front/back IV term-structure/skew → calendar-only OOS + B3/B4; reject-if-fragile; no menu |
| 8 | No live/shadow promotion | **PASS** | candidate/research-only; no broker/arm/shadow/live |

**Score: 8/8 PASS**

Non-blocking nits (labels only; do not reopen capital path):
1. Research **composite** table has **MU #3**; executor top list skipped MU and listed QQQ as top-8 (QQQ is #9). Evolve symbols were TSLL/SMCI/PLTR/NFLX/BAC/XOM/MU/TSLA — fine discovery set, just not identical to the prose top-8.
2. Calendar **evolve last_sim** is 2y n=33 SHIP; B3 full_history 5y n=100 pnl $148.05 — table correctly uses stress 5y; do not cite 2y evolve score as readiness.
3. Soft `cost_hold=true` on b195f5fe = **soft loss** at 5% (n=13 / −$18.32), **not** non-vacuous after-cost income.
4. Calendar DNA registry `dte_stop: 0` vs cost-lab base_config `dte_stop: 3` — stress may not be byte-identical to registered DNA; B4 still fails hard either way (−$895.64 / REJECT). Prefer exact DNA configs on next falsify.

## Verified quality bar (from dated stress JSON)

| hyp | ml | window max_dd | dense_neg≥3 | regime_hold | slip5 n/pnl | cost_hold | judgment |
|---|---:|---:|---:|---|---|---|---|
| TSLL PCS `b195f5fe` | 76.32 | 74.85 | 5 | true | 13 / −18.32 NULL | soft true | relative leader; not real-money ready |
| TSLL calendar `d5e00af5` | 146.84 | 230.79 | 7 | true | 94 / −895.64 REJECT | **false** | research-only reject |
| SMCI CCS `ee20a595` | 166.77 | 692.84 | 12 | **false** | 118 / −1614.13 REJECT | **false** | research-only reject |

Evidence checked:
- `.cache/platform/research_reports/2026-07-11_run18.md`
- `.cache/platform/evolve_audit.jsonl` @ `2026-07-11T04:27:57+00:00` (applied, n_ship=2)
- `.cache/platform/stress_regime_lab_2026-07-10T2123.json`
- `.cache/platform/stress_cost_lab_2026-07-10T2123.json`
- `trader_platform/research/calendar_sim.py` (single `iv_proxy`/`sigma` for front+back marks — limitation real)
- `trader_platform/data/hypotheses.yaml` — both new hyps `status: candidate`
- `reports/readiness/income-coverage-LATEST.md` — calendar_sim present; term-structure gap listed
- `reports/trader-wakes/moa/2026-07-10T2123/executor-closeout.md`

## Challenger judgment

Executor did the right BUILD loop: **scaffold missing time-structure sim → smoke/dispatch → one evolve → B3+B4 quality bar → refuse capital path**. Calendar baseline SHIP under same-IV BS is plumbing, not edge; B4 already kills it. SMCI CCS is a vanity/full-history reject (5y pnl −$422, regime fail). No diversify-for-fear seat.

Honest readiness: stay **BUILD**. Nothing is ready for a real account. Blocks unchanged: non-vacuous after-cost superiority, B6 multi-session paper, B7 shadow, unfunded Agentic options account, calendar model still incomplete, other sim classes (diagonal/butterfly/debit) still absent.

Hard stops held: no evolve `--apply` by challenger; no live/broker/arm/shadow.

## ONE NEXT SEED (merge keep)

Next BUILD only — add expiry-specific front/back IV term-structure/skew inputs to `calendar_sim`, then calendar-only OOS + B3/B4 cost falsification using the **registered** DNA config; reject the class for this data path if still fragile. No baseline-metric promotion. No shadow/live.

MOA_CHALL_DONE

# MOA BUILD lab executor closeout — 2026-07-11T2353

WAKE: 2026-07-11T2353 PDT
PHASE: BUILD
SLEEVE: 3000
EXECUTOR: GPT 5.6 Sol
MODE: paper/research only

## Chose

P1+P3: build and falsify one no-lookahead shared-position regime router over the existing PCS/CCS/IC engines, using the same event loop for standalone negative controls. This kept the prior NEXT because it was a higher-information combination test than another standalone proxy mutation.

## Hypothesis and falsifier

Hypothesis: bullish→PCS, bearish→CCS, neutral high-IV→IC, otherwise stand aside can improve after-cost path quality by avoiding each structure's hostile regimes.

Predeclared reject gate per symbol: synthetic claim labeled; completed population; one shared position; no future-row decision input; no same-bar re-entry; population purity; independent PnL/DD recomputation; 1-lot max loss ≤$300; dense non-vacuous 5% after-cost SHIP; positive non-vacuous $0.01-per-leg result; B3 soft hold; window max DD ≤$75; dense-negative windows ≤5; and competitive same-loop standalone controls.

## Built

- `trader_platform/research/regime_router_sim.py`
  - current-row-only route selector
  - shared open position across PCS/CCS/IC
  - close-bar re-entry prohibition
  - structure-specific management config
  - routing-purity, violation, and overlap counters
- `scripts/pcs_regime_router_lab.py`
  - exact eight-symbol population completion reporting
  - baseline, 5% adverse mark slip, and fixed $0.01 half-spread per leg
  - yearly + non-overlapping 126-bar windows
  - identical-loop standalone PCS/CCS/IC controls
  - independent ledger PnL/DD recomputation
- `tests/test_regime_router_sim.py`
  - route/stand-aside boundaries
  - shared-position/no-close-bar-reentry behavior
  - future-regime mutation negative control proving prior entries do not change

## Evidence

Primary: `.cache/platform/regime_router_lab_2026-07-11T2353.json`

Population: requested/completed **8/8** — TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ; errors **0**. Every baseline/5%/fixed policy ledger independently reproduced simulator PnL and DD exactly. Router routing violations **0** and same-bar re-entries **0** throughout.

| Symbol | Baseline n / PnL / DD | 5% n / PnL | $0.01/leg n / PnL / DD | Window DD | Decision driver |
|---|---:|---:|---:|---:|---|
| TSLL | 6 / +$34.22 / $89.49 | 3 / +$73.65 | 5 / +$86.77 / $21.28 | $89.49 | sparse; DD gate fail |
| SMCI | 20 / −$255.56 / $441.45 | 4 / −$226.23 | 18 / −$266.03 / $384.81 | $174.56 | cost + DD fail |
| TSLA | 12 / +$91.34 / $90.63 | 0 / $0 | 12 / +$44.68 / $94.63 | $90.63 | 5% vacuous; DD fail |
| PLTR | 21 / +$328.76 / $107.51 | 1 / −$3.34 | 19 / +$205.03 / $111.51 | $107.51 | cost density + DD fail |
| AAPL | 53 / −$413.93 / $538.75 | 0 / $0 | 18 / +$145.87 / $101.97 | $423.95 | baseline, cost, DD, dense-neg fail |
| AMD | 26 / −$318.34 / $502.45 | 0 / $0 | 23 / −$335.34 / $444.50 | $454.18 | baseline, cost, DD fail |
| ARM | 22 / +$161.08 / $142.27 | 0 / $0 | 20 / +$117.43 / $160.93 | $142.27 | 5% vacuous; DD fail |
| QQQ | 4 / −$79.03 / $128.68 | 0 / $0 | 1 / +$23.96 / $0 | $69.19 | sparse/vacuous and no control edge |

No symbol passed all gates. Five-percent slip left only 0–4 trades per symbol; fixed-dollar sensitivity preserved some positive rows but none combined density with window DD ≤$75. The router also often collapsed to one accepted structure despite three routing branches, so headline regime selection is not yet evidence of a genuinely mixed-direction population.

Test evidence:

- `.venv/bin/python -m unittest tests.test_regime_router_sim -v` → **3/3 pass**
- targeted related suite (`test_regime_router_sim`, direction scoreboard, expiry grid, fixed cost) → **15/15 pass**
- full discovery → **52/53 pass**; sole failure is the pre-existing unrelated PMCC fixture assertion (`test_assemble_pmcc_desk_live_yaml`, upside −0.5 expected >0)
- py_compile for router + lab → pass

## Judgment

Decision: **REJECT_ROUTER_FAMILY_THIS_CYCLE**. No registration, promotion, capital seat, shadow, or live action. There is no living quality leader, so absolute gates applied; historical `b195f5fe` was not treated as a seat.

Evidence level: **L0**. This is valid synthetic discovery and simulator capability, not L1, because no row has dense non-vacuous after-cost SHIP plus the absolute DD gate, and observed quote archives remain only one market date.

Progress type: **P1+P3**. Score: **4/5** — novel tested capability plus decisive multi-symbol falsification and no overclaim; no candidate advanced.

## Durable

- Direction-router capability and rejection are documented in `docs/BUILD_LAB_ENVIRONMENT.md` and `docs/INCOME_STRATEGY_COVERAGE.md`.
- Coverage generator now reports the router and its rejection rather than calling the direction axis only a scoreboard.
- Readiness remains BUILD/L0 with no living leader.

## Freedom audit

No prompt rule or tooling constraint blocked a higher-information valid experiment. The one-date observed archive prevented observed-contract L1 claims but did not block this labeled synthetic falsification. The 5% percentage-cost axis became mostly vacuous, so the lab also used the existing fixed-dollar per-leg axis rather than pretending vacuity was survival.

## ONE NEXT SEED

Build one entry-acceptance funnel for this router that records selected structure and exact rejection reason (IV, contract/strike, credit floor, max loss, or regime gate) on the same eight-symbol stream; do not tune DNA until the funnel proves whether CCS/IC routing is actually testable rather than silently collapsing to PCS/stand-aside.

GATES: none. No live / broker / agentic arm / shadow auto-promote.

MOA_EXEC_DONE

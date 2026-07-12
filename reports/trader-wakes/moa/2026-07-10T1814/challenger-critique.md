# MoA challenger critique — 2026-07-10T1814

**Role:** CHALLENGER (GPT) — read-only judgment
**Phase:** BUILD · Sleeve USD 3000 · paper/research only

## VERDICT_PER_HYP

| hyp | capital_fit honesty | defined risk | falsification | no overclaim | one next loop | no live/shadow promote | verdict — one-line why |
|---|---|---|---|---|---|---|---|
| TSLL PCS `b195f5fe` | PASS — 1-lot max loss $76.32 is `fit_3k` | PASS — $1 put vertical | PASS — B3/B4 numbers are present | PASS — executor leaves status `testing`, B6 partial, B7 fail | PASS — conditional OPEN_PCS/STAND_ASIDE is one RTH evaluation | PASS | **KEEP, but only as relative quality leader:** full SHIP +$115.90, yet 2026 is −$50.28, 2% slip is already NULL (+$14.57), and 5% slip is NULL/−$18.32. |
| MU PCS `55c7323a` | **FAIL — wording:** max loss $193.91 and open-risk fit are `fit_3k`; calling the capital label `research_toy` conflates fundability with failed quality | PASS — $2 put vertical | PASS — regime false and cost false are explicit | PASS — no promotion despite +$784.73 vanity SHIP | PASS — not added to seed | PASS | **RELABEL DISPOSITION, not capital fit:** keep `fit_3k`; reject from capital path/research-only because worst window −$409.31, window DD $499.57, and 5% slip −$192.58. |
| MU PCS `efca45f7` | PASS — 1-lot max loss $194.14 fits the sleeve/open-risk budget | PASS — $2 put vertical | PASS — soft B3/B4 plus adverse windows are shown | PASS — NULL@5% is correctly treated as edge erasure, not survival proof | PASS — not added to seed | PASS | **KEEP research-only:** `fit_3k` does not rescue $459.80 window DD, −$345.72 worst window, or zero trades/zero P&L at 5% slip. |
| BAC CCS `e6728888` | PASS — 1-lot max loss $81.69 is `fit_3k` | PASS — $0.50 call vertical | PASS — full-period and window/cost numbers are present | PASS — vacuous cost hold is not called edge | PASS — not added to seed | PASS | **PARK:** defined and fundable, but full-period NULL/−$107.36; 5% slip has zero trades, so `cost_hold=true` supplies no positive edge evidence. |

Evidence: `.cache/platform/stress_regime_defined_risk.json` and `.cache/platform/stress_cost_defined_risk.json`.

## DISAGREEMENTS with executor

1. **Do not relabel MU `55c7323a` capital fit as `research_toy`.** The regime JSON reports `capital_fit=fit_3k`, max loss $193.91; the registry evidence reports open-risk fit and max_lots=3. Its failure is quality, not fundability. Surgical merge wording: `fit_3k; research-only / capital-path rejected`.
2. **“Quality leader” must remain relative, not confident.** For `b195f5fe`, regime JSON has five negative dense windows, 2026 P&L −$50.28, and worst window −$54.30. Cost JSON turns the baseline SHIP into NULL at 2% slip (+$14.57) and NULL/−$18.32 at 5%. It is the best of this challenged set and the only justified B6 target, not live-ready evidence.
3. **Agree with the executor’s MU/BAC rejection.** `55c7323a` fails both holds; `efca45f7` has much worse max-loss/DD than the leader and no 5% activity; BAC has no baseline edge. Giving any of them a capital-path seat for diversification would be diversify-for-fear.
4. **Agree on gate honesty.** No fresh B6 fill was produced, B6 remains partial, B7 remains fail, and no shadow/live status changed.

## MERGE_ACTIONS

| action | target | merge instruction |
|---|---|---|
| keep | TSLL PCS `b195f5fe` | Keep `testing` and sole next-RTH B6 evaluation target; describe as relative quality leader only. |
| demote | MU PCS `55c7323a` | Reject from capital path; leave `candidate`; do not promote from raw SHIP score/trade density. |
| relabel | MU PCS `55c7323a` disposition | Replace “research_toy” capital wording with `capital_fit=fit_3k; research-only / quality-rejected`. No registry rewrite required. |
| keep | MU PCS `efca45f7` | Keep `candidate`, research-only; soft holds do not beat leader ml/DD or preserve edge under cost. |
| keep | BAC CCS `e6728888` | Keep `candidate`, parked NULL edge. |
| rewrite_next_seed | wake/readiness NEXT | Use exactly the single conditional RTH B6 loop in `merged-next-seed.md`; no optional BUILD branch. |

## RUBRIC_SCORECARD

| # | rubric | score | why |
|---|---|---|---|
| 1 | capital_fit honesty | **FAIL, surgical wording fix** | Executor’s `research_toy` label for MU `55c7323a` conflicts with explicit `fit_3k`/$193.91 defined risk; quality rejection should be separate. Other labels are honest. |
| 2 | defined-risk preferred for $3k | **PASS** | All four challenged structures are PCS/CCS verticals with explicit 1-lot max loss. |
| 3 | falsification quality | **PASS** | Fresh regime and cost JSON contain full, window, DD, max-loss, and slip outcomes for every hyp. |
| 4 | no overclaim | **PASS with caution** | Executor preserves B6 partial/B7 fail; merge narrows “quality leader” to a relative label because cost sensitivity is weak. |
| 5 | next seed is ONE closed loop | **PASS after merge wording** | One RTH evaluation with a conditional OPEN_PCS-or-STAND_ASIDE result; optional BUILD language is excluded. |
| 6 | no live/shadow promotion without gates | **PASS** | No live, arm, shadow, or status promotion occurred. |

**Overall:** accept executor evidence and ranking, with one surgical semantic correction: MU `55c7323a` is fundable (`fit_3k`) but quality-rejected, not a capital-unfit research toy.

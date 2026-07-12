# MoA CHALLENGER critique — 2026-07-10T0743

ROLE: CHALLENGER (GPT / openai-codex)
PHASE: BUILD | SLEEVE: 3000 | Read-only judgment; no evolve, broker, live, shadow, or hyp-registry write

## VERDICT_PER_HYP

| hyp | verdict | one-line why |
|---|---|---|
| `hyp_dna_tsll_put_credit_spread_b195f5fe` | **PASS — KEEP #1 for B6 evaluation only** | Defined-risk 1-lot max loss is about $76–77; full history is SHIP (n=57, +$115.90), but five dense negative regime windows and 5% slip NULL/−$18.32 mean this is a soft-hold paper candidate, not live-ready. |
| `hyp_dna_amd_iron_condor_b3056133` | **FAIL — DEMOTE current DNA from first-money/first-paper** | The 1-lot IC fits $3k, but execution-cost falsification is decisive: 2% slip REJECT/−$965.12 and 5% slip REJECT/−$2,567.58; calling for generic “more stress” is weaker than marking the present DNA cost-rejected. |
| `hyp_dna_xom_call_credit_spread_77766a47` | **PASS — KEEP PARKED #2** | Defined-risk 1-lot max loss is about $202–204; regime soft-hold and 2% slip SHIP/+$150.96 support continued research, while 5% slip NULL/−$68.13 and the incomplete CCS OPEN path prohibit first-paper or promotion. |

## DISAGREEMENTS with executor

1. **`max_lots=3` is not honest against the stated per-trade max-loss budget for AMD and XOM.** The registry reports AMD `max_loss_usd=173.7, max_lots=3` and XOM `max_loss_usd=202.44, max_lots=3` (`trader_platform/data/hypotheses.yaml:3128-3134, 4218-4228`). Three baseline lots imply $526.41 AMD risk and $607.38 XOM risk; under the cost ladder the three-lot worsts are $647.10 and $612.81. `capital_fit_pcs()` computes `max_lots` from sleeve/open-risk only and omits `max_loss_budget_usd` from the lot calculation (`trader_platform/research/pcs_sim.py:54-64`). **Keep the 1-lot `fit_3k` labels; do not relabel as research toys.** Surgical future fix: include `floor(max_loss_budget_usd / max_loss_usd)` in `max_lots`, yielding 1 lot for AMD and XOM and 3 for TSLL under these inputs. No registry rewrite in this merge.
2. **AMD is cost-rejected now, not merely waiting for unspecified “more stress.”** `.cache/platform/stress_cost_defined_risk.json:179-250` shows REJECT already at 2% slip (−$965.12, DD $1,044.02) and at 5% slip (−$2,567.58, DD $2,542.90), with `cost_hold=false`. Keep it as a research candidate if desired, but demote its current DNA from the first-capital path until a narrow simulator-audit or explicitly changed DNA earns a fresh test.
3. **“Cost hold” must stay explicitly soft.** TSLL and XOM are both negative/NULL at 5% slip, and 10% produces zero trades rather than demonstrated profitability (`stress_cost_defined_risk.json:83-126, 322-366`). The executor mostly says this correctly; readiness B4 PASS must not be read as cost-robust SHIP or income evidence.
4. **The executor NEXT seed is a menu.** `executor-closeout.md:81-87` contains five branches (PCS paper, CCS parking, IC exclusion, optional audit, no evolve/live), failing the one-closed-loop rubric. Merge it to one B6 condition-evaluation loop only.
5. **The ordering TSLL PCS > XOM CCS is acceptable only as an execution-readiness ranking.** XOM is stronger at 2% slip (SHIP/+$150.96 versus TSLL NULL/+$14.57), but TSLL has lower 1-lot risk and the wired `OPEN_PCS` path. It is not evidence that TSLL has the stronger cost-adjusted edge.

## MERGE_ACTIONS

| target | action | merge judgment |
|---|---|---|
| TSLL PCS `b195f5fe` | **keep** | Keep `testing`; B6 evaluation only; 1 lot; no shadow/live. |
| AMD IC `b3056133` | **demote** | Demote current DNA from first-paper/first-money ranking as cost-rejected; no YAML status change required. |
| XOM CCS `77766a47` | **keep** | Keep parked `candidate` #2; no paper action until an honest multi-leg CCS OPEN path exists. |
| Capital labels | **keep** | All three remain `fit_3k` at 1 lot; no `research_toy` relabel. Flag AMD/XOM `max_lots=3` as misleading under the $300 per-trade budget; surgical systems fix later. |
| NEXT seed | **rewrite_next_seed** | Replace the executor menu with one non-bear RTH B6 evaluation of TSLL PCS `OPEN_PCS`, 1 lot, ending in one logged paper intent/fill or an honest stand-aside. |

## RUBRIC_SCORECARD

Legend: PASS/FAIL judges the executor claim for each hyp; global seed failures are repeated because the fixed rubric requires a score per hyp.

| # | rubric | TSLL PCS | AMD IC | XOM CCS |
|---:|---|---|---|---|
| 1 | capital_fit honesty | **PASS** — 1-lot fit and stated risk are consistent; 3 lots also remain below $300 baseline/worst-slip risk. | **FAIL** — `fit_3k` is right at 1 lot, but reported `max_lots=3` conflicts with the $300 per-trade max-loss budget. | **FAIL** — `fit_3k` is right at 1 lot, but reported `max_lots=3` conflicts with the $300 per-trade max-loss budget. |
| 2 | defined-risk preferred for $3k | **PASS** — PCS has bounded max loss. | **PASS** — four-leg IC has bounded max loss. | **PASS** — CCS has bounded max loss. |
| 3 | falsification quality | **PASS** — full, window, and 0/2/5/10% slip numbers are present. | **PASS** — regime soft-hold and severe cost rejection are numeric. | **PASS** — full, window, and 0/2/5/10% slip numbers are present. |
| 4 | no overclaim | **PASS** — executor keeps it testing and separates B6/B7. | **PASS** — executor does not promote it, though “needs more stress” is too gentle. | **PASS** — executor parks it pending the CCS path and separates gates. |
| 5 | next seed is one closed loop | **FAIL → FIXED IN MERGE** — executor supplied a five-item menu. | **FAIL → FIXED IN MERGE** — same global seed defect. | **FAIL → FIXED IN MERGE** — same global seed defect. |
| 6 | no live/shadow promotion | **PASS** — none. | **PASS** — none. | **PASS** — none. |

Overall: keep TSLL as the sole next B6 evaluation target; keep XOM parked; demote the current AMD IC DNA from the capital path. SHIP is simulation evidence only. B6 remains partial and B7 remains fail.

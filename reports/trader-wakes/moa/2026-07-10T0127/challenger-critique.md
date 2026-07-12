# MoA CHALLENGER critique — 2026-07-10T0127

ROLE: CHALLENGER (GPT / openai-codex)
PHASE: BUILD | SLEEVE: 3000 | Read-only judgment; no broker; no evolve --apply

## VERDICT_PER_HYP

| hyp_id | verdict | one-line why |
|---|---|---|
| hyp_dna_tsll_put_credit_spread_b195f5fe | PASS | Defined-risk PCS, full-history SHIP n=57 pnl=115.90 max_loss=$76.32 fit_3k; regime_hold=True with 5 dense-negative windows worst=-54.30; cost_hold=True though 5% slip is NULL/-18.32, so paper-only B6 not live-ready. |
| hyp_dna_xom_call_credit_spread_77766a47 | PASS | Defined-risk CCS, full-history SHIP n=74 pnl=414.67 max_loss=$202.46 fit_3k; regime_hold=True with 4 dense-negative windows worst=-66.85; cost_hold=True with 2% still SHIP but 5% NULL/-68.13; second path only until CCS OPEN path is proven. |
| hyp_dna_amd_iron_condor_b3056133 | FAIL | Capital label fit_3k is honest on max_loss ($175.47 base, $200.84 at 5% slip), but edge fails cost stress: cost_hold=False, 2% slip REJECT/-965.12, 5% REJECT/-2567.58; demote from first-paper/first-money despite defined-risk structure. |

## DISAGREEMENTS with executor

1. NEXT SEED must be one closed loop, not a menu. Executor closeout lines 80-86 list B6 PCS, XOM parking, AMD avoidance, optional IC audit, and no evolve/live. The merge should collapse this to a single B6 paper-readiness action: b195f5fe OPEN_PCS only, 1-lot, non-bear RTH, record stand-aside/fill evidence.
2. AMD IC should be labeled `cost_fragile / not_first_paper`, not merely `NEEDS_MORE_STRESS` if that phrase could imply it remains a near-term B6 candidate. Evidence: `.cache/platform/stress_cost_defined_risk.json` summary for b3056133 has `cost_hold=false`, `slip_5_verdict=REJECT`, `slip_5_pnl=-2567.58`, and 2% slip already `REJECT` with pnl=-965.12. I agree it is not a `research_toy` on capital mechanics because max_loss remains fit_3k.
3. The executor's rank b195f5fe > XOM CCS >> AMD IC is supported, but the phrase "best first-money example" should remain explicitly non-live. Evidence: readiness still has B6 partial and B7 fail; SHIP/B3/B4 is not a live packet.
4. No registry bulk rewrite is justified. The only surgical label worth merging is conceptual: AMD IC `capital_fit=fit_3k` stays, but any first-paper language should be replaced with `cost_fragile_not_first_paper` in future edits. Registry write not required for this challenger pass.

## MERGE_ACTIONS

| hyp_id | action | detail |
|---|---|---|
| hyp_dna_tsll_put_credit_spread_b195f5fe | keep | Keep as top B6 paper candidate; fit_3k and defined-risk labels are supported by regime/cost JSON. |
| hyp_dna_xom_call_credit_spread_77766a47 | keep | Keep as second diversified defined-risk path; do not paper until CCS multi-leg OPEN/risk path is verified. |
| hyp_dna_amd_iron_condor_b3056133 | demote | Demote from first-paper/first-money set due to cost fragility; keep capital_fit=fit_3k, do not relabel research_toy. |
| next_seed | rewrite_next_seed | Single closed loop: run/verify B6 live-clock paper path for b195f5fe OPEN_PCS only, 1-lot, non-bear RTH; record evidence; no XOM/AMD/IC audit unless this loop closes. |
| readiness NEXT | relabel | Patch NEXT only to remove stale "challenger merge may tighten labels" and replace menu wording with the single B6 loop. |

## RUBRIC_SCORECARD

| rubric | b195f5fe TSLL PCS | 77766a47 XOM CCS | b3056133 AMD IC |
|---|---|---|---|
| 1. capital_fit honesty | PASS — max_loss $76.32 base / $77.29 at 5% slip, fit_3k, no open-risk conflict. | PASS — max_loss $202.46 base / $204.27 at 5% slip, fit_3k, no open-risk conflict. | PASS — max_loss $175.47 base / $200.84 at 5% slip, fit_3k is mechanically honest; performance, not funding, is the failure. |
| 2. defined-risk preferred for $3k | PASS — put_credit_spread, 1-lot max_loss under 10% sleeve. | PASS — call_credit_spread, 1-lot max_loss under 10% sleeve. | PASS — iron_condor is defined-risk, but 4-leg costs make it fragile. |
| 3. falsification quality | PASS — regime_hold=True, dense neg=5, worst=-54.30; cost 0/2/5/10% present. | PASS — regime_hold=True, dense neg=4, worst=-66.85; cost 0/2/5/10% present. | PASS — regime_hold=True but cost stress falsifies edge clearly at 2% and 5% slip. |
| 4. no overclaim | PASS — keep testing/paper-only; B6/B7 separate. | PASS — second path only; paper path still partial. | PASS with wording fix — do not let SHIP/full-history wording override B4 fail. |
| 5. next seed is ONE closed loop | FAIL in executor text — executor gave a menu; merge rewrites to one B6 PCS loop. | PASS after merge — explicitly parked, not part of next loop. | PASS after merge — explicitly excluded from next loop. |
| 6. no live/shadow promotion | PASS — no live, no shadow, no broker. | PASS — no live, no shadow, no broker. | PASS — no live, no shadow, no broker. |

Overall challenger verdict: keep TSLL PCS as the only immediate B6 paper seed, keep XOM CCS as second-path evidence, demote AMD IC from near-term paper due to cost fragility. No live packet.

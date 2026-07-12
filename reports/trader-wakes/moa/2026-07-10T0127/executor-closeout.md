# MoA EXECUTOR closeout — 2026-07-10T0127

ROLE: EXECUTOR (Grok / xai-oauth)
PHASE: BUILD | SLEEVE: 3000 | No live / no broker / no shadow promote
CHOSE: Regime + cost stress + capital judgment on fit_3k defined-risk SHIP set (no evolve spam)

Re-run stamp vs prior MoA-exec `2026-07-10T0038` (same hyp set). Metrics reconfirmed; no new vanity evolve.

## Hyps under test

| hyp_id | symbol | structure | registry status | capital (registry) |
|---|---|---|---|---|
| hyp_dna_tsll_put_credit_spread_b195f5fe | TSLL | put_credit_spread | testing | fit_3k ml≈$76.29 max_lots=3 |
| hyp_dna_amd_iron_condor_b3056133 | AMD | iron_condor | candidate | fit_3k ml≈$173.7 max_lots=3 |
| hyp_dna_xom_call_credit_spread_77766a47 | XOM | call_credit_spread | candidate | fit_3k ml≈$202.44 max_lots=3 |

## Commands run (real)

```bash
.venv/bin/python scripts/pcs_regime_stress.py \
  --hyps "hyp_dna_tsll_put_credit_spread_b195f5fe,hyp_dna_amd_iron_condor_b3056133,hyp_dna_xom_call_credit_spread_77766a47" \
  --out .cache/platform/stress_regime_defined_risk.json

.venv/bin/python scripts/pcs_cost_stress.py \
  --hyps "hyp_dna_tsll_put_credit_spread_b195f5fe,hyp_dna_amd_iron_condor_b3056133,hyp_dna_xom_call_credit_spread_77766a47" \
  --out .cache/platform/stress_cost_defined_risk.json
```

No `--write-hyps` (prefer JSON evidence; avoid yaml dump churn).

## Evidence paths

- `.cache/platform/stress_regime_defined_risk.json` — `at=2026-07-10T08:27:54.812902+00:00`, period=5y, structures=[call_credit_spread, iron_condor, put_credit_spread]
- `.cache/platform/stress_cost_defined_risk.json` — `generated_at=2026-07-10T08:27:57.601830+00:00`, slips=[0,0.02,0.05,0.10], `preferred_under_cost=hyp_dna_tsll_put_credit_spread_b195f5fe`

## Capital / rank judgment table

Metrics from regime JSON `results[].summary` + `full_history`, cost JSON `results[].summary` + `by_slip`.

| hyp | regime_hold | n_neg dense (n≥3) | worst_window_pnl | max_dd_windows | cost_hold | slip_5 verdict/pnl | capital_fit honesty | judgment |
|---|---|---:|---:|---:|---|---|---|---|
| **b195f5fe** TSLL PCS | **True** | 5 | −54.30 | 74.85 | **True** | NULL / **−18.32** (`soft_loss_at_5pct_defined_risk`) | **fit_3k** full+windows; full ml=76.32 | **HOLD #1** — best first-money *example*; keep testing; no auto shadow/live |
| **77766a47** XOM CCS | **True** | 4 | −66.85 | 147.25 | **True** | NULL / **−68.13** (`soft_loss_at_5pct_defined_risk`) | **fit_3k** full+windows; full ml=202.46 | **HOLD #2** — diversified non-TSLL defined-risk; paper-safe only; higher ml than PCS; not first paper until CCS OPEN path solid |
| **b3056133** AMD IC | **True** | 7 | −47.97 | 253.85 | **False** | REJECT / **−2567.58** (`fragile_at_5pct_slip`) | Structure still **fit_3k** (ml≈175–216 under slip) but **edge dies under slip** (4-leg compound) | **NEEDS_MORE_STRESS** — demote off first-money / first-paper; not `research_toy` (can fund) but **cost_fragile** |

### Full-history reference (regime JSON `full_history`)

| hyp | verdict | n | pnl/c | dd | max_loss_usd | capital_fit |
|---|---|---:|---:|---:|---:|---|
| b195f5fe | SHIP | 57 | 115.90 | 78.39 | 76.32 | fit_3k |
| b3056133 | SHIP | 121 | 578.28 | 253.85 | 175.47 | fit_3k |
| 77766a47 | SHIP | 74 | 414.67 | 147.25 | 202.46 | fit_3k |

### Dense negative windows (regime stdout / results)

- **b195f5fe:** year_2026 (−50.28 n5); chunk6m_2024-03→09 (−40.28 n12); chunk6m_2025-09→2026-03 (−4.18 n11); canon normal_down; canon v_recovery
- **b3056133:** year_2026 (−5.68 n13); chunk6m_2023-08→2024-02 (−47.97 n17); chunk6m_2025-02→08 (−4.14 n20); canon huge_down / normal_down / normal_up / v_recovery
- **77766a47:** chunk6m_2022-08→2023-02 (−31.1 n4); chunk6m_2025-08→2026-02 (−10.46 n8); canon normal_up (−59.31 n4); canon v_recovery

### Cost ladder honesty (cost JSON by_slip)

- **TSLL PCS:** 0% SHIP +115.9 → 2% NULL +14.57 → 5% NULL −18.32 → 10% zero_trades. Soft hold. capital_fit stays fit_3k.
- **XOM CCS:** 0% SHIP +414.67 → 2% SHIP +150.96 → 5% NULL −68.13 → 10% zero_trades. Soft hold; 2% still SHIP (stronger mid than PCS).
- **AMD IC:** 0% SHIP +578.28 → 2% REJECT −965.12 (dd 1044) → 5% REJECT −2567.58 (dd 2543) → 10% REJECT −2998.67. **Not cost-hold.** Four-leg slip taxes wings; dense n amplifies total_pnl loss while per-trade max_loss stays ~$175–216 fit_3k.

## Rank for $3k first capital path

1. **b195f5fe** — tightest open risk + B3/B4 soft-hold + preferred_under_cost
2. **77766a47** — diversified non-TSLL CCS; regime+cost soft-hold; ml≈$202 ≤ open_risk $750
3. **b3056133** — regime soft-hold only; **cost fail** → further DNA/slip work, not first paper

No promote to shadow/live. Status stays testing/candidate.

## Durable residue this executor pass

- Reconfirmed multi-structure B3/B4 artifacts at stamp 0127 (same paths, fresh `at`/`generated_at`)
- Judgment unchanged vs 0038: b195f5fe > XOM CCS >> AMD IC cost_fragile
- No hyp yaml churn; challenger may request surgical evidence_links only if merge wants pins

## NEXT SEED (for challenger merge)

1. B6 paper on **b195f5fe OPEN_PCS only** (1-lot), non-bear RTH when filters pass.
2. Park **XOM CCS** as second path; only paper if multi-leg CCS OPEN is wired — not first paper.
3. Do **not** first-paper AMD IC mid-mark SHIP (cost_fragile / needs_more_stress).
4. Optional systems: IC slip realism audit in multi-leg sim only if challenger flags model bug vs economics.
5. No free evolve vanity pass; no live packet.

## GATES

none (red lane clean)

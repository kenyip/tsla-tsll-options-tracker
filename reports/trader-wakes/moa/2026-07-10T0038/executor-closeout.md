# MoA EXECUTOR closeout — 2026-07-10T0038

ROLE: EXECUTOR (Grok / xai-oauth)
PHASE: BUILD | SLEEVE: 3000 | No live / no broker / no shadow promote
CHOSE: Regime + cost stress + capital judgment on fit_3k defined-risk SHIP set (no evolve spam)

## Hyps under test

| hyp_id | symbol | structure | prior capital |
|---|---|---|---|
| hyp_dna_tsll_put_credit_spread_b195f5fe | TSLL | put_credit_spread | fit_3k ml≈$76 |
| hyp_dna_amd_iron_condor_b3056133 | AMD | iron_condor | fit_3k ml≈$174 |
| hyp_dna_xom_call_credit_spread_77766a47 | XOM | call_credit_spread | fit_3k ml≈$202 |

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

- `.cache/platform/stress_regime_defined_risk.json` (at ≈ 2026-07-10T07:39:26Z)
- `.cache/platform/stress_cost_defined_risk.json` (at ≈ 2026-07-10T07:39:31Z; preferred_under_cost=b195f5fe)

## Capital / rank judgment table

Metrics cited from JSON `results[].summary` (+ cost `by_slip` for slip_5).

| hyp | regime_hold | n_neg dense (n≥3) | worst_window_pnl | max_dd_windows | cost_hold | slip_5 verdict/pnl | capital_fit honesty | judgment |
|---|---|---:|---:|---:|---|---|---|---|
| **b195f5fe** TSLL PCS | **True** | 5 | −54.30 | 74.85 | **True** | NULL / **−18.32** (`soft_loss_at_5pct_defined_risk`) | **fit_3k** full+windows; ml range ≈70–78 | **HOLD** — best first-money *example*; keep `testing`; do not auto shadow/live |
| **77766a47** XOM CCS | **True** | 4 | −66.85 | 147.25 | **True** | NULL / **−68.13** (`soft_loss_at_5pct_defined_risk`) | **fit_3k** full+windows; ml range ≈150–203 | **HOLD** — second diversified defined-risk path (non-TSLL CCS); paper-safe only; higher ml than PCS |
| **b3056133** AMD IC | **True** | 7 | −47.97 | 253.85 | **False** | REJECT / **−2567.58** (`fragile_at_5pct_slip`) | Structure ml still **fit_3k** (≈145–216 under slip) but **edge dies under slip** (4-leg); total_pnl compound not single-lot blowup | **NEEDS_MORE_STRESS** — demote off first-money / first-paper rank; not `research_toy` (can fund) but **cost_fragile**; needs IC slip-aware DNA or accept research-only mid marks |

### Full-history reference (regime JSON `full_history`)

| hyp | verdict | n | pnl/c | dd | max_loss_usd | capital_fit |
|---|---|---:|---:|---:|---:|---|
| b195f5fe | SHIP | 57 | 115.90 | 78.39 | 76.32 | fit_3k |
| b3056133 | SHIP | 121 | 578.28 | 253.85 | 175.47 | fit_3k |
| 77766a47 | SHIP | 74 | 414.67 | 147.25 | 202.46 | fit_3k |

### Dense negative windows (regime)

- **b195f5fe:** year_2026 (−50.28 n5); chunk6m_2024-03→09 (−40.28 n12); chunk6m_2025-09→2026-03 (−4.18 n11); canon normal_down; canon v_recovery
- **b3056133:** year_2026 (−5.68 n13); chunk6m_2023-08→2024-02 (−47.97 n17); chunk6m_2025-02→08 (−4.14 n20); canon huge_down / normal_down / normal_up / v_recovery
- **77766a47:** chunk6m_2022-08→2023-02 (−31.1 n4); chunk6m_2025-08→2026-02 (−10.46 n8); canon normal_up (−59.31 n4); canon v_recovery

### Cost ladder honesty (cost JSON `by_slip`)

- **TSLL PCS:** 0% SHIP +115.9 → 2% NULL +14.57 → 5% NULL −18.32 → 10% zero_trades. Soft hold.
- **XOM CCS:** 0% SHIP +414.67 → 2% SHIP +150.96 → 5% NULL −68.13 → 10% zero_trades. Soft hold; 2% still SHIP (stronger mid than PCS).
- **AMD IC:** 0% SHIP +578 → 2% REJECT −965 (dd 1044) → 5% REJECT −2568 (dd 2543) → 10% REJECT −2999. **Not cost-hold.** Four-leg slip model taxes both wings entry/exit; dense trade count amplifies total_pnl loss even while per-trade max_loss stays ~$200.

## Rank for $3k first capital path

1. **b195f5fe** — fewest dollars of open risk + only prior B3/B4 pedigree + cost soft-hold
2. **77766a47** — diversified non-TSLL CCS; regime+cost soft-hold; ml≈$202 still ≤ open_risk $750
3. **b3056133** — regime soft-hold only; **cost fail** → research / further DNA stress, not first paper probe

No promote to shadow/live. Status stays testing/candidate.

## Durable residue this executor pass

- New multi-structure regime artifact: `stress_regime_defined_risk.json` (TSLL PCS + AMD IC + XOM CCS)
- New multi-structure cost artifact: `stress_cost_defined_risk.json`
- Readiness B3/B4 extended beyond single-name TSLL PCS for **XOM CCS**; AMD IC B4 **fail**
- Honest demotion of AMD IC from “second non-TSLL ready” narrative to **cost_fragile / needs_more_stress**

## Hyp YAML

Skipped whole-store write. Challenger may request surgical `evidence_links` only if merge wants registry pins.

## NEXT SEED (for challenger merge)

1. Prefer first paper-path / B6 work on **b195f5fe OPEN_PCS** (non-bear RTH) and/or **XOM CCS paper path** if multi-leg CCS OPEN is wired; do **not** first-paper AMD IC mid-mark SHIP.
2. Optional systems: IC slip realism audit in `pcs_sim` (is 5%×4 legs fair vs vertical?) — only if challenger flags model bug vs economic truth.
3. No free evolve vanity pass; no live packet.

## GATES

none (red lane clean)

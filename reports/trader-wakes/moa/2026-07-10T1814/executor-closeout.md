# MoA executor closeout — 2026-07-10T1814

**Role:** EXECUTOR (Grok) — sole writer
**Phase:** BUILD · Sleeve USD 3000 · paper/research only
**Loop:** Post-1648 better-trades discovery challenge — reconfirm B3/B4 on quality set; capital/rank judgment; one NEXT SEED
**No free-evolve · no live · no agentic arm · no shadow promote**

## Orient

| Source | State |
|---|---|
| LATEST 1648 | Better-trades discovery: research run5 + defined-risk evolve; MU/BAC DNA falsified vs quality leader |
| Readiness 1648 | BUILD; TOP capital = `b195f5fe`; MU 55c7323a vanity FAIL; efca45f7 soft but worse ml/dd; BAC NULL |
| Prior stress | `stress_*_mu_bac_quality_20260710.json` had all 4 hyps; **defined_risk** JSON still on 0743 set (b195f5fe/AMD/XOM) — missing MU/BAC |

**CHOSE:** Surgical re-run B3+B4 for the four challenge hyps into canonical defined_risk paths (not thrash evolve).

## Act (tools)

```bash
.venv/bin/python scripts/pcs_regime_stress.py \
  --hyps "hyp_dna_tsll_put_credit_spread_b195f5fe,hyp_dna_mu_put_credit_spread_55c7323a,hyp_dna_mu_put_credit_spread_efca45f7,hyp_dna_bac_call_credit_spread_e6728888" \
  --out .cache/platform/stress_regime_defined_risk.json

.venv/bin/python scripts/pcs_cost_stress.py \
  --hyps "hyp_dna_tsll_put_credit_spread_b195f5fe,hyp_dna_mu_put_credit_spread_55c7323a,hyp_dna_mu_put_credit_spread_efca45f7,hyp_dna_bac_call_credit_spread_e6728888" \
  --out .cache/platform/stress_cost_defined_risk.json
```

- No `--write-hyps` (prefer JSON evidence; avoid yaml dump churn).
- No evolve-tick / research-tick / paper place / status promote.

## Evidence (cite JSON)

- Regime (fresh): `.cache/platform/stress_regime_defined_risk.json` · `at` ≈ `2026-07-11T01:15:26Z` · hyp_ids = four challenge IDs
- Cost (fresh): `.cache/platform/stress_cost_defined_risk.json` · preferred = `hyp_dna_tsll_put_credit_spread_b195f5fe`
- Cross-check (1648 discovery, same numbers):
  `.cache/platform/stress_regime_mu_bac_quality_20260710.json`
  `.cache/platform/stress_cost_mu_bac_quality_20260710.json`

## Capital / rank judgment table

Quality bar (leader): **TSLL PCS b195f5fe** — 1-lot ml≈$76, window max_dd≈$75, soft regime+cost.

| hyp | full (regime JSON) | regime_hold | n_neg dense (n≥3) | worst window pnl | window max_dd | cost_hold | slip_5 verdict / pnl | capital_fit honesty | judgment |
|---|---|---|---|---|---|---|---|---|---|
| **TSLL PCS b195f5fe** | SHIP n=57 pnl=+115.9 | **True** | **5** | **−54.3** | **74.85** | **True** | NULL / **−18.32** (soft_loss_at_5pct_defined_risk) | fit_3k · ml≈**76.32** | **HOLD capital-path quality example** · status stays `testing` · not promote shadow/live |
| MU PCS 55c7323a | SHIP n=133 pnl=+784.73 | **False** | 6 | **−409.31** | **499.57** | **False** | NMD / **−192.58** (large_loss_at_5pct_fragile) | fit_3k · ml≈**193.91** (fits open-risk but **2.5×** leader loss) | **demote research_toy / reject capital path** — vanity dense SHIP |
| MU PCS efca45f7 | SHIP n=58 pnl=+300.27 | True (soft) | 4 | −345.72 | **459.8** | True (soft) | NULL / **0.0** (survives_5pct_slip = edge-erased null) | fit_3k · ml≈**194.14** | **hold research-only** — soft B3/B4 but **fails quality bar** (ml/dd ≫ leader); not diversify-for-fear seat |
| BAC CCS e6728888 | **NULL** n=41 pnl=**−107.36** | True (soft) | 6 | −57.77 | 67.88 | True (vacuous) | NULL / 0.0 on NULL baseline | fit_3k · ml≈**81.69** | **park / no edge** — regime soft only because losses shallow; full-period NULL; not capital path |

### Notes for challenger (pre-empt vanity / overclaim)

1. **Vanity SHIP:** MU 55c7323a full +$785 / n=133 is **not** a seat — regime_hold false (worst −409) + cost fragile@5%.
2. **Soft cost ≠ edge under slip:** efca45f7 `cost_hold` + slip_5 NULL@0 is **edge gone**, not “survives better than leader.” Leader keeps soft defined-risk loss (−18) with real baseline SHIP.
3. **BAC soft regime is not quality:** full NULL −107; cost_hold on zero edge is vacuous.
4. **B6/B7 honesty:** B6 still **partial** (no multi-session live-clock OPEN_PCS fill this wake — after-hours). B7 still **fail**. Do not claim paper sample complete.
5. **Diversify-for-fear:** No capital seat for MU/BAC solely for multi-name optics.

## Status / promote

| hyp | prior status | action |
|---|---|---|
| b195f5fe | testing | **unchanged** — quality capital example only |
| 55c7323a | candidate | **unchanged** — research_toy (capital reject) |
| efca45f7 | candidate | **unchanged** — research only |
| e6728888 | candidate | **unchanged** — park NULL edge |

No shadow/live. No agentic arm. No hyp yaml rewrite this wake.

## DECISION

Capital path **unchanged**. Reconfirm matches 1648 discovery falsify.
**Primary seed remains one closed RTH loop** on quality leader only.

## NEXT SEED (one closed loop — for challenger merge)

**Non-bear RTH:** one B6 quality eval — 1-lot paper OPEN_PCS for `hyp_dna_tsll_put_credit_spread_b195f5fe` **or** honest STAND_ASIDE. Log max_loss_usd + open_risk. Stop.
No multi-item menu. Optional BUILD tighter defined-risk hunt only if new evidence-backed redesign (not this seed).

## GATES

none (paper/research only)

## Paths written by executor

- `reports/trader-wakes/moa/2026-07-10T1814/executor-closeout.md` (this file)
- `reports/trader-wakes/2026-07-10T1814-moa-exec.md`
- `reports/trader-wakes/LATEST.md`
- `reports/trader-wakes/INDEX.md` (prepend)
- `reports/readiness/LATEST.md`
- `.cache/platform/stress_regime_defined_risk.json`
- `.cache/platform/stress_cost_defined_risk.json`

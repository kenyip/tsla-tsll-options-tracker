# Merged NEXT SEED — 2026-07-11T1400 MoA

**Source:** executor closeout kept; Grok challenger PASS 8/8 (metrics verified against dated multi-hyp time grid + BAC transient B3/B4 + regime/cost/quality lab JSON + evolve_audit + run26).

## NEXT SEED (ONE closed loop — BUILD only)

Resize the **BAC Friday 7-DTE PCS** transient (`source hyp_dna_bac_put_credit_spread_5f52fa0e`; filters: `entry_weekdays=[Fri]`, `long_dte=7`, `dte_stop=5`, label `profit_target=0.35` — PT is non-binding at current width) by **`spread_width` grid $2 → $1 → $0.50**. Rerun **exact transient B3+B4** (no registry mutation). **Reject** unless **all** hold:

1. non-vacuous **positive** 5% after-cost (n≫0, SHIP/positive pnl)
2. 1-lot **max_loss_usd ≤ 76.32**
3. B3 **window max_dd ≤ 74.85**
4. **dense-negative windows ≤ 5**

Constraints:
- Paper/research only — no live, broker, agentic arm, or shadow auto-promote
- Do **not** register/promote the current width=$2 BAC Fri row (after-cost +$690.05 but ml $184.55 / window DD $87.29)
- If both $1 and $0.50 miss L1 or go vacuous/fragile@5%, **reject the width path** (success-as-reject) — do not thrash further BAC PT/DTE polish this residue
- Prefer defined-risk transient stress over free single-leg-only pop36 thrash
- Do not retune assumed BS surfaces on rejected calendar/butterfly/debit/diagonal proxies
- RTH (if seed still open at open): condition eval / stand-aside / paper path only — no free evolve mid-RTH

## Capital / readiness pin

- Sleeve: $3000 · Phase: **BUILD / L0**
- Quality example (not L1): `hyp_dna_tsll_put_credit_spread_b195f5fe` (ml≈$76.32 / window max DD≈$74.85 / regime soft-hold / 5% soft loss −$18.32)
- This wake: multi-hyp cost-aware time grid built (864 @5%); BAC Fri 7d dense +$690.05@5% fails L1 ml/dd; calendar/butterfly/base BAC PCS quality-rejected
- `l1_hyp_ids=[]`

# Merged NEXT seed — 2026-07-11T2353 (MoA)

**ONE BUILD NEXT (highest information):**

Instrument and run one **entry-acceptance funnel** on the existing shared-position regime router (`regime_router_sim` / `pcs_regime_router_lab`) over the **same eight-symbol stream** (TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ).

For every bar with valid IV, record at least:

1. `regime` and `selected_structure` (PCS / CCS / IC / stand_aside from current-row rule only)
2. if selected: `entry_accept` boolean
3. if rejected: exact `reject_reason` among {iv_gate, contract_or_strike, credit_floor, max_loss, capital_fit, other_entry_filter} — do **not** fold entry rejects into bare `stand_aside`
4. aggregate selection rate and accept rate per structure × symbol

**Stop conditions / judgment:**

- Do **not** tune DNA, IV floors, credit knobs, or widths until the funnel shows CCS and IC are both *selected* and *entry-testable* at non-trivial rates on more than the AAPL exception.
- If funnel proves CCS/IC are almost never selected or almost always entry-rejected under default DNA, leave router capital search this cycle and pick an independent income axis next wake (do not retune into a PCS-only “router”).
- Zero-trade control PnL must be treated as NA in any control comparison, not 0.0.

**Parallel (not a substitute BUILD seed):** on the next distinct NY RTH market date, append all-expiration TSLL archive 1→2/3 market dates; no provider-backed historical simulation before 3/3.

**Hard stops:** paper/research only; no evolve DNA retune as primary; no live / broker / agentic arm / shadow auto-promote; no capital seat without dense non-vacuous after-cost + B3 + absolute ml/dd gates; no living quality leader today.

**Context kept from executor:** family REJECT_ROUTER_FAMILY_THIS_CYCLE; L0 synthetic; absolute gates; primary evidence `.cache/platform/regime_router_lab_2026-07-11T2353.json`.

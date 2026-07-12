# Go-live readiness scoreboard — 2026-07-10T0810 (Ken pin: better trades ≠ diversify-for-fear)

Source: `docs/GO_LIVE_READINESS.md`. Honest pass/fail. Not an arm.

**2026-07-10T0810 Ken pin:** Strive for **better trades**. Multi-name freedom is discovery, not a capital-path quota. **Diversify-for-fear is lazy.** If a hyp sits on the capital path only as a TSLL diversifier, **remove it**. Re-decided XOM CCS `77766a47`: **testing → candidate** (off capital path); B3/B4 soft-hold preserved for research retest if quality wins without diversifier rationale. AMD IC remains candidate (cost-fragile). TSLL PCS `b195f5fe` remains the quality capital example (tight 1-lot ml + soft holds) — not because plumbing was first. Paper-only; no live/agentic/fund.

**Prior 0758 Ken pin (still holds where compatible):** Rank by capital/regime/cost/falsify; plumbing readiness is parallel build debt, not a rank key. OPEN_CCS/OPEN_IC paper path remains build debt. **Superseded:** promoting XOM to testing *because* it is a non-TSLL multi-name peer.

**Prior 0743 MoA-exec stress (unchanged metrics):** All 3 regime_hold; b195f5fe + XOM CCS cost_hold; AMD IC cost_fragile. RTH still STAND_ASIDE on PCS (bear). B6 partial.

```text
PHASE: BUILD
SLEEVE_USD: 3000
PLATFORM: A1=pass A2=pass A3=partial A4=partial A5=pass A6=pass A7=pass
FREEDOM: symbol=universe_open strategy=catalog_open allowlists_empty
RANK_DOCTRINE: evidence=capital+regime+cost+falsify; plumbing=build_debt_not_rank_key
BETTER_TRADES_DOCTRINE: capital_path=independent_trade_quality; diversify_for_fear=lazy; multi_name=discovery_not_quota
STRESS_REGIME: .cache/platform/stress_regime_defined_risk.json — all 3 soft-hold (at 2026-07-10T14:43:49Z)
STRESS_COST: .cache/platform/stress_cost_defined_risk.json — XOM stronger @2% slip still true; not a diversifier seat
TOP_HYP_CAPITAL_PATH: hyp_dna_tsll_put_credit_spread_b195f5fe (PCS; 1-lot ml≈$76; B3/B4 soft-hold; testing) — quality example
TOP_HYP_RESEARCH_ONLY: hyp_dna_xom_call_credit_spread_77766a47 (CCS; B3/B4 soft-hold; status=candidate; demoted diversifier-only capital seat) ; hyp_dna_amd_iron_condor_b3056133 (IC; B4 fail cost; candidate)
STRATEGY_PCS: B1=pass B2=pass B3=pass B4=pass B5=pass B6=partial B7=fail
STRATEGY_CCS: B3=pass (soft) B4=pass (soft 5% −68) — research only; not capital path until quality re-earn
STRATEGY_IC: B3=pass (soft) B4=fail (fragile_at_5pct_slip) — DNA demoted for cost
STRATEGY_WHEEL: B1=partial B2=pass B3=partial B4=unknown B5=pass B6=fail B7=fail
OPPORTUNITY: C1=pass_session_day C2=stand_aside_filters C3=fresh C4=blocked_unfunded_agentic
BLOCKERS:
  - No multi-session closed paper sample yet (B6 partial)
  - No shadow window evidence (B7)
  - Agentic RH account ~$0 / no options level
  - AMD IC cost_fragile; XOM CCS off capital path (diversifier-only seat)
NEXT: Best trade quality seeds only (not multi-name quota). (1) One closed-loop non-bear RTH B6 paper eval of quality leader TSLL PCS b195f5fe OPEN_PCS 1-lot or STAND_ASIDE. (2) Research may hunt better non-TSLL DNA that beats quality bar without diversifier rationale. (3) Plumbing debt for OPEN_* remains parallel build — not a rank key. No evolve spam thrash; no shadow/live.
```

## Freedom + rank note (Ken 2026-07-09 / 2026-07-10)

Trader free on symbol/strategy for **discovery**. Capital path is **earned by trade quality**, not ticker count and not OPEN_* wiring order.

## A. Platform

| # | Check | Status | Evidence |
|---|---|---|---|
| A1 | smoke_test green | **pass** | prior 0758 smoke OK; registry reloaded after recovery |
| A2 | Risk limits for **$3k** | **pass** | risk_limits + capital_fit; empty instrument/strategy allowlists |
| A3 | Paper path durable | **partial** | Multi-leg PCS + CCS + IC intent/ledger shape; B6 samples still thin |
| A4 | Shadow propose→risk→log | **partial** | Smoke shadow only |
| A5 | Kill switch | **pass** | kill_switch_file + risk_governor |
| A6 | No secrets/positions in git | **pass** | positions YAML gitignored |
| A7 | Live disarmed | **pass** | agentic.enabled: false |

## B. Strategy — capital path example (quality, not exclusive forever)

| # | Check | Status | Evidence |
|---|---|---|---|
| B1 | capital_fit ≤3000; max_loss budget | **pass** | b195f5fe ml≈$76 @1-lot |
| B2 | Ship bar denseness | **pass** | full_history n=57 SHIP (sim) |
| B3 | Multi-regime stress | **pass** | soft-hold |
| B4 | Costs/slippage at 1-lot | **pass** soft | soft_loss_at_5pct |
| B5 | Invalidation + management DNA | **pass** | Defined max loss + ladder |
| B6 | Live-clock paper sample | **partial** | path wired; fills pending non-filter RTH |
| B7 | Shadow window | **fail** | Not run |

## B′. Defined-risk set (stress 0743 + re-decision 0810)

| Structure / hyp | B3 regime | B4 cost | Status / judgment |
|---|---|---|---|
| TSLL PCS b195f5fe | **pass** soft | **pass** soft | **testing** — capital-path quality example (tight ml + soft holds) |
| XOM CCS 77766a47 | **pass** soft | **pass** soft (2% SHIP) | **candidate** — demoted off capital path (diversifier-only seat under better-trades doctrine); research retest only |
| AMD IC b3056133 | **pass** soft | **fail** fragile | candidate; demote DNA for cost |

## C. Opportunity (last RTH 2026-07-10T0731; pin does not invent fills)

| # | Check | Status | Evidence |
|---|---|---|---|
| C1 | Session data freshness | **pass** | engine date=2026-07-10 |
| C2 | Capital-fit opportunity | **none** | PCS bear aside under filters |
| C3 | Eval usable (not stale) | **pass** | not multi-day freeze |
| C4 | Agentic fundable/live | **blocked** | unfunded / no options level |

## Phase decision

Stay **BUILD**. Better trades > diversify-for-fear. Evidence ranks DNA; plumbing is debt; multi-name is search space. No auto-promote. No live packet.

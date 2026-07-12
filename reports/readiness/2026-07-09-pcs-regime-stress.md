# Go-live readiness scoreboard — 2026-07-09 (daily BUILD: PCS regime stress)

Source: `docs/GO_LIVE_READINESS.md`. Honest pass/fail. Not an arm.

```text
PHASE: BUILD
SLEEVE_USD: 3000
PLATFORM: A1=pass A2=pass A3=partial A4=partial A5=pass A6=pass A7=pass
TOP_HYP_CAPITAL: hyp_dna_tsll_put_credit_spread_b195f5fe (defined-risk; best regime profile)
TOP_HYP_PNL_DENSE: hyp_dna_tsll_put_credit_spread_0514c2af (denser n; slightly more neg windows)
STRATEGY_PCS: B1=pass B2=pass B3=pass B4=unknown B5=pass B6=partial B7=fail
STRATEGY_WHEEL: B1=partial B2=pass B3=partial B4=unknown B5=pass B6=fail B7=fail
OPPORTUNITY: C1=na_after_hours C2=na C3=na C4=blocked_unfunded_agentic
BLOCKERS:
  - No multi-session closed paper PCS sample yet (B6 partial — path only)
  - No shadow window evidence (B7)
  - Costs/slippage sensitivity not quantified at 1-lot (B4)
  - Agentic RH account ~$0 / no options level
  - Cash CSP/wheel collateral still exceeds max_open_risk $750 (wheel path)
  - YTD 2026 partial-year weak across all three PCS hyps (stand-aside bias OK)
NEXT: Paper-probe OPEN_PCS when non-bear filters pass; optional B4 cost stress; no live packet
```

## A. Platform

| # | Check | Status | Evidence |
|---|---|---|---|
| A1 | smoke_test green | **pass** | prior smoke; PCS multi-leg risk/ledger OK |
| A2 | Risk limits for **$3k** | **pass** | `risk_limits.yaml` + capital_fit |
| A3 | Paper path durable | **partial** | Multi-leg PCS ledger; need live-clock fills |
| A4 | Shadow propose→risk→log | **partial** | Smoke shadow only |
| A5 | Kill switch | **pass** | kill_switch_file + risk_governor |
| A6 | No secrets/positions in git | **pass** | positions YAML gitignored |
| A7 | Live disarmed | **pass** | `agentic.enabled: false` |

## B. Strategy — defined-risk PCS (preferred $3k path)

| # | Check | Status | Evidence |
|---|---|---|---|
| B1 | capital_fit ≤3000; max_loss budget | **pass** | ml≈$74–113; open_risk uses max_loss |
| B2 | Ship bar denseness | **pass** | 2y/5y SHIP n=56–121 full history |
| B3 | Multi-regime stress | **pass** | yearly+6m+canon; all 3 soft-hold; 0 dense REJECT; see stress JSON |
| B4 | Costs/slippage at 1-lot | **unknown** | BS path; not yet stressed |
| B5 | Invalidation + management DNA | **pass** | Defined max loss + ladder |
| B6 | Live-clock paper sample | **partial** | Path wired; RTH STAND_ASIDE bearish — no fill yet |
| B7 | Shadow window | **fail** | Not run |

### PCS candidates (testing only) — regime stress 2026-07-09

| id | width | dte | δ | max_loss | full SHIP | neg windows ≥3 | worst window $ | hold |
|---|---|---|---|---|---|---|---|---|
| hyp_dna_tsll_put_credit_spread_b195f5fe | 1.0 | 21 | 0.20 | ~76 | n=57 pnl≈116 | 5 | −54 | **best** |
| hyp_dna_tsll_put_credit_spread_0514c2af | 1.0 | 14 | 0.25 | ~74 | n=121 pnl≈125 | 7 | −59 | hold |
| hyp_dna_tsll_put_credit_spread_fd407d4f | 1.5 | 21 | 0.25 | ~113 | n=92 pnl≈147 | 7 | −72 | hold |

Shared caveats: year_2026 partial weak (NULL/few trades); gap_shock / normal_down soft losses; capital_fit=fit_3k every window.
Artifact: `.cache/platform/stress_regime_tsll_pcs.json`. Runner: `just pcs-regime-stress`.

Doc: `docs/PCS_PAPER_PATH.md`.

## B′. Strategy — legacy wheel / naked short premium

| # | Check | Status | Evidence |
|---|---|---|---|
| B1 | capital_fit | **partial / fail for naked call** | capital_reject on levered undefined max_loss |
| RTH signal | SELL_CALL TSLL | **reject for sleeve** | risk_governor capital_fit |

## C. Opportunity (after hours 2026-07-09)

| # | Check | Status | Evidence |
|---|---|---|---|
| C1 | Day-of trade decision | **na** | after RTH; daily BUILD wake |
| C2 | Open sleeve risk | **none** | prior paper open_risk=0.0 |
| C3 | Regime | **na this wake** | last RTH: bearish high IVR; PCS STAND_ASIDE |
| C4 | Account ready | **blocked** | Agentic ~$0, no options level |

## Phase decision

Stay **BUILD**. B3 closed for top PCS DNA (regime soft-hold). Still need B6 paper sample + B7 shadow before LIVE_PACKET. Prefer `b195f5fe` as first capital-fit candidate. No shadow auto-promote. No live packet.

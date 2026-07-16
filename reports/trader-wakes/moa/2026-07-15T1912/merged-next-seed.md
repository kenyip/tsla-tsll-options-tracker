# Merged NEXT seed — 2026-07-15T1912

SOURCE: Grok 4.5 challenger merge of executor closeout + independent critique
PHASE: BUILD partial (challenger complete; finalizer pending)

## Accepted strategy outcome

Wake: `BLOCKER_REMOVED_AND_RETESTED`
Retest disposition: `FAMILY_CLOSED` — `MULTINAME_NO_RECENT_DOWNSHOCK_PCS_21D_V1` /
`noncollapse|recent_5d_downshock_exclusion|spy_and_symbol_sma100_uptrend|positive_60d_momentum|10_session_close_barrier_5pct|pcs_21d_2wide_planned`

Funnel: `F0_MECHANISM` → `F0_MECHANISM_CLOSED`
Authority: research/L0 only; no F1/F2/L1, capital seat, registry, paper force, shadow, arm, broker, live.

Evidence: `reports/trader-wakes/moa/2026-07-15T1912/downside-shock-stand-aside-train.json`
Train: 703 episodes (eligible 548 / recent-shock 155, all 8 symbols); holdout 412 unread (identity `acedd4c8…`); eligible 5% breach 27.0073% vs gate ≤10%; recent edge +8.4766pp vs stale placebo +14.5722pp; LB90 +2.14pp; integrity []; pricing_calls 0.

Reassessment: `docs/SEARCH_DESIGN_REASSESSMENT_2026-07-15T1912.md`
Epoch: `2026-07-15-tail-hazard-discovery` started_stamp `2026-07-15T1912`; completed wakes 1; consecutive no-advance 1; pivot/burst-stop false.

## Quarantine add

Exact family above. Reopen only with a new economic mechanism or independent evidence class — not nearby 2%/4% shocks, 3/7-session windows, or looser absolute breach ceilings. Holdout remains sealed.

## Exactly one NEXT

`LOW_DOWNSIDE_SEMIVARIANCE_ETF_BARRIER_HAZARD_F0`

Freeze a cross-sectional **low downside-semivariance** rank on lower-volatility liquid ETFs (SPY, QQQ, IWM, XLF, XLE, XLK, XLI, XLV) **before reading outcomes**. Primary endpoints: ten-session **5% close-barrier** survival and worst-decile path loss versus the high-downside-semivariance rank. Use date-blocked uncertainty and an untouched holdout. **Stop before option pricing unless the absolute eligible breach gate (≤10% or a predeclared capital-protective equivalent) passes.**

Hard constraints:
1. New family key and Layered Edge Stack — not a silent reopen of closed low-HV / monthly low-HV **mean-return** selectors.
2. Downside-semivariance (left-tail second moment), not plain HV, is the ranking feature.
3. Absolute non-collapse quality is decision-critical; relative rank edge alone cannot advance short-gamma income.
4. Close-only barrier labeled as lower fidelity than intraday lows/option marks; no L1/proxy-only seat claim.
5. Panel bias and partition methodology must be stated; freeze design before outcomes.
6. No registry, paper force, shadow, arm, broker, or live action.

## Finalizer obligations (not challenger work)

- Accept PASS WITH NITS dispositions above.
- Optionally repair: survivorship/listing bias label; stale/recent overlap methodology note; dedicated stale-placebo-fail negative control if code touched.
- Re-run focused + full suite; regenerate handoff/learning/readiness decision surfaces.
- Integrate only after verification; challenger does not commit/push/merge or claim RUN COMPLETE.

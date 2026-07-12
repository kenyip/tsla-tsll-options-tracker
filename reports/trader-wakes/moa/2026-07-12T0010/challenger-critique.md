# MOA BUILD lab challenger critique — 2026-07-12T0010

WAKE: 2026-07-12T0010 PDT
PHASE: BUILD
SLEEVE: 3000
CHALLENGER: Grok 4.5 (read-only)
MODE: paper/research judgment only — no evolve --apply, no broker, no arm

## Rubric

| # | Check | Verdict | One line |
|---|---|---|---|
| 1 | Goal progress | **PASS** | Completed the prior merged NEXT with a real diagnostic that supports an honest family leave; frees future discovery capacity rather than retuning a cost/DD-rejected router. |
| 2 | Creativity and independence | **PASS** | Axis was the justified continuation of the 2353 NEXT, not a familiar-recipe tunnel; leave decision + non-router NEXT are independent of TSLL PCS polish. |
| 3 | Claim validity | **PASS** | Synthetic daily-bar discovery only; no observed-contract, provider-backed, or L1 claim; population pure 8/8; absolute gates remain the bar with no living leader. |
| 4 | Evidence and test quality | **PASS** | Primary JSON + 5/5 behavioral tests + independent recompute of funnel aggregates match; reject labels are counterfactual single-gate with composite remainder labeled conservatively. |
| 5 | Falsification | **PASS** | Predeclared falsifier ran; hypothesis supported (CCS/IC selected heavily, rejected at entry); decision stays `REJECT_ROUTER_FAMILY_THIS_CYCLE` with no retune thrash. |
| 6 | Capital honesty | **PASS** | No hyp registered/promoted; no capital seat; ml $163–$205 sleeve-fit shapes are research envelope only; 1-lot posture; b195f5fe not treated as a living leader. |
| 7 | Research freedom | **PASS** | One-date archive correctly did not freeze this synthetic diagnostic; no unnecessary freeze of unrelated axes. |
| 8 | ONE NEXT seed | **PASS** (tightened) | Leave router is correct; collar scaffold is an original class, but capital/universe constraints must be first-class or the class fails closed before DNA polish. |

**Overall: PASS 8/8** (NEXT wording tightened in merge).

## Verified evidence

Primary artifact: `.cache/platform/regime_router_funnel_lab_2026-07-12T0010.json`

Independent inspect (challenger, this wake):

- `population.completed` = 8/8 requested symbols; `errors=[]`
- `decision` = `REJECT_ROUTER_FAMILY_THIS_CYCLE`; `passing_symbols=[]`
- Baseline aggregate funnel **exact match** to executor table:
  - PCS selected 360 / accepted 122 (33.89%); reject reasons credit_floor 110, max_loss_budget 59, contract_strike_or_nonpositive_credit 69
  - CCS selected 2427 / accepted 19 (0.78%); credit_floor 2145, contract… 242, max_loss_budget 21
  - IC selected 2592 / accepted 23 (0.89%); credit_floor 1926, contract… 597, max_loss_budget 46
- Accepted CCS only AAPL(15)+QQQ(4); accepted IC only AAPL(23) — not a selection-coverage gap
- Baseline router worst `max_loss_usd`/`capital_fit_usd` per symbol: TSLL 163.24 … AMD 204.92 (matches claimed $163.24–$204.92)
- All `entry_funnel` selected = accepted + rejected reconciliations checked with **0 bad** nodes in the artifact (full matrix 8×4 policies×3 modes = 96; additional window funnels also present and clean)
- Tests: `.venv/bin/python -m unittest tests.test_regime_router_sim` → **5/5 OK** (routing purity, no same-bar reentry, IV-rank counterfactual reject, arithmetic reconcile, invalid_iv fail-closed)
- Code presence: `entry_funnel` + `diagnose_entry_rejection` in `trader_platform/research/regime_router_sim.py`; lab wiring in `scripts/pcs_regime_router_lab.py`
- Coverage docs/generator already reflect funnel + leave guidance (`income-coverage-LATEST.md` direction-bias gap text)

## Challenges (non-blocking unless noted)

1. **Progress type is diagnostic, not a new L1 edge.** That is the right job for this seed, but the lab still has zero living quality leader. Score 4/5 is fair for closing a real uncertainty; do not inflate into discovery-of-edge.
2. **Credit-floor dominance is informative, not a retune invitation.** >99% CCS/IC reject at default credit floor under synthetic marks. Tuning that floor after family B3/B4/DD rejection would be thrash; executor correctly left the family.
3. **Counterfactual labels are single-gate, not full pricing duplicates.** Composite remainder `contract_strike_or_nonpositive_credit` is honest; do not over-claim precision of reason taxonomy.
4. **`max_lots=3` envelope vs 1-lot research posture.** Executor stated 1-lot / no seat — keep that when anyone re-reads capital_fit fields.
5. **NEXT collar capital trap (binding tighten).** A true collared covered-call is 100 shares + long put + short call. On a $3k sleeve, **stock notional is the capital path**, not only option max_loss. Current `universe.yaml` is thin for liquid **non-levered** sub-$30 names (TSLL is often sub-$30 but is a 2× product — poor share-hold candidate). Without an explicit stock-notional fit gate and a non-empty eligible name set, the next wake can build a sim that is structurally un-sizable for the sleeve.
6. **Readiness NEXT was stale.** Formal B checks unchanged (correct not to rewrite whole scoreboard), but the funnel instrument seed is **done** and readiness NEXT still pointed at it — patch required (see merge).

## No overclaim found on promotion

No live/shadow/agentic arm. No registry promote. No L1 claim. Family leave is evidence-backed.

## Judgment on executor self-score

Agree: **P1 diagnostic capability + explicit family leave**, score **4/5**, honesty **L0**.
Discovery-of-edge contribution is modest by design; learning quality is high.

## Merged ONE NEXT SEED (authoritative)

Leave the shared-position router family off capital search this cycle.

**Highest-information next BUILD:** scaffold a minimal paper-only **collared covered-call** (100 shares + long protective put + short call) with:

- `capital_fit_usd` = **full 100-share notional** (plus net option debit if any), not option max-loss alone
- 1-lot `max_loss_usd` = downside floor (stock−put strike) net of option premia; `max_lots`
- Eligible names: liquid **non-levered** symbols where `spot*100 ≤ 3000` (expand `universe.yaml` with 3–5 liquid sub-$30 optionable names if fewer than two current members qualify; **do not** default to TSLL share-hold)
- No-close-bar re-entry; dividends/assignment/early-exercise labeled limitations
- Immediate falsify: 5% leg slip + $0.01/leg fixed half-spread + absolute gates (non-vacuous after-cost SHIP, max loss ≤$300, window max DD ≤$75, dense-neg ≤5)
- **Fail closed before DNA polish** if no eligible names or class cannot meet stock capital fit
- Do **not** register proxy SHIP first; no capital seat without the full gate set

RTH parallel (not this BUILD seed): next distinct NY market date append all-expiration TSLL archive 1→2/3; no provider-backed historical sim before 3/3.

GATES: none. No live / broker / agentic arm / shadow auto-promote.

## Challenger progress stamp

Progress type: **P3 judgment + NEXT capital honesty patch on P1 diagnostic**.
Score: **4/5**.
Honesty: **L0** (no living quality leader; BUILD).

MOA_CHALL_DONE

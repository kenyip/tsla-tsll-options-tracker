# MOA BUILD challenger critique — 2026-07-12T2315

WAKE: 2026-07-12 ~23:50 PDT (Sunday; market closed)
PHASE: BUILD / L0
SLEEVE: $3,000
ROLE: Grok 4.5 challenger (read-only judgment)
PAPER_ONLY: true
OUTCOME: PASS 8/8 (nits only; no claim-invalidating defect)

## Scope checked

- `reports/trader-wakes/moa/2026-07-12T2315/meta.json`
- `reports/trader-wakes/moa/2026-07-12T2315/executor-closeout.md`
- `reports/trader-wakes/2026-07-12T2315-moa-exec.md` / `reports/trader-wakes/LATEST.md`
- `reports/readiness/income-coverage-LATEST.md` (20/245/67, no leader)
- `reports/readiness/LATEST.md` (executor preface + empty capital path)
- `.cache/platform/dividend_exdate_crosscheck_2026-07-12T2315.json`
- `.cache/platform/dividend_event_crosscheck_2026-07-12T2237.json` (prior issuer bound)
- `trader_platform/research/dividend_event_crosscheck.py`
- `scripts/dividend_exdate_crosscheck.py`
- `tests/test_dividend_event_crosscheck.py`
- `docs/DIVIDEND_EVENT_DATA_BOUNDARY.md`
- Doctrine: `docs/BUILD_LAB_ENVIRONMENT.md`, `docs/INCOME_STRATEGY_COVERAGE.md`, skill `trader-self-evolution`

## Independent verification (read-only)

- Offline exact-set recompute from live JSON rows + AAPL Nasdaq archive + issuer coverage window:
  - target 40 / source window 20 / matched 20 / missing 20 / unexpected 0
  - status `insufficient_bounded_coverage`; `qualified_fields=()`
  - decision `CLOSE_EX_DATE_ROUTE_INSUFFICIENT_COVERAGE` is the only honest outcome for the predeclared 40-event claim
- Focused unit suite re-run: `tests.test_dividend_event_crosscheck` → **14/14 OK** (includes new StockAnalysis parser + incomplete/complete independent ex-date controls)
- Working tree is on `trader/run-2026-07-12T2315` with uncommitted executor residue (expected for partial phase)
- Living quality leader remains **none**; no hyp/paper/shadow/arm/live mutation claimed or observed in residue

## Rubric

| # | Criterion | Verdict | One line |
|---|---|---|---|
| 1 | Goal progress | **PASS** | Decisive route-close + durable stop rule frees BUILD from AAPL ex-date thrash and adds reusable fail-closed provenance tooling. |
| 2 | Creativity / independence | **PASS** | Prior NEXT was a justified stop-or-redirect test, not tunnel; close then redirect to a new structure class is correct independence. |
| 3 | Claim validity | **PASS** | Intersection 20/20 never promoted to 40-event completeness; issuer known_at/amount/identity stay as previously bounded; no L1/assignment/capital claim. |
| 4 | Evidence / test quality | **PASS** | Live dated JSON + exact-set gate + identity/source/schema/duplicate/incomplete/complete field-scope tests; labels and fail-closed semantics hold. |
| 5 | Falsification | **PASS** | Predeclared full-interval hypothesis, explicit coverage falsifier, honest `CLOSE_EX_DATE_ROUTE_INSUFFICIENT_COVERAGE`. |
| 6 | Capital honesty | **PASS** | No living leader, no seat, no invented capital_fit/max_loss/max_lots for a non-trade loop. |
| 7 | Research freedom | **PASS** | Only the narrow no-auth AAPL ex-date route closed; symbol/strategy freedom and unrelated historical-underlying/sim work remain open. |
| 8 | ONE NEXT seed | **PASS** | One L0 defined-debit double-diagonal scaffold + dual-cost chronological reject-unless is a valid high-info redirect; tighten wording below. |

**Score: 8/8 PASS** (nits optional for finalizer; none claim-invalidating)

## What the executor got right

1. **Chose the right stop-rule loop.** Goal text and prior merged NEXT both required a bounded inventory with quick close; executor did not open a multi-wake source hunt.
2. **Field-scoped exact-set semantics.** Qualify `ex_date` only on complete target-set equality; amount deliberately ignored for qualification (complete-path test uses amount 999) — correct anti-overclaim design.
3. **Window definition is coherent.** Target set is archive events with `known_at` in the issuer-qualified interval; source window is min/max target *ex_date* (so 2026-05-11 is inside the target ex span even though announcement end is 2026-04-30). Offline recompute confirms missing list is the first 20 targets.
4. **Durable doctrine update.** `docs/DIVIDEND_EVENT_DATA_BOUNDARY.md` and income-coverage gaps now state partial-L0 route close and forbid reopening via equivalent aggregator browsing.
5. **Capital / promotion hygiene.** Capability-only wake; BUILD/L0; empty capital path preserved.

## Nits (optional repair; do not block)

1. **Unexpected-date negative control missing.** Parser/incomplete/complete paths are tested, but there is no dedicated test that a source date inside the min/max ex window but outside the target set yields `ex_date_conflict` and empty `qualified_fields`. Low risk (logic is simple set difference) — finalizer should add one small control.
2. **StockAnalysis chronology/row-shape boundary tests.** Parser enforces `ex ≤ record ≤ pay` and positive finite amount at runtime, but unit coverage only hits identity/source/header/duplicate. Optional: one malformed chronology row and one bad amount assert.
3. **Inventory audit trail is prose-only.** Macrotrends / CMC / Investing / DividendMax / Yahoo rejects are narrative in the closeout and boundary doc. Not claim-invalidating (decisive evidence is the StockAnalysis 20/40 artifact), but a tiny JSON inventory note would make the “six-page” claim fully machine-auditable.
4. **Double-diagonal NEXT needs anti-fragility constraints.** Four-leg BS proxies (calendar/diagonal/IB/debit) have repeatedly cost-collapsed. NEXT is acceptable as a missing structure class, but must be predeclared DNA + dual-cost + absolute gates + L0 + no registration on first pass + no-same-bar reentry + exact four-leg cost accounting — not a knob polish invitation.

## Claim-invalidating defects

**None found.**

Do not reopen the closed no-auth AAPL ex-date route with equivalent aggregators. Do not treat 20/20 overlap as partial field qualification for the 40-event claim. Do not promote, paper, shadow, arm, or live from this residue.

## Judgment on executor NEXT

Accept direction: leave dividend provenance and open a **simulator-capability** loop.

Tighten to:

> Build one minimal paper-only `double_diagonal_spread` defined-debit BS/daily-bar scaffold (catalog + sim + smoke + exact four-leg % and fixed-$0.01 costs + no-same-bar reentry + one-lot `max_loss_usd`≤$300). Run **one** predeclared multi-symbol chronological dual-cost falsification; reject the class unless both cost axes are non-vacuously positive with window DD≤$75 and dense-neg≤5. Keep all results **L0**; do not register proxy SHIP, reopen AAPL ex-date inventory, reopen closed daily-bar proxy families, or paper/shadow/arm/live.

## Freedom audit

No removable over-restriction introduced. Closed family is correctly narrow: no-auth / explicitly labeled / full 40-event AAPL ex-date completeness. Paid/credentialed/filing-derived reopen requires a genuinely new source class covering 2016-08-04–2021-05-07 targets.

## Phase status

Challenger partial phase only. No commit, push, merge, evolve `--apply`, broker, shadow, arm, or live. Finalizer must repair accepted nits (if any), re-verify, promote learning, then deterministic integration.

MOA_CHALL_DONE

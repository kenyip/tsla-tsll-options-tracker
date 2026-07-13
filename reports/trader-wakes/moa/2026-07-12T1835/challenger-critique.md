# MOA BUILD challenger critique — 2026-07-12T1835

> **Finalizer disposition:** The first-event orphan below was accepted and repaired with earliest-`known_at` coverage plus pre-ex service/post-observation tamper tests. Split amount/security-class warnings remain explicit L0 blockers; MU/AAL inventory remains ineligible without archive/identity proof; the source pitfall was promoted to `trader-self-evolution`. Final verification is focused 25/25, smoke green, full 155/155, handoff green. Historical probes and 24/24/154/154 challenger results below are preserved as phase evidence.

WAKE: 2026-07-12 ~21:10 PDT re-verify (original residue ~18:50; market closed)
PHASE: BUILD / L0
SLEEVE: $3,000
ROLE: Grok 4.5 challenger (read-only judgment)
PAPER_ONLY: true
OUTCOME: CAPABILITY accepted with minor nits

## Rubric

| # | Criterion | Verdict | One line |
|---|---|---|---|
| 1 | Goal progress | **PASS** | Closes the prior 1806 NEXT’s honest `known_at` provider gap for supported eventful listings; unlocks claim-honest required-mode wiring without inventing edge. |
| 2 | Creativity / independence | **PASS** | Justified continuation of 1806 NEXT on an open capability route; inventory + fail-closed archive, not closed-family retune or TSLL monomania. |
| 3 | Claim validity | **PASS** | CAPABILITY_ONLY only; no L1/B3/B4/candidate/capital mutation; unsupported/ambiguous sources fail closed; proxy marks still L0. |
| 4 | Evidence and test quality | **PASS** | Real code/CLI/archive/smoke paths cited; challenger re-ran focused 24/24, smoke green, full 154/154; tests cover declaration mapping, fail-closed, tamper, no-leak. |
| 5 | Falsification | **PASS** | Predeclared falsifiers exercised (SMCI ambiguous, TSLL unsupported, missing/future declaration, row-count/coverage tamper); none opened a false coverage claim. |
| 6 | Capital honesty | **PASS** | No living leader, no seat language, no trade-shaped capital fields invented; readiness stays BUILD/L0. |
| 7 | Research freedom | **PASS** | One-date TSLL option archive did not freeze this capability loop; Nasdaq support is not an instrument allowlist; other routes remain open. |
| 8 | ONE NEXT seed; no live/shadow | **PASS** | Independent announcement-source cross-check or keep single-source L0 and redirect; no promotion language. |

**Overall: PASS (8/8)** — non-blocking nits for finalizer.

## What the executor chose

Orientation (`reports/trader-wakes/moa/2026-07-12T1835/orientation.json`): weekend; `redirect_required=false`; executable routes = historical proxy discovery + simulator capability; observed option replay blocked at 1/3 market dates; prior 1806 NEXT named inventory of no-paid announcement-time sources and implement provider only with honest `known_at`.

Executor closed that named loop: Nasdaq dividend-history inventory, immutable archive + as-of provider, capture CLI, decision doc, coverage/doctrine patch, AAPL live capture, required-mode diagonal/bull-call smoke, SMCI fail-closed live capture. No hyp registry, evolve `--apply`, B-check, paper, shadow, arm, or live mutation.

## Claim audit (challenged against live files)

### Accepted claims

1. **Declaration → `known_at` without ex-date fabrication** — `archive_from_nasdaq_payload` maps `declarationDate` only; old `N/A` rows truncate older history rather than backfill. Live AAPL: 82 source rows → 53 retained; `truncated_at_missing_known_at=true`; coverage_start `2013-02-07`. Evidence: `.cache/platform/dividend_event_archive_lab_2026-07-12T1835.json`, `.cache/platform/dividend_events/AAPL_nasdaq.json`, `test_nasdaq_rows_preserve_declaration_date_as_known_at`.

2. **Fail-closed unsupported/ambiguous** — empty/pending message → `coverage ambiguous` (SMCI); non-200 → `unsupported` (TSLL fixture); latest missing declaration / future declaration / row-count tamper / coverage-boundary tamper raise. Live SMCI capture exited non-zero; no SMCI archive written. Tests: `test_ambiguous_empty_or_unsupported_source_fails_closed`, `test_missing_latest_declaration_or_future_declaration_fails_closed`, tamper tests.

3. **Provider as coverage sentinel, not lookahead inventer** — wrong symbol or `as_of` outside `[coverage_start, observed_at]` → `None`; covered query returns archive events; consumer assessor still drops `known_at > as_of`. Test: `test_provider_enforces_symbol_and_asof_coverage_but_allows_future_through` + `test_future_announcement_remains_invisible_after_archive_load`.

4. **Required-mode sim wiring smoke (not edge)** — AAPL diagonal required-mode `ok` n_trades=0; bull-call `ok` n_trades=21; both `corporate_action_mode=required`; early_assignment_risk_exits=0. Decision label `CAPABILITY_ONLY_ARCHIVED_DIVIDEND_PROVIDER_SUPPORTED_FOR_AAPL`. Evidence: `.cache/platform/dividend_event_provider_sim_smoke_2026-07-12T1835.json`. Challenger sampled 105 weekly as_ofs over 2y: 0 missing coverage — smoke’s zero assignment exits are consistent with threshold non-fire / no-entry paths, not “no events exist.”

5. **Source inventory honesty** — `docs/DIVIDEND_EVENT_DATA_BOUNDARY.md` rejects yfinance ex-date relabel and SEC aggregate facts for event-level `known_at`; Nasdaq usable with caveats (unadjusted, preferred-security risk, fragile public API). No paid spend / broker / secrets.

6. **No capital-path mutation** — coverage still 20 structures / 245 hyps / 67 evolve artifacts; quality leader none. Claim limit strings present on lab/smoke JSON.

### Independent verification (challenger re-ran 2026-07-12 ~21:10 PDT)

```text
.venv/bin/python -m unittest tests.test_dividend_event_archive \
  tests.test_corporate_action_risk tests.test_debit_vertical_sim \
  tests.test_diagonal_oos_stress tests.test_defined_risk_fixed_cost -v
→ Ran 24 tests … OK (0.171s)

.venv/bin/python -m trader_platform.smoke_test
→ platform smoke OK; agentic_live blocked at Stage1 OAuth gate

.venv/bin/python -m unittest discover -s tests
→ Ran 154 tests in 6.747s … OK
```

Primary artifacts inspected: `dividend_event_archive.py`, `tests/test_dividend_event_archive.py`, capture CLI, boundary doc, lab/smoke JSON, live AAPL archive (53 events; first known_at 2013-01-23 / ex 2013-02-07 amount $2.65; last known_at 2026-04-30 / ex 2026-05-11 amount $0.27; pre-split scale amounts present), orientation.json, income-coverage-LATEST, executor closeout/exec report.

Independent first-event probe (AAPL archive on disk):

```text
as_of 2013-01-23 (on known_at) → None
as_of 2013-01-30 (mid known→ex) → None
as_of 2013-02-06 (day before first ex) → None
as_of 2013-02-07 (coverage_start = min ex_date) → n=53
2y weekly as_ofs 2024-07-12..2026-07-10: 105 weeks, 0 missing coverage
```

### Semantics / scope (honest limits — accepted)

- Provider enables **corporate-action guard input** on supported eventful listings only; not option-surface, contract-grid, adjusted-return, or edge evidence.
- Black-Scholes proxy marks remain L0; required-mode AAPL smoke is wiring proof.
- Empty `[]` under covered as_of is allowed only as genuine no-visible-event; `None` remains missing coverage. Contract preserved from 1806.
- SMCI/F/TSLL remain provider-blocked; SMCI diagonal required mode stays blocked — matches prior SMCI holdout rejection context.
- Default sim path remains opt-in (`require_dividend_events=False`); no silent restress of old proxy SHIP under a new provider.

## Nits (non-blocking; finalizer should consider)

1. **`coverage_start = min(ex_date)` first-event orphan** — provider requires `as_of >= coverage_start` while announcement visibility needs `as_of >= known_at` and `as_of < ex_date`. For the earliest AAPL event, known_at=2013-01-23 but coverage_start=2013-02-07, so the entire announced-pre-ex window returns `None`. Independent probe confirms. For multi-year AAPL this is mostly conservative fail-closed on pre-2013 and only orphans the first event — **not claim-invalidating** for the 2y smoke. Prefer `coverage_start = min(known_at)` (or explicit known_at lower bound) + a boundary test that an announced-but-not-yet-ex first event is servable under required mode. Note loader currently asserts `coverage_start == min(ex_date)`, so both write and load paths must move together.

2. **Split-unadjusted amounts** — Nasdaq page caveat is documented; AAPL retained history includes pre-split-scale amounts ($2.65 / $3.05 / $3.29) mixed with recent $0.20–$0.27. Against split-adjusted underlyings, pre-split amounts can distort historical assignment thresholds. Acceptable at L0 guard with explicit caveat; do not treat long-history AAPL required-mode assignment *counts* as calibrated. Optional: document “recent contiguous post-split window only” or amount/spot sanity bounds before relying on deep history.

3. **MU/AAL inventory without archived artifacts** — boundary doc claims MU 20 / AAL 23 declaration rows from live inventory, but only AAPL archive is on disk. NEXT correctly requires cross-check; if MU is in scope, capture MU archive first — do not cite unarchived inventory as provider eligibility.

4. **Preferred / security-class contamination** — documented as source limitation; no positive test that preferred rows are rejected. Keep L0 single-source until independent completeness/identity proof; do not broaden to “all Nasdaq dividends safe.”

5. **Readiness LATEST was topped at 1806 inventory NEXT** — that NEXT is now executed for supported listings. Challenger patches living NEXT (see readiness LATEST top); finalizer must still prepend a full 1835 outcome after its own verification and may refine wording.

6. **Skill pitfall optional** — 1806 skill already pins `None` vs `[]` and non-fabricated `known_at`. Optional source-specific pitfall: “Nasdaq usable only with contiguous declaration-dated cash rows; truncate at first N/A; never treat empty history as covered/no-event.”

None of these reverse PASS.

## Freedom / thrash audit

- Prior closed families (close-shock, momentum, pullback, multi-horizon trend-pullback, vol-compression, CCS vol-expansion, collar, asymmetric IC, BAC Fri7 management) were **not** reopened.
- One-date TSLL option archive was **not** treated as platform stop.
- No evolve `--apply`, hyp registration, B-check mutation, broker login, or live path.
- Choice matches orientation + prior NEXT: simulator capability with a named new evidence class (honest archived `known_at`).

## Capital / readiness

- Phase: **BUILD / L0** unchanged.
- Living quality leader: **none**.
- Formal B checks: unchanged.
- Trade-shaped candidates still require structure, `capital_fit_usd`, 1-lot `max_loss_usd`, `max_lots`, non-vacuous dual-cost evidence, regime windows, competitive DD — plus honest corporate-action provenance when required mode is claimed.
- Supported-listing provider does **not** restore SMCI/other blocked symbols to required-mode capital claims.

## Disposition for finalizer

- **Accept** capability delta as useful durable learning.
- **Do not** invent edge, promote statuses, or restress old proxy SHIP as L1 because a dividend provider exists.
- Optional repair: coverage_start/known_at lower-bound + first-event servable test (write+load boundary together); MU archive only if NEXT uses MU.
- Promote: dated outcome → wake/readiness; boundary doc already project truth; optional skill pitfall for Nasdaq contiguous-declaration rule.
- Preserve ONE NEXT: independent issuer/filing cross-check for completeness + security-class identity, else keep single-source L0 and allow redirect to another open historical/capability route.
- Prepend readiness LATEST 1835 outcome after finalizer verification (challenger only refreshed living NEXT).

## Phase status

Challenger phase only. Finalizer repair/verification/learning promotion, deterministic commit/integration/push/postflight, and RUN COMPLETE remain pending. Challenger did not commit, push, merge, evolve `--apply`, broker, arm, or claim completion.

MOA_CHALL_DONE

# MOA BUILD executor closeout — 2026-07-12T1835

> **Finalizer supersession:** This is the immutable executor-phase closeout. The finalizer repaired the challenger's first-event coverage finding (`coverage_start=2013-01-23` from earliest retained `known_at`), added boundary/tamper tests, and passed focused 25/25 plus full 155/155. See `learning-promotion.md` and the final merge report for current evidence; the CAPABILITY/L0/no-live judgment remains unchanged.

WAKE: 2026-07-12 18:46 PDT (Sunday; market closed)
PHASE: BUILD / L0
SLEEVE: $3,000
ROLE: GPT 5.6 Sol executor; only writer; challenger/finalizer/integration pending
OUTCOME: CAPABILITY_ONLY
PAPER_ONLY: true

## ORIENTATION / CHOICE

Current living leader: **none**. Coverage remains 20 catalog structures / 245 hypotheses / 67 evolve artifacts. The observed option archive remains one market date and blocks only observed-option replay/calibration. Recent daily-bar signal families in `orientation.json` are closed; `redirect_required=false`.

Prior NEXT was accepted because it named a genuinely open capability route, not a closed-family retune: inventory no-paid announcement-time dividend sources and implement a provider only if `known_at` is honest.

**Hypothesis:** a no-auth Nasdaq dividend-history response can supply event-level `declarationDate`, `exOrEffDate`, and cash amount for supported listings, allowing an immutable no-lookahead `DividendEventProvider` without relabeling ex-date as announcement time.

**Falsifier:** unsupported/ambiguous/empty/malformed responses, missing declaration dates, future declarations, archive tampering, or out-of-coverage as-of queries must fail closed (`None`/error), never fabricate `known_at` or covered/no-event `[]`.

## DID

- Added `trader_platform/research/dividend_event_archive.py`: normalized immutable archive, public Nasdaq snapshot adapter, atomic JSON writer/loader, strict row/count/timing validation, conservative truncation at old `N/A` declaration rows, and an as-of-bounded provider.
- Added `scripts/dividend_event_observations.py` for capture/validation and summary generation.
- Added `tests/test_dividend_event_archive.py` covering honest declaration mapping, future-announcement non-leakage, unsupported/ambiguous failure, malformed/future declaration failure, symbol/as-of boundaries, atomic round-trip, coverage tamper, and row-count tamper.
- Added `docs/DIVIDEND_EVENT_DATA_BOUNDARY.md` with the tested source inventory and claim boundary.
- Updated BUILD/coverage doctrine and the generated coverage gap text so the new provider is not later overwritten as “missing,” while unsupported symbols and observed-surface gaps stay explicit.
- Captured a local AAPL archive and required-mode simulator smoke. Raw provider/runtime JSON remains under ignored `.cache/platform/`; no raw dump, secret, token, or private position file was added to tracked residue.

## EVIDENCE / JUDGMENT

- `.cache/platform/dividend_event_archive_lab_2026-07-12T1835.json`: AAPL live endpoint returned 82 source rows; 53 contiguous recent rows retained; honest coverage begins 2013-02-07; older missing-declaration rows truncated.
- `.cache/platform/dividend_event_provider_sim_smoke_2026-07-12T1835.json`: AAPL required-mode diagonal completed `ok` with 0 entries; required-mode bull-call completed `ok` with 21 proxy trades; both report `corporate_action_mode=required` and zero assignment exits. This proves wiring only, not edge.
- Live SMCI capture exited non-zero with `Nasdaq dividend coverage ambiguous`; no SMCI archive was written. Direct source inventory also found F unavailable as non-Nasdaq and TSLL unsupported, while AAPL/MU/AAL exposed declaration dates.
- SEC Company Facts exposed aggregate dividend facts but not a normalized event declaration/ex-date stream. yfinance 1.5.1 exposed ex-date-indexed actions/current calendar fields but not historical announcement timestamps. Neither was used to fabricate `known_at`.
- Nasdaq’s page warns history is aggregated, unadjusted for splits, and may include preferred securities. The provider therefore remains a narrow corporate-action guard input, not adjusted-return, option-surface, contract, or edge evidence.

## CAPITAL / CLAIM BOUNDARY

No trade-shaped candidate was created, registered, promoted, or ranked. Therefore this wake makes no new `capital_fit_usd`, one-lot `max_loss_usd`, `max_lots`, B3/B4, B6, paper, shadow, arm, or live claim. Existing proxy structures remain defined-debit research only; Black-Scholes marks cannot earn L1. Readiness stays BUILD/L0 with no living leader.

## VERIFICATION

- Focused behavioral/boundary/negative-control/regression suite: `.venv/bin/python -m unittest tests.test_dividend_event_archive tests.test_corporate_action_risk tests.test_debit_vertical_sim tests.test_diagonal_oos_stress tests.test_defined_risk_fixed_cost -v` → **24/24 OK**.
- Platform smoke: `.venv/bin/python -m trader_platform.smoke_test` → **platform smoke OK**; `agentic_live` remained blocked at the Stage1 OAuth gate.
- Full suite: `.venv/bin/python -m unittest discover -s tests` → **154/154 OK**.
- Coverage: `.venv/bin/python scripts/trader_income_coverage.py --write --stamp 2026-07-12T1835` → **20 structures / 245 hypotheses / 67 artifacts / no leader**.
- Hygiene: `git diff --check` → clean.
- Preflight note: deterministic preflight correctly returned dirty because the wrapper had already created run-owned `meta.json`, `orientation.json`, prompt/session scaffolding, and the 1835 coverage preflight surface on branch `trader/run-2026-07-12T1835` at base `2702fa8`. No unrelated pre-existing residue was absorbed, hidden, stashed, reset, or deleted.

## FREEDOM AUDIT

Symbol and strategy freedom remained open. This loop added a provider capability for supported eventful listings but did not create an instrument allowlist, require Nasdaq support for unrelated research, reopen a closed strategy family, or let the blocked TSLL option archive freeze historical-underlying/capability work.

## DURABLE / LESSON

Durable truth is in `docs/DIVIDEND_EVENT_DATA_BOUNDARY.md`, BUILD/coverage docs, provider code, capture CLI, and fail-closed tests. Future Trader can now preserve real declaration dates as `known_at` for supported archived histories and distinguish an explicit covered no-event result from ambiguous source emptiness. It must still treat unsupported/empty symbols as missing coverage and must not confuse corporate-action timing with observed option evidence.

No skill or memory update in executor phase: the 1806 skill already pins non-fabricated `known_at`, `None` versus `[]`, and precedence controls; this wake implements that rule in repo machinery. Finalizer may promote an additional source-specific pitfall after challenger review.

## NEXT SEED

Cross-check the archived AAPL/MU declaration/ex-date/amount sequence against one independent issuer/filing announcement source and add a per-symbol provenance qualification only if event completeness and security-class identity can be proved; otherwise keep the Nasdaq provider L0/single-source and redirect to another open historical simulation or capability route.

## PHASE STATUS

Executor phase only. Do not commit, push, merge, switch branches, or claim RUN COMPLETE. Grok challenger must critique; finalizer must repair and rerun gates; deterministic integration remains authoritative.

MOA_EXEC_DONE

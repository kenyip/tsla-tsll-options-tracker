# Learning promotion — 2026-07-15T2344

## VERIFICATION

Strategy charter/outcome: `CROSS_SECTION_RESIDUAL_REVERSAL_BULL_CALL_21D_V1` / `CROSS_SECTION_FIVE_SESSION_RESIDUAL_REVERSAL`, `F0_MECHANISM -> F0_MECHANISM`, exact `FAMILY_CLOSED`, strategy advancement false. The mechanism tested whether bottom-three five-session peer-residual laggards rebound absolutely and relative to same-date neutral-three controls. The future one-lot 18–24 DTE `$2`-wide bull-call debit spread remains conditional context only: `capital_fit_usd=$200`, future same-expiry frictionless debit/max-loss ceiling `$200` before unmodeled closing friction, `max_lots=1`; observed/simulated option-path max loss is unmeasured. No holdout opening, option pricing, F1/F2/L1, capital seat, registry, paper, shadow, arm, broker, funding, or live authority.

- Focused behavioral/boundary/negative-control/regression: `.venv/bin/python -m unittest tests.test_cross_section_residual_reversal_train_lab tests.test_trader_build_compounding tests.test_trader_income_coverage` -> `Ran 37 tests in 6.921s — OK`.
- Required full suite: `.venv/bin/python -m unittest discover -s tests` -> `Ran 379 tests in 20.838s — OK`.
- Full pytest regression: `.venv/bin/python -m pytest -q` -> `389 passed, 18 subtests passed in 23.16s`.
- Compile: `.venv/bin/python -m py_compile scripts/cross_section_residual_reversal_train_lab.py tests/test_cross_section_residual_reversal_train_lab.py` -> exit `0`, no output.
- Canonical finalizer regeneration: `.venv/bin/python scripts/cross_section_residual_reversal_train_lab.py --out .cache/platform/cross_section_residual_reversal_train_2026-07-15T2344-finalizer.json` -> exact `FAMILY_CLOSED`, train `n=144`, failed gate `treated_worst_decile_at_least_negative_5pct`, holdout identity `453bf4b4fafd86bd5570afe1a473acfc51b328ebc4cdd4ed6ece54fddf89d263`. After moving the finalizer payload to the canonical path, SHA-256 is `fad32750fd051a57a1676b330034e0ef947bdc5fcc76124446d91a70891379fe`.
- Substantive replay comparison against executor artifact SHA `d98828afe6e3c5b7436c7c26b30477a775ace00951456a8d115aa8ba89e93191` -> equality `true` after excluding nondeterministic `generated_at` and the expected finalizer-added quarantine/capital/authority fields. Economic metrics, failed gate, 144 train rows, and sealed holdout identity did not change.
- Finalizer evidence: treated/control means after labeled 20 bps `+1.340640%/+0.763662%`; paired mean `+0.576978%`; paired median `+0.720953%`; paired LB90 `+0.142252%`; paired positive frequency `58.3333%`; treated positive frequency `66.6667%`; worst-decile `n=15`, mean `-6.119049%`; integrity violations `0`; option pricing calls `0`.
- Coverage regeneration: `just trader-income-coverage` -> 21 structures / 246 hypotheses / 70 evolve artifacts / no living leader; dated surface `reports/readiness/income-coverage-2026-07-16T0014.md` and matching LATEST written.
- Schema-v2 role validation: `.venv/bin/python scripts/trader_build_compounding.py validate-handoff --repo . --stamp 2026-07-15T2344 --base-head e264e7bd4a89cf570a3b625810845f96ca00e9a0 --baseline .cache/platform/completion/2026-07-15T2344-finalizer-baseline.json` -> `ok=true`, `role_ready=true`, `outcome=FAMILY_CLOSED`, `strategy_advanced=false`, 3 useful deltas, 3 grouped critic dispositions.
- Temporary-index deterministic prepare: `GIT_INDEX_FILE=<temp> git read-tree HEAD; GIT_INDEX_FILE=<temp> git add -A; GIT_INDEX_FILE=<temp> .venv/bin/python scripts/trader_run_completion_gate.py prepare ...` -> `ok=true`, `mode=prepare`, 19 staged files; `git diff --cached --check` produced no output. The real index remained untouched.
- Complete-diff audit: 19 intended paths; no sensitive/private-position/cache/auth paths, raw secret markers/assignments, conflict markers, or TODO/FIXME residue; every changed JSON parsed; finalizer merge equals wake LATEST byte-for-byte; dated coverage equals coverage LATEST byte-for-byte; living surfaces contain the finalizer hash/NEXT/burst stop and no full old executor hash or stale coverage path.

Accepted/repaired challenger findings:

1. F1 accepted: schema-v2 `compounding.json` is now the orientation source of record. The schema-v1 lab artifact remains local evidence only.
2. F2 accepted: exact family, candidate, fixed 14-name panel, bottom-three/neutral-three construction, nearby `-4%` threshold, and nearby five-session feature/forward-horizon retunes are registered in machine-readable quarantine and `closed_families`.
3. F3 accepted: any future event-risk route must use genuinely prior-known event taxonomy, labels, and thresholds frozen independently before outcomes. Inspected worst episodes cannot select symbols, exclusions, or gates; the 96-blueprint holdout stays sealed.
4. F4 accepted: `$200` is future same-expiry frictionless debit/admission context before closing friction, not observed or simulated option-path loss. Machinery now emits `observed_or_simulated_option_path_max_loss_usd=null`, split F2/L1 labels, and explicit status text under tests.
5. F5 accepted: favorable mean, paired excess, hit rate, and positive LB90 are diagnostic only. The predeclared `-5%` worst-decile gate is decisive; no F1 or control relabel/inversion is allowed.
6. F6 accepted: finalizer independently reran focused, full unittest, full pytest, compile, canonical regeneration, and substantive replay checks.
7. F7 accepted: readiness, epoch progress, merge/LATEST/INDEX, coverage, compounding, and NEXT surfaces now agree on the exact family close, false advancement, three-no-advance burst stop, and one reassessment seed.

Rejected challenger findings: none. Rejected interpretations are post-inspection symbol deletion, gate loosening, nearby threshold/group/horizon tuning, holdout salvage, favorable-center promotion, control inversion, option-stage laundering, registry/paper force, or any shadow/live authority.

Integration is pending the deterministic wrapper gate. This artifact is a green handoff, not a `RUN COMPLETE` claim.

## DURABLE

- Machinery: `scripts/cross_section_residual_reversal_train_lab.py` provides chronology-safe train-only peer-residual blueprints, paired neutral controls, global non-overlap, strict integrity checks, dependence-aware uncertainty, tail gates, sealed holdout identity, split authority labels, honest unmeasured option-path loss, and explicit anti-salvage quarantine.
- Tests: `tests/test_cross_section_residual_reversal_train_lab.py` now has six behavioral/boundary/negative-control cases, including completed-feature/entry-bar exclusion, absolute-plus-relative pass, positive-center/control failure, tamper fail-close, exact quarantine/prior-known-event boundaries, and CLI import smoke.
- Project truth/history: finalizer merge/LATEST/INDEX/readiness/coverage surfaces and this learning record state the exact F0 close, favorable center, decisive continuation tail, no option authority, and burst stop.
- Orientation durability: schema-v2 `compounding.json` registers the closed family/candidate/retune class with unique novelty keys; `configs/search_epoch.json` records three completed no-advance decisions and `strategy_burst_stop_required=true`.
- Skill: no edit. The loaded `trader-self-evolution` skill already requires predeclared tail falsification, no favorable-point-estimate rescue, prior-known event chronology, sealed holdouts, capital/authority labels, and full-suite completion. This wake adds experiment-specific project evidence, not a missing reusable procedure.
- Memory: no edit. The outcome and quarantine are dated project state rather than a stable user preference or routing fact; repo/config/compounding surfaces are authoritative, and profile memory is near capacity.

## LESSON

Future Trader can now test peer-residual reversal without leaking the entry bar or holdout and can distinguish an attractive center from a capital-protection failure. Here the average reversal signal was real enough to be tempting—treated `+1.340640%`, paired `+0.576978%`, LB90 `+0.142252%`—but the treated worst decile was `-6.119049%`, below the frozen `-5%` floor. For a `$3,000` sleeve, that left-tail failure closes the exact mechanism before option expression; favorable means and uncertainty bounds do not override a predeclared loss-distribution gate.

Worst-episode symbol concentration is a research question, not a salvage license. A valid successor event-risk design must source event knowledge before each decision and freeze its taxonomy before outcomes. It may not delete AMD/TSLA/AAPL, relax the tail gate, retune the same five-session panel, open the sealed reserve, or relabel the neutral control after seeing train results. The third active-epoch no-advance decision also means the next strategy wake must reassess search design/data rather than buy a fourth mechanism search.

## NEXT

`SEARCH_DESIGN_REASSESS_AFTER_RESIDUAL_REVERSAL_TAIL_CLOSE`: stop strategy-volume search; reconcile the three active-epoch no-advance outcomes, assess whether favorable centers with failed tails indicate a genuinely new prior-known event-risk evidence route or a broader data/design limitation, carry forward the parked observed-diagonal data floor without same-date churn, and start a successor epoch only after a dated reassessment names a non-quarantined mechanism or evidence class. Do not open the sealed 96-blueprint holdout, delete high-beta symbols post hoc, loosen the `-5%` tail gate, force registry/paper, or enter shadow/arm/broker/live paths.

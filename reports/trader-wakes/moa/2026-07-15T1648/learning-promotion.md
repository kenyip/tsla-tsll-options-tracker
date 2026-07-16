# Learning promotion — 2026-07-15T1648

## VERIFICATION

- Focused behavioral/boundary/negative-control plus handoff-contract suite:
  - command: `.venv/bin/python -m unittest -v tests.test_breakout_bull_call_option_lab tests.test_trader_build_compounding`
  - exact result: `Ran 38 tests in 6.129s — OK`.
  - covered exact-width fail-closed behavior, expiration-before-stop on a sparse calendar, signed closing friction, no same-day reentry, negative first-loss drawdown accounting, conjunctive dual-population gates, overwrite refusal with byte preservation, normalized-hash negative control, completed-epoch orientation, repaired-critic artifact requirements, schema-v2 outcomes, and anti-thrash boundaries.
- Broader focused regression suite:
  - command: `.venv/bin/python -m unittest -v tests.test_breakout_bull_call_option_lab tests.test_trader_build_compounding tests.test_breakout_continuation_train_lab tests.test_breakout_continuation_holdout_lab tests.test_debit_vertical_sim tests.test_trader_income_coverage`
  - exact result: `Ran 57 tests in 6.849s — OK`.
  - the chained `py_compile` step passed; its first `git diff --check` then exited `2` solely because two pre-existing trailing-space lines were found in `reports/trader-wakes/LATEST.md`. Those lines were repaired rather than normalized as acceptable; final diff verification remains part of the deterministic handoff check.
- Full suite, exactly as required:
  - command: `.venv/bin/python -m unittest discover -s tests`
  - exact result: `Ran 331 tests in 16.076s — OK`.
- Claim-bearing payoff retest on current code:
  - command: `.venv/bin/python scripts/breakout_bull_call_option_lab.py --frozen-train .cache/platform/breakout_continuation_train_2026-07-15T1515.json --f2-summary reports/trader-wakes/moa/2026-07-15T1606/breakout-holdout-summary.json --out .cache/platform/breakout_bull_call_option_2026-07-15T1648-v7.json`
  - exact result: exit `0`, `strategy_outcome=FAMILY_CLOSED`, `funnel_stage_after=F2_UNTOUCHED_HOLDOUT`, `capital_fit_usd=92.56501618263479`, `one_lot_max_loss_usd=246.90032488027197`, and the same 16 failed checks.
  - v7 strict-JSON bytes: `494767`; raw SHA-256: `acc1cc365690c5c7652d180da3da431310d597b754c4ec9056964cdae6cbd526`; normalized SHA-256 excluding only `generated_at`: `b32c951ff607a0f2262005634191bd94c6fd36bc599338ec1a34e599b3ba166e`.
  - exact comparison: v6 and v7 are substantively equal after excluding `generated_at` and the repaired `exit_management` label; output was `substantive_equal_excluding_label_and_time True`.
- Derived-state regeneration:
  - `trader_build_compounding.py context` exited `0` and regenerated orientation with completed epoch `2026-07-15-time-series-breakout-payoff`, `status=completed`, and non-null reassessment/charter/goal/success-definition fields.
  - `trader_income_coverage.py --write --stamp 2026-07-15T1648` exited `0`, reporting 21 catalog structures, 246 hypotheses, and 70 evolve sim artifacts, and wrote both dated and LATEST coverage surfaces.

Integration is pending the deterministic wrapper gate. This finalizer does not commit, push, merge, switch branches, or claim `RUN COMPLETE`.

## DURABLE

Strategy charter and outcome:
- The frozen charter is `reports/trader-wakes/moa/2026-07-15T1648/strategy-decision-charter.md`. Its exit precedence now matches executable behavior: from the next completed session, contract expiration first, then 50%-of-max-value harvest, pre-breakout-high invalidation, and the hard ten-session stop.
- Outcome is `FAMILY_CLOSED`, not an advance. The exact `MULTINAME_BREAKOUT_BULL_CALL_14D_V1` option expression failed 16 conjunctive gates on the frozen 168-row development decision population plus the already-opened 113-row secondary stress. It remains F2/L0 with no L1, capital seat, registry promotion, paper force, shadow, arm, broker, or live authority.
- Dominant economics are unchanged: on development, the 5% adverse leg-price axis produced 104 eligible events across seven symbols, `-$1,760.00` event PnL and `-$1,321.71` one-unit portfolio PnL with `$1,352.24` max DD and 9 dense negative windows; the fixed-dollar axis produced 105 eligible events across seven symbols, `+$27.79` event PnL and `+$21.54` portfolio PnL but still failed with `$183.13` max DD and 6 dense negative windows. Secondary stress had only 13 eligible rows across three symbols on each axis; fixed-dollar event PnL was `+$10.78` but portfolio PnL was `-$11.31`, while the 5% portfolio lost `-$353.24`. One-lot max loss was `$246.90`, within the `$300` cap but far above the `$75` window-DD quality bar.

Accepted challenger findings and repairs:
- Accepted the expiration-precedence charter defect. Repaired the charter and emitted payload label; retained and re-ran the sparse-calendar behavioral test; current-code v7 remained `FAMILY_CLOSED`.
- Accepted the completed-search-epoch orientation defect. `scripts/trader_build_compounding.py` now retains completed epoch context until replacement, and `tests/test_trader_build_compounding.py` proves status/identity/reassessment/charter/goal/success-definition preservation.
- Accepted the missing durable replay-guard tests. `scripts/breakout_bull_call_option_lab.py` now exposes normalized substantive hashing that excludes only `generated_at`; tests prove timestamp invariance, substantive-change sensitivity, early overwrite refusal, and byte preservation.
- Accepted challenger verification ownership. The finalizer re-ran focused, adjacent, compile, current-code experiment, and full-suite checks rather than relying on executor logs.

Rejected critique finding:
- Rejected the claim that NEXT still needed wording repair. `merged-next-seed.md` already contains the challenger-strengthened requirement for one genuinely new candidate and one predeclared F0 mechanism test while quarantining the closed bull-call expression. Final surfaces propagate that exact single seed without another semantic rewrite.

Promotion routing:
- Dated outcome/current project truth: this learning record, schema-v2 `compounding.json`, final merge/LATEST/INDEX/readiness surfaces, strategy charter, and income coverage reports.
- Reusable machinery/tests: `scripts/breakout_bull_call_option_lab.py`, `tests/test_breakout_bull_call_option_lab.py`, `scripts/trader_build_compounding.py`, and `tests/test_trader_build_compounding.py`.
- Reusable procedure/pitfall: patched profile skill `trader-self-evolution` so completed search epochs remain successor-wake context and require active-plus-completed regression coverage.
- Memory: no addition. The stable autonomy/evidence stance is already present; dated metrics, hashes, and completion state belong in repo residue, not persistent profile memory.

## LESSON

Future Trader can now distinguish an underlying discovery advance from a viable option expression with a concrete frozen payoff path. A continuation signal that passed F2 did not survive a one-dollar 14-DTE bull-call debit expression under adverse multi-leg costs, portfolio drawdown, density, and secondary-stress gates; structural max-loss fit alone was insufficient. The exact expression is quarantined, not retuned.

Future Trader also has two stronger system guarantees: claim-bearing proxy evidence can be reproduced with a canonical hash that ignores only nondeterministic generation time while detecting substantive drift, and a completed search epoch remains durable orientation context until a successor epoch replaces it. These prevent timestamp churn and lifecycle status from silently erasing reproducibility or anti-thrash context.

## NEXT

THETA_EXPRESSIONS_NONMONOTONIC_PAYOFF_F0: in the next zero-input BUILD wake, use the current full-universe rank to select where risk belongs, then search a non-monotonic theta-led payoff class that is not the closed bull-call expression: broken-wing/iron butterfly, asymmetric iron condor, or calendar/diagonal chosen from current regime, liquidity, and capital fit. Freeze symbol(s), exact legs, DTE, delta/width, debit-or-credit bounds, entry timing, profit/stop/time exits, assignment/dividend handling, and one-lot capital_fit_usd/max_loss_usd/max_lots before outcomes; require one genuinely new candidate and one predeclared F0 mechanism test using labeled Black-Scholes/listed-expiry proxy over historical underlying paths with chronology, dual multi-leg costs, overlap/concentration controls, negative controls, and no subset salvage. Reuse the option payoff lab when useful but do not retune or reopen MULTINAME_BREAKOUT_BULL_CALL_14D_V1. Discovery bar only: no L1, registry auto-promote, paper force, shadow, arm, broker, or live action.

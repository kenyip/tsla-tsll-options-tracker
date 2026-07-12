# Learning promotion

## VERIFICATION
- `.venv/bin/python -m unittest tests.test_trader_completion_contract tests.test_trader_run_completion_gate` → 13 tests, OK.
- `.venv/bin/python -m unittest discover -s tests` → 86 tests, OK.
- `bash -n scripts/bootstrap_trader_profile.sh scripts/trader_build_lab_moa.sh scripts/trader_wake_moa.sh` → exit 0.
- `git diff --check` → exit 0.
- dirty-preflight negative orchestration → exit 1 with RUN INCOMPLETE and exact recovery text.
- `hermes -p trader config check` → config version 33 valid; required skills enabled.
- `hermes -p trader cron list` → all active BUILD scripts route through the canonical BUILD wrapper; RTH agent wake loads trader-self-evolution.

## DURABLE
- Repo contract: `AGENTS.md`; truthful coding-agent guidance: `CLAUDE.md`.
- Enforcement: BUILD wrapper, completion gate, stress adapter, bootstrap preservation.
- Reusable regression evidence: completion-contract and local-bare gate tests.
- Live Trader SOUL, workspace AGENTS, self-evolution skill, and compact memory already contain the completion doctrine and were verified, so no redundant profile rewrite was made.

## LESSON
Completion doctrine needs both semantic prompts and deterministic state proofs. Static wording alone cannot prove bootstrap preservation, exact NEXT cardinality, secret safety, run ancestry, or resumable shell failure.

## NEXT
Add a deterministic test that interrupts integration after the run-branch push and proves the preserved branch can be resumed without force, stash, or evidence loss.

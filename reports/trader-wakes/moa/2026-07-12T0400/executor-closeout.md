# MOA BUILD executor closeout — 2026-07-12T0400

WAKE: 2026-07-12T0400 PDT (evening; market closed)
PHASE: BUILD
SLEEVE_USD: 3000
PAPER_ONLY: true
ROLE: GPT 5.6 Sol executor / only writer

## Chosen loop

P1+P3 asymmetric capped-jade iron-condor capability + immediate reject-unless falsification. This superseded the RTH-only archive NEXT because the market was closed and a distinct valid direction/structure axis was available.

## Hypothesis and falsifier

Hypothesis: on bullish/neutral, high-optionality names, a nearer put wing (16–22 delta) plus farther call wing (8–12 delta) can harvest downside skew while capping both tails and keep one-lot risk inside the $3k sleeve.

Falsifier: no tested DNA is non-vacuous and positive/SHIP under both 5% adverse leg slip and $0.01-per-leg half-spread, with max loss <=$300, fixed-cost window DD <=$75, dense-negative windows <=5, exact ledger, and zero close-bar re-entry.

## Validity prerequisite and repair

Inspection found a claim-invalidating IC boundary flaw: close debit was capped at put-width + call-width although non-overlapping iron-condor wings cannot both finish in the money. That could exceed the advertised max loss. `pcs_sim.max_close_debit()` now caps at the widest wing; a behavioral test forces a $4 mark against a 1x2-width IC and verifies the realized loss is exactly the stated $160 max loss.

The experiment remains synthetic listed-Friday/rounded-strike BS proxy discovery. Observed contract availability and costs are not claimed; the forward archive remains 1/3 market dates.

## Experiment

- Added transient IC controls: `put_target_delta`, `call_target_delta`, `put_spread_width`, `call_spread_width`, side credit floors, and `ic_allowed_regimes`.
- Grid: BAC, TSLL, SMCI, PLTR, SOFI, F; DTE 14/30; put delta 0.16/0.22; call delta 0.08/0.12; combined credit floor 0.05/0.10; $1 nominal wings; bullish/neutral only.
- Complete population: 96/96 rows, no errors.
- Baseline: 44/96 positive; 29/96 positive SHIP.
- 5% adverse leg slip: 0/96 positive; best PnL -$99.86; all 96 non-vacuous.
- Fixed $0.01 half-spread per leg: 0/96 positive; best PnL -$156.89; all 96 non-vacuous.
- Integrity: 288/288 full-run ledgers exact; zero same-bar re-entries.
- Deep candidates: 0; absolute passes: 0.

Decision: `REJECT_ASYMMETRIC_CONDOR_THIS_CYCLE`. No hypothesis registered, no status promotion, no living leader, no capital seat.

## Evidence

- Lab: `.cache/platform/asymmetric_condor_lab_2026-07-12T0400.json`
- Runner: `scripts/asymmetric_condor_lab.py`
- Simulator: `trader_platform/research/pcs_sim.py`
- Behavioral tests: `tests/test_pcs_expiry_grid.py`
- Targeted verification: `.venv/bin/python -m unittest tests.test_pcs_expiry_grid tests.test_regime_router_sim tests.test_defined_risk_fixed_cost` -> 19/19 OK
- Independent artifact assertions: rows=96; baseline positive SHIP=29; slip positive=0; fixed positive=0; ledger exact=288/288; same-bar=0.

## Capital statement

Structure: one-lot four-leg defined-risk asymmetric iron condor. `capital_fit_usd` and `max_loss_usd` are widest wing less total credit; tested realized max loss stayed below the $300 gate where entries existed; `max_lots` is emitted by `capital_fit_pcs`, but default posture remains 1 lot. This is rejected proxy research, not a capital candidate.

## Freedom audit

No prompt rule blocked a higher-information valid experiment. The one-date observed archive blocked only observed-surface/L1 claims, not this independent proxy falsification. `execute_code` was unavailable in cron mode, but equivalent terminal assertions completed with no information loss.

## Close

Progress type: P1 capability repair + P3 quality falsification — 4/5.
Honesty: L0 BUILD; no living quality leader; formal B checks unchanged.
ONE NEXT SEED: on the next distinct New York RTH market date, append the all-expiration TSLL archive from 1 to 2 of 3 dates and verify append/dedup density; do not run provider-backed historical simulation before 3/3.

MOA_EXEC_DONE

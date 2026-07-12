# MOA BUILD executor closeout — 2026-07-12T1000

WAKE: 2026-07-12T1000 PDT (weekly; market closed)
PHASE: BUILD
SLEEVE_USD: 3000
PAPER_ONLY: true
ROLE: GPT 5.6 Sol executor / only writer

## Chosen loop

P2+P3 lagged close-shock PCS direction/time hypothesis with immediate chronological falsification. This superseded the RTH-only quote-archive seed while the market was closed because it tested a valid independent axis and could change the research decision without observed historical chains.

## Hypothesis and falsifier

Hypothesis: after a completed high-volume downside close shock, waiting one bar and opening a short-DTE defined-risk PCS can harvest mean reversion with better cost-adjusted path risk than unconditional or mirror-up entries.

Falsifier: no train-selected DNA remains non-vacuous and positive on an untouched chronological holdout under both 5% adverse leg slip and $0.01-per-leg half-spread, while max loss <=$300, max DD <=$75, ledgers exact, and lagged-signal/no-close-bar integrity clean.

## Validity prerequisite and repair

The first exploratory run evaluated the completed close/volume signal and priced entry on that same close. That execution-timing ambiguity could invalidate the result, so its four apparent proxy passes were discarded. `pcs_sim` now supports `entry_signal_lag_bars`; the final experiment uses lag=1, meaning a completed signal bar is consumed only when pricing entry at the following close. Tests cover inclusive thresholds, missing-feature fail-close, and the prohibition on signal-bar entry.

The experiment remains synthetic listed-Friday/rounded-strike Black-Scholes proxy research. Observed contract availability/cost calibration is not claimed; the archive is still one distinct market date and cannot support L1.

## Experiment

- Population: BAC, F, SOFI, PLTR, TSLL, SMCI, AMD, AAPL; put-credit-spread only.
- Grid: 7/14 DTE × downside close <=-1%/-2% × volume surge >=1.0/1.5; 64 signal DNA.
- Controls: 16 same-DTE unconditional rows plus 64 matched high-volume mirror-up rows.
- Cost axes: 5% adverse leg slip and $0.01 half-spread per leg at entry/exit.
- Full-sample result: one absolute proxy pass, SMCI 7-DTE / <=-2% / volume>=1.5. Fixed cost n15/+$70.49/DD $38.06/max loss $89.67; 5% n17/+$4.15/DD $53.89/max loss $94.49. This is selection-biased context, not a candidate seat.
- Chronological 60/40 selection→untouched holdout: only PLTR and TSLL produced train candidates; **0/2 holdout pass**.
- PLTR holdout stayed positive but failed path risk: 5% n19/+$50.71/DD $155.05; fixed n19/+$198.27/DD $122.80.
- TSLL holdout failed edge and risk: 5% n14/−$7.70/DD $74.03; fixed n14/−$14.88/DD $76.10.
- Full-grid integrity: 432/432 mode ledgers exact; zero same-bar re-entry; zero lagged-signal violations.

Decision: `REJECT_CLOSE_SHOCK_PCS_WALKFORWARD`. No hypothesis registration, status promotion, living leader, capital seat, or B-check change.

## Evidence

- Full grid: `.cache/platform/pcs_close_shock_lab_2026-07-12T1000.json`
- Chronological falsifier: `.cache/platform/pcs_close_shock_walkforward_2026-07-12T1000.json`
- Runners: `scripts/pcs_close_shock_lab.py`, `scripts/pcs_close_shock_walkforward.py`
- Simulator: `trader_platform/research/pcs_sim.py`
- Behavioral tests: `tests/test_pcs_expiry_grid.py`
- Targeted verification: `.venv/bin/python -m unittest tests.test_pcs_expiry_grid tests.test_defined_risk_fixed_cost tests.test_regime_router_sim` -> 21/21 OK.

## Capital statement

Structure: one-lot defined-risk put credit spread. The sole full-sample row had `capital_fit_usd`/max loss below $95 and emitted `max_lots`, but default posture is one lot. Chronological holdout rejection means it is not a $3k capital candidate and not L1.

## Freedom audit

No prompt rule prevented a higher-information valid experiment. The one-date observed archive blocked only observed-cost/L1 claims, not this independent proxy falsification. Cron mode blocked `execute_code`; a checked local analysis script plus terminal execution reproduced all integrity summaries without information loss.

## Close

Progress type: P2 time+direction capability + P3 walk-forward falsification — 4/5.
Honesty: L0 BUILD. Full-sample proxy pass rejected by untouched holdout; no living quality leader; formal B checks unchanged.
ONE NEXT SEED: on the next distinct New York RTH market date, append the all-expiration TSLL quote archive from 1 to 2 of 3 dates and verify append/dedup density; do not run provider-backed historical simulation before 3/3.

MOA_EXEC_DONE

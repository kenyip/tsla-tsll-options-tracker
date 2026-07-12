# MOA BUILD lab executor closeout — 2026-07-11T2159

WAKE: 2026-07-11T2159 PDT
PHASE: BUILD
SLEEVE: 3000
EXECUTOR: GPT 5.6 Sol
MODE: paper/research only

## Chose

P1 + P3: build and immediately falsify a bearish 1x2 put ratio backspread. I kept the prior NEXT because this payoff is materially different from the prior symmetric credit scaffolds: it has a finite valley loss and convex crash payoff. Falsification was explicit: no capital path without dense positive after-cost evidence, B3 hold, max loss <= $300, window max DD <= $75, and dense-negative windows <= 5.

## Validity boundary

- The payoff and max loss are closed-form and behavior-tested at expiry.
- Entry/exit costs are adverse per leg under both percentage slip and fixed-dollar half-spread sensitivity.
- The experiment is structure-pure: 22/22 simulated DNA are `put_ratio_backspread`.
- Market history is daily underlying bars with Black-Scholes option marks. Expiry-specific observed surfaces, listed contract grids, assignment, and historical bid/ask replay are not present for this structure, so results are proxy discovery only.
- The one-date observed archive remains insufficient for provider-backed history; no observed-data or L1 claim is made.

## Built

- Added `put_ratio_backspread` to `STRUCTURE_CATALOG`: sell 1 higher-strike put, buy 2 lower-strike puts; stand aside in bullish regimes.
- Added `trader_platform/research/put_ratio_backspread_sim.py` with signed 1x2 payoff, adverse entry/exit marks, closed-form `max_loss=(short_strike-long_strike+entry_debit)*100`, one-position daily management, and explicit capital fields.
- Wired evolve, B3 regime stress, B4 percentage-slip stress, and fixed-dollar per-leg stress.
- Fixed explicit `--structures` evolve populations to remain structure-pure after family seeding/mutation.
- Added four behavioral tests: expiry valley-loss recomputation, adverse-cost monotonicity, bullish fail-close, and explicit-population purity.

## Evidence and decision

Structure-pure evolve:

- `.cache/platform/put_ratio_backspread_evolve_lab_2026-07-11T2159.json`
- Population 22, structures exactly [`put_ratio_backspread`]; SHIP 6 / NULL 8 / REJECT 8; eight candidate/research hypotheses created.

Exact stress set:

- `.cache/platform/stress_regime_put_ratio_lab_2026-07-11T2159.json`
- `.cache/platform/stress_cost_put_ratio_lab_2026-07-11T2159.json`
- `.cache/platform/fixed_cost_put_ratio_lab_2026-07-11T2159.json`

SMCI `hyp_dna_smci_put_ratio_backspread_86a2d26a`:

- Structure `put_ratio_backspread`; baseline n=71, +$3,532.07, DD $617.17; `capital_fit_usd=$365.81`, `max_loss_usd=$365.81`, `max_lots=2` by open-risk arithmetic (research posture remains 1 lot).
- B3: FAIL; worst window -$467.12, window max DD $530.47, dense-negative windows 2.
- B4 5%: non-vacuous SHIP, +$1,842.02; 10% becomes REJECT, -$921.28.
- Fixed $0.01/leg: n=71, +$3,200.48, DD $687.83.
- Judgment: cost survival is real within the proxy, but max loss exceeds $300 and path risk is far beyond the $75 DD gate. REJECT from L1/capital path.

BAC `hyp_dna_bac_put_ratio_backspread_967b8c06`:

- Structure `put_ratio_backspread`; baseline n=64, +$851.28, DD $149.68; `capital_fit_usd=$119.06`, `max_loss_usd=$119.06`, `max_lots=3` by open-risk arithmetic (research posture remains 1 lot).
- B3: soft hold; worst window -$51.58, window max DD $149.86, dense-negative windows 1.
- B4 5%: non-vacuous NULL, -$81.48.
- Fixed $0.01/leg: n=64, +$576.58, DD $197.70.
- Judgment: defined risk and fixed-cost survival do not overcome negative 5% PnL or DD roughly 2x the absolute gate. REJECT from L1/capital path.

Family decision: research capability retained; no capital seat and no living quality leader. This is not the same cost-collapse as prior butterfly families, but the surviving rows fail absolute path-risk gates. Do not count raw SHIP score as readiness.

## Verification

- Targeted structural/cost tests: 10/10 pass.
- Full unittest discovery: 47/48 pass; only pre-existing unrelated `test_assemble_pmcc_desk_live_yaml` fails (`upside=-0.5`, expected >0).
- Platform smoke: pass.
- No live, broker, arm, shadow promotion, or main-account action.

## Durable residue

- New simulator, catalog DNA, pure-population boundary, stress dispatch, behavioral tests, doctrine updates, and refreshed coverage.
- Candidate statuses remain research-only; formal B checks and phase remain unchanged.

## Freedom audit

No prompt rule blocked the chosen valid experiment. The higher-information observed-surface version remains tool/data-blocked by only one archived market date and no verified historical option-chain source; I narrowed the claim rather than freezing research.

## Progress

- Type: P1 new sim class + P3 immediate quality falsification
- Score: 4/5
- Honesty: L0 BUILD — novel proxy capability and decisive capital-path rejection; not paper-ready and not real-account ready

## ONE NEXT SEED

Run one exact, structure-pure BAC put-ratio management grid over `defined_loss_exit_frac` x `dte_stop`, including 5% slip and chronological OOS; stress only rows that are non-vacuous positive after cost, and reject the family for this cycle unless max loss <= $300, window DD <= $75, dense-negative windows <= 5, and OOS remains dense.

GATES: none. Paper/research only.

MOA_EXEC_DONE

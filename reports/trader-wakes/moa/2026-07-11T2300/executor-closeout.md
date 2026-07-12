# MOA BUILD lab executor closeout — 2026-07-11T2300

WAKE: 2026-07-11T2300 PDT
PHASE: BUILD
SLEEVE: 3000
EXECUTOR: GPT 5.6 Sol
MODE: paper/research only

## Chose

P3 quality falsification: restress the exact registered SMCI and BAC put-ratio DNA after the shared proxy event-loop correction. I superseded the prior immediate management-grid seed because every pre-fix put-ratio metric was stale; tuning before exact post-fix baselines would optimize against invalid cadence.

Hypothesis: removing same-bar re-entry would preserve at least one dense baseline and reveal whether a final management/OOS grid was warranted.

Falsifier: reject the family from this cycle without tuning unless one exact row simultaneously retained baseline SHIP, non-vacuous positive 5% PnL, B3 hold, max loss <= $300, window max DD <= $75, and dense-negative windows <= 5.

## Validity boundary

- Exact registered DNA only: SMCI `86a2d26a` and BAC `967b8c06`; both are pure `put_ratio_backspread` rows.
- Behavioral test verifies no close-bar re-entry; an independent trade-ledger recomputation found zero same-bar re-entries in all four baseline/5% runs and reproduced reported PnL and drawdown exactly.
- B3 uses yearly, six-month, and canonical windows over cached daily underlying history through 2026-07-10. There is no future join in this experiment.
- Option marks, strike availability, and percentage/fixed-dollar costs remain Black-Scholes proxies. No observed historical surface, listed contract archive, assignment, or bid/ask calibration claim is made.
- The one-date observed archive is irrelevant to this narrow proxy falsification but still blocks provider-backed historical promotion evidence. These results cannot earn L1.
- There is no current living quality leader. Absolute gates are used; former `b195f5fe` is historical context only.

## Evidence and decision

Artifacts:

- B3: `.cache/platform/stress_regime_put_ratio_postfix_2026-07-11T2300.json`
- B4: `.cache/platform/stress_cost_put_ratio_postfix_2026-07-11T2300.json`
- Fixed cost: `.cache/platform/fixed_cost_put_ratio_postfix_2026-07-11T2300.json`
- Independent ledger check: `.cache/platform/put_ratio_postfix_independent_2026-07-11T2300.json`

SMCI `hyp_dna_smci_put_ratio_backspread_86a2d26a`:

- Structure: 1x2 put ratio backspread; research posture 1 lot.
- Baseline: n=66, +$3,704.56, full DD $306.07, SHIP.
- Risk: `capital_fit_usd=$374.23`, `max_loss_usd=$374.23`, `max_lots=2` by open-risk arithmetic. It fails the explicit <=$300 one-lot gate despite the generic `fit_3k` label.
- B3: soft hold, zero dense-negative windows, worst window -$101.92, but window max DD $365.32.
- B4 5%: n=61, +$1,350.40, DD $599.41, SHIP; 10% becomes REJECT at -$593.35.
- Fixed $0.01/leg: n=66, +$3,397.40, DD $328.37.
- Judgment: non-vacuous proxy cost survival is real, but max loss and path drawdown fail absolute gates. REJECT from L1/capital path.

BAC `hyp_dna_bac_put_ratio_backspread_967b8c06`:

- Structure: 1x2 put ratio backspread; research posture 1 lot.
- Baseline: n=59, +$321.51, full DD $148.33, SHIP.
- Risk: `capital_fit_usd=$118.11`, `max_loss_usd=$118.11`, `max_lots=3` by open-risk arithmetic.
- B3: soft hold, two dense-negative windows, worst window -$62.38, window max DD $159.85.
- B4 5%: n=58, +$70.15, DD $190.59, NULL but positive and non-vacuous; 10% is -$342.06.
- Fixed $0.01/leg: n=59, +$71.59, DD $198.72, NULL.
- Judgment: fits the sleeve and survives moderate proxy costs, but baseline, B3, 5%, and fixed-cost drawdowns all exceed $75. REJECT from L1/capital path.

Family decision: both post-fix baselines remain dense and after-cost-positive, but neither clears the complete absolute gate. Per the predeclared falsifier, no management grid or OOS tuning was run. The simulator remains useful research tooling; the put-ratio family leaves the capital search for this cycle. No living leader emerges.

## Verification

- `.venv/bin/python -m unittest tests.test_put_ratio_backspread_sim`: 6/6 pass.
- Independent recomputation: exact PnL/DD equality and zero same-bar re-entry for SMCI/BAC at 0% and 5% slip.
- No hypothesis status mutation, live action, broker access, shadow promotion, arm, or main-account action.

## Durable residue

Post-correction exact B3/B4/fixed artifacts replace the stale pre-fix put-ratio metrics for decision use. Formal readiness remains BUILD/L0; the capital path and living-leader set remain empty.

## Freedom audit

No prompt rule blocked a higher-information valid experiment. Observed historical option surfaces remain a data/tool constraint for promotion-grade evidence, but they did not block this exact proxy falsification.

## Progress

- Type: P3 post-fix quality falsification / family rejection
- Score: 3/5
- Honesty: L0 BUILD — decisive research rejection with valid corrected cadence; not paper-testable at L1 and not real-account ready

## ONE NEXT SEED

Build a no-lookahead regime-router simulator over existing defined-risk credit engines: choose PCS in bullish/non-bearish bars, CCS in bearish bars, IC only in range-bound bars, otherwise stand aside; enforce one shared position and 1-lot risk <=$300, then compare exact same-window baseline/5%-cost/DD against each standalone negative control. Reject unless dense after-cost SHIP, B3 hold, window DD <=$75, dense-negative windows <=5, and no routing/population contamination.

GATES: none. Paper/research only.

MOA_EXEC_DONE

# Merged NEXT seed — 2026-07-12T1323

ONE seed (BUILD, paper/research only):

**Run one predeclared rolling-origin walk-forward of a mild bearish-pullback PCS on the same eight symbols (BAC, F, SOFI, PLTR, TSLL, SMCI, AMD, AAPL), reusing `scripts/pcs_momentum_walkforward_lab.py` (or a thin rolling-origin wrapper), with no grid expansion and no free DNA search.**

Hard rules for that run:
1. **Predeclare DNA before any fold holdout is scored.** Prefer the exact mirror of the only bullish train-pass cell (BAC-selected: 7 DTE, bullish ret≥0.5% / RSI 50–65 → mirror `entry_ret_1d_max=-0.005`, RSI 35–50, same PCS management knobs, `entry_signal_lag_bars=1`). If ranking is used, rank **only on that fold’s train slice**, evaluate once on the next untouched segment.
2. **Train-gate required before each fold’s holdout evaluation** (`walkforward_pass` semantics: both cost axes dense positive SHIP, max_loss≤$300, DD≤$75, integrity).
3. Cost axes fixed: 5% adverse leg slip and $0.01 half-spread per leg entry/exit.
4. **Reject the axis** unless both costs and window max DD ≤$75 clear across the rolling folds (absolute gates; no soft promote).
5. **Do not** treat the current SOFI (or F/PLTR) holdout bearish-mirror control as a candidate, seed DNA, or capital seat — those rows are selection-biased control context only.
6. No hyp registration / status promote / L1 seat / paper order from a single proxy fold.
7. Leave closed: bullish-momentum family, close-shock PCS, asymmetric IC, collar, BAC Fri7 management, put-ratio, BWIB, regime-router capital search.
8. **Parallel RTH (when a distinct NY market date exists):** append all-expiration TSLL quote archive 1→2/3; no provider-backed historical entry sim before 3/3.

No live / shadow / agentic arm.

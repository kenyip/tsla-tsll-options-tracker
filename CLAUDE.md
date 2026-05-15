# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
just setup                            # one-time: venv + deps (uv if available, else stdlib venv + pip)
just test                             # today's live recommendation (TSLA + TSLL) — runs live.py
just run                              # Streamlit dashboard on localhost
just backtest                         # full 5y backtest on TSLA + TSLL with per-ticker config
just backtest -- --tickers TSLA --period 10y --dump-trades   # --dump-trades writes .cache/<ticker>_trades.csv
just scenarios                        # 12-regime stress test — REQUIRED before/after every strategy tweak
just scenarios-discover               # re-curate canonical regime windows (after data drift)
just optimize                         # walk-forward grid search over StrategyConfig knobs
just optimize -- --static             # walk-forward OOS validation of current per-ticker defaults
just sweep KNOB --values v1,v2,v3                            # single-knob sweep (LLM-critic harness)
just sweep K1 --values … --vs K2 --vs-values …               # 2-D grid
just analyze                          # feature-importance + candidate adaptive-rule sketches (v1.12)
just positions                        # status of open positions (positions.yaml, gitignored)
just positions add TSLA put 385 2026-05-08 2026-05-15 4.40
just positions example                # write a sample positions.yaml
```

For CLI help on any underlying script: `.venv/bin/python <script>.py --help` (`live.py`, `run_backtest.py`, `optimize.py`, `run_scenarios.py`, `sweep.py`, `analyze.py`, `manage_positions.py`).

There is **no unit-test suite**. The behavioural regression gate is `just scenarios` (the canonical 12-regime windows in `scenarios.py`). A single regime can be inspected with `just scenarios -- --regime huge_up` (see `run_scenarios.py --help`).

## Architecture at a glance

This is a research engine, not an app. Three concerns are kept strictly separate, and almost every other file is a thin caller on top of them:

1. **Data + pricing** — `data.py` (yfinance loader with `.cache/` disk cache, feature pipeline, regime classifier in `_classify_regime`); `pricing.py` (Black-Scholes price/greeks + closed-form `strike_from_delta`). Strict no-future-leakage: row t is computed from past bars only.
2. **Strategy** — `strategies.py`: `StrategyConfig` dataclass, `DEFAULT_CONFIG_BY_TICKER` + `get_config(ticker)` for per-underlying defaults, `pick_entry()`, `check_exits()` (7-rung ladder), `pick_covered_call()` (wheel side), and the `adapt_entry_params(row, cfg)` hook (v1.11 architecture; no adaptive rule ships by default — it is the extension point for future LLM-proposed rules).
3. **Harness** — `backtest.py`: `Position` (mark-to-market), `Backtester` event loop. Per-bar sequence: if a position is open, mark and run `check_exits()`; otherwise run `pick_entry()`. **One position per ticker, daily granularity, no intraday.** End-of-data closes any open position with reason `end_of_data`.

Callers on top:

- **CLIs:** `run_backtest.py`, `run_scenarios.py`, `optimize.py`, `sweep.py`, `analyze.py`.
- **Live signal:** `live.py::make_recommendation()` calls `strategies.pick_entry()` directly — **the live signal IS the backtest signal**. Never fork.
- **Position tracker:** `positions.py` + `manage_positions.py` load `positions.yaml` and run `check_exits()` against user-held positions; read-only against trading state.
- **Dashboard:** `tsla_options_dashboard.py` is a Streamlit view over the engine modules (Today / Positions / Performance / Scenarios tabs). It surfaces `StrategyConfig` read-only — tuning happens in code, not the UI.

Scenario suite (`scenarios.py`) freezes canonical 21-day historical windows per regime (`huge_down`, `normal_down`, `flat`, `normal_up`, `huge_up`, `v_recovery`, `inverse_v`, plus shape regimes like `gap_shock`, `vol_crush`, `vol_expansion`, `chop_whipsaw`, `earnings_window`). The suite is the regression gate; do not edit it casually — re-curate with `just scenarios-discover` if data drifts.

**Development workflow is the LLM-critic loop:** propose a knob change → validate with `just sweep` (or `just optimize`) → run `just scenarios` to confirm no regime regression → adopt or reject → append a `STRATEGY.md` history entry (including null results — those prevent re-proposing the same change). See `MEMORY.md` and `STRATEGY.md` history for the trail.

## Documentation convention

Two docs are the source of truth. Keep them in sync when you change the engine or the strategy.

| Doc | Covers | When to update |
|---|---|---|
| [ENGINE.md](ENGINE.md) | Backtest harness — modules, data flow, pricing assumptions, event-loop semantics, known limitations, roadmap | Any change to `data.py`, `pricing.py`, `backtest.py`, the event loop, metrics, or known limitations |
| [STRATEGY.md](STRATEGY.md) | Trading rules — entry logic, exit ladder, `StrategyConfig` defaults, latest baseline results, tuning targets | Any change to `strategies.py`, default knob values, exit-ladder ordering, regime gates, or backtest results worth pinning |

Both follow the same format:

1. **Current state at the top** — rewrite this section in place each time the truth changes. Do not append updates to the top section; replace the relevant content so a reader can trust the top to be current.
2. **Dated history entry at the bottom** — append a new entry with the date (YYYY-MM-DD) summarising what changed and why. Never edit old history entries.

Bias toward updating in the same commit that changes the code. If a session ends with code changed but docs stale, treat the docs as the next task.

## Code style for this repo

- Default to no comments unless the *why* is non-obvious. Don't comment what well-named identifiers already say.
- Don't add docstrings beyond one line for simple functions. Module-level docstrings at the top of each file are fine.
- Don't write helper layers, abstractions, or feature flags for hypothetical future needs. Build for the case in front of you.
- Don't add backwards-compatibility shims when refactoring. If the project is small enough to rewrite, rewrite it.
- Prefer extending `StrategyConfig` with a new knob over hard-coding new logic. The whole point of the engine is parameter sweeps.

## Backtest hygiene

- **No future leakage.** Every feature in `data.py` is computed using only past bars relative to its row. The engine reads row t and uses row t for both decisions and the mark; outcomes show up on row t+1.
- **Calendar days for time decay** (not trading days). Options decay over weekends.
- **One position per ticker.** v1 doesn't model stacking.
- **Daily bars are the granularity.** The exit ladder cannot fire intraday. When tightening stops, remember this is the source of most catastrophic losses.
- **Per-contract P/L** in reports. Multiply by 100 for per-share if you want dollars, or by contracts traded for portfolio sizing.

## When changing strategy parameters

Don't eyeball "better defaults" into `strategies.py`. Run the optimizer (`just optimize`) and let walk-forward results justify the change. Then update STRATEGY.md's "Current config defaults" table and append a history entry.

## The required pre/post-change check: `just scenarios`

**Before AND after every change to `strategies.py`, `data.py::_classify_regime`, or any `StrategyConfig` default**, run `just scenarios` and compare the per-regime table. Aggregate P/L can hide regime-specific failures. The scenario suite covers `huge_down`, `normal_down`, `flat`, `normal_up`, `huge_up`, `v_recovery`, `inverse_v` — every change must improve or hold each regime, not just the average.

If a change improves one regime but degrades another, that's a tradeoff to surface explicitly in the STRATEGY.md history entry, not paper over with "aggregate improved."

`just optimize` answers "what's the best static config across history." `just scenarios` answers "where does the current strategy break." Both are needed.

## Live and backtest must stay unified

`live.py::make_recommendation()` calls `strategies.pick_entry()` directly. **Do not create a parallel "live" entry function or duplicate the regime/strike/credit logic anywhere else.** If the live recommendation needs a new field, add it to the dict in `live.py`; if it needs different *logic*, change `strategies.py` (and re-run `just scenarios` per the rule above). The legacy `dynamic_parameter_engine.py` is retired — do not tune it, do not import it from new code.

Same principle for the dashboard: `tsla_options_dashboard.py` calls into `data.py`, `backtest.py`, `strategies.py`, `scenarios.py`, `live.py`. It is a view, not a fork.

## Legacy files

The repo has a layer of pre-engine `.md` docs and `.py` stubs in the root. Don't extend or modify them — they're historical artifacts. The active code is what's listed in README.md → Code map.

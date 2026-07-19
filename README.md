# Trader — personal desk + Agentic autonomy engine

**Monorepo (dual desk).** Repo: [`kenyip/trader`](https://github.com/kenyip/trader) · local: `~/dev/trader` · package: `trader_platform`.

| Desk | For | Do not |
|---|---|---|
| **A — Personal tracker** | Your positions, PMCC, TSLA/TSLL methods, AI coaching | Auto-trade main book |
| **B — Agentic engine** | Find → evaluate → wait → paper → (Ken-armed) live on $3k sleeve | Live without arm |

See [docs/TRADER_DUAL_DESK.md](docs/TRADER_DUAL_DESK.md) and [docs/TRADER_SPINE_ARCHITECTURE.md](docs/TRADER_SPINE_ARCHITECTURE.md).

## Quick start

```bash
just setup                            # one-time: venv + deps
just positions                        # Desk A: your open positions (positions.yaml)
just pmcc-manage                      # Desk A: PMCC / LEAPS desk
just desk-brief                       # Desk A: daily gather for AI stance
just test                             # Desk A: TSLA/TSLL live recommendation
just run                              # Streamlit dashboard

# Desk B — discovery is tight sims; opportunity wait is separate
just trader-discover                  # tight multi-gen strategy search/proof
just trader-opportunity               # patient watch + paper handoff (no evolve)
just trader-eval-iv-rich              # evaluate IV-rich seed
just trader-living                    # living seats
just trader-watch                     # watch only
just trader-paper-handoff             # dry-run paper intent when setup exists

just backtest && just scenarios       # classic engine validation
just analyze                          # critic loop (Desk A methods research)
```

## Source-of-truth documents

| Doc | Covers |
|---|---|
| [**docs/TRADER_DUAL_DESK.md**](docs/TRADER_DUAL_DESK.md) | Personal tracker vs Agentic engine; rename decision |
| [**docs/TRADER_PLATFORM_GOAL.md**](docs/TRADER_PLATFORM_GOAL.md) | Desk B product pin — research → paper → armed live |
| [**docs/TRADER_SPINE_ARCHITECTURE.md**](docs/TRADER_SPINE_ARCHITECTURE.md) | StrategySpec → evaluate → living seats → watcher |
| [**GOAL.md**](GOAL.md) | Legacy critic-loop engine goal (Desk A seed methods) |
| [**ENGINE.md**](ENGINE.md) | Backtest harness modules and pricing assumptions |
| [**STRATEGY.md**](STRATEGY.md) | Seed TSLA/TSLL trading rules and history |
| [**docs/DESK_BRIEF.md**](docs/DESK_BRIEF.md) | Daily desk brief playbook |
| [**docs/TRADER_AGENT_PROFILE.md**](docs/TRADER_AGENT_PROFILE.md) | Hermes `trader` profile |
| [**docs/PMCC_MONITOR_DEPLOYMENT.md**](docs/PMCC_MONITOR_DEPLOYMENT.md) | PMCC monitor deployment |

Both follow the same convention: **current state at the top, dated history at the bottom.**

## Code map

```
# active engine
data.py                       yfinance loader + feature pipeline + regime classifier
pricing.py                    Black-Scholes price/greeks + strike-from-delta solver
backtest.py                   Position, Backtester event loop, metrics, wheel state machine
strategies.py                 StrategyConfig, DEFAULT_CONFIG_BY_TICKER, get_config(ticker),
                              pick_entry, check_exits, pick_covered_call (wheel)
scenarios.py                  canonical 12-regime windows (huge_down, flat, gap_shock,
                              vol_crush, vol_expansion, chop_whipsaw, earnings_window, ...)
run_backtest.py               CLI for the baseline backtest (--wheel flag for wheel mode)
run_scenarios.py              CLI for the canonical scenario suite
optimize.py                   walk-forward grid search + --static OOS validation of fixed config
sweep.py                      reusable knob-sweep harness (LLM-critic loop)
live.py                       today's recommendation (uses pick_entry + per-ticker get_config)
positions.py                  active-position tracker — runs exit ladder on user's open positions
manage_positions.py           CLI driver for positions (add/close/check/example)
tsla_options_dashboard.py     Streamlit dashboard — Today / Positions / Performance / Scenarios

# user-supplied (gitignored)
positions.yaml                user's open option positions, source of truth for `just positions`

# retired — kept as historical artifacts, do not extend or tune:
dynamic_parameter_engine.py   pre-engine "live" recommender (superseded by live.py)
strategy_v6_dynamic.py        thin wrapper for above
strategy_v5_optimized.py      scenario classifier class (logic absorbed into data.py)
walk_forward_optimizer.py     broken — replaced by optimize.py
tsla_tsll_options_tracker.py  one-line stub
strategy_v4.py / strategy_final.py / recent_performance.py / ab_test_v4_vs_v5.py  stubs
backtest_short_term_calls.py / backtest_strangle_early_exit.py  early synthetic-GBM experiments
sweep_*.py (multiple)         per-round bespoke sweep scripts from critic rounds 1-4 — all
                              superseded by sweep.py; kept for now as artifacts of each round.
```

## Session arc (2026-05-12 to 2026-05-14)

Strategy went from **v1.1 (−$6,242 on TSLA 5y, $12,292 max DD, profit factor 0.87)** to
**v1.13 (+$17,790 on TSLA 5y, $1,107 max DD, profit factor 5.25, 92% win rate)** —
a +$24,032 swing with 91% DD reduction, via the LLM-critic loop and a fleet of 5
empirically-validated adaptive rules.

- **v1.9** introduces the *symmetric direction* rule: regime tells us which side of
  the chain to sell (bullish/neutral → put, bearish → call), then per-ticker DTE ×
  delta tunes for reversal-resistance.
- **v1.10** decouples *exits* from entry signals per ticker. TSLA drops the
  `regime_flip` exit (+$2,214 P/L from letting positions ride to profit-based exits
  instead of being prematurely closed on regime change). TSLL effectively disables
  the `max_loss` dollar-threshold stop — the leveraged-ETF `delta_breach=0.45` is
  the real tail protection.
- **v1.11** lands the *adaptive-rules architecture* — `adapt_entry_params(row, cfg)`
  hook that lets context-aware rules adjust entry params on each bar using all
  available features. No rule ships in v1.11; the architecture is the extension
  point.
- **v1.12** wires the *data-driven proposer* — `analyze.py` ingests trade-log +
  feature-panel + greeks-at-entry, ranks features by effect size, emits rule
  sketches in hook syntax. Ships `tsll_skip_marginal_up` (first adaptive rule)
  validated triple-win.
- **v1.13** (this session) brings the loop to *production:* analyzer extensions
  (`--scan-narrow` with BH-FDR correction, `--pairs` for 2-feature interactions),
  per-position knob overrides (M4), an exit-side adaptive hook (M5), the
  `validate_rule.py` A/B harness, and **4 new adaptive rules** all surfaced
  directly by the analyzer:
  - `tsla_skip_mild_intraday_up` — skip when 0.5% ≤ intraday_return ≤ 1.6%
    (triple-win: +$1,511 P/L, −$749 DD, +$1,604 OOS)
  - `tsll_skip_tuesday` — skip Tuesday entries (3-of-4 surfaces positive)
  - `tsll_skip_post_earnings_drift` — skip 11–21 days after earnings (triple-win)
  - `tsll_skip_downtrend_high_iv` — pair conjunction `ret_14d × iv_rank`
    (triple-win, from `--pairs` scan)
  5 rules total; GOAL.md success criteria reached.

Full progression and per-version learning trail: see [STRATEGY.md history](STRATEGY.md#history)
and [ENGINE.md history](ENGINE.md#history).

## Disclaimer

Educational use only. This is research code, not trading advice.

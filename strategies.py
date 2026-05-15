#!/usr/bin/env python3
"""
Strategy layer: entry signals + exit ladder.

Single-leg short premium. The classifier in data.py picks one side per evaluation;
this module turns that signal into a Position and manages it through the exit
ladder. No state held outside Position itself — the engine re-evaluates every bar.

Exit ladder (first to fire wins, checked in this order):
    1. expiration           T <= 0  →  settle intrinsic
    2. max loss             pnl <= -max_loss_mult * credit
    3. daily profit capture pnl/days >= daily_capture_mult * (credit / dte_at_entry)
    4. profit target        pnl >= profit_target * credit
    5. delta breach         |delta| > delta_breach
    6. DTE stop             dte_remaining <= dte_stop (longer-dated only)
    7. regime flip          puts close on reversal/bearish; calls close on bullish
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
import numpy as np
import pandas as pd

import pricing
from backtest import Position


@dataclass
class StrategyConfig:
    # entry filter
    iv_rank_min: float = 10.0           # skip if iv_rank below this
    min_credit_pct: float = 0.010       # v1.3: skip if credit / strike < this (1.0% floor; swept best for both tickers)

    # default ("long-dated") trade — used outside reversal/high-iv
    long_target_delta: float = 0.15     # v1.1: walk-forward modal (6/11 windows)
    long_dte: int = 30

    # defensive trade — used on reversal or high_iv (in non-bearish regimes)
    short_target_delta: float = 0.17
    short_dte: int = 7

    # bearish-regime trade — symmetric to the long-put trade, but sells a call.
    # `bear_dte = 0` means disabled (legacy stand-aside behavior). Any positive
    # value enables the call branch in bearish regimes with these parameters.
    bear_dte: int = 0
    bear_target_delta: float = 0.20

    # exits
    profit_target: float = 0.55         # fraction of credit
    max_loss_mult: float = 1.8          # in multiples of credit
    delta_breach: float = 0.38          # |delta| trigger
    dte_stop: int = 21                  # close longer trades at this DTE
    dte_stop_min_entry: int = 14        # only apply dte_stop for entries above this
    regime_flip_exit_enabled: bool = True   # when False, only profit-side + max_loss + delta_breach fire (regime-change doesn't close)

    # daily profit capture multipliers, picked at entry by DTE bucket
    daily_capture_mult_short: float = 1.0   # DTE <= 7
    daily_capture_mult_mid: float = 1.5     # DTE 8 – 15
    daily_capture_mult_long: float = 1.5    # v1.1: walk-forward consensus (10/11 windows)

    # execution
    slippage_pct: float = 0.0           # applied to every exit fill
    gap_slippage_mult: float = 0.15     # v1.3: extra slippage on max_loss exits after a gap day
    gap_threshold_pct: float = 0.03     # v1.3: overnight |gap| that triggers gap_slippage_mult
    risk_free_rate: float = 0.04

    # wheel mechanic (v1.4) — accept put assignment, sell aggressive covered calls
    wheel_enabled: bool = False         # off by default — existing backtests unchanged
    cc_dte: int = 14                    # DTE for covered calls (shorter than puts → more cycles)
    cc_target_delta: float = 0.30       # used only if cc_strike_mode == 'delta'
    cc_strike_mode: str = 'basis'       # 'basis' (aggressive, sell AT basis to cycle out) | 'delta'
    wheel_put_dte: int = 14             # DTE for wheel-mode puts (shorter than long_dte=30 → less time for regime_flip to fire before expiration)
    wheel_put_max_loss_mult: float = 3.0  # override max_loss_mult for wheel-mode puts; ≥3.0 lets puts survive deeper before stopping out
    wheel_skip_regime_flip: bool = True   # in wheel mode, don't close puts on bearish regime — accept assignment instead

    # roll-on-max_loss (v1.11) — when max_loss fires, attempt a credit roll instead of leaving flat
    roll_on_max_loss: bool = False      # off by default — preserves v1.10 behavior
    roll_dte: int = 14                  # DTE of the rolled position (longer = more theta room to recover)
    roll_target_delta: float = 0.15     # delta of the rolled strike (lower than entry → further OTM)
    roll_credit_ratio: float = 1.0      # require new_credit >= roll_credit_ratio × close_cost (1.0 = credit roll)
    # v1.10 — trade-group cap policy. A "chain" is one originating entry + up to
    # max_rolls_per_group rolls. max_chain_loss_mult bounds total realized loss
    # across the chain (relative to the first position's credit). When either is
    # exceeded the chain accepts the loss and terminates; a fresh entry starts a
    # new group on the next bar.
    max_rolls_per_group: int = 1        # legacy: 1 keeps v1.11 single-roll behavior
    max_chain_loss_mult: float = 2.0    # hard cap on cumulative chain loss in multiples of first credit

    # adaptive rules (v1.11) — extension point for context-aware knob adjustment
    # at pick_entry time. Each rule is a function (row, cfg, current) -> dict that
    # may modify the per-entry params or set 'skip': True. Default = no rules =
    # behavior identical to v1.10. Rules are registered in `ADAPTIVE_RULES`.
    adaptive_rules: tuple = ()
    # v1.13 — exit-side adaptive rules. Each rule is a function
    # (position, mark, row, cfg) -> dict. May return {'close': True, 'reason': str}
    # to close the position with a custom reason. Empty dict = no-op (defer to
    # the standard ladder). Rules are registered in `ADAPTIVE_EXIT_RULES`.
    # When set, exit rules fire BEFORE the standard ladder (highest priority).
    exit_rules: tuple = ()
    ticker: str = ''                    # set by get_config so rules can branch per-ticker without re-plumbing


# v1.5: per-ticker defaults from the DTE × delta sweep on 5y backtest + 12-regime suite validation.
# Different underlyings have different optimal entry params (TSLL is 2x-leveraged, smaller price,
# higher relative IV → shorter DTE / higher delta is the sweet spot).
DEFAULT_CONFIG_BY_TICKER = {
    'TSLA': {'long_dte': 7,  'long_target_delta': 0.20, 'min_credit_pct': 0.010, 'delta_breach': 0.50, 'daily_capture_mult_short': 2.0, 'bear_dte': 3, 'bear_target_delta': 0.20, 'regime_flip_exit_enabled': False, 'adaptive_rules': ('tsla_skip_mild_intraday_up',)},
    'TSLL': {'long_dte': 3,  'long_target_delta': 0.30, 'min_credit_pct': 0.012, 'delta_breach': 0.45, 'daily_capture_mult_short': 1.25, 'max_loss_mult': 10.0, 'bear_dte': 5, 'bear_target_delta': 0.20, 'adaptive_rules': ('tsll_skip_marginal_up', 'tsll_skip_tuesday', 'tsll_skip_post_earnings_drift', 'tsll_skip_downtrend_high_iv')},
}


def get_config(ticker: str, **overrides) -> StrategyConfig:
    """Return the per-ticker default config, optionally with field overrides."""
    base = DEFAULT_CONFIG_BY_TICKER.get(ticker, {})
    merged = {'ticker': ticker, **base, **overrides}
    return StrategyConfig(**merged)


# v1.11 — adaptive-rules registry. Each entry is name → callable.
# A rule has signature: (row: pd.Series, cfg: StrategyConfig, current: dict) -> dict
# and may return any subset of {'skip': True, 'side': 'put'|'call', 'dte': int,
# 'target_delta': float}. Returning {} means no-op. Rules see the current resolved
# params via `current` and the row's features via `row`. They can branch on
# cfg.ticker to apply per-ticker logic.
ADAPTIVE_RULES: dict[str, Callable] = {}

# v1.13 — exit-side adaptive rules registry. Each entry is name → callable
# with signature: (position, mark, row, cfg) -> dict. Return {'close': True,
# 'reason': str} to short-circuit the standard ladder. Default empty dict =
# defer to the ladder.
ADAPTIVE_EXIT_RULES: dict[str, Callable] = {}


def adapt_exit_params(position, mark: dict, row: pd.Series, cfg: StrategyConfig) -> dict:
    """Run any active exit-side rules in registration order. The first rule
    that returns {'close': True, ...} wins."""
    if not getattr(cfg, 'exit_rules', ()):
        return {}
    for name in cfg.exit_rules:
        rule = ADAPTIVE_EXIT_RULES.get(name)
        if rule is None:
            continue
        diff = rule(position, mark, row, cfg)
        if diff and diff.get('close'):
            return diff
    return {}


def _rule_tsll_skip_marginal_up(row, cfg, current):
    """v1.12 — skip TSLL entries when ret_14d ∈ [0, +5%].

    Empirical motivation (v1.10 trade-log bucket analysis):
        ret_14d in [0, +0.05] on TSLL: n=28, wr=57%, avg=$-0.9, total=-$25
        All other ret_14d buckets are clearly profitable.

    Hypothesis: "stalled rally after a small up-move" is the symmetric-direction
    blind spot — regime says bullish but momentum is fading, so put entries get
    caught by reversals more often than the larger-move buckets.
    """
    if cfg.ticker != 'TSLL':
        return {}
    r14 = row.get('ret_14d')
    if r14 is None or not np.isfinite(r14):
        return {}
    if 0.0 <= r14 <= 0.05:
        return {'skip': True}
    return {}


ADAPTIVE_RULES['tsll_skip_marginal_up'] = _rule_tsll_skip_marginal_up


def _rule_tsll_skip_low_gamma(row, cfg, current):
    """v1.13 — skip TSLL entries when the would-be position's gamma_dollar
    is in the low-but-not-tiny band [0.02, 0.08].

    Empirical motivation (analyze.py bins=5 on TSLL 5y trade log):
        peek_gamma_dollar ∈ (0.0209, 0.0767]: n=48, wr=56%, avg=$-3.9, t=-2.50

    Mechanism: gamma_dollar = γ × S² × IV² / 365 is the expected daily P/L cost
    from gamma. A *moderately low* gamma_dollar combined with TSLL's high
    realized vol implies the strike is far enough OTM that credit is thin
    relative to the still-meaningful adverse-move risk — small credit, real
    tail. The lowest gamma_dollar bucket (extremely OTM) is empirically
    neutral because protection-by-distance compensates; this band is the
    "stuck in the middle" zone.
    """
    if cfg.ticker != 'TSLL':
        return {}
    g = current.get('gamma_dollar')
    if g is None or not np.isfinite(g):
        return {}
    if 0.02 <= g <= 0.08:
        return {'skip': True}
    return {}


ADAPTIVE_RULES['tsll_skip_low_gamma'] = _rule_tsll_skip_low_gamma


def _rule_tsll_skip_late_post_earnings(row, cfg, current):
    """Candidate: skip TSLL entries 49-70 days after earnings.

    Empirical motivation (analyze.py bins=4 on TSLL 5y trade log):
        days_since_earnings ∈ (49, 70.75]: n=58, wr=64%, avg=$-2.8, t=-1.76

    Mechanism (hypothesized): this window often falls 7-10 trading days before
    the next earnings event — IV is creeping up but not yet at the earnings
    premium that would meaningfully justify entry credit. Bull-side puts get
    caught in the IV crush or pre-event chop.
    """
    if cfg.ticker != 'TSLL':
        return {}
    d = row.get('days_since_earnings')
    if d is None or not np.isfinite(d):
        return {}
    if 49 <= d <= 70:
        return {'skip': True}
    return {}


ADAPTIVE_RULES['tsll_skip_late_post_earnings'] = _rule_tsll_skip_late_post_earnings


def _rule_tsla_skip_mild_intraday_up(row, cfg, current):
    """v1.13 — skip TSLA entries when intraday_return ∈ [0.5%, 1.6%].

    Empirical motivation (analyze.py narrow-window scan on TSLA 5y trade log):
        intraday_return ∈ (0.505, 1.605]: n=13, wr=62%, avg=$-113.4, t=-1.98
        total impact in bucket: $-1,474 (≈9% of 5y P/L on 12% of trades)

    Hypothesis: "exhaustion candle into a mild green day" — small positive
    intraday moves often precede next-bar reversals. The bullish-regime path
    fires (so we sell puts) but the realized continuation is reversed,
    catching the short put. Sharper moves (>1.6%) typically trend; this
    middle zone is the failure mode.
    """
    if cfg.ticker != 'TSLA':
        return {}
    ir = row.get('intraday_return')
    if ir is None or not np.isfinite(ir):
        return {}
    if 0.505 <= ir <= 1.605:
        return {'skip': True}
    return {}


ADAPTIVE_RULES['tsla_skip_mild_intraday_up'] = _rule_tsla_skip_mild_intraday_up


def _rule_tsll_skip_tuesday(row, cfg, current):
    """v1.13 — skip TSLL entries on Tuesdays.

    Empirical motivation (analyze.py narrow-window scan on TSLL 5y trade log):
        day_of_week ∈ [0.8, 1.5] (Tuesday only): n=49, wr=65%, avg=$-5.7, t=-1.91
        total impact: $-279 across 49 trades.

    Mechanism (hypothesized): Tuesday TSLL puts at 3-DTE expire Friday, so
    they sit through a full Wed→Thu→Fri trading sequence — typically more
    overnight gap risk than Wed or Thu entries, and the daily_capture-friendly
    Friday entries skew much better (Friday n=56 avg=$+34 wr=88%, the
    strongest day of the week).
    """
    if cfg.ticker != 'TSLL':
        return {}
    d = row.get('day_of_week')
    if d is None or not np.isfinite(d):
        return {}
    if int(d) == 1:  # Tuesday (Mon=0, Tue=1, …, Fri=4)
        return {'skip': True}
    return {}


ADAPTIVE_RULES['tsll_skip_tuesday'] = _rule_tsll_skip_tuesday


def _rule_tsll_skip_low_gamma_band(row, cfg, current):
    """v1.13 — skip TSLL entries when gamma_dollar ∈ [0.037, 0.070] (narrow band).

    Empirical motivation (analyze.py narrow-window scan on TSLL 5y trade log,
    measured AFTER tsll_skip_tuesday is active so the residual signal is the
    remaining gamma_dollar effect):
        peek_gamma_dollar ∈ (0.037, 0.070]: n=23, wr=48%, avg=$-6.5, t=-2.34
        total impact: $-150 in this narrow band.

    Replaces the earlier wider [0.02, 0.08] band (null result — that band
    swept up neutral trades). The narrow scan finds the sharper "moderately
    OTM with thin credit" zone where the wider band was diluted by either
    extremely-OTM (safe) or higher-gamma (well-credited) trades.
    """
    if cfg.ticker != 'TSLL':
        return {}
    g = current.get('gamma_dollar')
    if g is None or not np.isfinite(g):
        return {}
    if 0.037 <= g <= 0.070:
        return {'skip': True}
    return {}


ADAPTIVE_RULES['tsll_skip_low_gamma_band'] = _rule_tsll_skip_low_gamma_band


def _rule_tsll_skip_post_earnings_drift(row, cfg, current):
    """v1.13 — skip TSLL entries 11-21 days after earnings.

    Empirical motivation (analyze.py narrow-window scan on TSLL 5y trade log,
    measured AFTER tsll_skip_tuesday is active):
        days_since_earnings ∈ (11.4, 20.8]: n=21, wr=62%, avg=$-6.8, t=-2.15
        total impact: $-143.

    Hypothesis: this window catches the post-earnings drift / IV-rank decay
    period where IV-rank often re-crosses the entry threshold, but realized
    moves are still driven by the recent earnings reaction. The IV-rank
    signal is misleading — TSLL puts entered here get caught by the residual
    post-earnings volatility.
    """
    if cfg.ticker != 'TSLL':
        return {}
    d = row.get('days_since_earnings')
    if d is None or not np.isfinite(d):
        return {}
    if 11 <= d <= 21:
        return {'skip': True}
    return {}


ADAPTIVE_RULES['tsll_skip_post_earnings_drift'] = _rule_tsll_skip_post_earnings_drift


def _rule_tsll_skip_downtrend_high_iv(row, cfg, current):
    """v1.13 — skip TSLL puts when 14-day return is meaningfully negative AND
    iv_rank is elevated. The interaction is the signal.

    Empirical motivation (analyze.py --pairs scan on TSLL 5y trade log,
    measured AFTER all other v1.13 rules are active):
        ret_14d ∈ (-0.632, -0.073] × iv_rank ∈ (77.4, 100]: n=19, wr=58%,
        avg=$-11.7, t=-2.49, p=0.022 (total = $-222).

    Hypothesis: post-decline IV spike that hasn't yet capitulated — premium
    looks rich (high iv_rank) but the underlying is still trending down, so
    the bullish-regime put-sell pretext gets caught by continued downside.
    The combo is more selective than either feature alone (ret_14d quartile
    bucket alone is positive; iv_rank quartile alone is positive).
    """
    if cfg.ticker != 'TSLL':
        return {}
    r14 = row.get('ret_14d')
    ivr = row.get('iv_rank')
    if r14 is None or ivr is None or not (np.isfinite(r14) and np.isfinite(ivr)):
        return {}
    if -0.632 <= r14 <= -0.073 and ivr >= 77.0:
        return {'skip': True}
    return {}


ADAPTIVE_RULES['tsll_skip_downtrend_high_iv'] = _rule_tsll_skip_downtrend_high_iv


def _exit_rule_take_half_on_reversal(position, mark: dict, row: pd.Series, cfg: StrategyConfig) -> dict:
    """v1.13 EXAMPLE exit rule — close early when we're already ≥50% in profit AND
    today is a reversal (puts) or bearish (calls). Locks in half-credit before the
    standard daily_capture/profit_target rungs do, on the day the context turns against
    us. Not enabled by default; demonstrates the exit-side hook contract.
    """
    pnl = position.credit - mark['price'] * (1.0 + cfg.slippage_pct)
    if pnl < 0.5 * position.credit:
        return {}
    if position.side == 'put' and bool(row.get('reversal', False)):
        return {'close': True, 'reason': 'adapt_exit_half_reversal'}
    if position.side == 'call' and row.get('regime') == 'bullish':
        return {'close': True, 'reason': 'adapt_exit_half_bull_flip'}
    return {}


ADAPTIVE_EXIT_RULES['take_half_on_reversal'] = _exit_rule_take_half_on_reversal


def _peek(row: pd.Series, cfg: StrategyConfig, current: dict) -> dict:
    """v1.12 — call pricing.peek_position with the current resolved params.
    Returns the peek dict; caller merges its keys into `current` so rules can
    read greeks (delta, gamma, theta, vega) and derived metrics (theta_yield,
    gamma_dollar, strike, credit) for the would-be position."""
    return pricing.peek_position(
        S=float(row['close']),
        dte=int(current['dte']),
        target_delta=float(current['target_delta']),
        side=current['side'],
        iv=float(row['iv_proxy']),
        r=cfg.risk_free_rate,
    )


def adapt_entry_params(row: pd.Series, cfg: StrategyConfig, base: dict) -> dict:
    """Apply the active adaptive rules to `base` in registration order.

    Each rule sees the current intended params + the row's features + the
    would-be position's greeks (peeked from BSM at the current candidate
    params). Each rule can modify side / dte / target_delta or set
    'skip': True. After any rule modifies dte/target_delta, the peek is
    refreshed so the next rule sees current greeks.

    Default (no rules) returns `base` unchanged → zero behavior change vs v1.10.
    """
    if not cfg.adaptive_rules:
        return base
    current = dict(base)
    # Initial peek for the regime-branch base params
    current.update(_peek(row, cfg, current))
    for name in cfg.adaptive_rules:
        rule = ADAPTIVE_RULES.get(name)
        if rule is None:
            continue
        diff = rule(row, cfg, current)
        if diff:
            params_changed = any(k in diff for k in ('dte', 'target_delta', 'side'))
            current.update(diff)
            if params_changed and not current.get('skip'):
                current.update(_peek(row, cfg, current))
        if current.get('skip'):
            break
    return current


def _daily_capture_mult_for(dte: int, cfg: StrategyConfig) -> float:
    if dte <= 7:
        return cfg.daily_capture_mult_short
    if dte <= 15:
        return cfg.daily_capture_mult_mid
    return cfg.daily_capture_mult_long


def pick_entry(row: pd.Series, cfg: StrategyConfig, S: float, today: pd.Timestamp):
    """Decide side + parameters from regime flags, then size a Position."""
    iv = float(row['iv_proxy'])
    if not np.isfinite(iv) or iv <= 0:
        return None
    if row['iv_rank'] < cfg.iv_rank_min:
        return None

    if row['regime'] == 'bearish':
        if cfg.bear_dte <= 0:
            return None  # legacy stand-aside behavior
        side = 'call'
        target_delta = cfg.bear_target_delta
        dte = cfg.bear_dte
    else:
        defensive = bool(row['reversal']) or (
            bool(row['high_iv']) and row['ema_21'] < row['ema_55']
        )
        if defensive:
            side = 'call'
            target_delta = cfg.short_target_delta
            dte = cfg.short_dte
        elif cfg.wheel_enabled:
            side = 'put'
            target_delta = cfg.long_target_delta
            dte = cfg.wheel_put_dte    # shorter DTE in wheel mode → less time for regime_flip to fire
        else:
            side = 'put'
            target_delta = cfg.long_target_delta
            dte = cfg.long_dte

    # v1.11 — adaptive rules may adjust (side, dte, target_delta) or force skip
    # v1.13 — rules may also return per-position knob overrides:
    #   min_credit_pct, max_loss_mult, delta_breach, profit_target, daily_capture_mult
    resolved = adapt_entry_params(row, cfg, {'side': side, 'dte': dte, 'target_delta': target_delta})
    if resolved.get('skip'):
        return None
    side = resolved['side']
    dte = int(resolved['dte'])
    target_delta = float(resolved['target_delta'])

    T = dte / 365.0
    try:
        K_exact = pricing.strike_from_delta(S, T, iv, target_delta, side, r=cfg.risk_free_rate)
    except ValueError:
        return None
    K = pricing.round_strike(K_exact, 2.5)

    credit = pricing.price(S, K, T, iv, side, r=cfg.risk_free_rate)
    credit *= (1.0 - cfg.slippage_pct)
    if credit <= 0.01:
        return None
    # v1.13 — adaptive rule may override the credit floor for this entry
    eff_min_credit_pct = float(resolved.get('min_credit_pct', cfg.min_credit_pct))
    if K > 0 and credit / K < eff_min_credit_pct:
        return None

    expiration = today + pd.Timedelta(days=dte)
    # v1.13 — if a rule supplied a daily_capture_mult override, use it; else DTE-bucket default
    if 'daily_capture_mult' in resolved:
        dcap = float(resolved['daily_capture_mult'])
    else:
        dcap = _daily_capture_mult_for(dte, cfg)

    return Position(
        side=side,
        entry_date=today,
        expiration=expiration,
        strike=K,
        credit=credit,
        dte_at_entry=dte,
        iv_at_entry=iv,
        regime_at_entry=str(row['regime']),
        daily_theta_target=credit / dte,
        daily_capture_mult=dcap,
        max_loss_mult_override=(
            float(resolved['max_loss_mult']) if 'max_loss_mult' in resolved else None
        ),
        delta_breach_override=(
            float(resolved['delta_breach']) if 'delta_breach' in resolved else None
        ),
        profit_target_override=(
            float(resolved['profit_target']) if 'profit_target' in resolved else None
        ),
    )


def check_exits(position: Position, mark: dict, row: pd.Series, cfg: StrategyConfig):
    """Return an exit-reason string if any ladder rung fires, else None.

    Wheel covered calls (`position.is_wheel_cc`) run a simplified ladder: only
    expiration + early profit-take rungs fire — we WANT assignment-away, so
    max_loss / delta_breach / regime_flip don't apply.

    In wheel mode, short puts skip dte_stop and delta_breach so they can ride
    to expiration (where ITM puts become wheel assignments). Loss-protection
    (max_loss) and profit-take (daily_capture, profit_target) still fire.
    """
    cur_price = mark['price'] * (1.0 + cfg.slippage_pct)  # cost to close eats slippage
    cur_delta = mark['delta']
    dte_remaining = mark['dte_remaining']

    if dte_remaining <= 0:
        return 'expired'

    pnl = position.credit - cur_price
    days_held = max((row.name - position.entry_date).days, 1)

    # v1.13 — exit-side adaptive rules run BEFORE the standard ladder so they
    # can close positions on context the ladder can't see (e.g. intraday-reversal
    # take-profit). Skip for wheel-CC since those have their own simplified ladder.
    if not getattr(position, 'is_wheel_cc', False):
        exit_diff = adapt_exit_params(position, mark, row, cfg)
        if exit_diff and exit_diff.get('close'):
            return str(exit_diff.get('reason', 'adapt_exit'))

    if getattr(position, 'is_wheel_cc', False):
        # Wheel covered call: only fast-cycle early profits. Let it ride to assignment.
        if pnl > 0 and pnl / days_held >= position.daily_capture_mult * position.daily_theta_target:
            return 'daily_capture'
        if pnl >= cfg.profit_target * position.credit:
            return 'profit_target'
        return None

    wheel_put = position.side == 'put' and getattr(cfg, 'wheel_enabled', False)

    # 2. max loss — hardest stop, check before profit-side rungs
    # In wheel mode puts get more rope (`wheel_put_max_loss_mult`) so they can survive
    # to expiration; only truly catastrophic dives stop them out before assignment.
    # v1.13 — per-position override (set by adaptive rule at entry) wins over cfg.
    if wheel_put:
        max_loss_mult = cfg.wheel_put_max_loss_mult
    else:
        max_loss_mult = position.max_loss_mult_override if position.max_loss_mult_override is not None else cfg.max_loss_mult
    if pnl <= -max_loss_mult * position.credit:
        return 'max_loss'

    # 3. daily profit capture
    if pnl > 0 and pnl / days_held >= position.daily_capture_mult * position.daily_theta_target:
        return 'daily_capture'

    # 4. hard profit target (v1.13: per-position override allowed)
    profit_target = position.profit_target_override if position.profit_target_override is not None else cfg.profit_target
    if pnl >= profit_target * position.credit:
        return 'profit_target'

    # 5. delta breach (skipped for wheel-mode puts so they can ride into ITM territory)
    # v1.13 — per-position override allowed.
    delta_breach = position.delta_breach_override if position.delta_breach_override is not None else cfg.delta_breach
    if not wheel_put and abs(cur_delta) > delta_breach:
        return 'delta_breach'

    # 6. DTE stop (skipped for wheel-mode puts so they can reach expiration)
    if not wheel_put and position.dte_at_entry > cfg.dte_stop_min_entry and dte_remaining <= cfg.dte_stop:
        return 'dte_stop'

    # 7. regime flip (skipped for wheel-mode puts when wheel_skip_regime_flip — bearish exits would prevent assignment)
    if getattr(cfg, 'regime_flip_exit_enabled', True):
        if position.side == 'put' and (bool(row['reversal']) or row['regime'] == 'bearish'):
            if not (wheel_put and getattr(cfg, 'wheel_skip_regime_flip', False)):
                return 'regime_flip'
        if position.side == 'call' and row['regime'] == 'bullish' and not bool(row['reversal']):
            return 'regime_flip'

    return None


def pick_roll(row: pd.Series, cfg: StrategyConfig, S: float, today: pd.Timestamp,
              closed_position: Position, close_cost: float):
    """v1.11 — when max_loss fires, try to construct a credit-roll position.

    Rules:
    - Same side as the closed position
    - Strike MUST be strictly further OTM than the closed strike (no doubling down)
    - DTE = `roll_dte`, delta = `roll_target_delta`
    - Accept only if new_credit >= roll_credit_ratio × close_cost (credit roll by default)

    Returns a `Position` if a valid roll exists, else None (engine falls through to flat).
    """
    iv = float(row['iv_proxy'])
    if not np.isfinite(iv) or iv <= 0:
        return None

    side = closed_position.side
    dte = cfg.roll_dte
    target_delta = cfg.roll_target_delta
    T = dte / 365.0
    try:
        K_exact = pricing.strike_from_delta(S, T, iv, target_delta, side, r=cfg.risk_free_rate)
    except ValueError:
        return None
    K = pricing.round_strike(K_exact, 2.5)

    # Safety rail: the rolled strike MUST be strictly further OTM than the original.
    # For a put this means a LOWER strike; for a call, a HIGHER strike.
    if side == 'put' and K >= closed_position.strike:
        return None
    if side == 'call' and K <= closed_position.strike:
        return None

    credit = pricing.price(S, K, T, iv, side, r=cfg.risk_free_rate) * (1.0 - cfg.slippage_pct)
    if credit <= 0.01:
        return None
    if credit < cfg.roll_credit_ratio * close_cost:
        return None

    expiration = today + pd.Timedelta(days=dte)
    return Position(
        side=side,
        entry_date=today,
        expiration=expiration,
        strike=K,
        credit=credit,
        dte_at_entry=dte,
        iv_at_entry=iv,
        regime_at_entry='rolled',
        daily_theta_target=credit / dte,
        daily_capture_mult=_daily_capture_mult_for(dte, cfg),
    )


def pick_covered_call(row: pd.Series, cfg: StrategyConfig, S: float, today: pd.Timestamp, stock_basis: float):
    """Wheel: select a covered call against stock acquired at `stock_basis`.

    Aggressive mode (`cc_strike_mode='basis'`): strike = round(basis). We WANT
    to be assigned away — that completes the cycle and frees cash. If stock is
    below basis, this is OTM (we collect premium while waiting for recovery).
    If stock is at/above basis, this is ATM/ITM (immediate assignment likely,
    P/L = credit collected).
    """
    iv = float(row['iv_proxy'])
    if not np.isfinite(iv) or iv <= 0:
        return None
    if row['iv_rank'] < cfg.iv_rank_min:
        return None

    dte = cfg.cc_dte
    T = dte / 365.0

    if cfg.cc_strike_mode == 'basis':
        K = pricing.round_strike(stock_basis, 2.5)
    else:
        try:
            K_exact = pricing.strike_from_delta(S, T, iv, cfg.cc_target_delta, 'call', r=cfg.risk_free_rate)
        except ValueError:
            return None
        K = pricing.round_strike(K_exact, 2.5)

    if K <= 0:
        return None

    credit = pricing.price(S, K, T, iv, 'call', r=cfg.risk_free_rate)
    credit *= (1.0 - cfg.slippage_pct)
    if credit <= 0.01:
        return None
    if credit / K < cfg.min_credit_pct:
        return None

    expiration = today + pd.Timedelta(days=dte)
    pos = Position(
        side='call',
        entry_date=today,
        expiration=expiration,
        strike=K,
        credit=credit,
        dte_at_entry=dte,
        iv_at_entry=iv,
        regime_at_entry='wheel_cc',
        daily_theta_target=credit / dte,
        daily_capture_mult=_daily_capture_mult_for(dte, cfg),
    )
    pos.is_wheel_cc = True
    return pos

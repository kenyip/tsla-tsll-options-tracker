#!/usr/bin/env python3
"""
Backtest engine: daily event loop + per-position mark-to-market.

The engine is strategy-agnostic. It owns:
- the Position dataclass and its daily mark-to-market
- the event loop (iterate features DataFrame, manage at most one open position
  per ticker, defer entry/exit decisions to the strategy layer)
- post-run metric aggregation

The strategy layer (strategies.py) decides what to open and when to close.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable
import numpy as np
import pandas as pd

import pricing


@dataclass
class Position:
    side: str                       # 'put' | 'call' | 'stock' (synthetic, wheel only)
    entry_date: pd.Timestamp
    expiration: pd.Timestamp
    strike: float
    credit: float                   # per share, received at entry (or sale proceeds for 'stock' legs)
    dte_at_entry: int
    iv_at_entry: float
    regime_at_entry: str
    daily_theta_target: float       # = credit / dte_at_entry
    daily_capture_mult: float       # frozen at entry from DTE bucket
    closed: bool = False
    exit_date: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None   # per-share cost to close (or cost basis for 'stock' legs)
    exit_reason: Optional[str] = None
    is_wheel_cc: bool = False            # v1.4 — tag covered calls so check_exits runs simplified ladder
    is_roll: bool = False                # v1.11 — tag positions opened via roll-on-max_loss (no further rolls)
    # v1.13 — per-position knob overrides set by adaptive rules at entry. None → fall back to cfg.
    max_loss_mult_override: Optional[float] = None
    delta_breach_override: Optional[float] = None
    profit_target_override: Optional[float] = None
    # v1.10 — chain id. Fresh entries get a new id; rolled positions and wheel-continuation
    # legs (assigned-stock, CC during HOLDING) inherit it. A "trade group" is the chain
    # of Positions sharing one group_id — the unit at which the strategy is scored.
    group_id: int = -1

    def mark(self, S: float, sigma: float, today: pd.Timestamp, r: float = 0.04) -> dict:
        """Return price / delta / dte_remaining at today's close."""
        days_to_exp = (self.expiration - today).days
        if days_to_exp <= 0:
            if self.side == 'call':
                intrinsic = max(S - self.strike, 0.0)
                d = 1.0 if S > self.strike else 0.0
            else:
                intrinsic = max(self.strike - S, 0.0)
                d = -1.0 if S < self.strike else 0.0
            return {'price': intrinsic, 'delta': d, 'dte_remaining': days_to_exp}

        T = days_to_exp / 365.0
        p = pricing.price(S, self.strike, T, sigma, self.side, r=r)
        d = pricing.delta(S, self.strike, T, sigma, self.side, r=r)
        return {'price': max(p, 0.0), 'delta': d, 'dte_remaining': days_to_exp}

    def pnl_per_share(self, current_price: float) -> float:
        return self.credit - current_price


@dataclass
class Backtester:
    df: pd.DataFrame
    config: object
    entry_fn: Callable
    exit_fn: Callable
    ticker: str = 'TSLA'
    trades: list = field(default_factory=list)
    position: Optional[Position] = None
    # Wheel state (active only when config.wheel_enabled is True)
    stock_basis: Optional[float] = None
    stock_entry_date: Optional[pd.Timestamp] = None
    wheel_cc_fn: Optional[Callable] = None  # set by driver: pick_covered_call
    roll_fn: Optional[Callable] = None      # set by driver: pick_roll (v1.11)
    # v1.10 — trade-group bookkeeping. _current is the id of the currently-open chain
    # (None when flat with no continuation). Reset to None when a chain truly terminates;
    # stays set through rolls and wheel state transitions.
    _next_group_id: int = 0
    _current_group_id: Optional[int] = None
    # v1.10 — chain accumulators used to enforce cap policies (max_rolls_per_group,
    # max_chain_loss_mult). Reset together with _current_group_id.
    _chain_position_count: int = 0
    _chain_realized_pnl: float = 0.0       # per-share, summed across closed positions in chain
    _chain_original_credit: float = 0.0    # credit of first position in chain

    def run(self) -> list[Position]:
        prev_close: Optional[float] = None
        wheel_on = getattr(self.config, 'wheel_enabled', False)

        for today, row in self.df.iterrows():
            S = float(row['close'])
            sigma = float(row['iv_proxy'])
            if not np.isfinite(sigma) or sigma <= 0:
                prev_close = S
                continue

            # 1. Manage existing option position
            if self.position is not None:
                mark = self.position.mark(S, sigma, today)
                exit_decision = self.exit_fn(self.position, mark, row, self.config)
                if exit_decision is not None:
                    if wheel_on and exit_decision == 'expired':
                        # Wheel: handle assignment at expiration. _current_group_id stays
                        # set across put→stock and through CC; only resets when the chain
                        # truly ends (stock leg closes via _close_stock).
                        if self.position.side == 'put' and self.stock_basis is None and S < self.position.strike:
                            self._assign_put(today, S)
                        elif self.position.side == 'call' and self.stock_basis is not None and S > self.position.strike:
                            self._assign_call_away(today)
                        else:
                            fill = self._fill_price(mark['price'], exit_decision, row, prev_close)
                            self._close(today, fill, exit_decision)
                            self._reset_chain()
                    else:
                        fill = self._fill_price(mark['price'], exit_decision, row, prev_close)
                        closing_pos = self.position
                        closing_pnl_share = closing_pos.credit - fill
                        # Update chain accumulators BEFORE _close clears self.position
                        self._chain_realized_pnl += closing_pnl_share
                        self._close(today, fill, exit_decision)

                        max_rolls = getattr(self.config, 'max_rolls_per_group', 1)
                        max_chain_loss_mult = getattr(self.config, 'max_chain_loss_mult', 2.0)
                        cap_chain_loss = max_chain_loss_mult * self._chain_original_credit
                        chain_loss_so_far = -self._chain_realized_pnl  # positive = net loss
                        was_roll_eligible = (
                            exit_decision == 'max_loss'
                            and getattr(self.config, 'roll_on_max_loss', False)
                            and self.roll_fn is not None
                            and self._chain_position_count <= max_rolls
                            and (self._chain_original_credit <= 0 or chain_loss_so_far < cap_chain_loss)
                        )
                        if was_roll_eligible:
                            rolled = self.roll_fn(row, self.config, S, today, closing_pos, fill)
                            if rolled is not None:
                                rolled.is_roll = True
                                rolled.group_id = closing_pos.group_id
                                self.position = rolled
                                self._chain_position_count += 1
                            else:
                                self._reset_chain()
                        else:
                            self._reset_chain()

            # 2. Open a new position
            if self.position is None:
                if wheel_on and self.stock_basis is not None:
                    # HOLDING state: try to open a covered call (inherits chain id)
                    if self.wheel_cc_fn is not None:
                        cc = self.wheel_cc_fn(row, self.config, S, today, self.stock_basis)
                        if cc is not None:
                            cc.group_id = self._current_group_id if self._current_group_id is not None else self._assign_new_group()
                            self.position = cc
                elif self.stock_basis is None:
                    # IDLE state: normal entry — fresh chain
                    new_pos = self.entry_fn(row, self.config, S, today)
                    if new_pos is not None:
                        new_pos.group_id = self._assign_new_group()
                        self._chain_position_count = 1
                        self._chain_realized_pnl = 0.0
                        self._chain_original_credit = new_pos.credit
                        self.position = new_pos

            prev_close = S

        # End-of-data: close any straggler option, and stock if held
        last_date = self.df.index[-1]
        last_row = self.df.iloc[-1]
        S_last = float(last_row['close'])

        if self.position is not None:
            mark = self.position.mark(S_last, float(last_row['iv_proxy']), last_date)
            fill = self._fill_price(mark['price'], 'end_of_data', last_row, prev_close)
            self._close(last_date, fill, 'end_of_data')
            self._reset_chain()

        if self.stock_basis is not None:
            self._close_stock(last_date, S_last, 'end_of_data')

        return self.trades

    def _assign_new_group(self) -> int:
        gid = self._next_group_id
        self._next_group_id += 1
        self._current_group_id = gid
        return gid

    def _reset_chain(self) -> None:
        self._current_group_id = None
        self._chain_position_count = 0
        self._chain_realized_pnl = 0.0
        self._chain_original_credit = 0.0

    def _fill_price(self, mark_price: float, reason: str, row: pd.Series, prev_close: Optional[float]) -> float:
        """Effective price the engine fills at. Mirrors slippage in check_exits and
        applies an extra gap-slippage shock when max_loss fires after an overnight gap."""
        slip = getattr(self.config, 'slippage_pct', 0.0)
        fill = mark_price * (1.0 + slip)
        if reason != 'max_loss' or prev_close is None or prev_close <= 0:
            return fill
        open_px = float(row.get('open', row['close']))
        gap = abs(open_px - prev_close) / prev_close
        if gap > getattr(self.config, 'gap_threshold_pct', 0.03):
            fill *= (1.0 + getattr(self.config, 'gap_slippage_mult', 0.0))
        return fill

    def _close(self, date, price, reason):
        self.position.closed = True
        self.position.exit_date = date
        self.position.exit_price = price
        self.position.exit_reason = reason
        self.trades.append(self.position)
        self.position = None

    def _assign_put(self, today: pd.Timestamp, S: float):
        """Put expired ITM. Record put as 'assigned' with intrinsic exit_price.
        Acquire stock at strike (cost basis = strike, accounting via stock leg later)."""
        p = self.position
        intrinsic = max(p.strike - S, 0.0)
        self._close(today, intrinsic, 'assigned')
        self.stock_basis = p.strike
        self.stock_entry_date = today

    def _assign_call_away(self, today: pd.Timestamp):
        """Covered call expired ITM. Record CC as 'assigned_away'. Sell stock at strike."""
        p = self.position
        # CC intrinsic at expiry is built into the exit; we close it at the intrinsic value
        # corresponding to selling stock at strike. The CC's exit cost = max(S - strike, 0) = S - strike
        # (since S > strike for assignment). But we only need to record the CC's pnl; the stock leg
        # captures the strike-for-basis gain separately.
        strike = p.strike
        # CC intrinsic = whatever the price() mark returned for it; for clarity, recompute as last_S - strike
        # but we don't have last_S handy. Use intrinsic from the mark by reading the latest row's close.
        # Simpler: use strike as a notional exit_price since CC was assigned at strike effectively zero out
        # The cleanest accounting: CC pnl = credit (we kept) - 0 (we didn't pay anything, just delivered shares).
        # The stock leg books the (-basis + strike) gain/loss.
        self._close(today, 0.0, 'assigned_away')
        # Stock sold at strike — realize P/L vs basis
        self._close_stock(today, strike, 'wheel_close')

    def _close_stock(self, date: pd.Timestamp, sale_price: float, reason: str):
        """Realize the stock leg as a synthetic Position(side='stock')."""
        if self.stock_basis is None:
            return
        leg = Position(
            side='stock',
            entry_date=self.stock_entry_date or date,
            expiration=date,
            strike=0.0,
            credit=sale_price,
            dte_at_entry=max((date - (self.stock_entry_date or date)).days, 0),
            iv_at_entry=0.0,
            regime_at_entry='wheel',
            daily_theta_target=0.0,
            daily_capture_mult=0.0,
            closed=True,
            exit_date=date,
            exit_price=self.stock_basis,
            exit_reason=reason,
            group_id=self._current_group_id if self._current_group_id is not None else -1,
        )
        self.trades.append(leg)
        self.stock_basis = None
        self.stock_entry_date = None
        self._current_group_id = None


def trades_to_dataframe(trades: list[Position]) -> pd.DataFrame:
    """Flatten trade objects into a tidy DataFrame for inspection / CSV export."""
    if not trades:
        return pd.DataFrame()
    rows = []
    for t in trades:
        d = asdict(t)
        d['pnl_per_share'] = t.credit - (t.exit_price or 0.0)
        d['pnl_per_contract'] = d['pnl_per_share'] * 100
        d['days_held'] = (t.exit_date - t.entry_date).days if t.exit_date else None
        rows.append(d)
    return pd.DataFrame(rows)


def compute_metrics(trades: list[Position]) -> dict:
    if not trades:
        return {'n_trades': 0}

    pnl_share = np.array([t.credit - t.exit_price for t in trades])
    pnl_contract = pnl_share * 100

    wins = pnl_share[pnl_share > 0]
    losses = pnl_share[pnl_share <= 0]

    equity = np.cumsum(pnl_contract)
    peak = np.maximum.accumulate(equity)
    drawdown = peak - equity

    reason_counts = {}
    for t in trades:
        reason_counts[t.exit_reason] = reason_counts.get(t.exit_reason, 0) + 1

    gross_win = wins.sum()
    gross_loss = abs(losses.sum())
    profit_factor = gross_win / gross_loss if gross_loss > 0 else float('inf')

    days_held = np.array([
        (t.exit_date - t.entry_date).days for t in trades if t.exit_date is not None
    ])

    # v1.10 — group-level metrics. A "trade group" is the chain of Positions sharing
    # a group_id (rolls + wheel continuation legs). Legacy trades pre-v1.10 carry
    # group_id == -1; we synthesize unique ids per position so they're treated as
    # single-position groups (which is what they were).
    group_pnl: dict[int, float] = {}
    group_size: dict[int, int] = {}
    legacy_fallback = -1
    for i, t in enumerate(trades):
        gid = t.group_id if t.group_id >= 0 else (1_000_000 + i)
        group_pnl[gid] = group_pnl.get(gid, 0.0) + (t.credit - (t.exit_price or 0.0)) * 100
        group_size[gid] = group_size.get(gid, 0) + 1
        if t.group_id < 0:
            legacy_fallback = max(legacy_fallback, i)
    group_pnls = np.array(list(group_pnl.values()))
    group_sizes = np.array(list(group_size.values()))
    n_groups = len(group_pnls)
    group_wins = group_pnls[group_pnls >= 0]

    # Capital-time accounting. Capital at risk per option position is roughly the
    # strike (assignment cost ceiling for a short put; same for a covered short call).
    # capital_days = strike * days_held; annualized return = pnl / capital_days * 365.
    capital_days = 0.0
    for t in trades:
        if t.exit_date is None:
            continue
        days = max((t.exit_date - t.entry_date).days, 1)
        cap = t.strike if t.side in ('put', 'call') else (t.exit_price or 0.0)
        capital_days += cap * days
    total_pnl_share = float(pnl_share.sum())
    pnl_per_capital_year = (total_pnl_share / capital_days * 365.0) if capital_days > 0 else 0.0

    # Trade density: groups per year of elapsed market time.
    first_entry = min(t.entry_date for t in trades)
    last_exit = max((t.exit_date or t.entry_date) for t in trades)
    span_days = max((last_exit - first_entry).days, 1)
    trade_density_per_year = n_groups / span_days * 365.0

    return {
        'n_trades': len(trades),
        'win_rate_pct': float(len(wins) / len(trades) * 100),
        'total_pnl_per_contract': float(pnl_contract.sum()),
        'avg_pnl_per_contract': float(pnl_contract.mean()),
        'avg_win_per_contract': float(wins.mean() * 100) if len(wins) else 0.0,
        'avg_loss_per_contract': float(losses.mean() * 100) if len(losses) else 0.0,
        'profit_factor': float(profit_factor),
        'max_dd_per_contract': float(drawdown.max()) if len(drawdown) else 0.0,
        'avg_days_held': float(days_held.mean()) if len(days_held) else 0.0,
        'exit_reasons': reason_counts,
        # v1.10 — group-level
        'n_groups': int(n_groups),
        'group_win_rate_pct': float(len(group_wins) / n_groups * 100) if n_groups else 0.0,
        'avg_group_pnl_per_contract': float(group_pnls.mean()) if n_groups else 0.0,
        'worst_group_pnl_per_contract': float(group_pnls.min()) if n_groups else 0.0,
        'best_group_pnl_per_contract': float(group_pnls.max()) if n_groups else 0.0,
        'avg_positions_per_group': float(group_sizes.mean()) if n_groups else 0.0,
        'max_positions_per_group': int(group_sizes.max()) if n_groups else 0,
        # v1.10 — capital-time
        'capital_days_per_contract': float(capital_days * 100),
        'pnl_per_capital_year_pct': float(pnl_per_capital_year * 100),
        'trade_density_per_year': float(trade_density_per_year),
    }


def groupwise_pnl_by_period(trades: list[Position], freq: str = 'Q') -> pd.DataFrame:
    """v1.10 — bucket trade-group P/L by close-date period. Returns DataFrame with
    one row per period containing n_groups, group_pnl, group_win_rate, worst_group_pnl.
    Used to verify the "every quarter ≥ 0" archetype acceptance criterion.

    freq follows pandas offset aliases: 'Q' (quarter), 'ME' (month-end), 'YE' (year-end).
    Groups span periods by their *last* close date (the chain's terminal exit)."""
    if not trades:
        return pd.DataFrame(columns=['n_groups', 'group_pnl', 'group_win_rate_pct', 'worst_group_pnl'])

    # Aggregate to group level: pnl summed, period determined by max exit_date in chain.
    by_group: dict[int, dict] = {}
    for i, t in enumerate(trades):
        gid = t.group_id if t.group_id >= 0 else (1_000_000 + i)
        pnl_c = (t.credit - (t.exit_price or 0.0)) * 100
        end_date = t.exit_date or t.entry_date
        rec = by_group.setdefault(gid, {'pnl': 0.0, 'end_date': end_date})
        rec['pnl'] += pnl_c
        if end_date and (rec['end_date'] is None or end_date > rec['end_date']):
            rec['end_date'] = end_date

    df = pd.DataFrame([{'end_date': r['end_date'], 'pnl': r['pnl']} for r in by_group.values()])
    df['period'] = pd.to_datetime(df['end_date']).dt.to_period(freq)

    agg = df.groupby('period').agg(
        n_groups=('pnl', 'size'),
        group_pnl=('pnl', 'sum'),
        group_win_rate_pct=('pnl', lambda s: float((s >= 0).mean() * 100)),
        worst_group_pnl=('pnl', 'min'),
    )
    return agg


def format_metrics(m: dict, header: str = '') -> str:
    if m.get('n_trades', 0) == 0:
        return f"{header}\n  no trades"
    lines = [
        header,
        f"  trades            {m['n_trades']}",
        f"  win rate          {m['win_rate_pct']:.1f}%",
        f"  total P/L (1x)    ${m['total_pnl_per_contract']:.2f}",
        f"  avg trade         ${m['avg_pnl_per_contract']:.2f}",
        f"  avg win / loss    ${m['avg_win_per_contract']:.2f} / ${m['avg_loss_per_contract']:.2f}",
        f"  profit factor     {m['profit_factor']:.2f}",
        f"  max drawdown      ${m['max_dd_per_contract']:.2f}",
        f"  avg days held     {m['avg_days_held']:.1f}",
        f"  exit reasons      {m['exit_reasons']}",
    ]
    if 'n_groups' in m:
        lines += [
            f"  -- trade groups (chain of rolls = one group)",
            f"  n groups          {m['n_groups']}  (avg {m['avg_positions_per_group']:.2f} positions/group, max {m['max_positions_per_group']})",
            f"  group win rate    {m['group_win_rate_pct']:.1f}%",
            f"  avg group P/L     ${m['avg_group_pnl_per_contract']:.2f}",
            f"  worst group P/L   ${m['worst_group_pnl_per_contract']:.2f}",
            f"  best group P/L    ${m['best_group_pnl_per_contract']:.2f}",
            f"  -- capital-time (annualized return on strike-days at risk)",
            f"  pnl / cap·yr      {m['pnl_per_capital_year_pct']:.2f}%",
            f"  trade density     {m['trade_density_per_year']:.1f} groups/yr",
        ]
    return '\n'.join(lines)

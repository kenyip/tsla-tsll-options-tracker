"""Paper-only Black-Scholes daily-bar simulator for long call butterflies."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd

import pricing
from trader_platform.research.pcs_sim import capital_fit_pcs, strike_increment_for


def _num(cfg: dict[str, Any], key: str, default: float) -> float:
    try:
        return float(cfg.get(key, default))
    except (TypeError, ValueError):
        return float(default)


@dataclass
class ButterflyTrade:
    entry_date: pd.Timestamp
    expiration: pd.Timestamp
    lower_strike: float
    middle_strike: float
    upper_strike: float
    entry_debit: float
    dte_at_entry: int
    iv_at_entry: float
    regime_at_entry: str
    closed: bool = False
    exit_date: Optional[pd.Timestamp] = None
    exit_credit: Optional[float] = None
    exit_reason: Optional[str] = None

    def mark_credit(
        self,
        spot: float,
        sigma: float,
        today: pd.Timestamp,
        *,
        r: float = 0.04,
        slippage_pct: float = 0.0,
        half_spread_per_leg: float = 0.0,
    ) -> float:
        days = max((self.expiration - today).days, 0)
        if days == 0:
            lower = max(spot - self.lower_strike, 0.0)
            middle = max(spot - self.middle_strike, 0.0)
            upper = max(spot - self.upper_strike, 0.0)
        else:
            t = days / 365.0
            lower = pricing.price(spot, self.lower_strike, t, sigma, "call", r=r)
            middle = pricing.price(spot, self.middle_strike, t, sigma, "call", r=r)
            upper = pricing.price(spot, self.upper_strike, t, sigma, "call", r=r)
        slip = max(float(slippage_pct), 0.0)
        half_spread = max(float(half_spread_per_leg), 0.0)
        return max(
            float(
                (lower + upper) * (1.0 - slip)
                - 2.0 * middle * (1.0 + slip)
                - 4.0 * half_spread
            ),
            0.0,
        )


@dataclass
class ButterflySimResult:
    symbol: str
    ok: bool
    skipped: bool = False
    reason: str = ""
    period: str = ""
    n_trades: int = 0
    metrics: dict[str, Any] = field(default_factory=dict)
    trades: list[ButterflyTrade] = field(default_factory=list)
    capital: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["trades"] = [
            {
                "entry": str(t.entry_date.date()),
                "exit": str(t.exit_date.date()) if t.exit_date is not None else None,
                "lower_strike": t.lower_strike,
                "middle_strike": t.middle_strike,
                "upper_strike": t.upper_strike,
                "dte": t.dte_at_entry,
                "debit": round(t.entry_debit, 4),
                "exit_credit": None if t.exit_credit is None else round(t.exit_credit, 4),
                "pnl_share": None if t.exit_credit is None else round(t.exit_credit - t.entry_debit, 4),
                "reason": t.exit_reason,
            }
            for t in self.trades
        ]
        return data


def pick_butterfly_entry(
    row: pd.Series, spot: float, today: pd.Timestamp, cfg: dict[str, Any]
) -> Optional[ButterflyTrade]:
    sigma = float(row.get("iv_proxy") or 0.0)
    if not np.isfinite(sigma) or sigma <= 0:
        return None
    if float(row.get("iv_rank") or 0.0) < _num(cfg, "iv_rank_min", 0.0):
        return None
    if str(row.get("regime") or "").lower() in {"bearish", "huge_down", "normal_down"}:
        return None

    dte = max(int(round(_num(cfg, "long_dte", 21))), 3)
    target_delta = min(max(_num(cfg, "long_target_delta", 0.35), 0.15), 0.50)
    width = max(_num(cfg, "spread_width", 1.0), 0.5)
    r = _num(cfg, "risk_free_rate", 0.04)
    try:
        middle_exact = pricing.strike_from_delta(
            spot, dte / 365.0, sigma, target_delta, "call", r=r
        )
    except ValueError:
        return None
    increment = strike_increment_for(spot)
    middle = pricing.round_strike(middle_exact, increment)
    wing_steps = max(int(round(width / increment)), 1)
    actual_width = wing_steps * increment
    lower = middle - actual_width
    upper = middle + actual_width
    if lower <= 0:
        return None

    t = dte / 365.0
    slip = max(_num(cfg, "slippage_pct", 0.0), 0.0)
    half_spread = max(_num(cfg, "half_spread_per_leg", 0.0), 0.0)
    lower_call = pricing.price(spot, lower, t, sigma, "call", r=r) * (1.0 + slip) + half_spread
    middle_call = max(
        pricing.price(spot, middle, t, sigma, "call", r=r) * (1.0 - slip) - half_spread,
        0.0,
    )
    upper_call = pricing.price(spot, upper, t, sigma, "call", r=r) * (1.0 + slip) + half_spread
    debit = float(lower_call - 2.0 * middle_call + upper_call)
    if debit <= 0.01 or debit >= actual_width:
        return None
    if debit * 100.0 > _num(cfg, "max_loss_budget_usd", 300.0):
        return None
    return ButterflyTrade(
        entry_date=today,
        expiration=pd.Timestamp(today + pd.Timedelta(days=dte)),
        lower_strike=float(lower),
        middle_strike=float(middle),
        upper_strike=float(upper),
        entry_debit=debit,
        dte_at_entry=dte,
        iv_at_entry=sigma,
        regime_at_entry=str(row.get("regime") or ""),
    )


def _metrics(trades: list[ButterflyTrade]) -> dict[str, Any]:
    if not trades:
        return {"n_trades": 0, "structure": "butterfly_spread"}
    pnl = np.array([((t.exit_credit or 0.0) - t.entry_debit) * 100.0 for t in trades], dtype=float)
    equity = np.cumsum(pnl)
    dd = np.maximum.accumulate(equity) - equity
    wins = pnl[pnl > 0]
    losses = pnl[pnl <= 0]
    gross_loss = float(abs(losses.sum())) if len(losses) else 0.0
    reasons: dict[str, int] = {}
    for trade in trades:
        reasons[trade.exit_reason or "unknown"] = reasons.get(trade.exit_reason or "unknown", 0) + 1
    max_losses = np.array([t.entry_debit * 100.0 for t in trades], dtype=float)
    return {
        "n_trades": len(trades),
        "win_rate_pct": float(len(wins) / len(trades) * 100.0),
        "total_pnl_per_contract": float(pnl.sum()),
        "avg_pnl_per_contract": float(pnl.mean()),
        "profit_factor": float(wins.sum() / gross_loss) if gross_loss > 0 else float("inf"),
        "max_dd_per_contract": float(dd.max()) if len(dd) else 0.0,
        "avg_days_held": float(
            np.mean([(t.exit_date - t.entry_date).days for t in trades if t.exit_date is not None])
        ),
        "exit_reasons": reasons,
        "avg_max_loss_usd": float(max_losses.mean()),
        "p95_max_loss_usd": float(np.percentile(max_losses, 95)),
        "worst_max_loss_usd": float(max_losses.max()),
        "structure": "butterfly_spread",
    }


def run_butterfly_backtest(
    symbol: str,
    *,
    period: str = "2y",
    use_cache: bool = True,
    config: Optional[dict[str, Any]] = None,
    sleeve_usd: float = 3000.0,
    open_risk_budget_usd: float = 750.0,
    df: Optional[pd.DataFrame] = None,
    min_bars: int = 15,
) -> ButterflySimResult:
    """Run one-position-at-a-time long-call-butterfly research simulation."""
    cfg = dict(config or {})
    sym = symbol.upper()
    if df is None:
        try:
            from data import build

            df = build(sym, period=period, use_cache=use_cache)
        except Exception as exc:  # noqa: BLE001
            return ButterflySimResult(sym, False, True, f"build failed: {exc}", period, config=cfg)
    if df is None or len(df) < min_bars:
        return ButterflySimResult(sym, False, True, "insufficient history", period, config=cfg)

    trades: list[ButterflyTrade] = []
    open_trade: Optional[ButterflyTrade] = None
    r = _num(cfg, "risk_free_rate", 0.04)
    slip = max(_num(cfg, "slippage_pct", 0.0), 0.0)
    half_spread = max(_num(cfg, "half_spread_per_leg", 0.0), 0.0)
    for index_value, row in df.iterrows():
        today = pd.Timestamp(index_value)
        spot = float(row["close"])
        sigma = float(row["iv_proxy"])
        if not np.isfinite(sigma) or sigma <= 0:
            continue
        if open_trade is not None:
            credit = open_trade.mark_credit(
                spot,
                sigma,
                today,
                r=r,
                slippage_pct=slip,
                half_spread_per_leg=half_spread,
            )
            pnl = credit - open_trade.entry_debit
            days = (open_trade.expiration - today).days
            reason = None
            if pnl >= _num(cfg, "profit_target", 0.40) * open_trade.entry_debit:
                reason = "profit_target"
            elif pnl <= -_num(cfg, "defined_loss_exit_frac", 0.70) * open_trade.entry_debit:
                reason = "defined_loss"
            elif days <= int(round(_num(cfg, "dte_stop", 3))):
                reason = "dte_stop"
            if reason is not None:
                open_trade.exit_date = today
                open_trade.exit_credit = credit
                open_trade.exit_reason = reason
                open_trade.closed = True
                trades.append(open_trade)
                open_trade = None
        if open_trade is None and (not trades or trades[-1].exit_date != today):
            open_trade = pick_butterfly_entry(row, spot, today, cfg)

    if open_trade is not None:
        today = pd.Timestamp(df.index[-1])
        row = df.iloc[-1]
        credit = open_trade.mark_credit(
            float(row["close"]),
            max(float(row["iv_proxy"]), 1e-6),
            today,
            r=r,
            slippage_pct=slip,
            half_spread_per_leg=half_spread,
        )
        open_trade.exit_date = today
        open_trade.exit_credit = credit
        open_trade.exit_reason = "end_of_data"
        open_trade.closed = True
        trades.append(open_trade)

    metrics = _metrics(trades)
    representative_loss = (
        float(np.percentile([t.entry_debit * 100.0 for t in trades], 95))
        if trades
        else _num(cfg, "max_loss_budget_usd", 300.0)
    )
    capital = capital_fit_pcs(
        max_loss_usd=representative_loss,
        sleeve_usd=sleeve_usd,
        open_risk_budget_usd=open_risk_budget_usd,
        max_loss_budget_usd=_num(cfg, "max_loss_budget_usd", 300.0),
        structure="butterfly_spread",
    )
    capital["note"] = (
        "defined_debit_risk=max_entry_debit_usd; paper BS same-expiry symmetric call butterfly; "
        "pin/assignment and observed option surfaces not modeled"
    )
    return ButterflySimResult(sym, True, False, "ok", period, len(trades), metrics, trades, capital, cfg)

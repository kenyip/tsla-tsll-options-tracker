"""Paper-only Black-Scholes daily-bar simulator for 1x2 put ratio backspreads."""

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
class PutRatioBackspreadTrade:
    entry_date: pd.Timestamp
    expiration: pd.Timestamp
    long_strike: float
    short_strike: float
    entry_debit: float
    max_loss_per_share: float
    dte_at_entry: int
    iv_at_entry: float
    regime_at_entry: str
    closed: bool = False
    exit_date: Optional[pd.Timestamp] = None
    exit_value: Optional[float] = None
    exit_reason: Optional[str] = None

    def mark_value(
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
            long_put = max(self.long_strike - spot, 0.0)
            short_put = max(self.short_strike - spot, 0.0)
        else:
            t = days / 365.0
            long_put = pricing.price(spot, self.long_strike, t, sigma, "put", r=r)
            short_put = pricing.price(spot, self.short_strike, t, sigma, "put", r=r)
        slip = max(float(slippage_pct), 0.0)
        half_spread = max(float(half_spread_per_leg), 0.0)
        long_sale = max(long_put * (1.0 - slip) - half_spread, 0.0)
        short_buyback = short_put * (1.0 + slip) + half_spread
        return float(2.0 * long_sale - short_buyback)


@dataclass
class PutRatioBackspreadSimResult:
    symbol: str
    ok: bool
    skipped: bool = False
    reason: str = ""
    period: str = ""
    n_trades: int = 0
    metrics: dict[str, Any] = field(default_factory=dict)
    trades: list[PutRatioBackspreadTrade] = field(default_factory=list)
    capital: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["trades"] = [
            {
                "entry": str(t.entry_date.date()),
                "exit": str(t.exit_date.date()) if t.exit_date is not None else None,
                "long_strike": t.long_strike,
                "short_strike": t.short_strike,
                "dte": t.dte_at_entry,
                "entry_debit": round(t.entry_debit, 4),
                "max_loss_usd": round(t.max_loss_per_share * 100.0, 2),
                "exit_value": None if t.exit_value is None else round(t.exit_value, 4),
                "pnl_share": None if t.exit_value is None else round(t.exit_value - t.entry_debit, 4),
                "reason": t.exit_reason,
            }
            for t in self.trades
        ]
        return data


def pick_put_ratio_backspread_entry(
    row: pd.Series, spot: float, today: pd.Timestamp, cfg: dict[str, Any]
) -> Optional[PutRatioBackspreadTrade]:
    sigma = float(row.get("iv_proxy") or 0.0)
    if not np.isfinite(sigma) or sigma <= 0:
        return None
    if float(row.get("iv_rank") or 0.0) < _num(cfg, "iv_rank_min", 0.0):
        return None
    if str(row.get("regime") or "").lower() in {"bull", "bullish", "huge_up", "normal_up"}:
        return None

    dte = max(int(round(_num(cfg, "long_dte", 21))), 3)
    short_delta = min(max(_num(cfg, "short_target_delta", 0.30), 0.10), 0.45)
    width = max(_num(cfg, "spread_width", 2.0), 0.5)
    r = _num(cfg, "risk_free_rate", 0.04)
    try:
        short_exact = pricing.strike_from_delta(spot, dte / 365.0, sigma, short_delta, "put", r=r)
    except ValueError:
        return None
    increment = strike_increment_for(spot)
    short_strike = pricing.round_strike(short_exact, increment)
    width_steps = max(int(round(width / increment)), 1)
    actual_width = width_steps * increment
    long_strike = short_strike - actual_width
    if long_strike <= 0:
        return None

    t = dte / 365.0
    slip = max(_num(cfg, "slippage_pct", 0.0), 0.0)
    half_spread = max(_num(cfg, "half_spread_per_leg", 0.0), 0.0)
    long_buy = pricing.price(spot, long_strike, t, sigma, "put", r=r) * (1.0 + slip) + half_spread
    short_sale = max(
        pricing.price(spot, short_strike, t, sigma, "put", r=r) * (1.0 - slip) - half_spread,
        0.0,
    )
    entry_debit = float(2.0 * long_buy - short_sale)
    max_loss = float(actual_width + entry_debit)
    if max_loss <= 0.01 or max_loss * 100.0 > _num(cfg, "max_loss_budget_usd", 300.0):
        return None
    return PutRatioBackspreadTrade(
        entry_date=today,
        expiration=pd.Timestamp(today + pd.Timedelta(days=dte)),
        long_strike=float(long_strike),
        short_strike=float(short_strike),
        entry_debit=entry_debit,
        max_loss_per_share=max_loss,
        dte_at_entry=dte,
        iv_at_entry=sigma,
        regime_at_entry=str(row.get("regime") or ""),
    )


def _metrics(trades: list[PutRatioBackspreadTrade]) -> dict[str, Any]:
    if not trades:
        return {"n_trades": 0, "structure": "put_ratio_backspread"}
    pnl = np.array([((t.exit_value or 0.0) - t.entry_debit) * 100.0 for t in trades], dtype=float)
    equity = np.cumsum(pnl)
    dd = np.maximum.accumulate(equity) - equity
    wins = pnl[pnl > 0]
    losses = pnl[pnl <= 0]
    gross_loss = float(abs(losses.sum())) if len(losses) else 0.0
    reasons: dict[str, int] = {}
    for trade in trades:
        reasons[trade.exit_reason or "unknown"] = reasons.get(trade.exit_reason or "unknown", 0) + 1
    max_losses = np.array([t.max_loss_per_share * 100.0 for t in trades], dtype=float)
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
        "structure": "put_ratio_backspread",
    }


def run_put_ratio_backspread_backtest(
    symbol: str,
    *,
    period: str = "2y",
    use_cache: bool = True,
    config: Optional[dict[str, Any]] = None,
    sleeve_usd: float = 3000.0,
    open_risk_budget_usd: float = 750.0,
    df: Optional[pd.DataFrame] = None,
    min_bars: int = 15,
) -> PutRatioBackspreadSimResult:
    """Run one-position-at-a-time 1x2 put ratio backspread research simulation."""
    cfg = dict(config or {})
    sym = symbol.upper()
    if df is None:
        try:
            from data import build

            df = build(sym, period=period, use_cache=use_cache)
        except Exception as exc:  # noqa: BLE001
            return PutRatioBackspreadSimResult(sym, False, True, f"build failed: {exc}", period, config=cfg)
    if df is None or len(df) < min_bars:
        return PutRatioBackspreadSimResult(sym, False, True, "insufficient history", period, config=cfg)

    trades: list[PutRatioBackspreadTrade] = []
    open_trade: Optional[PutRatioBackspreadTrade] = None
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
            value = open_trade.mark_value(
                spot,
                sigma,
                today,
                r=r,
                slippage_pct=slip,
                half_spread_per_leg=half_spread,
            )
            pnl = value - open_trade.entry_debit
            days = (open_trade.expiration - today).days
            reason = None
            if pnl >= _num(cfg, "profit_target", 0.50) * open_trade.max_loss_per_share:
                reason = "profit_target"
            elif pnl <= -_num(cfg, "defined_loss_exit_frac", 0.70) * open_trade.max_loss_per_share:
                reason = "defined_loss"
            elif days <= int(round(_num(cfg, "dte_stop", 3))):
                reason = "dte_stop"
            if reason is not None:
                open_trade.exit_date = today
                open_trade.exit_value = value
                open_trade.exit_reason = reason
                open_trade.closed = True
                trades.append(open_trade)
                open_trade = None
        if open_trade is None and (not trades or trades[-1].exit_date != today):
            open_trade = pick_put_ratio_backspread_entry(row, spot, today, cfg)

    if open_trade is not None:
        today = pd.Timestamp(df.index[-1])
        row = df.iloc[-1]
        value = open_trade.mark_value(
            float(row["close"]),
            max(float(row["iv_proxy"]), 1e-6),
            today,
            r=r,
            slippage_pct=slip,
            half_spread_per_leg=half_spread,
        )
        open_trade.exit_date = today
        open_trade.exit_value = value
        open_trade.exit_reason = "end_of_data"
        open_trade.closed = True
        trades.append(open_trade)

    metrics = _metrics(trades)
    representative_loss = (
        float(np.percentile([t.max_loss_per_share * 100.0 for t in trades], 95))
        if trades
        else _num(cfg, "max_loss_budget_usd", 300.0)
    )
    capital = capital_fit_pcs(
        max_loss_usd=representative_loss,
        sleeve_usd=sleeve_usd,
        open_risk_budget_usd=open_risk_budget_usd,
        max_loss_budget_usd=_num(cfg, "max_loss_budget_usd", 300.0),
        structure="put_ratio_backspread",
    )
    capital["note"] = (
        "defined_valley_risk=(short_strike-long_strike+entry_debit)*100; sell one higher-strike "
        "put and buy two lower-strike puts; paper BS proxy without observed surfaces or assignment"
    )
    return PutRatioBackspreadSimResult(sym, True, False, "ok", period, len(trades), metrics, trades, capital, cfg)

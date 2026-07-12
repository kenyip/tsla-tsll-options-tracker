"""Paper-only Black-Scholes daily-bar simulator for credit iron butterflies."""

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
class IronButterflyTrade:
    entry_date: pd.Timestamp
    expiration: pd.Timestamp
    lower_strike: float
    middle_strike: float
    upper_strike: float
    entry_credit: float
    max_loss_per_share: float
    dte_at_entry: int
    iv_at_entry: float
    regime_at_entry: str
    structure: str = "iron_butterfly"
    closed: bool = False
    exit_date: Optional[pd.Timestamp] = None
    exit_debit: Optional[float] = None
    exit_reason: Optional[str] = None

    def mark_debit(
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
            long_put = max(self.lower_strike - spot, 0.0)
            short_put = max(self.middle_strike - spot, 0.0)
            short_call = max(spot - self.middle_strike, 0.0)
            long_call = max(spot - self.upper_strike, 0.0)
        else:
            t = days / 365.0
            long_put = pricing.price(spot, self.lower_strike, t, sigma, "put", r=r)
            short_put = pricing.price(spot, self.middle_strike, t, sigma, "put", r=r)
            short_call = pricing.price(spot, self.middle_strike, t, sigma, "call", r=r)
            long_call = pricing.price(spot, self.upper_strike, t, sigma, "call", r=r)
        slip = max(float(slippage_pct), 0.0)
        half_spread = max(float(half_spread_per_leg), 0.0)
        short_buyback = (short_put + short_call) * (1.0 + slip) + 2.0 * half_spread
        long_sale = max(long_put * (1.0 - slip) - half_spread, 0.0) + max(
            long_call * (1.0 - slip) - half_spread, 0.0
        )
        return max(float(short_buyback - long_sale), 0.0)


@dataclass
class IronButterflySimResult:
    symbol: str
    ok: bool
    skipped: bool = False
    reason: str = ""
    period: str = ""
    n_trades: int = 0
    metrics: dict[str, Any] = field(default_factory=dict)
    trades: list[IronButterflyTrade] = field(default_factory=list)
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
                "credit": round(t.entry_credit, 4),
                "max_loss_usd": round(t.max_loss_per_share * 100.0, 2),
                "exit_debit": None if t.exit_debit is None else round(t.exit_debit, 4),
                "pnl_share": None if t.exit_debit is None else round(t.entry_credit - t.exit_debit, 4),
                "reason": t.exit_reason,
            }
            for t in self.trades
        ]
        return data


def pick_iron_butterfly_entry(
    row: pd.Series, spot: float, today: pd.Timestamp, cfg: dict[str, Any]
) -> Optional[IronButterflyTrade]:
    sigma = float(row.get("iv_proxy") or 0.0)
    if not np.isfinite(sigma) or sigma <= 0:
        return None
    if float(row.get("iv_rank") or 0.0) < _num(cfg, "iv_rank_min", 20.0):
        return None
    structure = str(cfg.get("structure") or "iron_butterfly")
    regime = str(row.get("regime") or "").lower()
    if structure == "broken_wing_iron_butterfly":
        if regime == "bear":
            return None
    elif regime != "neutral":
        return None

    dte = max(int(round(_num(cfg, "long_dte", 21))), 3)
    width = max(_num(cfg, "spread_width", 2.0), 0.5)
    lower_width = (
        max(_num(cfg, "far_wing_width", width), width)
        if structure == "broken_wing_iron_butterfly"
        else width
    )
    upper_width = width
    r = _num(cfg, "risk_free_rate", 0.04)
    increment = strike_increment_for(spot)
    middle = pricing.round_strike(spot, increment)
    upper_steps = max(int(round(upper_width / increment)), 1)
    lower_steps = max(int(round(lower_width / increment)), 1)
    if structure == "broken_wing_iron_butterfly":
        lower_steps = max(lower_steps, upper_steps + 1)
    actual_lower_width = lower_steps * increment
    actual_upper_width = upper_steps * increment
    widest_width = max(actual_lower_width, actual_upper_width)
    lower = middle - actual_lower_width
    upper = middle + actual_upper_width
    if lower <= 0:
        return None

    t = dte / 365.0
    slip = max(_num(cfg, "slippage_pct", 0.0), 0.0)
    half_spread = max(_num(cfg, "half_spread_per_leg", 0.0), 0.0)
    long_put = pricing.price(spot, lower, t, sigma, "put", r=r) * (1.0 + slip) + half_spread
    short_put = max(
        pricing.price(spot, middle, t, sigma, "put", r=r) * (1.0 - slip) - half_spread,
        0.0,
    )
    short_call = max(
        pricing.price(spot, middle, t, sigma, "call", r=r) * (1.0 - slip) - half_spread,
        0.0,
    )
    long_call = pricing.price(spot, upper, t, sigma, "call", r=r) * (1.0 + slip) + half_spread
    credit = float(short_put + short_call - long_put - long_call)
    if credit <= 0.01 or credit >= widest_width:
        return None
    if credit / widest_width < _num(cfg, "min_credit_pct", 0.25):
        return None
    max_loss = widest_width - credit
    if max_loss * 100.0 > _num(cfg, "max_loss_budget_usd", 300.0):
        return None
    return IronButterflyTrade(
        entry_date=today,
        expiration=pd.Timestamp(today + pd.Timedelta(days=dte)),
        lower_strike=float(lower),
        middle_strike=float(middle),
        upper_strike=float(upper),
        entry_credit=credit,
        max_loss_per_share=float(max_loss),
        dte_at_entry=dte,
        iv_at_entry=sigma,
        regime_at_entry=str(row.get("regime") or ""),
        structure=structure,
    )


def _metrics(trades: list[IronButterflyTrade], structure: str) -> dict[str, Any]:
    if not trades:
        return {"n_trades": 0, "structure": structure}
    pnl = np.array([(t.entry_credit - (t.exit_debit or 0.0)) * 100.0 for t in trades], dtype=float)
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
        "structure": structure,
    }


def run_iron_butterfly_backtest(
    symbol: str,
    *,
    period: str = "2y",
    use_cache: bool = True,
    config: Optional[dict[str, Any]] = None,
    sleeve_usd: float = 3000.0,
    open_risk_budget_usd: float = 750.0,
    df: Optional[pd.DataFrame] = None,
    min_bars: int = 15,
) -> IronButterflySimResult:
    """Run one-position-at-a-time credit iron-butterfly research simulation."""
    cfg = dict(config or {})
    sym = symbol.upper()
    structure = str(cfg.get("structure") or "iron_butterfly")
    if df is None:
        try:
            from data import build

            df = build(sym, period=period, use_cache=use_cache)
        except Exception as exc:  # noqa: BLE001
            return IronButterflySimResult(sym, False, True, f"build failed: {exc}", period, config=cfg)
    if df is None or len(df) < min_bars:
        return IronButterflySimResult(sym, False, True, "insufficient history", period, config=cfg)

    trades: list[IronButterflyTrade] = []
    open_trade: Optional[IronButterflyTrade] = None
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
            debit = open_trade.mark_debit(
                spot,
                sigma,
                today,
                r=r,
                slippage_pct=slip,
                half_spread_per_leg=half_spread,
            )
            pnl = open_trade.entry_credit - debit
            days = (open_trade.expiration - today).days
            reason = None
            if pnl >= _num(cfg, "profit_target", 0.40) * open_trade.entry_credit:
                reason = "profit_target"
            elif pnl <= -_num(cfg, "defined_loss_exit_frac", 0.70) * open_trade.max_loss_per_share:
                reason = "defined_loss"
            elif days <= int(round(_num(cfg, "dte_stop", 3))):
                reason = "dte_stop"
            if reason is not None:
                open_trade.exit_date = today
                open_trade.exit_debit = debit
                open_trade.exit_reason = reason
                open_trade.closed = True
                trades.append(open_trade)
                open_trade = None
        if open_trade is None and (not trades or trades[-1].exit_date != today):
            open_trade = pick_iron_butterfly_entry(row, spot, today, cfg)

    if open_trade is not None:
        today = pd.Timestamp(df.index[-1])
        row = df.iloc[-1]
        debit = open_trade.mark_debit(
            float(row["close"]),
            max(float(row["iv_proxy"]), 1e-6),
            today,
            r=r,
            slippage_pct=slip,
            half_spread_per_leg=half_spread,
        )
        open_trade.exit_date = today
        open_trade.exit_debit = debit
        open_trade.exit_reason = "end_of_data"
        open_trade.closed = True
        trades.append(open_trade)

    metrics = _metrics(trades, structure)
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
        structure=structure,
    )
    capital["note"] = (
        "defined_credit_risk=(widest_wing_width-entry_credit)*100; paper BS same-expiry "
        "iron butterfly; pin/assignment and observed option surfaces not modeled"
    )
    return IronButterflySimResult(sym, True, False, "ok", period, len(trades), metrics, trades, capital, cfg)

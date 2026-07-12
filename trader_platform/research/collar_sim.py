"""Paper-only collared covered-call simulator (100 sh + long put + short call).

Capital honesty for the $3k sleeve:
  capital_fit_usd = 100 * entry_spot + max(0, net_option_debit) * 100
  max_loss_usd    = (entry_spot - put_strike + net_option_debit) * 100

Eligibility: non-levered names with spot*100 <= sleeve (default 3000).
TSLL / other levered ETFs are hard-rejected — do not default to share-hold on them.

Limitations (labeled): dividends, early assignment, and hard-to-borrow not modeled.
Research BS daily-bar marks only — not observed option surfaces.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional, Sequence

import numpy as np
import pandas as pd

import pricing
from trader_platform.research.pcs_sim import strike_increment_for

# Explicit levered / exotic denylist — never default collar share-hold here.
LEVERED_OR_EXOTIC: frozenset[str] = frozenset(
    {
        "TSLL",
        "TSLQ",
        "TSLT",
        "TQQQ",
        "SQQQ",
        "SOXL",
        "SOXS",
        "UPRO",
        "SPXU",
        "TNA",
        "TZA",
        "UVXY",
        "VIXY",
        "SVXY",
        "LABU",
        "LABD",
        "FAS",
        "FAZ",
        "NUGT",
        "DUST",
        "BOIL",
        "KOLD",
    }
)

# Absolute reject gates (merged NEXT 2026-07-12) — reject-unless; no proxy SHIP first.
GATE_MAX_LOSS_USD = 300.0
GATE_WINDOW_MAX_DD_USD = 75.0
GATE_DENSE_NEG_MAX = 5
GATE_SLIP_PCT = 0.05
GATE_HALF_SPREAD_PER_LEG = 0.01
GATE_MIN_TRADES = 8  # vacuous n=1 must not clear reject-unless


def _num(cfg: dict[str, Any], key: str, default: float) -> float:
    try:
        return float(cfg.get(key, default))
    except (TypeError, ValueError):
        return float(default)


def is_levered_symbol(symbol: str) -> bool:
    return str(symbol or "").upper() in LEVERED_OR_EXOTIC


def collar_symbol_eligible(
    symbol: str,
    spot: float,
    *,
    sleeve_usd: float = 3000.0,
) -> tuple[bool, str]:
    """Non-levered + full 100-share notional fits sleeve."""
    sym = str(symbol or "").upper()
    if not sym:
        return False, "missing_symbol"
    if is_levered_symbol(sym):
        return False, "levered_or_exotic_rejected"
    s = float(spot or 0.0)
    if s <= 0:
        return False, "no_spot"
    lot = s * 100.0
    if lot > float(sleeve_usd):
        return False, f"share_lot_usd={lot:.2f}>sleeve={sleeve_usd:.0f}"
    return True, "ok"


def capital_fit_collar(
    *,
    entry_spot: float,
    net_option_debit_per_share: float,
    max_loss_usd: float,
    sleeve_usd: float = 3000.0,
    open_risk_budget_usd: float = 750.0,
    max_loss_budget_usd: float = 300.0,
    structure: str = "collared_covered_call",
) -> dict[str, Any]:
    """Stock-notional capital envelope (not defined-risk vertical BP)."""
    spot = float(entry_spot)
    lot = max(spot, 0.0) * 100.0
    opt = max(float(net_option_debit_per_share), 0.0) * 100.0
    capital_fit_usd = lot + opt
    ml = float(max_loss_usd)
    fits_sleeve = capital_fit_usd > 0 and capital_fit_usd <= sleeve_usd
    fits_open_risk = ml > 0 and ml <= open_risk_budget_usd
    fits_budget = ml > 0 and ml <= max_loss_budget_usd
    max_lots = 1 if fits_sleeve else 0
    if fits_sleeve and fits_budget and fits_open_risk:
        fit = "fit_3k" if sleeve_usd <= 3000 else "fit_sleeve"
    elif fits_sleeve:
        fit = "fit_sleeve_soft"  # funds stock but soft on ml/open-risk
    elif capital_fit_usd <= 5000:
        fit = "fit_5k"
    elif capital_fit_usd <= 15000:
        fit = "fit_15k"
    else:
        fit = "oversized" if capital_fit_usd > 0 else "unknown"
    return {
        "structure": structure,
        "capital_fit_usd": round(capital_fit_usd, 2),
        "share_lot_usd": round(lot, 2),
        "net_option_debit_usd": round(float(net_option_debit_per_share) * 100.0, 2),
        "max_loss_usd": round(ml, 2),
        "max_lots": int(max_lots),
        "capital_fit": fit,
        "fits_open_risk_budget": fits_open_risk,
        "fits_max_loss_budget": fits_budget,
        "fits_stock_notional_sleeve": fits_sleeve,
        "open_risk_budget_usd": open_risk_budget_usd,
        "max_loss_budget_usd": max_loss_budget_usd,
        "sleeve_usd": sleeve_usd,
        "note": (
            "capital_fit_usd=100*spot+max(0,net_option_debit)*100; "
            "max_loss_usd=(spot-put_strike+net_option_debit)*100 downside floor"
        ),
    }


def defined_collar_max_loss_per_share(
    entry_spot: float,
    put_strike: float,
    net_option_debit: float,
) -> float:
    """Worst-case 1-lot downside to put protection (per share)."""
    return max(float(entry_spot) - float(put_strike), 0.0) + float(net_option_debit)


@dataclass
class CollarTrade:
    entry_date: pd.Timestamp
    expiration: pd.Timestamp
    entry_spot: float
    put_strike: float
    call_strike: float
    put_debit: float
    call_credit: float
    net_option_debit: float
    max_loss_per_share: float
    dte_at_entry: int
    iv_at_entry: float
    regime_at_entry: str
    closed: bool = False
    exit_date: Optional[pd.Timestamp] = None
    exit_value: Optional[float] = None  # mark of stock+put-call package (per share)
    exit_reason: Optional[str] = None

    @property
    def entry_package(self) -> float:
        """Per-share entry cost of stock + net options."""
        return float(self.entry_spot + self.net_option_debit)

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
        """Mark full package (stock + long put − short call) per share, exit-side costs."""
        days = max((self.expiration - today).days, 0)
        slip = max(float(slippage_pct), 0.0)
        half = max(float(half_spread_per_leg), 0.0)
        if days == 0:
            put_m = max(self.put_strike - spot, 0.0)
            call_m = max(spot - self.call_strike, 0.0)
        else:
            t = days / 365.0
            put_m = pricing.price(spot, self.put_strike, t, sigma, "put", r=r)
            call_m = pricing.price(spot, self.call_strike, t, sigma, "call", r=r)
        # Exit: sell stock, sell put, buy back call — adverse slip/spread on option legs.
        stock_exit = float(spot)  # mid; stock spread not modeled
        put_sale = max(put_m * (1.0 - slip) - half, 0.0)
        call_buyback = call_m * (1.0 + slip) + half
        return float(stock_exit + put_sale - call_buyback)


@dataclass
class CollarSimResult:
    symbol: str
    ok: bool
    skipped: bool = False
    reason: str = ""
    period: str = ""
    n_trades: int = 0
    metrics: dict[str, Any] = field(default_factory=dict)
    trades: list[CollarTrade] = field(default_factory=list)
    capital: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    eligibility: dict[str, Any] = field(default_factory=dict)
    gate: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["trades"] = [
            {
                "entry": str(t.entry_date.date()),
                "exit": str(t.exit_date.date()) if t.exit_date is not None else None,
                "entry_spot": round(t.entry_spot, 4),
                "put_strike": t.put_strike,
                "call_strike": t.call_strike,
                "dte": t.dte_at_entry,
                "put_debit": round(t.put_debit, 4),
                "call_credit": round(t.call_credit, 4),
                "net_option_debit": round(t.net_option_debit, 4),
                "max_loss_usd": round(t.max_loss_per_share * 100.0, 2),
                "capital_fit_usd": round(
                    t.entry_spot * 100.0 + max(t.net_option_debit, 0.0) * 100.0, 2
                ),
                "exit_value": None if t.exit_value is None else round(t.exit_value, 4),
                "pnl_share": None
                if t.exit_value is None
                else round(t.exit_value - t.entry_package, 4),
                "reason": t.exit_reason,
            }
            for t in self.trades
        ]
        return data


def pick_collar_entry(
    row: pd.Series,
    spot: float,
    today: pd.Timestamp,
    cfg: dict[str, Any],
    *,
    symbol: str = "",
    sleeve_usd: float = 3000.0,
) -> Optional[CollarTrade]:
    sym = str(symbol or cfg.get("symbol") or "").upper()
    if sym:
        ok, _why = collar_symbol_eligible(sym, spot, sleeve_usd=sleeve_usd)
        if not ok:
            return None
    elif not bool(cfg.get("allow_unlabeled_symbol")):
        return None

    sigma = float(row.get("iv_proxy") or 0.0)
    if not np.isfinite(sigma) or sigma <= 0:
        return None
    if float(row.get("iv_rank") or 0.0) < _num(cfg, "iv_rank_min", 0.0):
        return None
    regime = str(row.get("regime") or "").lower()
    # Prefer non-bearish for covered-call collars (stand aside in hard bear).
    if regime in {"bear", "bearish", "huge_down", "normal_down"} and not bool(
        cfg.get("allow_bearish_entry")
    ):
        return None

    dte = max(int(round(_num(cfg, "long_dte", 21))), 3)
    put_delta = min(max(_num(cfg, "collar_put_delta", 0.25), 0.08), 0.45)
    call_delta = min(max(_num(cfg, "collar_call_delta", 0.25), 0.08), 0.45)
    r = _num(cfg, "risk_free_rate", 0.04)
    try:
        put_exact = pricing.strike_from_delta(spot, dte / 365.0, sigma, put_delta, "put", r=r)
        call_exact = pricing.strike_from_delta(spot, dte / 365.0, sigma, call_delta, "call", r=r)
    except ValueError:
        return None
    increment = strike_increment_for(spot)
    put_strike = pricing.round_strike(put_exact, increment)
    call_strike = pricing.round_strike(call_exact, increment)
    if put_strike <= 0 or call_strike <= put_strike:
        # Require call above put (collar width); widen call by one increment if needed.
        call_strike = max(call_strike, put_strike + increment)
    if call_strike <= put_strike:
        return None

    t = dte / 365.0
    slip = max(_num(cfg, "slippage_pct", 0.0), 0.0)
    half = max(_num(cfg, "half_spread_per_leg", 0.0), 0.0)
    # Entry: buy put (pay ask), sell call (receive bid); 2 option legs for half-spread.
    put_mid = pricing.price(spot, put_strike, t, sigma, "put", r=r)
    call_mid = pricing.price(spot, call_strike, t, sigma, "call", r=r)
    put_debit = put_mid * (1.0 + slip) + half
    call_credit = max(call_mid * (1.0 - slip) - half, 0.0)
    net_opt = float(put_debit - call_credit)
    max_loss_ps = defined_collar_max_loss_per_share(spot, put_strike, net_opt)
    if max_loss_ps * 100.0 > _num(cfg, "max_loss_budget_usd", 300.0):
        return None
    capital_need = spot * 100.0 + max(net_opt, 0.0) * 100.0
    if capital_need > sleeve_usd:
        return None

    return CollarTrade(
        entry_date=today,
        expiration=pd.Timestamp(today + pd.Timedelta(days=dte)),
        entry_spot=float(spot),
        put_strike=float(put_strike),
        call_strike=float(call_strike),
        put_debit=float(put_debit),
        call_credit=float(call_credit),
        net_option_debit=net_opt,
        max_loss_per_share=float(max_loss_ps),
        dte_at_entry=dte,
        iv_at_entry=sigma,
        regime_at_entry=str(row.get("regime") or ""),
    )


def _metrics(trades: list[CollarTrade]) -> dict[str, Any]:
    if not trades:
        return {"n_trades": 0, "structure": "collared_covered_call"}
    pnl = np.array(
        [((t.exit_value or 0.0) - t.entry_package) * 100.0 for t in trades], dtype=float
    )
    equity = np.cumsum(pnl)
    dd = np.maximum.accumulate(equity) - equity
    wins = pnl[pnl > 0]
    losses = pnl[pnl <= 0]
    gross_loss = float(abs(losses.sum())) if len(losses) else 0.0
    reasons: dict[str, int] = {}
    for trade in trades:
        reasons[trade.exit_reason or "unknown"] = reasons.get(trade.exit_reason or "unknown", 0) + 1
    max_losses = np.array([t.max_loss_per_share * 100.0 for t in trades], dtype=float)
    capital_fits = np.array(
        [t.entry_spot * 100.0 + max(t.net_option_debit, 0.0) * 100.0 for t in trades],
        dtype=float,
    )
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
        "avg_capital_fit_usd": float(capital_fits.mean()),
        "p95_capital_fit_usd": float(np.percentile(capital_fits, 95)),
        "structure": "collared_covered_call",
    }


def window_stress_metrics(trades: list[CollarTrade]) -> dict[str, Any]:
    """Yearly + trailing ~6m dense windows for absolute DD / dense-neg gates."""
    if not trades:
        return {
            "window_max_dd_usd": 0.0,
            "dense_neg_count": 0,
            "windows": [],
        }
    rows = []
    for t in trades:
        if t.exit_date is None or t.exit_value is None:
            continue
        rows.append(
            {
                "exit": pd.Timestamp(t.exit_date),
                "pnl": (t.exit_value - t.entry_package) * 100.0,
            }
        )
    if not rows:
        return {"window_max_dd_usd": 0.0, "dense_neg_count": 0, "windows": []}
    frame = pd.DataFrame(rows).sort_values("exit")
    windows: list[dict[str, Any]] = []
    # Calendar years present
    years = sorted({int(ts.year) for ts in frame["exit"]})
    for y in years:
        sub = frame[frame["exit"].dt.year == y]
        if len(sub) < 3:
            continue
        pnl = sub["pnl"].to_numpy(dtype=float)
        eq = np.cumsum(pnl)
        dd = float((np.maximum.accumulate(eq) - eq).max()) if len(eq) else 0.0
        windows.append(
            {
                "label": f"year_{y}",
                "n": int(len(sub)),
                "pnl": float(pnl.sum()),
                "max_dd": dd,
            }
        )
    # Trailing ~126 trading-day windows by exit date span
    if len(frame) >= 5:
        t0 = frame["exit"].min()
        t1 = frame["exit"].max()
        cursor = t0
        while cursor < t1:
            end = cursor + pd.Timedelta(days=183)
            sub = frame[(frame["exit"] >= cursor) & (frame["exit"] < end)]
            if len(sub) >= 3:
                pnl = sub["pnl"].to_numpy(dtype=float)
                eq = np.cumsum(pnl)
                dd = float((np.maximum.accumulate(eq) - eq).max()) if len(eq) else 0.0
                windows.append(
                    {
                        "label": f"6m_{cursor.date()}",
                        "n": int(len(sub)),
                        "pnl": float(pnl.sum()),
                        "max_dd": dd,
                    }
                )
            cursor = cursor + pd.Timedelta(days=90)

    dense = [w for w in windows if w["n"] >= 3]
    dense_neg = sum(1 for w in dense if w["pnl"] < 0)
    window_max_dd = max((w["max_dd"] for w in dense), default=0.0)
    return {
        "window_max_dd_usd": float(window_max_dd),
        "dense_neg_count": int(dense_neg),
        "n_dense_windows": len(dense),
        "windows": dense[:40],
    }


def evaluate_collar_absolute_gates(
    metrics: dict[str, Any],
    capital: dict[str, Any],
    window_meta: dict[str, Any],
    *,
    max_loss_cap: float = GATE_MAX_LOSS_USD,
    window_dd_cap: float = GATE_WINDOW_MAX_DD_USD,
    dense_neg_cap: int = GATE_DENSE_NEG_MAX,
    min_trades: int = GATE_MIN_TRADES,
) -> dict[str, Any]:
    """Reject-unless absolute gates — no proxy SHIP promotion path."""
    ml = float(
        capital.get("max_loss_usd")
        or metrics.get("worst_max_loss_usd")
        or metrics.get("p95_max_loss_usd")
        or 0.0
    )
    wdd = float(window_meta.get("window_max_dd_usd") or metrics.get("max_dd_per_contract") or 0.0)
    dneg = int(window_meta.get("dense_neg_count") or 0)
    n = int(metrics.get("n_trades") or 0)
    pnl = float(metrics.get("total_pnl_per_contract") or 0.0)
    n_dense = int(window_meta.get("n_dense_windows") or 0)
    reasons: list[str] = []
    if n < int(min_trades):
        reasons.append(f"vacuous_n{n}<{min_trades}")
    if n_dense <= 0 and n >= int(min_trades):
        # Need at least one dense window to trust window DD / dense-neg counts.
        reasons.append("no_dense_windows")
    if pnl <= 0:
        reasons.append(f"non_positive_after_cost_pnl_{pnl:.2f}")
    if ml > max_loss_cap:
        reasons.append(f"max_loss_{ml:.2f}>{max_loss_cap}")
    if wdd > window_dd_cap:
        reasons.append(f"window_dd_{wdd:.2f}>{window_dd_cap}")
    if dneg > dense_neg_cap:
        reasons.append(f"dense_neg_{dneg}>{dense_neg_cap}")
    passed = len(reasons) == 0
    return {
        "passed": passed,
        "decision": "PASS_GATES" if passed else "REJECT_COLLAR_ABSOLUTE_GATES",
        "max_loss_usd": round(ml, 2),
        "window_max_dd_usd": round(wdd, 2),
        "dense_neg_count": dneg,
        "total_pnl_per_contract": round(pnl, 2),
        "n_trades": n,
        "n_dense_windows": n_dense,
        "reasons": reasons,
        "register_proxy_ship": False,  # hard policy: never register proxy SHIP first
        "caps": {
            "max_loss_usd": max_loss_cap,
            "window_max_dd_usd": window_dd_cap,
            "dense_neg_max": dense_neg_cap,
            "min_trades": min_trades,
        },
    }


def run_collar_backtest(
    symbol: str,
    *,
    period: str = "2y",
    use_cache: bool = True,
    config: Optional[dict[str, Any]] = None,
    sleeve_usd: float = 3000.0,
    open_risk_budget_usd: float = 750.0,
    df: Optional[pd.DataFrame] = None,
    min_bars: int = 15,
    apply_absolute_gates: bool = True,
) -> CollarSimResult:
    """One-position-at-a-time collared covered-call research simulation."""
    cfg = dict(config or {})
    sym = symbol.upper()
    eligibility: dict[str, Any] = {"symbol": sym}

    if is_levered_symbol(sym):
        return CollarSimResult(
            sym,
            False,
            True,
            "levered_or_exotic_rejected",
            period,
            config=cfg,
            eligibility={"symbol": sym, "ok": False, "reason": "levered_or_exotic_rejected"},
            gate={"passed": False, "decision": "REJECT_LEVERED_SYMBOL", "register_proxy_ship": False},
        )

    if df is None:
        try:
            from data import build

            df = build(sym, period=period, use_cache=use_cache)
        except Exception as exc:  # noqa: BLE001
            return CollarSimResult(
                sym, False, True, f"build failed: {exc}", period, config=cfg, eligibility=eligibility
            )
    if df is None or len(df) < min_bars:
        return CollarSimResult(
            sym, False, True, "insufficient history", period, config=cfg, eligibility=eligibility
        )

    last_spot = float(df["close"].iloc[-1])
    ok_el, why_el = collar_symbol_eligible(sym, last_spot, sleeve_usd=sleeve_usd)
    eligibility = {
        "symbol": sym,
        "ok": ok_el,
        "reason": why_el,
        "last_spot": last_spot,
        "share_lot_usd": round(last_spot * 100.0, 2),
    }
    if not ok_el:
        return CollarSimResult(
            sym,
            False,
            True,
            why_el,
            period,
            config=cfg,
            eligibility=eligibility,
            gate={
                "passed": False,
                "decision": "REJECT_SYMBOL_ELIGIBILITY",
                "reason": why_el,
                "register_proxy_ship": False,
            },
        )

    trades: list[CollarTrade] = []
    open_trade: Optional[CollarTrade] = None
    r = _num(cfg, "risk_free_rate", 0.04)
    slip = max(_num(cfg, "slippage_pct", 0.0), 0.0)
    half = max(_num(cfg, "half_spread_per_leg", 0.0), 0.0)
    entry_cfg = {**cfg, "symbol": sym}

    for index_value, row in df.iterrows():
        today = pd.Timestamp(index_value)
        spot = float(row["close"])
        sigma = float(row["iv_proxy"])
        if not np.isfinite(sigma) or sigma <= 0:
            continue
        if open_trade is not None:
            value = open_trade.mark_value(
                spot, sigma, today, r=r, slippage_pct=slip, half_spread_per_leg=half
            )
            pnl = value - open_trade.entry_package
            days = (open_trade.expiration - today).days
            reason = None
            # Profit vs residual room to call cap is noisy; use fraction of max_loss budget.
            if pnl >= _num(cfg, "profit_target", 0.40) * max(open_trade.max_loss_per_share, 0.01):
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
        # No close-bar reentry (canonical one-position sequence).
        if open_trade is None and (not trades or trades[-1].exit_date != today):
            open_trade = pick_collar_entry(
                row, spot, today, entry_cfg, symbol=sym, sleeve_usd=sleeve_usd
            )

    if open_trade is not None:
        today = pd.Timestamp(df.index[-1])
        row = df.iloc[-1]
        value = open_trade.mark_value(
            float(row["close"]),
            max(float(row["iv_proxy"]), 1e-6),
            today,
            r=r,
            slippage_pct=slip,
            half_spread_per_leg=half,
        )
        open_trade.exit_date = today
        open_trade.exit_value = value
        open_trade.exit_reason = "end_of_data"
        open_trade.closed = True
        trades.append(open_trade)

    metrics = _metrics(trades)
    window_meta = window_stress_metrics(trades)
    metrics["window_max_dd_usd"] = window_meta["window_max_dd_usd"]
    metrics["dense_neg_count"] = window_meta["dense_neg_count"]

    if trades:
        rep_ml = float(np.percentile([t.max_loss_per_share * 100.0 for t in trades], 95))
        rep_spot = float(np.median([t.entry_spot for t in trades]))
        rep_net = float(np.median([t.net_option_debit for t in trades]))
    else:
        rep_ml = _num(cfg, "max_loss_budget_usd", 300.0)
        rep_spot = last_spot
        rep_net = 0.0
    capital = capital_fit_collar(
        entry_spot=rep_spot,
        net_option_debit_per_share=rep_net,
        max_loss_usd=rep_ml,
        sleeve_usd=sleeve_usd,
        open_risk_budget_usd=open_risk_budget_usd,
        max_loss_budget_usd=_num(cfg, "max_loss_budget_usd", 300.0),
        structure="collared_covered_call",
    )
    capital["limitations"] = [
        "dividends_not_modeled",
        "early_assignment_not_modeled",
        "paper_bs_proxy_not_observed_surface",
    ]

    gate: dict[str, Any] = {}
    if apply_absolute_gates:
        gate = evaluate_collar_absolute_gates(metrics, capital, window_meta)
    else:
        gate = {"passed": None, "decision": "GATES_SKIPPED", "register_proxy_ship": False}

    return CollarSimResult(
        sym,
        True,
        False,
        "ok",
        period,
        len(trades),
        metrics,
        trades,
        capital,
        cfg,
        eligibility,
        gate,
    )


def run_collar_cost_axes(
    symbol: str,
    *,
    df: pd.DataFrame,
    config: Optional[dict[str, Any]] = None,
    sleeve_usd: float = 3000.0,
) -> dict[str, Any]:
    """Immediate mid / 5% slip / $0.01-per-leg axes + absolute reject-unless."""
    base = dict(config or {})
    axes: dict[str, Any] = {}
    for label, overrides in (
        ("mid", {}),
        ("slip_5pct", {"slippage_pct": GATE_SLIP_PCT}),
        ("half_spread_0p01", {"half_spread_per_leg": GATE_HALF_SPREAD_PER_LEG}),
    ):
        res = run_collar_backtest(
            symbol,
            period="lab",
            df=df,
            config={**base, **overrides},
            sleeve_usd=sleeve_usd,
            apply_absolute_gates=True,
        )
        axes[label] = {
            "ok": res.ok,
            "skipped": res.skipped,
            "reason": res.reason,
            "n_trades": res.n_trades,
            "metrics": res.metrics,
            "capital": res.capital,
            "gate": res.gate,
            "eligibility": res.eligibility,
        }
    # Class decision: reject unless ANY cost axis clears absolute gates with non-vacuous n.
    any_pass = any(
        bool((axes[k].get("gate") or {}).get("passed")) for k in ("slip_5pct", "half_spread_0p01", "mid")
    )
    # Stricter NEXT: require cost axes (5% and $0.01) specifically — mid alone is not enough.
    cost_pass = all(
        bool((axes[k].get("gate") or {}).get("passed")) for k in ("slip_5pct", "half_spread_0p01")
    )
    decision = "PASS_COLLAR_COST_GATES" if cost_pass else "REJECT_COLLAR_CLASS_THIS_CYCLE"
    return {
        "symbol": symbol.upper(),
        "decision": decision,
        "any_axis_pass": any_pass,
        "cost_axes_pass": cost_pass,
        "register_proxy_ship": False,
        "axes": axes,
    }


def list_collar_candidates(
    symbols: Sequence[str],
    spots: dict[str, float],
    *,
    sleeve_usd: float = 3000.0,
) -> dict[str, Any]:
    """Filter symbols for collar capital honesty; fail closed if none qualify."""
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for raw in symbols:
        sym = str(raw).upper()
        spot = float(spots.get(sym) or spots.get(raw) or 0.0)
        ok, why = collar_symbol_eligible(sym, spot, sleeve_usd=sleeve_usd)
        row = {"symbol": sym, "spot": spot, "share_lot_usd": round(spot * 100.0, 2), "reason": why}
        if ok:
            accepted.append(row)
        else:
            rejected.append(row)
    return {
        "accepted": accepted,
        "rejected": rejected,
        "n_accepted": len(accepted),
        "fail_closed": len(accepted) == 0,
        "note": "do_not_default_to_TSLL_share_hold",
    }

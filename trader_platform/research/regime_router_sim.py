"""No-lookahead shared-position router for defined-risk credit structures."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, cast

import numpy as np
import pandas as pd

from trader_platform.research.pcs_sim import (
    PcsTrade,
    capital_fit_pcs,
    check_pcs_exit,
    compute_pcs_metrics,
    pick_structure_entry,
)
from trader_platform.strategy_dna import STRUCTURE_CATALOG


STRUCTURES = ("put_credit_spread", "call_credit_spread", "iron_condor")


@dataclass
class RegimeRouterResult:
    symbol: str
    policy: str
    ok: bool
    reason: str = ""
    period: str = ""
    n_trades: int = 0
    metrics: dict[str, Any] = field(default_factory=dict)
    trades: list[PcsTrade] = field(default_factory=list)
    capital: dict[str, Any] = field(default_factory=dict)
    route_counts: dict[str, int] = field(default_factory=dict)
    entry_funnel: dict[str, Any] = field(default_factory=dict)


def default_structure_configs() -> dict[str, dict[str, Any]]:
    return {
        structure: {
            **dict(STRUCTURE_CATALOG[structure]["config_seed"]),
            "structure": structure,
        }
        for structure in STRUCTURES
    }


def select_structure(row: pd.Series, configs: dict[str, dict[str, Any]]) -> str | None:
    """Select from the current row only; neutral low-IV bars stand aside."""
    regime = str(row.get("regime") or "").lower()
    if regime == "bullish":
        return "put_credit_spread"
    if regime == "bearish":
        return "call_credit_spread"
    if regime == "neutral":
        threshold = float(configs["iron_condor"].get("iv_rank_min", 15.0))
        if float(row.get("iv_rank") or 0.0) >= threshold:
            return "iron_condor"
    return None


def _policy_structure(
    row: pd.Series,
    policy: str,
    configs: dict[str, dict[str, Any]],
) -> str | None:
    if policy == "router":
        return select_structure(row, configs)
    if policy in STRUCTURES:
        return policy
    raise ValueError(f"unknown policy {policy!r}")


def diagnose_entry_rejection(
    row: pd.Series,
    spot: float,
    today: pd.Timestamp,
    cfg: dict[str, Any],
    *,
    structure: str,
) -> str:
    """Classify a rejected synthetic entry through implementation-level counterfactuals."""
    iv = float(row.get("iv_proxy") or 0.0)
    if not np.isfinite(iv) or iv <= 0:
        return "invalid_iv"
    if float(row.get("iv_rank") or 0.0) < float(cfg.get("iv_rank_min", 0.0)):
        relaxed = {**cfg, "iv_rank_min": 0.0}
        if pick_structure_entry(row, spot, today, relaxed, structure=structure) is not None:
            return "iv_rank_below_min"
    relaxed_credit = {**cfg, "min_credit_pct": 0.0}
    if pick_structure_entry(row, spot, today, relaxed_credit, structure=structure) is not None:
        return "credit_floor"
    relaxed_risk = {**cfg, "max_loss_budget_usd": 1e9}
    if pick_structure_entry(row, spot, today, relaxed_risk, structure=structure) is not None:
        return "max_loss_budget"
    return "contract_strike_or_nonpositive_credit"


def run_regime_router_backtest(
    symbol: str,
    *,
    df: pd.DataFrame,
    policy: str = "router",
    period: str = "",
    configs: Optional[dict[str, dict[str, Any]]] = None,
    sleeve_usd: float = 3000.0,
    open_risk_budget_usd: float = 750.0,
    min_bars: int = 15,
) -> RegimeRouterResult:
    """Run one shared position across routed PCS/CCS/IC entries."""
    sym = symbol.upper()
    if df is None or len(df) < min_bars:
        return RegimeRouterResult(sym, policy, False, "insufficient history", period=period)

    cfgs = default_structure_configs()
    for structure, override in (configs or {}).items():
        if structure in cfgs:
            cfgs[structure].update(override)
            cfgs[structure]["structure"] = structure

    trades: list[PcsTrade] = []
    open_trade: PcsTrade | None = None
    open_structure: str | None = None
    gid = 0
    route_counts = {structure: 0 for structure in STRUCTURES}
    route_counts["stand_aside"] = 0
    selected_counts = {structure: 0 for structure in STRUCTURES}
    accepted_counts = {structure: 0 for structure in STRUCTURES}
    reject_reason_counts: dict[str, dict[str, int]] = {structure: {} for structure in STRUCTURES}

    for today, row in df.iterrows():
        spot = float(cast(Any, row["close"]))
        sigma = float(cast(Any, row["iv_proxy"]))
        if not np.isfinite(sigma) or sigma <= 0:
            continue
        timestamp = cast(pd.Timestamp, pd.Timestamp(str(today)))
        closed_this_bar = False

        if open_trade is not None and open_structure is not None:
            cfg = cfgs[open_structure]
            half_spread = max(float(cfg.get("half_spread_per_leg", 0.0)), 0.0)
            mark = open_trade.mark_net_debit(
                spot,
                sigma,
                timestamp,
                r=float(cfg.get("risk_free_rate", 0.04)),
                half_spread_per_leg=half_spread,
            )
            decision = check_pcs_exit(open_trade, mark, row, cfg)
            if decision is not None:
                debit = float(mark["net_debit"]) * (1.0 + float(cfg.get("slippage_pct", 0.0)))
                max_debit = (
                    float(open_trade.width) + float(open_trade.call_width or open_trade.width)
                    if open_trade.right == "iron_condor"
                    else float(open_trade.width)
                )
                open_trade.exit_date = timestamp
                open_trade.exit_debit = min(debit, max_debit)
                open_trade.exit_reason = decision
                open_trade.closed = True
                trades.append(open_trade)
                open_trade = None
                open_structure = None
                closed_this_bar = True

        if open_trade is None and not closed_this_bar:
            structure = _policy_structure(row, policy, cfgs)
            if structure is None:
                route_counts["stand_aside"] += 1
                continue
            selected_counts[structure] += 1
            entry = pick_structure_entry(row, spot, timestamp, cfgs[structure], structure=structure)
            if entry is None:
                route_counts["stand_aside"] += 1
                reason = diagnose_entry_rejection(
                    row,
                    spot,
                    timestamp,
                    cfgs[structure],
                    structure=structure,
                )
                reject_reason_counts[structure][reason] = reject_reason_counts[structure].get(reason, 0) + 1
                continue
            entry.group_id = gid
            gid += 1
            open_trade = entry
            open_structure = structure
            route_counts[structure] += 1
            accepted_counts[structure] += 1

    if open_trade is not None and open_structure is not None:
        last_date = cast(pd.Timestamp, pd.Timestamp(str(df.index[-1])))
        last_row = df.iloc[-1]
        cfg = cfgs[open_structure]
        mark = open_trade.mark_net_debit(
            float(last_row["close"]),
            max(float(last_row["iv_proxy"]), 1e-6),
            last_date,
            r=float(cfg.get("risk_free_rate", 0.04)),
            half_spread_per_leg=max(float(cfg.get("half_spread_per_leg", 0.0)), 0.0),
        )
        max_debit = (
            float(open_trade.width) + float(open_trade.call_width or open_trade.width)
            if open_trade.right == "iron_condor"
            else float(open_trade.width)
        )
        open_trade.exit_date = last_date
        open_trade.exit_debit = min(
            float(mark["net_debit"]) * (1.0 + float(cfg.get("slippage_pct", 0.0))),
            max_debit,
        )
        open_trade.exit_reason = "end_of_data"
        open_trade.closed = True
        trades.append(open_trade)

    routing_violations = [
        trade
        for trade in trades
        if policy == "router"
        and not (
            (trade.regime_at_entry == "bullish" and trade.right == "put")
            or (trade.regime_at_entry == "bearish" and trade.right == "call")
            or (trade.regime_at_entry == "neutral" and trade.right == "iron_condor")
        )
    ]
    entry_funnel = {
        "selected": selected_counts,
        "accepted": accepted_counts,
        "rejected": {
            structure: selected_counts[structure] - accepted_counts[structure]
            for structure in STRUCTURES
        },
        "reject_reasons": reject_reason_counts,
    }
    metrics = compute_pcs_metrics(trades)
    metrics.update(
        {
            "policy": policy,
            "contract_grid_mode": "synthetic",
            "route_counts": route_counts,
            "entry_funnel": entry_funnel,
            "population_pure": not routing_violations,
            "routing_violations": len(routing_violations),
            "same_bar_reentries": sum(
                previous.exit_date == following.entry_date
                for previous, following in zip(trades, trades[1:])
            ),
        }
    )
    worst_max_loss = float(metrics.get("worst_max_loss_usd") or 0.0)
    capital = capital_fit_pcs(
        max_loss_usd=worst_max_loss,
        sleeve_usd=sleeve_usd,
        open_risk_budget_usd=open_risk_budget_usd,
        max_loss_budget_usd=300.0,
        structure="regime_router" if policy == "router" else policy,
    )
    capital["worst_trade_max_loss_usd"] = round(worst_max_loss, 2)
    return RegimeRouterResult(
        symbol=sym,
        policy=policy,
        ok=True,
        reason="ok",
        period=period,
        n_trades=len(trades),
        metrics=metrics,
        trades=trades,
        capital=capital,
        route_counts=route_counts,
        entry_funnel=entry_funnel,
    )

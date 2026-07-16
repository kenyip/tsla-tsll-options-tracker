#!/usr/bin/env python3
"""Frozen L0 proxy payoff lab for the F2 breakout bull-call candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np
import pandas as pd

import pricing
from trader_platform.research.pcs_sim import listed_weekly_expiration, strike_increment_for

try:
    from scripts.breakout_continuation_holdout_lab import (
        load_frozen_panel,
        verify_frozen_population,
    )
    from scripts.breakout_continuation_train_lab import build_matched_blueprints
except ModuleNotFoundError:  # Direct script execution places scripts/ on sys.path.
    from breakout_continuation_holdout_lab import (  # type: ignore[no-redef]
        load_frozen_panel,
        verify_frozen_population,
    )
    from breakout_continuation_train_lab import build_matched_blueprints  # type: ignore[no-redef]


FROZEN_DNA: dict[str, Any] = {
    "candidate_id": "MULTINAME_BREAKOUT_BULL_CALL_14D_V1",
    "option_dna_id": "BREAKOUT_BULL_CALL_14D_055D_1W_10S_V1",
    "structure": "bull_call_debit_spread",
    "target_dte_calendar_days": 14,
    "long_call_delta": 0.55,
    "width_usd": 1.0,
    "hard_time_stop_sessions": 10,
    "profit_harvest_fraction_of_max_value": 0.50,
    "risk_free_rate": 0.04,
}


def normalized_evidence_sha256(payload: dict[str, Any]) -> str:
    """Hash substantive evidence while excluding only nondeterministic time."""
    normalized = dict(payload)
    normalized.pop("generated_at", None)
    encoded = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def select_proxy_contract(
    *, spot: float, sigma: float, entry_date: str | pd.Timestamp
) -> dict[str, Any] | None:
    """Select the frozen exact-$1 call vertical or fail closed on the proxy grid."""
    s = float(spot)
    vol = float(sigma)
    today = pd.Timestamp(entry_date).normalize()
    if s <= 0.0 or vol <= 0.0 or pd.isna(today):
        return None
    increment = float(strike_increment_for(s))
    width = float(FROZEN_DNA["width_usd"])
    steps = width / increment
    if abs(steps - round(steps)) > 1e-12:
        return None
    expiration = listed_weekly_expiration(today, int(FROZEN_DNA["target_dte_calendar_days"]))
    dte = int((expiration - today).days)
    try:
        exact = pricing.strike_from_delta(
            s,
            dte / 365.0,
            vol,
            float(FROZEN_DNA["long_call_delta"]),
            "call",
            r=float(FROZEN_DNA["risk_free_rate"]),
        )
    except ValueError:
        return None
    long_strike = float(pricing.round_strike(exact, increment))
    short_strike = long_strike + width
    if long_strike <= 0.0 or short_strike <= long_strike:
        return None
    return {
        "expiration": expiration,
        "dte": dte,
        "long_strike": long_strike,
        "short_strike": short_strike,
        "width": width,
        "grid_increment": increment,
        "grid_provenance": "synthetic_exchange_convention_proxy",
    }


def price_vertical_package(
    *,
    spot: float,
    sigma: float,
    today: str | pd.Timestamp,
    expiration: str | pd.Timestamp,
    long_strike: float,
    short_strike: float,
    side: str,
    slippage_pct: float,
    half_spread_per_leg: float,
) -> float:
    """Return an adverse executable debit/credit without flooring closing friction."""
    if side not in {"entry", "exit"}:
        raise ValueError("side must be entry or exit")
    current = pd.Timestamp(today)
    expiry = pd.Timestamp(expiration)
    s = float(spot)
    vol = float(sigma)
    days = max(int((expiry.date() - current.date()).days), 0)
    if days == 0:
        long_value = max(s - float(long_strike), 0.0)
        short_value = max(s - float(short_strike), 0.0)
    else:
        t = days / 365.0
        r = float(FROZEN_DNA["risk_free_rate"])
        long_value = float(pricing.price(s, float(long_strike), t, vol, "call", r=r))
        short_value = float(pricing.price(s, float(short_strike), t, vol, "call", r=r))
    slip = max(float(slippage_pct), 0.0)
    half_spread = max(float(half_spread_per_leg), 0.0)
    if side == "entry":
        return float(
            long_value * (1.0 + slip)
            - short_value * (1.0 - slip)
            + 2.0 * half_spread
        )
    return float(
        long_value * (1.0 - slip)
        - short_value * (1.0 + slip)
        - 2.0 * half_spread
    )


def simulate_signal(
    *,
    symbol: str,
    close: pd.Series,
    entry_date: str | pd.Timestamp,
    sigma: float,
    prebreakout_high: float,
    cost: dict[str, float],
) -> dict[str, Any] | None:
    """Simulate one frozen signal on completed daily closes."""
    series = pd.to_numeric(close, errors="coerce").astype(float)
    series.index = pd.DatetimeIndex(pd.to_datetime(series.index)).tz_localize(None).normalize()
    entry = pd.Timestamp(entry_date).normalize()
    if (
        series.empty
        or not series.index.is_unique
        or not series.index.is_monotonic_increasing
        or entry not in series.index
        or not bool((series > 0.0).all())
        or not bool(series.notna().all())
    ):
        raise ValueError("close path must be finite, positive, unique, increasing, and include entry")
    entry_position = int(series.index.get_loc(entry))
    hard_stop = int(FROZEN_DNA["hard_time_stop_sessions"])
    if entry_position + hard_stop >= len(series):
        return None
    contract = select_proxy_contract(spot=float(series.loc[entry]), sigma=float(sigma), entry_date=entry)
    if contract is None:
        return None
    expiration = pd.Timestamp(contract["expiration"]).normalize()
    expiry_sessions = series.index[(series.index >= entry) & (series.index <= expiration)]
    if len(expiry_sessions) == 0:
        return None
    expiry_session = pd.Timestamp(expiry_sessions[-1]).normalize()
    slip = float(cost.get("slippage_pct", 0.0))
    half_spread = float(cost.get("half_spread_per_leg", 0.0))
    entry_debit = price_vertical_package(
        spot=float(series.loc[entry]),
        sigma=float(sigma),
        today=entry,
        expiration=contract["expiration"],
        long_strike=float(contract["long_strike"]),
        short_strike=float(contract["short_strike"]),
        side="entry",
        slippage_pct=slip,
        half_spread_per_leg=half_spread,
    )
    width = float(contract["width"])
    if entry_debit <= 0.01 or entry_debit >= width:
        return None
    exit_date = entry
    exit_credit = entry_debit
    exit_reason = "hard_10_session_stop"
    sessions_held = hard_stop
    for offset in range(1, hard_stop + 1):
        current_date = pd.Timestamp(series.index[entry_position + offset])
        current_spot = float(series.iloc[entry_position + offset])
        is_expiry_session = current_date >= expiry_session
        valuation_date = expiration if is_expiry_session else current_date
        liquidation = price_vertical_package(
            spot=current_spot,
            sigma=float(sigma),
            today=valuation_date,
            expiration=expiration,
            long_strike=float(contract["long_strike"]),
            short_strike=float(contract["short_strike"]),
            side="exit",
            slippage_pct=slip,
            half_spread_per_leg=half_spread,
        )
        reason = None
        if is_expiry_session:
            reason = "contract_expiration_session"
        elif liquidation >= float(FROZEN_DNA["profit_harvest_fraction_of_max_value"]) * width:
            reason = "profit_harvest_50pct_max_value"
        elif current_spot < float(prebreakout_high):
            reason = "breakout_invalidation"
        elif offset == hard_stop:
            reason = "hard_10_session_stop"
        if reason is not None:
            exit_date = current_date
            exit_credit = float(liquidation)
            exit_reason = reason
            sessions_held = offset
            break
    pnl_usd = float((exit_credit - entry_debit) * 100.0)
    return {
        "symbol": str(symbol).upper(),
        "entry_date": str(entry.date()),
        "exit_date": str(exit_date.date()),
        "sessions_held": int(sessions_held),
        "expiration": str(expiration.date()),
        "expiration_session": str(expiry_session.date()),
        "long_strike": float(contract["long_strike"]),
        "short_strike": float(contract["short_strike"]),
        "width": width,
        "grid_increment": float(contract["grid_increment"]),
        "grid_provenance": str(contract["grid_provenance"]),
        "sigma_fixed": float(sigma),
        "prebreakout_high": float(prebreakout_high),
        "entry_debit": float(entry_debit),
        "exit_credit": float(exit_credit),
        "pnl_usd": pnl_usd,
        "entry_debit_risk_usd": float(entry_debit * 100.0),
        "managed_path_loss_usd": float(max(-pnl_usd, 0.0)),
        "one_lot_max_loss_usd": float(max(entry_debit * 100.0, -pnl_usd, 0.0)),
        "exit_reason": exit_reason,
    }


def build_portfolio_ledger(
    trades: list[dict[str, Any]], *, symbol_order: list[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Admit one global risk unit with deterministic date/symbol priority."""
    priorities = {str(symbol).upper(): index for index, symbol in enumerate(symbol_order)}
    ordered = sorted(
        trades,
        key=lambda row: (
            str(row["entry_date"]),
            priorities.get(str(row["symbol"]).upper(), len(priorities)),
        ),
    )
    ledger: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    last_exit: pd.Timestamp | None = None
    for row in ordered:
        entry = pd.Timestamp(row["entry_date"])
        exit_date = pd.Timestamp(row["exit_date"])
        if exit_date < entry:
            raise ValueError("trade exit cannot precede entry")
        if last_exit is not None and entry <= last_exit:
            skipped.append(
                {
                    "symbol": str(row["symbol"]).upper(),
                    "entry_date": str(entry.date()),
                    "reason": "global_risk_unit_open_or_same_day_exit",
                }
            )
            continue
        ledger.append(row)
        last_exit = exit_date
    return ledger, skipped


def _pnl_metrics(trades: list[dict[str, Any]]) -> dict[str, Any]:
    pnl = np.asarray([float(row["pnl_usd"]) for row in trades], dtype=float)
    if len(pnl) and not np.isfinite(pnl).all():
        raise ValueError("trade PnL must be finite")
    equity = np.concatenate(([0.0], np.cumsum(pnl)))
    drawdown = np.maximum.accumulate(equity) - equity
    chunks = [pnl[start : start + 6] for start in range(0, len(pnl), 6)]
    dense_negative = sum(len(chunk) >= 3 and float(chunk.sum()) < 0.0 for chunk in chunks)
    max_loss = max((float(row["one_lot_max_loss_usd"]) for row in trades), default=0.0)
    return {
        "n_trades": len(trades),
        "total_pnl_usd": float(pnl.sum()) if len(pnl) else 0.0,
        "mean_pnl_usd": float(pnl.mean()) if len(pnl) else 0.0,
        "win_rate": float(np.mean(pnl > 0.0)) if len(pnl) else 0.0,
        "max_drawdown_usd": float(drawdown.max()) if len(drawdown) else 0.0,
        "dense_negative_windows": int(dense_negative),
        "one_lot_max_loss_usd": float(max_loss),
    }


def summarize_axis(
    trades: list[dict[str, Any]],
    *,
    requested: int,
    symbol_order: list[str],
    min_event_trades: int,
    min_portfolio_trades: int,
    min_symbols: int,
) -> dict[str, Any]:
    """Summarize absolute option PnL and the executable one-unit ledger."""
    if requested < len(trades) or min(min_event_trades, min_portfolio_trades, min_symbols) < 1:
        raise ValueError("requested and gate minima must be positive and coherent")
    ledger, admission_skips = build_portfolio_ledger(trades, symbol_order=symbol_order)
    event_metrics = _pnl_metrics(trades)
    portfolio_metrics = _pnl_metrics(ledger)
    symbols = sorted({str(row["symbol"]).upper() for row in trades})
    event_metrics["symbols"] = symbols
    event_metrics["by_symbol"] = {
        symbol: _pnl_metrics(
            [row for row in trades if str(row["symbol"]).upper() == symbol]
        )
        for symbol in symbols
    }
    ordered_events = sorted(trades, key=lambda row: (str(row["entry_date"]), str(row["symbol"])))
    event_metrics["chronological_tertiles"] = [
        {
            "tertile": index,
            "first_entry_date": str(chunk[0]["entry_date"]),
            "last_entry_date": str(chunk[-1]["entry_date"]),
            **_pnl_metrics(chunk),
        }
        for index, positions in enumerate(np.array_split(np.arange(len(ordered_events)), 3), start=1)
        if (chunk := [ordered_events[int(position)] for position in positions])
    ]
    one_lot_max_loss = max(
        float(event_metrics["one_lot_max_loss_usd"]),
        float(portfolio_metrics["one_lot_max_loss_usd"]),
    )
    integrity = bool(
        all(pd.Timestamp(row["entry_date"]) < pd.Timestamp(row["exit_date"]) for row in trades)
        and all(float(row["one_lot_max_loss_usd"]) >= 0.0 for row in trades)
        and all(
            pd.Timestamp(ledger[index - 1]["exit_date"])
            < pd.Timestamp(ledger[index]["entry_date"])
            for index in range(1, len(ledger))
        )
        and len({(row["symbol"], row["entry_date"]) for row in trades}) == len(trades)
    )
    gate_checks = {
        "minimum_event_trades": len(trades) >= int(min_event_trades),
        "minimum_symbol_breadth": len(symbols) >= int(min_symbols),
        "positive_event_total_pnl": float(event_metrics["total_pnl_usd"]) > 0.0,
        "minimum_portfolio_trades": len(ledger) >= int(min_portfolio_trades),
        "positive_portfolio_total_pnl": float(portfolio_metrics["total_pnl_usd"]) > 0.0,
        "one_lot_max_loss_lte_300": 0.0 < one_lot_max_loss <= 300.0,
        "portfolio_max_drawdown_lte_75": float(portfolio_metrics["max_drawdown_usd"]) <= 75.0,
        "dense_negative_windows_lte_5": int(portfolio_metrics["dense_negative_windows"]) <= 5,
        "integrity": integrity,
    }
    return {
        "n_requested": int(requested),
        "n_eligible": len(trades),
        "n_listing_or_pricing_skipped": int(requested - len(trades)),
        "event": event_metrics,
        "portfolio": portfolio_metrics,
        "portfolio_admission_skips": admission_skips,
        "one_lot_max_loss_usd": float(one_lot_max_loss),
        "capital_fit_usd": float(
            max((float(row.get("entry_debit_risk_usd", 0.0)) for row in trades), default=0.0)
        ),
        "max_lots": 1 if 0.0 < one_lot_max_loss <= 300.0 else 0,
        "integrity": integrity,
        "gate_checks": gate_checks,
        "gate_pass": bool(all(gate_checks.values())),
        "trades": trades,
        "portfolio_ledger": ledger,
    }


def evaluate_partition(
    close_panel: pd.DataFrame,
    blueprints: list[dict[str, Any]],
    *,
    cost: dict[str, float],
    symbol_order: list[str],
    min_event_trades: int,
    min_portfolio_trades: int,
    min_symbols: int,
) -> dict[str, Any]:
    """Price the frozen treated entries only; controls never enter option PnL."""
    trades: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for index, blueprint in enumerate(blueprints):
        symbol = str(blueprint["symbol"]).upper()
        if symbol not in close_panel.columns:
            raise ValueError(f"blueprint {index} symbol is outside the panel")
        series = close_panel[symbol]
        signal = pd.Timestamp(blueprint["treated_signal_date"]).normalize()
        entry = pd.Timestamp(blueprint["treated_entry_date"]).normalize()
        if signal not in series.index or entry not in series.index:
            raise ValueError(f"blueprint {index} dates are outside the panel")
        signal_position = int(series.index.get_loc(signal))
        entry_position = int(series.index.get_loc(entry))
        if signal_position < 20 or entry_position != signal_position + 1:
            raise ValueError(f"blueprint {index} violates signal/entry chronology")
        prebreakout_high = float(series.iloc[signal_position - 20 : signal_position].max())
        sigma = float(blueprint["treated_hv_20"])
        trade = simulate_signal(
            symbol=symbol,
            close=series,
            entry_date=entry,
            sigma=sigma,
            prebreakout_high=prebreakout_high,
            cost=cost,
        )
        if trade is None:
            spot = float(series.loc[entry])
            contract = select_proxy_contract(spot=spot, sigma=sigma, entry_date=entry)
            skipped.append(
                {
                    "index": index,
                    "symbol": symbol,
                    "entry_date": str(entry.date()),
                    "spot": spot,
                    "reason": (
                        "exact_one_dollar_proxy_grid_unavailable"
                        if contract is None
                        else "invalid_or_overwide_adverse_cost_debit"
                    ),
                }
            )
            continue
        trade["blueprint_index"] = index
        trade["signal_date"] = str(signal.date())
        trades.append(trade)
    result = summarize_axis(
        trades,
        requested=len(blueprints),
        symbol_order=symbol_order,
        min_event_trades=min_event_trades,
        min_portfolio_trades=min_portfolio_trades,
        min_symbols=min_symbols,
    )
    result["pricing_skips"] = skipped
    result["option_mark_provenance"] = "black_scholes_proxy_fixed_signal_day_realized_volatility"
    result["listing_grid_provenance"] = "synthetic_exchange_convention_proxy"
    return result


def decide_strategy_outcome(partitions: dict[str, dict[str, dict[str, Any]]]) -> dict[str, Any]:
    """Close the frozen option family from all predeclared partition/cost gates."""
    expected = ("development", "inspected_secondary_stress")
    failed_axes: list[str] = []
    failed_checks: list[str] = []
    for partition in expected:
        axes = partitions.get(partition, {})
        for axis in ("percentage_5pct", "fixed_0p01"):
            result = axes.get(axis)
            label = f"{partition}.{axis}"
            if result is None or not bool(result.get("gate_pass", False)):
                failed_axes.append(label)
                if result is None:
                    failed_checks.append(f"{label}.missing")
                else:
                    failed_checks.extend(
                        f"{label}.{name}"
                        for name, passed in dict(result.get("gate_checks", {})).items()
                        if not bool(passed)
                    )
    advanced = not failed_axes
    return {
        "strategy_outcome": "STRATEGY_ADVANCED" if advanced else "FAMILY_CLOSED",
        "funnel_stage_before": "F2_UNTOUCHED_HOLDOUT",
        "funnel_stage_after": "F3_ROBUST_PAPER_PLAN" if advanced else "F2_UNTOUCHED_HOLDOUT",
        "failed_axes": failed_axes,
        "failed_checks": failed_checks,
        "dominant_failure_mechanism": None if advanced else failed_checks[0] if failed_checks else failed_axes[0],
    }


def run_lab_from_panel(
    frozen_train: dict[str, Any],
    f2_summary: dict[str, Any],
    close_panel: pd.DataFrame,
) -> dict[str, Any]:
    """Reproduce the frozen population, price fixed DNA, and close F2->F3 or family."""
    if frozen_train.get("candidate_id") != FROZEN_DNA["candidate_id"]:
        raise ValueError("unexpected frozen train candidate")
    if f2_summary.get("candidate_id") != FROZEN_DNA["candidate_id"]:
        raise ValueError("unexpected F2 summary candidate")
    if (
        f2_summary.get("strategy_outcome") != "STRATEGY_ADVANCED"
        or f2_summary.get("funnel_stage_after") != "F2_UNTOUCHED_HOLDOUT"
        or bool(f2_summary.get("authority", {}).get("l1_or_capital_seat", True))
    ):
        raise ValueError("option payoff may run only from F2/L0 with no L1 authority")
    config = dict(frozen_train["config"])
    bounds = list(config["control_breakout_ratio_bounds"])
    blueprints = build_matched_blueprints(
        close_panel,
        breakout_lookback_sessions=int(config["breakout_lookback_sessions"]),
        breakout_ratio_min=float(config["breakout_ratio_min"]),
        control_breakout_ratio_low=float(bounds[0]),
        control_breakout_ratio_high=float(bounds[1]),
        trend_lookback_sessions=int(config["trend_lookback_sessions"]),
        forward_sessions=int(config["forward_sessions"]),
        max_match_distance_sessions=int(config["max_match_distance_sessions"]),
        max_return_20d_distance=float(config["max_return_20d_distance"]),
        max_hv_20d_distance=float(config["max_hv_20d_distance"]),
    )
    verification = verify_frozen_population(
        frozen_train,
        blueprints,
        train_fraction=float(config["train_fraction"]),
    )
    expected_verification = dict(f2_summary["population_verification"])
    for key in (
        "matched_blueprints",
        "train_blueprints",
        "holdout_blueprints",
        "all_identity_sha256",
        "train_identity_sha256",
        "holdout_identity_sha256",
    ):
        if verification[key] != expected_verification[key]:
            raise ValueError(f"F2 population verification mismatch: {key}")
    ordered = sorted(
        blueprints,
        key=lambda row: (pd.Timestamp(row["treated_signal_date"]), str(row["symbol"])),
    )
    split = int(len(ordered) * float(config["train_fraction"]))
    development = ordered[:split]
    inspected_secondary = ordered[split:]
    symbols = [str(symbol).upper() for symbol in config["symbols"]]
    costs = {
        "percentage_5pct": {"slippage_pct": 0.05, "half_spread_per_leg": 0.0},
        "fixed_0p01": {"slippage_pct": 0.0, "half_spread_per_leg": 0.01},
    }
    partitions: dict[str, dict[str, dict[str, Any]]] = {
        "development": {
            axis: evaluate_partition(
                close_panel,
                development,
                cost=cost,
                symbol_order=symbols,
                min_event_trades=80,
                min_portfolio_trades=30,
                min_symbols=6,
            )
            for axis, cost in costs.items()
        },
        "inspected_secondary_stress": {
            axis: evaluate_partition(
                close_panel,
                inspected_secondary,
                cost=cost,
                symbol_order=symbols,
                min_event_trades=40,
                min_portfolio_trades=20,
                min_symbols=6,
            )
            for axis, cost in costs.items()
        },
    }
    decision = decide_strategy_outcome(partitions)
    all_axes = [result for axes in partitions.values() for result in axes.values()]
    max_loss = max(float(result["one_lot_max_loss_usd"]) for result in all_axes)
    capital_fit = max(float(result["capital_fit_usd"]) for result in all_axes)
    advanced = decision["strategy_outcome"] == "STRATEGY_ADVANCED"
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD_L0_PROXY",
        "paper_only": True,
        "sleeve_usd": 3000.0,
        "candidate_id": FROZEN_DNA["candidate_id"],
        "option_dna_id": FROZEN_DNA["option_dna_id"],
        "mechanism_family": "TIME_SERIES_20D_BREAKOUT_CONTINUATION_EXPRESSED_AS_BULL_CALL_DEBIT",
        "economic_mechanism": (
            "post-breakout information diffusion and trend-following demand may produce enough positive "
            "ten-session drift to overcome fixed-DNA bull-call theta and two-leg friction"
        ),
        "forecast_type": "conditional_direction_up_10_sessions",
        "structure": "bull_call_debit_spread",
        "frozen_dna": dict(FROZEN_DNA),
        "regime_envelope": (
            "completed close at least 1.02 times the prior completed 20-session high and above the prior "
            "completed SMA100; otherwise stand aside"
        ),
        "entry_trigger": "next-session close after the lag-safe completed breakout",
        "exit_management": (
            "from the next completed session: contract-expiration session first, else 50% of $1 max-value "
            "harvest, else close below pre-breakout 20-session high, else hard ten-session stop; no same-bar reentry"
        ),
        "greek_exposures": {
            "intended": "positive delta and bounded positive gamma",
            "dangerous": "theta, long-vega/model error, short-call dividend/assignment, pin, and multi-leg friction",
        },
        "cost_axes": costs,
        "option_mark_provenance": "black_scholes_proxy_fixed_signal_day_realized_volatility",
        "listing_grid_provenance": "synthetic_exchange_convention_proxy_not_observed_historical_listing",
        "population_verification": verification,
        "partition_roles": {
            "development": "original 168 inspected development blueprints; primary DNA judgment",
            "inspected_secondary_stress": (
                "opened 113 F2 holdout blueprints; secondary fixed-DNA stress only, never a new untouched holdout"
            ),
            "retune_from_secondary_stress": False,
        },
        "partitions": partitions,
        **decision,
        "bar_claimed": "L0_proxy_F2_to_F3_only" if advanced else "L0_proxy_family_falsification",
        "confidence_stage": "F3_ROBUST_PAPER_PLAN/L0_PROXY" if advanced else "F2_UNDERLYING_CONTEXT_OPTION_EXPRESSION_CLOSED",
        "l1_claim": False,
        "capital_seat": False,
        "registration_eligible": False,
        "capital_fit_usd": capital_fit,
        "structural_expiry_max_loss_usd": capital_fit,
        "stress_managed_max_loss_usd": max_loss,
        "one_lot_max_loss_usd": max_loss,
        "max_loss_usd": max_loss,
        "max_lots": 1 if 0.0 < max_loss <= 300.0 else 0,
        "portfolio_overlap": "one global breakout risk unit; deterministic date then frozen-symbol priority",
        "stand_aside_rule": (
            "stand aside on missing signal, unavailable exact-$1 proxy grid, invalid debit, risk-unit overlap, "
            "or any failed after-cost/loss-quality gate; observed contract and quote checks remain mandatory"
        ),
        "closed_family": None if advanced else FROZEN_DNA["option_dna_id"],
        "underlying_f2_preserved_as_context": True,
        "paired_underlying_excess_can_rescue_option_failure": False,
        "authority": {
            "research_l0_proxy": True,
            "l1_or_capital_seat": False,
            "paper_order_or_status": False,
            "shadow_or_live": False,
        },
        "evidence_critique": (
            "Uses frozen adjusted-close histories and exact population identities, but option marks, volatility, "
            "expiration, and strike availability remain proxy abstractions. Fixed signal-day realized volatility "
            "does not model implied-volatility/skew paths; dividends/American exercise and observed fills are absent. "
            "The fixed present-day universe is survivorship/listing biased. Percentage-per-leg friction can "
            "make a forced managed close lose more than the spread's expiry debit; that is retained as a stress "
            "loss, while structural expiry max loss is reported separately. Therefore this result can only advance "
            "or close the exact L0 option expression; it cannot earn L1 or a capital seat."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-train", required=True)
    parser.add_argument("--f2-summary", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    frozen_path = Path(args.frozen_train).expanduser().resolve()
    summary_path = Path(args.f2_summary).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite option payoff evidence: {out_path}")
    frozen_bytes = frozen_path.read_bytes()
    summary_bytes = summary_path.read_bytes()
    frozen_train = json.loads(frozen_bytes)
    f2_summary = json.loads(summary_bytes)
    panel, source_verification = load_frozen_panel(
        frozen_train,
        repo_root=Path(__file__).resolve().parents[1],
    )
    payload = run_lab_from_panel(frozen_train, f2_summary, panel)
    payload["source_artifacts"] = {
        "frozen_train": {
            "path": str(frozen_path),
            "sha256": hashlib.sha256(frozen_bytes).hexdigest(),
        },
        "f2_summary": {
            "path": str(summary_path),
            "sha256": hashlib.sha256(summary_bytes).hexdigest(),
        },
    }
    payload["data_verification"] = source_verification
    encoded = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(out_path),
                "strategy_outcome": payload["strategy_outcome"],
                "funnel_stage_after": payload["funnel_stage_after"],
                "failed_checks": payload["failed_checks"],
                "capital_fit_usd": payload["capital_fit_usd"],
                "one_lot_max_loss_usd": payload["one_lot_max_loss_usd"],
            },
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

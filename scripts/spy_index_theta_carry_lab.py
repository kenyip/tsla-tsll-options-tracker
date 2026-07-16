#!/usr/bin/env python3
"""Frozen SPY regime-gated index theta-carry discovery lab (BUILD/L0 only)."""
from __future__ import annotations

from typing import Any

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pricing
from data import add_features
from scripts.spy_vrp_pcs_study import (
    _adverse_entry,
    _adverse_exit,
    _put_mid,
    _select_integer_put_strikes,
    load_spy,
    load_vix,
)
from trader_platform.research.pcs_sim import listed_weekly_expiration

COST_AXES = ("slippage_5pct", "fixed_0p01_per_leg")
MIN_TRADES = 20
MIN_REGIME_CONTRAST_TRADES = 8
MAX_DD = 150.0
MAX_EXPECTED_SHORTFALL_LOSS = 125.0
MAX_ONE_LOT_LOSS = 300.0


def candidate_config() -> dict[str, Any]:
    return {
        "symbol": "SPY",
        "target_dte": 21,
        "target_delta": 0.20,
        "spread_width": 2.0,
        "min_credit": 0.30,
        "max_sessions": 10,
        "profit_target": 0.50,
        "defined_loss_exit_frac": 0.70,
        "delta_breach": 0.45,
        "allowed_signal_regimes": ["bullish", "neutral"],
    }


def control_config() -> dict[str, Any]:
    return {
        **candidate_config(),
        "allowed_signal_regimes": ["bullish", "neutral", "bearish"],
    }


def build_features(spy: pd.DataFrame, vix: pd.Series) -> pd.DataFrame:
    frame = add_features(spy.copy())
    frame["vix"] = vix.reindex(frame.index)
    frame["latest_prior_vix"] = frame["vix"].shift(1).ffill()
    return frame.dropna(subset=["ema_200", "close", "regime", "vix", "latest_prior_vix"])


def select_blueprints(features: pd.DataFrame, config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    next_entry_position = 1
    allowed = set(config["allowed_signal_regimes"])
    for entry_position in range(1, len(features) - 1):
        if entry_position < next_entry_position:
            continue
        signal_position = entry_position - 1
        signal = features.iloc[signal_position]
        if str(signal.get("regime")) not in allowed:
            continue
        sigma = float(signal.get("vix", 0.0)) / 100.0
        spot = float(features.iloc[entry_position]["close"])
        if sigma <= 0.0 or spot <= 0.0:
            continue
        entry_date = pd.Timestamp(features.index[entry_position])
        signal_date = pd.Timestamp(features.index[signal_position])
        expiration = listed_weekly_expiration(entry_date, int(config["target_dte"]))
        dte = int((expiration.date() - entry_date.date()).days)
        short_strike, _, actual_delta = _select_integer_put_strikes(spot, dte, sigma)
        long_strike = short_strike - float(config["spread_width"])
        short_mid = _put_mid(spot, short_strike, dte, sigma)
        long_mid = _put_mid(spot, long_strike, dte, sigma)
        entry_credits = {
            axis: _adverse_entry(short_mid, long_mid, axis)[2]
            for axis in COST_AXES
        }
        if any(credit < float(config["min_credit"]) for credit in entry_credits.values()):
            continue
        structural_max_loss = (
            float(config["spread_width"]) - min(entry_credits.values())
        ) * 100.0
        if not 0.0 < structural_max_loss <= MAX_ONE_LOT_LOSS:
            continue
        rows.append(
            {
                "signal_date": signal_date,
                "entry_date": entry_date,
                "expiration": expiration,
                "signal_regime": str(signal["regime"]),
                "entry_vix_strictly_prior": float(signal["vix"]),
                "entry_spot": spot,
                "short_strike": short_strike,
                "long_strike": long_strike,
                "entry_short_delta_abs": actual_delta,
                "zero_cost_short_mid": short_mid,
                "zero_cost_long_mid": long_mid,
                "entry_credits": entry_credits,
                "structural_max_loss_usd": structural_max_loss,
            }
        )
        next_entry_position = entry_position + int(config["max_sessions"]) + 1
    return rows


def select_anchored_blueprints(
    features: pd.DataFrame,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    anchored: list[dict[str, Any]] = []
    contrast_config = {
        **config,
        "allowed_signal_regimes": ["bullish", "neutral", "bearish"],
    }
    cadence = int(config["max_sessions"]) + 1
    for entry_position in range(1, len(features) - 1, cadence):
        window = features.iloc[entry_position - 1 : entry_position + 2]
        rows = select_blueprints(window, contrast_config)
        if rows:
            anchored.append(rows[0])
    return anchored


def _simulate_trade(
    features: pd.DataFrame,
    blueprint: dict[str, Any],
    config: dict[str, Any],
    axis: str,
) -> dict[str, Any]:
    entry_date = pd.Timestamp(blueprint["entry_date"])
    entry_position = int(features.index.get_loc(entry_date))
    expiration = pd.Timestamp(blueprint["expiration"])
    short_strike = float(blueprint["short_strike"])
    long_strike = float(blueprint["long_strike"])
    short_sale, long_buy, entry_credit = _adverse_entry(
        float(blueprint["zero_cost_short_mid"]),
        float(blueprint["zero_cost_long_mid"]),
        axis,
    )
    structural_max_loss = (float(config["spread_width"]) - entry_credit) * 100.0
    chosen: dict[str, Any] | None = None
    last_position = min(entry_position + int(config["max_sessions"]), len(features) - 1)
    for position in range(entry_position + 1, last_position + 1):
        date = pd.Timestamp(features.index[position])
        spot = float(features.iloc[position]["close"])
        sigma = float(features.iloc[position]["latest_prior_vix"]) / 100.0
        dte = int((expiration.date() - date.date()).days)
        short_mid = _put_mid(spot, short_strike, max(dte, 0), sigma)
        long_mid = _put_mid(spot, long_strike, max(dte, 0), sigma)
        short_buy, long_sale, exit_debit = _adverse_exit(short_mid, long_mid, axis)
        pnl_usd = (entry_credit - exit_debit) * 100.0
        short_delta_abs = (
            1.0
            if dte <= 0 and spot < short_strike
            else 0.0
            if dte <= 0
            else abs(
                pricing.delta(
                    spot,
                    short_strike,
                    dte / 365.0,
                    sigma,
                    "put",
                    r=0.04,
                    q=0.015,
                )
            )
        )
        sessions_held = position - entry_position
        reason = None
        if date >= expiration:
            reason = "expiration"
        elif pnl_usd >= float(config["profit_target"]) * entry_credit * 100.0:
            reason = "profit_target"
        elif pnl_usd <= -float(config["defined_loss_exit_frac"]) * structural_max_loss:
            reason = "defined_loss"
        elif short_delta_abs >= float(config["delta_breach"]):
            reason = "delta_breach"
        elif sessions_held >= int(config["max_sessions"]):
            reason = "session_stop"
        if reason is None and position != last_position:
            continue
        if reason is None:
            reason = "end_of_partition"
        chosen = {
            "signal_date": str(pd.Timestamp(blueprint["signal_date"]).date()),
            "entry_date": str(entry_date.date()),
            "exit_date": str(date.date()),
            "expiration": str(expiration.date()),
            "axis": axis,
            "signal_regime": blueprint["signal_regime"],
            "entry_spot": float(blueprint["entry_spot"]),
            "exit_spot": spot,
            "short_strike": short_strike,
            "long_strike": long_strike,
            "entry_vix_strictly_prior": float(blueprint["entry_vix_strictly_prior"]),
            "exit_vix_latest_strictly_prior": sigma * 100.0,
            "entry_short_sale": short_sale,
            "entry_long_buy": long_buy,
            "entry_credit": entry_credit,
            "exit_short_buy": short_buy,
            "exit_long_sale": long_sale,
            "exit_debit": exit_debit,
            "pnl_usd": pnl_usd,
            "structural_max_loss_usd": structural_max_loss,
            "realized_loss_usd": max(-pnl_usd, 0.0),
            "sessions_held": sessions_held,
            "exit_reason": reason,
            "entry_cost_adverse": bool(
                short_sale <= float(blueprint["zero_cost_short_mid"]) + 1e-12
                and long_buy >= float(blueprint["zero_cost_long_mid"]) - 1e-12
            ),
            "exit_cost_adverse": bool(short_buy >= short_mid - 1e-12 and long_sale <= long_mid + 1e-12),
            "ledger_error_usd": abs((entry_credit - exit_debit) * 100.0 - pnl_usd),
            "max_loss_reconciliation_error_usd": abs(
                (float(config["spread_width"]) - entry_credit) * 100.0 - structural_max_loss
            ),
        }
        break
    if chosen is None:
        raise ValueError(f"no exit row for blueprint {entry_date.date()}")
    return chosen


def _drawdown(values: list[float]) -> float:
    equity = np.concatenate(([0.0], np.cumsum(np.asarray(values, dtype=float))))
    peak = np.maximum.accumulate(equity)
    return float(np.max(peak - equity))


def _axis_metrics(axis: str, trades: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(trades, key=lambda row: row["entry_date"])
    pnls = [float(row["pnl_usd"]) for row in ordered]
    gross_profit = sum(value for value in pnls if value > 0.0)
    gross_loss = -sum(value for value in pnls if value < 0.0)
    tail_n = int(math.ceil(0.10 * len(pnls))) if pnls else 0
    expected_shortfall = float(np.mean(sorted(pnls)[:tail_n])) if tail_n else None
    violations: list[str] = []
    for trade in ordered:
        if pd.Timestamp(trade["signal_date"]) >= pd.Timestamp(trade["entry_date"]):
            violations.append(f"chronology:{trade['entry_date']}")
        if not trade["entry_cost_adverse"] or not trade["exit_cost_adverse"]:
            violations.append(f"cost:{trade['entry_date']}")
        if float(trade["ledger_error_usd"]) > 0.01:
            violations.append(f"ledger:{trade['entry_date']}")
        if float(trade["max_loss_reconciliation_error_usd"]) > 0.01:
            violations.append(f"max_loss:{trade['entry_date']}")
    entries = [row["entry_date"] for row in ordered]
    if len(entries) != len(set(entries)):
        violations.append("duplicate_entries")
    for previous, following in zip(ordered, ordered[1:]):
        if pd.Timestamp(previous["exit_date"]) >= pd.Timestamp(following["entry_date"]):
            violations.append(f"position_overlap:{previous['entry_date']}->{following['entry_date']}")
    maximum_loss = max(
        (
            max(float(row["structural_max_loss_usd"]), float(row["realized_loss_usd"]))
            for row in ordered
        ),
        default=0.0,
    )
    return {
        "axis": axis,
        "n_completed": len(ordered),
        "total_pnl_usd": float(sum(pnls)),
        "avg_pnl_usd": float(np.mean(pnls)) if pnls else 0.0,
        "win_rate": float(np.mean(np.asarray(pnls) > 0.0)) if pnls else 0.0,
        "gross_profit_usd": float(gross_profit),
        "gross_loss_usd": float(gross_loss),
        "profit_factor": None if gross_loss == 0.0 else float(gross_profit / gross_loss),
        "max_drawdown_usd": _drawdown(pnls),
        "expected_shortfall_90_usd": expected_shortfall,
        "maximum_structural_or_realized_one_trade_loss_usd": maximum_loss,
        "capital_fit_usd": maximum_loss,
        "one_lot_max_loss_usd": maximum_loss,
        "max_lots": 1,
        "entry_dates": entries,
        "integrity_violations": violations,
        "trades": ordered,
    }


def simulate_axes(
    features: pd.DataFrame,
    blueprints: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        axis: _axis_metrics(
            axis,
            [_simulate_trade(features, blueprint, config, axis) for blueprint in blueprints],
        )
        for axis in COST_AXES
    }


def summarize_entry_coverage(
    axes: dict[str, dict[str, Any]],
    *,
    train_start: str,
    train_end: str,
) -> dict[str, Any]:
    """Persist where qualifying entries occur so train-period claims cannot overreach."""
    entries_by_axis = {
        axis: [str(value) for value in axes.get(axis, {}).get("entry_dates", [])]
        for axis in COST_AXES
    }
    all_entries = sorted({value for entries in entries_by_axis.values() for value in entries})
    return {
        "train_start": train_start,
        "train_end": train_end,
        "first_entry_date": all_entries[0] if all_entries else None,
        "last_entry_date": all_entries[-1] if all_entries else None,
        "n_unique_entry_dates": len(all_entries),
        "entry_year_counts": {
            year: sum(value.startswith(year) for value in all_entries)
            for year in sorted({value[:4] for value in all_entries})
        },
        "identical_entries_across_cost_axes": (
            entries_by_axis[COST_AXES[0]] == entries_by_axis[COST_AXES[1]]
        ),
        "claim_boundary": (
            "absolute dual-cost results describe only the observed entry-date window; "
            "they do not establish compatibility across the full train period"
        ),
    }


def build_regime_contrast(
    features: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate outcome-independent calendar anchors by prior completed regime."""
    anchored = select_anchored_blueprints(features, config)
    groups = {
        "non_bearish": [
            row for row in anchored if row["signal_regime"] in {"bullish", "neutral"}
        ],
        "bearish": [row for row in anchored if row["signal_regime"] == "bearish"],
    }
    axes = {
        name: simulate_axes(features, blueprints, config)
        for name, blueprints in groups.items()
    }
    return {
        "selection": (
            "every 11th train session from the first eligible entry index; both adverse "
            "entry credits must clear the frozen $0.30 floor; prior completed regime label"
        ),
        "cadence_sessions": int(config["max_sessions"]) + 1,
        "n_calendar_anchors_considered": len(
            range(1, len(features) - 1, int(config["max_sessions"]) + 1)
        ),
        "minimum_completed_trades_per_regime_cost_axis": MIN_REGIME_CONTRAST_TRADES,
        "n_anchored_blueprints": len(anchored),
        "n_blueprints_by_regime": {name: len(rows) for name, rows in groups.items()},
        "identical_entries_across_cost_axes": all(
            axes[name][COST_AXES[0]]["entry_dates"]
            == axes[name][COST_AXES[1]]["entry_dates"]
            for name in groups
        ),
        **axes,
    }


def _axis_pass(row: dict[str, Any]) -> bool:
    pf = row.get("profit_factor")
    total_pnl = float(row.get("total_pnl_usd", 0.0))
    pf_pass = (pf is None and total_pnl > 0.0 and float(row.get("gross_loss_usd", 0.0)) == 0.0) or (
        pf is not None and float(pf) >= 1.05
    )
    return bool(
        int(row.get("n_completed", 0)) >= MIN_TRADES
        and total_pnl > 0.0
        and pf_pass
        and float(row.get("max_drawdown_usd", float("inf"))) <= MAX_DD
        and float(row.get("expected_shortfall_90_usd", float("-inf")))
        >= -MAX_EXPECTED_SHORTFALL_LOSS
        and 0.0
        < float(row.get("maximum_structural_or_realized_one_trade_loss_usd", 0.0))
        <= MAX_ONE_LOT_LOSS
        and not row.get("integrity_violations")
    )


def evaluate_discovery(
    candidate_axes: dict[str, dict[str, Any]],
    control_axes: dict[str, dict[str, Any]],
    *,
    holdout_identity: dict[str, Any],
    regime_contrast: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if any(axis not in candidate_axes or axis not in control_axes for axis in COST_AXES):
        return {
            "pass": False,
            "outcome": "FAMILY_CLOSED",
            "checks": {"dual_cost_axes_complete": False},
            "failed_checks": ["dual_cost_axes_complete"],
            "diagnostics": {},
        }
    candidate_entries = [candidate_axes[axis].get("entry_dates", []) for axis in COST_AXES]
    control_entries = [control_axes[axis].get("entry_dates", []) for axis in COST_AXES]
    control_clean = all(
        int(control_axes[axis].get("n_completed", 0)) >= MIN_TRADES
        and not control_axes[axis].get("integrity_violations")
        for axis in COST_AXES
    )
    path_comparator_pass = min(
        float(candidate_axes[axis].get("avg_pnl_usd", float("-inf"))) for axis in COST_AXES
    ) > min(float(control_axes[axis].get("avg_pnl_usd", float("-inf"))) for axis in COST_AXES)
    checks = {
        "candidate_dual_cost_gate": all(_axis_pass(candidate_axes[axis]) for axis in COST_AXES),
        "candidate_identical_entries_across_cost_axes": candidate_entries[0] == candidate_entries[1],
        "control_non_vacuous_and_integrity_clean": control_clean,
        "control_identical_entries_across_cost_axes": control_entries[0] == control_entries[1],
        "holdout_identity_sealed": bool(
            holdout_identity.get("sealed")
            and holdout_identity.get("start")
            and holdout_identity.get("end")
            and holdout_identity.get("option_outcomes_evaluated") is False
        ),
    }
    diagnostics = {
        "path_control_candidate_worst_axis_average_gt_control": path_comparator_pass,
        "path_control_shared_candidate_entries": len(
            set(candidate_entries[0]).intersection(control_entries[0])
        ),
        "path_control_unique_entry_dates": len(
            set(candidate_entries[0]).symmetric_difference(control_entries[0])
        ),
    }
    if regime_contrast is None:
        checks["candidate_worst_axis_average_gt_control"] = path_comparator_pass
    else:
        contrast_complete = all(
            name in regime_contrast
            and all(axis in regime_contrast[name] for axis in COST_AXES)
            for name in ("non_bearish", "bearish")
        )
        if contrast_complete:
            contrast_non_vacuous = all(
                int(regime_contrast[name][axis].get("n_completed", 0))
                >= MIN_REGIME_CONTRAST_TRADES
                and not regime_contrast[name][axis].get("integrity_violations")
                for name in ("non_bearish", "bearish")
                for axis in COST_AXES
            )
            non_bearish_better = contrast_non_vacuous and min(
                float(regime_contrast["non_bearish"][axis].get("avg_pnl_usd", float("-inf")))
                for axis in COST_AXES
            ) > min(
                float(regime_contrast["bearish"][axis].get("avg_pnl_usd", float("-inf")))
                for axis in COST_AXES
            )
        else:
            contrast_non_vacuous = False
            non_bearish_better = False
        checks.update(
            {
                "anchored_regime_contrast_complete": contrast_complete,
                "anchored_regime_contrast_non_vacuous": contrast_non_vacuous,
                "anchored_regime_contrast_identical_entries_across_cost_axes": bool(
                    regime_contrast.get("identical_entries_across_cost_axes")
                ),
                "non_bearish_worst_axis_average_gt_bearish": non_bearish_better,
            }
        )
    passed = all(checks.values())
    return {
        "pass": passed,
        "outcome": "STRATEGY_ADVANCED" if passed else "FAMILY_CLOSED",
        "checks": checks,
        "failed_checks": [name for name, value in checks.items() if not value],
        "diagnostics": diagnostics,
    }


def run_lab(
    spy: pd.DataFrame,
    vix: pd.Series,
    *,
    spy_provenance: dict[str, Any],
    vix_provenance: dict[str, Any],
    train_fraction: float = 0.60,
) -> dict[str, Any]:
    if not 0.50 <= train_fraction <= 0.80:
        raise ValueError("train_fraction must be between 0.50 and 0.80")
    features = build_features(spy, vix)
    if len(features) < 50:
        raise ValueError("at least 50 fully warmed aligned rows are required")
    split_index = int(len(features) * train_fraction)
    if split_index <= 1 or split_index >= len(features):
        raise ValueError("chronological split produced an empty partition")
    train = features.iloc[:split_index].copy()
    holdout = features.iloc[split_index:].copy()
    holdout_identity = {
        "sealed": True,
        "option_outcomes_evaluated": False,
        "start": str(pd.Timestamp(holdout.index[0]).date()),
        "end": str(pd.Timestamp(holdout.index[-1]).date()),
        "n_feature_rows": len(holdout),
        "source_sha256": {
            "spy": spy_provenance.get("sha256"),
            "vix": vix_provenance.get("sha256"),
        },
    }
    candidate = candidate_config()
    control = control_config()
    candidate_blueprints = select_blueprints(train, candidate)
    control_blueprints = select_blueprints(train, control)
    candidate_axes = simulate_axes(train, candidate_blueprints, candidate)
    control_axes = simulate_axes(train, control_blueprints, control)
    regime_contrast = build_regime_contrast(train, candidate)
    train_start = str(pd.Timestamp(train.index[0]).date())
    train_end = str(pd.Timestamp(train.index[-1]).date())
    decision = evaluate_discovery(
        candidate_axes,
        control_axes,
        holdout_identity=holdout_identity,
        regime_contrast=regime_contrast,
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD",
        "paper_only": True,
        "candidate_id": "SPY_INDEX_THETA_CARRY_PCS_21D_V1",
        "family": "SPY_INDEX_THETA_CARRY_REGIME_GATED_21D",
        "economic_mechanism": "broad-index downside-insurance carry conditioned on a lag-safe non-bearish regime",
        "forecast_type": ["non_collapse", "realized_vs_implied_vol"],
        "claim_scope": "L0 discovery only; observed daily VIX-conditioned Black-Scholes proxy marks, synthetic listed Friday and integer strikes, no observed option quotes/fills; cannot earn L1",
        "funnel_stage_before": "F0_MECHANISM",
        "funnel_stage_after": "F1_TRAIN" if decision["pass"] else "F0_MECHANISM",
        "data_provenance": {"spy": spy_provenance, "vix": vix_provenance},
        "partition": {
            "method": "strict chronological 60/40; only train option outcomes evaluated",
            "train_fraction": train_fraction,
            "n_feature_rows": len(features),
            "n_train_rows": len(train),
            "train_start": train_start,
            "train_end": train_end,
            "n_holdout_rows": len(holdout),
        },
        "holdout_identity": holdout_identity,
        "gates": {
            "minimum_completed_trades_each_cost_axis": MIN_TRADES,
            "positive_after_cost_pnl": True,
            "profit_factor_gte": 1.05,
            "max_drawdown_usd": MAX_DD,
            "expected_shortfall_worst_10pct_gte_usd": -MAX_EXPECTED_SHORTFALL_LOSS,
            "one_lot_max_loss_usd": MAX_ONE_LOT_LOSS,
            "path_control_comparison": "diagnostic_only_after_low-density repair",
            "anchored_regime_contrast_minimum_trades_each_regime_cost_axis": MIN_REGIME_CONTRAST_TRADES,
            "non_bearish_worst_axis_average_gt_bearish": True,
            "integrity": True,
        },
        "candidate": {
            "config": candidate,
            "n_blueprints": len(candidate_blueprints),
            "entry_coverage": summarize_entry_coverage(
                candidate_axes,
                train_start=train_start,
                train_end=train_end,
            ),
            "train_axes": candidate_axes,
        },
        "control": {
            "description": "same DNA with bearish signal regimes enabled; retained as a low-density path diagnostic",
            "config": control,
            "n_blueprints": len(control_blueprints),
            "entry_coverage": summarize_entry_coverage(
                control_axes,
                train_start=train_start,
                train_end=train_end,
            ),
            "train_axes": control_axes,
        },
        "regime_contrast": regime_contrast,
        "decision": decision,
        "wake_outcome": "BLOCKER_REMOVED_AND_RETESTED",
        "retest_decision": decision["outcome"],
        "strategy_outcome": decision["outcome"],
        "authority": "research only; no registry, paper, shadow, broker, arm, funding, or live authority",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spy",
        default=".cache/platform/spy_tom_adjusted_20160101_20260714.csv",
    )
    parser.add_argument("--vix", default=".cache/VIX_10y.csv")
    parser.add_argument("--train-fraction", type=float, default=0.60)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    spy, spy_provenance = load_spy(Path(args.spy))
    vix, vix_provenance = load_vix(Path(args.vix))
    payload = run_lab(
        spy,
        vix,
        spy_provenance=spy_provenance,
        vix_provenance=vix_provenance,
        train_fraction=args.train_fraction,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "candidate_id": payload["candidate_id"],
                "strategy_outcome": payload["strategy_outcome"],
                "funnel_stage_after": payload["funnel_stage_after"],
                "decision": payload["decision"],
                "out": str(out),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

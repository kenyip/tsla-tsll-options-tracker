#!/usr/bin/env python3
"""Train-only TSLL-versus-TSLA tracking-dislocation discovery lab."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from scripts.low_hv_cross_section_train_lab import circular_block_bootstrap_lower_bound
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from low_hv_cross_section_train_lab import (  # type: ignore[no-redef]
        circular_block_bootstrap_lower_bound,
    )


def _validate_panel(close_panel: pd.DataFrame) -> pd.DataFrame:
    if close_panel.empty or not {"TSLA", "TSLL"}.issubset(close_panel.columns):
        raise ValueError("close panel must contain TSLA and TSLL")
    prepared = close_panel.loc[:, ["TSLA", "TSLL"]].copy()
    prepared.index = pd.DatetimeIndex(pd.to_datetime(prepared.index)).tz_localize(None).normalize()
    prepared = prepared.apply(pd.to_numeric, errors="coerce")
    values = prepared.to_numpy(dtype=float)
    if (
        not prepared.index.is_unique
        or not prepared.index.is_monotonic_increasing
        or not np.isfinite(values).all()
        or (values <= 0.0).any()
    ):
        raise ValueError("close panel must be increasing, unique, finite, and positive")
    return prepared


def _overlaps(window: tuple[pd.Timestamp, pd.Timestamp], occupied: list[tuple[pd.Timestamp, pd.Timestamp]]) -> bool:
    start, end = window
    return any(not (end < prior_start or start > prior_end) for prior_start, prior_end in occupied)


def build_matched_blueprints(
    close_panel: pd.DataFrame,
    *,
    residual_threshold: float = -0.04,
    neutral_residual_low: float = -0.01,
    neutral_residual_high: float = 0.01,
    feature_sessions: int = 5,
    trend_lookback_sessions: int = 100,
    tsla_return_floor: float = -0.05,
    forward_sessions: int = 5,
    max_match_distance_sessions: int = 63,
    max_tsla_return_distance: float = 0.05,
    max_trend_distance: float = 0.15,
) -> list[dict[str, Any]]:
    """Build non-overlapping treated episodes with earlier outcome-independent controls."""
    panel = _validate_panel(close_panel)
    if feature_sessions < 1 or trend_lookback_sessions < 2 or forward_sessions < 1:
        raise ValueError("feature, trend, and forward sessions must be positive")
    if not neutral_residual_low <= neutral_residual_high:
        raise ValueError("neutral residual bounds are inverted")
    if max_match_distance_sessions < 1:
        raise ValueError("match distance must be positive")

    tsla_return = panel["TSLA"] / panel["TSLA"].shift(feature_sessions) - 1.0
    tsll_return = panel["TSLL"] / panel["TSLL"].shift(feature_sessions) - 1.0
    residual = tsll_return - 2.0 * tsla_return
    sma = panel["TSLA"].rolling(
        trend_lookback_sessions, min_periods=trend_lookback_sessions
    ).mean()
    trend_distance = panel["TSLA"] / sma - 1.0
    features = pd.DataFrame(
        {
            "tsla_return_5d": tsla_return,
            "residual_5d": residual,
            "trend_distance": trend_distance,
        },
        index=panel.index,
    )

    last_signal_position = len(panel) - forward_sessions - 2
    eligible_positions = [
        position
        for position in range(len(panel))
        if position <= last_signal_position
        and np.isfinite(features.iloc[position].to_numpy(dtype=float)).all()
        and features.iloc[position]["trend_distance"] > 0.0
        and features.iloc[position]["tsla_return_5d"] >= tsla_return_floor
    ]
    treated_positions = [
        position
        for position in eligible_positions
        if features.iloc[position]["residual_5d"] <= residual_threshold
    ]
    neutral_positions = [
        position
        for position in eligible_positions
        if neutral_residual_low
        <= features.iloc[position]["residual_5d"]
        <= neutral_residual_high
    ]

    occupied: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    used_control_positions: set[int] = set()
    blueprints: list[dict[str, Any]] = []
    for treated_position in treated_positions:
        treated_window = (
            pd.Timestamp(panel.index[treated_position + 1]),
            pd.Timestamp(panel.index[treated_position + 1 + forward_sessions]),
        )
        if _overlaps(treated_window, occupied):
            continue
        treated_feature = features.iloc[treated_position]
        candidates: list[tuple[float, int]] = []
        for control_position in neutral_positions:
            if control_position >= treated_position or control_position in used_control_positions:
                continue
            calendar_distance = treated_position - control_position
            if calendar_distance > max_match_distance_sessions:
                continue
            control_window = (
                pd.Timestamp(panel.index[control_position + 1]),
                pd.Timestamp(panel.index[control_position + 1 + forward_sessions]),
            )
            if _overlaps(control_window, occupied) or _overlaps(control_window, [treated_window]):
                continue
            if occupied and control_window[0] <= max(end for _, end in occupied):
                continue
            control_feature = features.iloc[control_position]
            return_distance = abs(
                float(treated_feature["tsla_return_5d"])
                - float(control_feature["tsla_return_5d"])
            )
            trend_gap = abs(
                float(treated_feature["trend_distance"])
                - float(control_feature["trend_distance"])
            )
            if return_distance > max_tsla_return_distance or trend_gap > max_trend_distance:
                continue
            score = (
                return_distance / max_tsla_return_distance
                + trend_gap / max_trend_distance
                + calendar_distance / max_match_distance_sessions
            )
            candidates.append((float(score), control_position))
        if not candidates:
            continue
        _, control_position = min(candidates, key=lambda item: (item[0], -item[1]))
        control_window = (
            pd.Timestamp(panel.index[control_position + 1]),
            pd.Timestamp(panel.index[control_position + 1 + forward_sessions]),
        )
        control_feature = features.iloc[control_position]
        blueprints.append(
            {
                "treated_signal_date": pd.Timestamp(panel.index[treated_position]),
                "treated_entry_date": treated_window[0],
                "treated_exit_date": treated_window[1],
                "treated_residual_5d": float(treated_feature["residual_5d"]),
                "treated_tsla_return_5d": float(treated_feature["tsla_return_5d"]),
                "treated_trend_distance": float(treated_feature["trend_distance"]),
                "control_signal_date": pd.Timestamp(panel.index[control_position]),
                "control_entry_date": control_window[0],
                "control_exit_date": control_window[1],
                "control_residual_5d": float(control_feature["residual_5d"]),
                "control_tsla_return_5d": float(control_feature["tsla_return_5d"]),
                "control_trend_distance": float(control_feature["trend_distance"]),
                "calendar_distance_sessions": int(treated_position - control_position),
                "tsla_return_match_distance": abs(
                    float(treated_feature["tsla_return_5d"])
                    - float(control_feature["tsla_return_5d"])
                ),
                "trend_match_distance": abs(
                    float(treated_feature["trend_distance"])
                    - float(control_feature["trend_distance"])
                ),
            }
        )
        used_control_positions.add(control_position)
        occupied.extend([control_window, treated_window])
    return blueprints


def evaluate_train_partition(
    close_panel: pd.DataFrame,
    train_blueprints: list[dict[str, Any]],
    *,
    min_pairs: int = 20,
    round_trip_cost_bps: float = 20.0,
    bootstrap_samples: int = 10_000,
    residual_threshold: float = -0.04,
    neutral_residual_low: float = -0.01,
    neutral_residual_high: float = 0.01,
    max_match_distance_sessions: int = 63,
    max_tsla_return_distance: float = 0.05,
    max_trend_distance: float = 0.15,
) -> dict[str, Any]:
    """Evaluate only the train pairs against the frozen discovery falsifier."""
    panel = _validate_panel(close_panel)
    if min_pairs < 1 or not train_blueprints:
        raise ValueError("non-empty train blueprints and positive min_pairs are required")
    if not np.isfinite(round_trip_cost_bps) or round_trip_cost_bps < 0.0:
        raise ValueError("round-trip cost bps must be finite and non-negative")
    cost_fraction = float(round_trip_cost_bps) / 10_000.0
    rows: list[dict[str, Any]] = []
    occupied: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    controls: set[pd.Timestamp] = set()
    violations: list[str] = []

    for index, blueprint in enumerate(train_blueprints):
        control_signal = pd.Timestamp(blueprint["control_signal_date"])
        control_entry = pd.Timestamp(blueprint["control_entry_date"])
        control_exit = pd.Timestamp(blueprint["control_exit_date"])
        treated_signal = pd.Timestamp(blueprint["treated_signal_date"])
        treated_entry = pd.Timestamp(blueprint["treated_entry_date"])
        treated_exit = pd.Timestamp(blueprint["treated_exit_date"])
        if not (
            control_signal < control_entry < control_exit <= treated_signal
            and treated_signal < treated_entry < treated_exit
        ):
            violations.append(f"chronology:{index}")
        windows = [(control_entry, control_exit), (treated_entry, treated_exit)]
        if any(_overlaps(window, occupied) for window in windows):
            violations.append(f"overlap:{index}")
        occupied.extend(windows)
        if control_signal in controls:
            violations.append(f"control_reuse:{index}")
        controls.add(control_signal)
        if float(blueprint["treated_residual_5d"]) > residual_threshold:
            violations.append(f"treated_residual:{index}")
        control_residual = float(blueprint["control_residual_5d"])
        if not neutral_residual_low <= control_residual <= neutral_residual_high:
            violations.append(f"control_residual:{index}")
        if int(blueprint["calendar_distance_sessions"]) > max_match_distance_sessions:
            violations.append(f"calendar_distance:{index}")
        if float(blueprint["tsla_return_match_distance"]) > max_tsla_return_distance:
            violations.append(f"return_distance:{index}")
        if float(blueprint["trend_match_distance"]) > max_trend_distance:
            violations.append(f"trend_distance:{index}")
        required_dates = {control_entry, control_exit, treated_entry, treated_exit}
        if not required_dates.issubset(set(panel.index)):
            raise ValueError(f"blueprint {index} dates are outside the close panel")
        treated_return = (
            float(panel.loc[treated_exit, "TSLL"] / panel.loc[treated_entry, "TSLL"] - 1.0)
            - cost_fraction
        )
        control_return = (
            float(panel.loc[control_exit, "TSLL"] / panel.loc[control_entry, "TSLL"] - 1.0)
            - cost_fraction
        )
        rows.append(
            {
                "control_signal_date": str(control_signal.date()),
                "control_entry_date": str(control_entry.date()),
                "control_exit_date": str(control_exit.date()),
                "treated_signal_date": str(treated_signal.date()),
                "treated_entry_date": str(treated_entry.date()),
                "treated_exit_date": str(treated_exit.date()),
                "treated_return_after_cost": treated_return,
                "control_return_after_cost": control_return,
                "paired_excess_return": treated_return - control_return,
                "treated_residual_5d": float(blueprint["treated_residual_5d"]),
                "control_residual_5d": control_residual,
                "calendar_distance_sessions": int(blueprint["calendar_distance_sessions"]),
                "tsla_return_match_distance": float(
                    blueprint["tsla_return_match_distance"]
                ),
                "trend_match_distance": float(blueprint["trend_match_distance"]),
            }
        )

    treated_values = np.asarray([row["treated_return_after_cost"] for row in rows])
    control_values = np.asarray([row["control_return_after_cost"] for row in rows])
    excess = treated_values - control_values
    lower_bound = circular_block_bootstrap_lower_bound(
        excess,
        samples=bootstrap_samples,
        seed=20260715,
    )
    gate_checks = {
        "minimum_train_pairs": len(rows) >= min_pairs,
        "positive_treated_mean_after_cost": float(treated_values.mean()) > 0.0,
        "positive_paired_excess_mean": float(excess.mean()) > 0.0,
        "paired_excess_bootstrap_lb90_positive": lower_bound > 0.0,
        "zero_integrity_violations": not violations,
    }
    return {
        "n_pairs": len(rows),
        "round_trip_cost_bps": float(round_trip_cost_bps),
        "treated_mean_return_after_cost": float(treated_values.mean()),
        "control_mean_return_after_cost": float(control_values.mean()),
        "paired_excess_mean": float(excess.mean()),
        "paired_excess_median": float(np.median(excess)),
        "paired_excess_positive_frequency": float(np.mean(excess > 0.0)),
        "paired_excess_bootstrap_lb90": lower_bound,
        "bootstrap_samples": int(bootstrap_samples),
        "bootstrap_block_length": 3,
        "max_calendar_distance_sessions": max(
            int(row["calendar_distance_sessions"]) for row in rows
        ),
        "max_tsla_return_match_distance": max(
            float(row["tsla_return_match_distance"]) for row in rows
        ),
        "max_trend_match_distance": max(float(row["trend_match_distance"]) for row in rows),
        "integrity_violations": violations,
        "gate_checks": gate_checks,
        "gate_pass": bool(all(gate_checks.values())),
        "pairs": rows,
    }


def split_blueprints(
    blueprints: list[dict[str, Any]], *, train_fraction: float = 0.60
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0.50 <= float(train_fraction) <= 0.80:
        raise ValueError("train_fraction must be between 0.50 and 0.80")
    if len(blueprints) < 2:
        raise ValueError("at least two matched blueprints are required")
    ordered = sorted(blueprints, key=lambda row: pd.Timestamp(row["treated_signal_date"]))
    split = int(len(ordered) * train_fraction)
    train, holdout = ordered[:split], ordered[split:]
    if not train or not holdout:
        raise ValueError("train and untouched holdout must both be non-empty")
    train_last_exit = max(
        max(pd.Timestamp(row["control_exit_date"]), pd.Timestamp(row["treated_exit_date"]))
        for row in train
    )
    holdout_first_entry = min(
        min(pd.Timestamp(row["control_entry_date"]), pd.Timestamp(row["treated_entry_date"]))
        for row in holdout
    )
    if train_last_exit >= holdout_first_entry:
        raise ValueError("train and untouched holdout pair windows must be strictly chronological")
    return train, holdout


def selection_diagnostics(
    close_panel: pd.DataFrame,
    *,
    matched_blueprints: int,
    residual_threshold: float,
    neutral_residual_low: float,
    neutral_residual_high: float,
    feature_sessions: int,
    trend_lookback_sessions: int,
    tsla_return_floor: float,
    forward_sessions: int,
) -> dict[str, Any]:
    panel = _validate_panel(close_panel)
    tsla_return = panel["TSLA"] / panel["TSLA"].shift(feature_sessions) - 1.0
    residual = panel["TSLL"] / panel["TSLL"].shift(feature_sessions) - 1.0 - 2.0 * tsla_return
    trend = panel["TSLA"] / panel["TSLA"].rolling(
        trend_lookback_sessions, min_periods=trend_lookback_sessions
    ).mean() - 1.0
    has_forward = pd.Series(False, index=panel.index)
    if len(panel) > forward_sessions + 1:
        has_forward.iloc[: -(forward_sessions + 1)] = True
    eligible = (
        tsla_return.notna()
        & residual.notna()
        & trend.notna()
        & (trend > 0.0)
        & (tsla_return >= tsla_return_floor)
        & has_forward
    )
    eligible_residuals = residual[eligible]
    treated = eligible & (residual <= residual_threshold)
    neutral = eligible & residual.between(neutral_residual_low, neutral_residual_high)
    return {
        "eligible_signal_dates": int(eligible.sum()),
        "treated_signal_candidates": int(treated.sum()),
        "neutral_control_candidates": int(neutral.sum()),
        "matched_blueprints": int(matched_blueprints),
        "eligible_residual_min": (
            float(eligible_residuals.min()) if not eligible_residuals.empty else None
        ),
        "eligible_residual_p01": (
            float(eligible_residuals.quantile(0.01)) if not eligible_residuals.empty else None
        ),
        "eligible_residual_p05": (
            float(eligible_residuals.quantile(0.05)) if not eligible_residuals.empty else None
        ),
    }


def run_lab_from_panel(
    close_panel: pd.DataFrame,
    *,
    provenance: dict[str, Any],
    train_fraction: float = 0.60,
    residual_threshold: float = -0.04,
    neutral_residual_low: float = -0.01,
    neutral_residual_high: float = 0.01,
    feature_sessions: int = 5,
    trend_lookback_sessions: int = 100,
    tsla_return_floor: float = -0.05,
    forward_sessions: int = 5,
    max_match_distance_sessions: int = 63,
    max_tsla_return_distance: float = 0.05,
    max_trend_distance: float = 0.15,
    min_train_pairs: int = 20,
    round_trip_cost_bps: float = 20.0,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    panel = _validate_panel(close_panel)
    blueprints = build_matched_blueprints(
        panel,
        residual_threshold=residual_threshold,
        neutral_residual_low=neutral_residual_low,
        neutral_residual_high=neutral_residual_high,
        feature_sessions=feature_sessions,
        trend_lookback_sessions=trend_lookback_sessions,
        tsla_return_floor=tsla_return_floor,
        forward_sessions=forward_sessions,
        max_match_distance_sessions=max_match_distance_sessions,
        max_tsla_return_distance=max_tsla_return_distance,
        max_trend_distance=max_trend_distance,
    )
    diagnostics = selection_diagnostics(
        panel,
        matched_blueprints=len(blueprints),
        residual_threshold=residual_threshold,
        neutral_residual_low=neutral_residual_low,
        neutral_residual_high=neutral_residual_high,
        feature_sessions=feature_sessions,
        trend_lookback_sessions=trend_lookback_sessions,
        tsla_return_floor=tsla_return_floor,
        forward_sessions=forward_sessions,
    )
    if len(blueprints) < 2:
        train, holdout = blueprints, []
        train_result = {
            "n_pairs": len(train),
            "round_trip_cost_bps": float(round_trip_cost_bps),
            "treated_mean_return_after_cost": None,
            "control_mean_return_after_cost": None,
            "paired_excess_mean": None,
            "paired_excess_median": None,
            "paired_excess_positive_frequency": None,
            "paired_excess_bootstrap_lb90": None,
            "bootstrap_samples": int(bootstrap_samples),
            "bootstrap_block_length": 3,
            "max_calendar_distance_sessions": None,
            "max_tsla_return_match_distance": None,
            "max_trend_match_distance": None,
            "integrity_violations": [],
            "gate_checks": {
                "minimum_train_pairs": False,
                "positive_treated_mean_after_cost": False,
                "positive_paired_excess_mean": False,
                "paired_excess_bootstrap_lb90_positive": False,
                "zero_integrity_violations": True,
            },
            "gate_pass": False,
            "pairs": [],
        }
    else:
        train, holdout = split_blueprints(blueprints, train_fraction=train_fraction)
        train_result = evaluate_train_partition(
            panel,
            train,
            min_pairs=min_train_pairs,
            round_trip_cost_bps=round_trip_cost_bps,
            bootstrap_samples=bootstrap_samples,
            residual_threshold=residual_threshold,
            neutral_residual_low=neutral_residual_low,
            neutral_residual_high=neutral_residual_high,
            max_match_distance_sessions=max_match_distance_sessions,
            max_tsla_return_distance=max_tsla_return_distance,
            max_trend_distance=max_trend_distance,
        )
    advanced = bool(train_result["gate_pass"])
    failed_checks = [name for name, passed in train_result["gate_checks"].items() if not passed]
    if diagnostics["treated_signal_candidates"] == 0:
        failure_mechanism = (
            "no eligible treated signals met the frozen -4% five-session tracking-shortfall "
            "threshold under the positive fully warmed TSLA trend filter"
        )
    elif diagnostics["matched_blueprints"] == 0:
        failure_mechanism = (
            "eligible treated signals existed but none admitted an earlier neutral-residual "
            "control inside the frozen match bounds and disjoint chronology"
        )
    elif int(train_result["n_pairs"]) < min_train_pairs:
        failure_mechanism = (
            f"only {train_result['n_pairs']} chronological train pairs survived versus the "
            f"predeclared minimum {min_train_pairs}"
        )
    else:
        failure_mechanism = "frozen train gate failed: " + ", ".join(failed_checks)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD_L0_UNDERLYING_DISCOVERY",
        "paper_only": True,
        "sleeve_usd": 3000.0,
        "candidate_id": "TSLL_RELATIVE_DISLOCATION_BULL_CALL_14D_V1",
        "mechanism_family": "TSLL_TSLA_5D_TRACKING_SHORTFALL_REBOUND",
        "economic_mechanism": (
            "a path-dependent five-session TSLL tracking shortfall versus twice TSLA's return "
            "may be a transient leveraged-ETF rebalance/noise dislocation when TSLA remains in "
            "a positive fully warmed trend"
        ),
        "candidate_or_family_scope": (
            "TSLL five-session return minus twice TSLA five-session return at or below -4%, "
            "TSLA above fully warmed SMA100 and five-session return at least -5%, next-session "
            "entry, five-session hold, and earlier neutral-residual matched controls"
        ),
        "funnel_stage_before": "F0_MECHANISM",
        "funnel_stage_after": "F1_TRAIN" if advanced else "F0_MECHANISM",
        "falsifier": (
            "fewer than 20 chronological matched train pairs, any integrity or frozen match-bound "
            "violation, non-positive treated mean after 20-bps underlying round-trip sensitivity, "
            "non-positive paired excess, or non-positive one-sided 90% circular-block-bootstrap "
            "lower bound closes the exact family"
        ),
        "claim_scope": (
            "split/dividend-adjusted TSLA/TSLL underlying closes only; train-only L0 discovery; "
            "no option marks, option costs, fills, L1, capital seat, or paper eligibility claim"
        ),
        "all_train_rows_are_inspected_development_data": True,
        "f2_or_l1_claim": False,
        "config": {
            "symbols": ["TSLA", "TSLL"],
            "feature_sessions": feature_sessions,
            "residual_threshold": residual_threshold,
            "neutral_residual_bounds": [neutral_residual_low, neutral_residual_high],
            "trend_lookback_sessions": trend_lookback_sessions,
            "tsla_return_floor": tsla_return_floor,
            "forward_sessions": forward_sessions,
            "train_fraction": train_fraction,
            "minimum_train_pairs": min_train_pairs,
            "round_trip_cost_bps": round_trip_cost_bps,
            "max_match_distance_sessions": max_match_distance_sessions,
            "max_tsla_return_distance": max_tsla_return_distance,
            "max_trend_distance": max_trend_distance,
            "bootstrap_confidence": 0.90,
            "bootstrap_samples": bootstrap_samples,
            "bootstrap_block_length": 3,
            "controls_prior_only": True,
            "matched_without_replacement": True,
            "non_overlapping_pair_windows": True,
        },
        "data_provenance": provenance,
        "selection_diagnostics": diagnostics,
        "population_validity": {
            "population_type": "fixed TSLA/TSLL economic pair from TSLL availability",
            "population_pure": True,
            "ranking_complete": True,
            "survivorship_bias": True,
            "listing_bias": True,
            "generalization_allowed": False,
        },
        "train": train_result,
        "untouched_holdout": {
            "n_blueprints": len(holdout),
            "first_control_signal_date": (
                str(pd.Timestamp(holdout[0]["control_signal_date"]).date())
                if holdout
                else None
            ),
            "first_treated_signal_date": (
                str(pd.Timestamp(holdout[0]["treated_signal_date"]).date())
                if holdout
                else None
            ),
            "last_treated_exit_date": (
                str(pd.Timestamp(holdout[-1]["treated_exit_date"]).date())
                if holdout
                else None
            ),
            "outcome_metrics_read": False,
            "simulation_run": False,
        },
        "option_stage": {
            "status": "NOT_RUN_PENDING_UNTOUCHED_HOLDOUT" if advanced else "NOT_RUN_TRAIN_GATE_FAILED",
            "pricing_run": False,
            "pricing_calls": 0,
            "planned_structure": "bull_call_debit_spread",
            "planned_dte": 14,
            "planned_width_usd": 1.0,
            "option_mark_provenance": None,
        },
        "structure": "conditional_bull_call_debit_spread_not_yet_priced",
        "capital_fit_usd": 100.0,
        "one_lot_max_loss_usd": 100.0,
        "max_loss_usd": 100.0,
        "max_lots": 1,
        "capital_basis": (
            "structural upper bound for a future $1-wide debit vertical before closing friction; "
            "not an observed or simulated trade loss"
        ),
        "strategy_outcome": "STRATEGY_ADVANCED" if advanced else "FAMILY_CLOSED",
        "decision": (
            "ADVANCE_TSLL_TRACKING_SHORTFALL_REBOUND_TO_F1_TRAIN"
            if advanced
            else "CLOSE_TSLL_TRACKING_SHORTFALL_REBOUND_TRAIN_FAMILY"
        ),
        "closed_family": None if advanced else "TSLL_TSLA_5D_TRACKING_SHORTFALL_REBOUND",
        "dominant_failure_mechanism": (
            None if advanced else failure_mechanism
        ),
        "registration_eligible": False,
        "authority": "research only; no registry, paper, shadow, funding, broker, arm, or live authority",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2022-08-01")
    parser.add_argument("--end", default="2026-07-15")
    parser.add_argument(
        "--cache-dir", default=".cache/platform/tsll_tracking_dislocation"
    )
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    try:
        from scripts.low_hv_cross_section_train_lab import load_adjusted_history
    except ModuleNotFoundError as exc:
        if exc.name != "scripts":
            raise
        from low_hv_cross_section_train_lab import (  # type: ignore[no-redef]
            load_adjusted_history,
        )

    histories: dict[str, pd.Series] = {}
    sources: dict[str, Any] = {}
    for symbol in ("TSLA", "TSLL"):
        history, source = load_adjusted_history(
            symbol,
            cache_dir=Path(args.cache_dir),
            start=args.start,
            end=args.end,
        )
        histories[symbol] = history
        sources[symbol] = source
    panel = pd.concat(
        [histories["TSLA"], histories["TSLL"]], axis=1, join="inner"
    ).dropna()
    panel.columns = ["TSLA", "TSLL"]
    payload = run_lab_from_panel(
        panel,
        provenance={
            "sources": sources,
            "common_panel": {
                "rows": int(len(panel)),
                "start": str(panel.index[0].date()),
                "end": str(panel.index[-1].date()),
                "join": "inner join on trading dates; no forward fill",
            },
        },
        bootstrap_samples=args.bootstrap_samples,
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
                "decision": payload["decision"],
                "funnel_stage_after": payload["funnel_stage_after"],
                "train_gate_pass": payload["train"]["gate_pass"],
                "train_n": payload["train"]["n_pairs"],
                "treated_mean_after_cost": payload["train"][
                    "treated_mean_return_after_cost"
                ],
                "paired_excess_mean": payload["train"]["paired_excess_mean"],
                "paired_excess_bootstrap_lb90": payload["train"][
                    "paired_excess_bootstrap_lb90"
                ],
                "out": str(out),
            },
            indent=2,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

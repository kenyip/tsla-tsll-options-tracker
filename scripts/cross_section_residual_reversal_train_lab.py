#!/usr/bin/env python3
"""Train-only cross-sectional five-session residual-reversal discovery lab.

BUILD/L0 only. The lab tests whether extreme liquid-stock peer underperformance
mean-reverts over five completed sessions. The final chronological 40% remains
outcome-unread and no option pricing is performed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from scripts.low_hv_cross_section_train_lab import (
        assemble_close_panel,
        circular_block_bootstrap_lower_bound,
        load_adjusted_history,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from low_hv_cross_section_train_lab import (  # type: ignore[no-redef]
        assemble_close_panel,
        circular_block_bootstrap_lower_bound,
        load_adjusted_history,
    )

DEFAULT_SYMBOLS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "AMD",
    "NFLX",
    "TSLA",
    "AVGO",
    "MU",
    "JPM",
    "XOM",
    "BAC",
]
CANDIDATE_ID = "CROSS_SECTION_RESIDUAL_REVERSAL_BULL_CALL_21D_V1"
FAMILY_ID = "CROSS_SECTION_FIVE_SESSION_RESIDUAL_REVERSAL"


def _validate_panel(close_panel: pd.DataFrame) -> pd.DataFrame:
    if close_panel.empty or close_panel.shape[1] < 6:
        raise ValueError("close panel must contain at least six symbols")
    panel = close_panel.copy()
    panel.index = pd.DatetimeIndex(pd.to_datetime(panel.index)).tz_localize(None).normalize()
    panel.columns = [str(column).strip().upper() for column in panel.columns]
    panel = panel.apply(pd.to_numeric, errors="coerce")
    values = panel.to_numpy(dtype=float)
    if (
        not panel.index.is_unique
        or not panel.index.is_monotonic_increasing
        or len(set(panel.columns)) != len(panel.columns)
        or not np.isfinite(values).all()
        or (values <= 0.0).any()
    ):
        raise ValueError("close panel must be unique, increasing, finite, and positive")
    return panel


def _overlaps(
    window: tuple[pd.Timestamp, pd.Timestamp],
    occupied: list[tuple[pd.Timestamp, pd.Timestamp]],
) -> bool:
    start, end = window
    return any(not (end < prior_start or start > prior_end) for prior_start, prior_end in occupied)


def build_residual_reversal_blueprints(
    close_panel: pd.DataFrame,
    *,
    feature_sessions: int = 5,
    forward_sessions: int = 5,
    rebalance_sessions: int = 5,
    group_size: int = 3,
    treated_mean_residual_max: float = -0.04,
) -> list[dict[str, Any]]:
    """Freeze prior-close ranks and reserve globally non-overlapping episodes."""
    panel = _validate_panel(close_panel)
    if min(feature_sessions, forward_sessions, rebalance_sessions, group_size) < 1:
        raise ValueError("lookbacks, horizon, rebalance, and group size must be positive")
    if 2 * group_size > panel.shape[1]:
        raise ValueError("treated and control groups must be disjoint")
    if not np.isfinite(treated_mean_residual_max) or treated_mean_residual_max >= 0.0:
        raise ValueError("treated residual threshold must be finite and negative")

    blueprints: list[dict[str, Any]] = []
    occupied: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    last_signal_position = len(panel) - forward_sessions - 2
    for signal_position in range(feature_sessions, last_signal_position + 1, rebalance_sessions):
        feature_start_position = signal_position - feature_sessions
        entry_position = signal_position + 1
        exit_position = entry_position + forward_sessions
        entry_window = (
            pd.Timestamp(panel.index[entry_position]),
            pd.Timestamp(panel.index[exit_position]),
        )
        if _overlaps(entry_window, occupied):
            continue
        returns = panel.iloc[signal_position] / panel.iloc[feature_start_position] - 1.0
        median_return = float(returns.median())
        residuals = returns - median_return
        if not np.isfinite(residuals.to_numpy(dtype=float)).all():
            continue
        ordered = sorted(
            ((float(value), str(symbol)) for symbol, value in residuals.items()),
            key=lambda item: (item[0], item[1]),
        )
        treated = [symbol for _, symbol in ordered[:group_size]]
        treated_set = set(treated)
        controls = [
            symbol
            for _, symbol in sorted(
                ((abs(float(value)), str(symbol)) for symbol, value in residuals.items()),
                key=lambda item: (item[0], item[1]),
            )
            if symbol not in treated_set
        ][:group_size]
        treated_mean = float(residuals[treated].mean())
        if treated_mean > treated_mean_residual_max:
            continue
        blueprints.append(
            {
                "feature_start_date": pd.Timestamp(panel.index[feature_start_position]),
                "feature_max_date": pd.Timestamp(panel.index[signal_position]),
                "signal_date": pd.Timestamp(panel.index[signal_position]),
                "entry_date": entry_window[0],
                "exit_date": entry_window[1],
                "treated_symbols": treated,
                "control_symbols": controls,
                "peer_median_feature_return": median_return,
                "treated_residuals": {symbol: float(residuals[symbol]) for symbol in treated},
                "control_residuals": {symbol: float(residuals[symbol]) for symbol in controls},
                "treated_mean_residual": treated_mean,
            }
        )
        occupied.append(entry_window)
    return blueprints


def _worst_decile_mean(values: np.ndarray) -> tuple[float, int]:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or not len(vector) or not np.isfinite(vector).all():
        raise ValueError("worst-decile input must be non-empty and finite")
    count = max(1, int(np.ceil(0.10 * len(vector))))
    return float(np.sort(vector)[:count].mean()), count


def evaluate_train_partition(
    close_panel: pd.DataFrame,
    train_blueprints: list[dict[str, Any]],
    *,
    feature_sessions: int = 5,
    forward_sessions: int = 5,
    group_size: int = 3,
    treated_mean_residual_max: float = -0.04,
    min_episodes: int = 40,
    min_signal_years: int = 8,
    round_trip_cost_bps: float = 20.0,
    min_paired_excess_mean: float = 0.0025,
    min_positive_frequency: float = 0.55,
    minimum_tail_return: float = -0.05,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    panel = _validate_panel(close_panel)
    if not train_blueprints or min(min_episodes, min_signal_years, bootstrap_samples) < 1:
        raise ValueError("non-empty train blueprints and positive gates are required")
    if not np.isfinite(round_trip_cost_bps) or round_trip_cost_bps < 0.0:
        raise ValueError("round-trip cost must be finite and non-negative")
    cost = float(round_trip_cost_bps) / 10_000.0
    occupied: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    violations: list[str] = []
    rows: list[dict[str, Any]] = []

    for index, blueprint in enumerate(train_blueprints):
        feature_start = pd.Timestamp(blueprint["feature_start_date"])
        feature_max = pd.Timestamp(blueprint["feature_max_date"])
        signal = pd.Timestamp(blueprint["signal_date"])
        entry = pd.Timestamp(blueprint["entry_date"])
        exit_date = pd.Timestamp(blueprint["exit_date"])
        treated = [str(symbol).upper() for symbol in blueprint["treated_symbols"]]
        controls = [str(symbol).upper() for symbol in blueprint["control_symbols"]]
        window = (entry, exit_date)
        required_dates = {feature_start, feature_max, signal, entry, exit_date}
        if not (feature_start < feature_max == signal < entry < exit_date):
            violations.append(f"chronology:{index}")
        if _overlaps(window, occupied):
            violations.append(f"overlap:{index}")
        occupied.append(window)
        if len(treated) != group_size or len(controls) != group_size or set(treated) & set(controls):
            violations.append(f"groups:{index}")
        missing = sorted((set(treated) | set(controls)) - set(panel.columns))
        if missing or not required_dates.issubset(set(panel.index)):
            raise ValueError(f"blueprint {index} is outside the panel: {missing}")
        feature_position_gap = int(panel.index.get_loc(feature_max)) - int(
            panel.index.get_loc(feature_start)
        )
        outcome_position_gap = int(panel.index.get_loc(exit_date)) - int(panel.index.get_loc(entry))
        if feature_position_gap != feature_sessions or outcome_position_gap != forward_sessions:
            violations.append(f"horizon:{index}")

        feature_returns = panel.loc[feature_max] / panel.loc[feature_start] - 1.0
        median_return = float(feature_returns.median())
        residuals = feature_returns - median_return
        recomputed_treated_mean = float(residuals[treated].mean())
        if recomputed_treated_mean > treated_mean_residual_max + 1e-12:
            violations.append(f"threshold:{index}")
        if not np.isclose(
            recomputed_treated_mean,
            float(blueprint["treated_mean_residual"]),
            rtol=0.0,
            atol=1e-12,
        ):
            violations.append(f"serialized_feature:{index}")
        ordered_treated = [
            symbol
            for _, symbol in sorted(
                ((float(value), str(symbol)) for symbol, value in residuals.items()),
                key=lambda item: (item[0], item[1]),
            )[:group_size]
        ]
        treated_set = set(ordered_treated)
        ordered_controls = [
            symbol
            for _, symbol in sorted(
                ((abs(float(value)), str(symbol)) for symbol, value in residuals.items()),
                key=lambda item: (item[0], item[1]),
            )
            if symbol not in treated_set
        ][:group_size]
        if treated != ordered_treated or controls != ordered_controls:
            violations.append(f"ranking:{index}")

        treated_return = float((panel.loc[exit_date, treated] / panel.loc[entry, treated] - 1.0).mean()) - cost
        control_return = float((panel.loc[exit_date, controls] / panel.loc[entry, controls] - 1.0).mean()) - cost
        rows.append(
            {
                "feature_start_date": str(feature_start.date()),
                "signal_date": str(signal.date()),
                "entry_date": str(entry.date()),
                "exit_date": str(exit_date.date()),
                "treated_symbols": treated,
                "control_symbols": controls,
                "treated_mean_residual": recomputed_treated_mean,
                "treated_return_after_cost": treated_return,
                "control_return_after_cost": control_return,
                "paired_excess_return": treated_return - control_return,
            }
        )

    treated_values = np.asarray([row["treated_return_after_cost"] for row in rows], dtype=float)
    control_values = np.asarray([row["control_return_after_cost"] for row in rows], dtype=float)
    excess = treated_values - control_values
    lower_bound = circular_block_bootstrap_lower_bound(
        excess,
        block_length=3,
        samples=bootstrap_samples,
        seed=20260715,
    )
    signal_years = sorted({pd.Timestamp(row["signal_date"]).year for row in rows})
    tail, tail_count = _worst_decile_mean(treated_values)
    treated_mean = float(treated_values.mean())
    control_mean = float(control_values.mean())
    paired_mean = float(excess.mean())
    positive_frequency = float(np.mean(treated_values > 0.0))
    gate_checks = {
        "minimum_train_episodes": len(rows) >= min_episodes,
        "minimum_signal_years": len(signal_years) >= min_signal_years,
        "positive_treated_mean_after_cost": treated_mean > 0.0,
        "paired_excess_mean_at_least_0_25pct": paired_mean >= min_paired_excess_mean,
        "paired_excess_bootstrap_lb90_positive": lower_bound > 0.0,
        "treated_positive_frequency_at_least_55pct": positive_frequency >= min_positive_frequency,
        "treated_worst_decile_at_least_negative_5pct": tail >= minimum_tail_return,
        "treated_mean_above_neutral_control": treated_mean > control_mean,
        "zero_integrity_violations": not violations,
    }
    return {
        "n_episodes": len(rows),
        "signal_years": signal_years,
        "signal_year_counts": {
            str(year): sum(pd.Timestamp(row["signal_date"]).year == year for row in rows)
            for year in signal_years
        },
        "round_trip_underlying_cost_bps_per_group_member": float(round_trip_cost_bps),
        "treated_mean_return_after_cost": treated_mean,
        "control_mean_return_after_cost": control_mean,
        "treated_positive_frequency_after_cost": positive_frequency,
        "paired_excess_mean": paired_mean,
        "paired_excess_median": float(np.median(excess)),
        "paired_excess_positive_frequency": float(np.mean(excess > 0.0)),
        "paired_excess_bootstrap_lb90": lower_bound,
        "treated_worst_decile_return_after_cost": tail,
        "worst_decile_n": tail_count,
        "bootstrap_samples": int(bootstrap_samples),
        "bootstrap_block_length_episodes": 3,
        "integrity_violations": violations,
        "gate_checks": gate_checks,
        "gate_pass": bool(all(gate_checks.values())),
        "episodes": rows,
    }


def _split_blueprints(
    blueprints: list[dict[str, Any]], *, train_fraction: float
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0.50 <= train_fraction <= 0.80:
        raise ValueError("train fraction must be between 0.50 and 0.80")
    if len(blueprints) < 2:
        raise ValueError("at least two blueprints are required")
    ordered = sorted(blueprints, key=lambda row: pd.Timestamp(row["signal_date"]))
    split = int(len(ordered) * train_fraction)
    train, holdout = ordered[:split], ordered[split:]
    if not train or not holdout:
        raise ValueError("train and holdout must both be non-empty")
    if pd.Timestamp(train[-1]["signal_date"]) >= pd.Timestamp(holdout[0]["signal_date"]):
        raise ValueError("train and holdout must be strictly chronological")
    return train, holdout


def _holdout_identity(blueprints: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [
        {
            "feature_start_date": str(pd.Timestamp(row["feature_start_date"]).date()),
            "signal_date": str(pd.Timestamp(row["signal_date"]).date()),
            "entry_date": str(pd.Timestamp(row["entry_date"]).date()),
            "exit_date": str(pd.Timestamp(row["exit_date"]).date()),
            "treated_symbols": list(row["treated_symbols"]),
            "control_symbols": list(row["control_symbols"]),
        }
        for row in blueprints
    ]
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "n_frozen_blueprints": len(rows),
        "first_signal_date": rows[0]["signal_date"],
        "last_signal_date": rows[-1]["signal_date"],
        "last_exit_date": rows[-1]["exit_date"],
        "identity_sha256": hashlib.sha256(encoded).hexdigest(),
        "outcome_metrics_read": False,
        "simulation_run": False,
    }


def _dominant_failure(failed_gates: list[str]) -> str:
    if "treated_worst_decile_at_least_negative_5pct" in failed_gates:
        return (
            "mechanism-specific left-tail failure: average recovery can coexist with continued "
            "idiosyncratic selloffs, and the frozen treated-basket worst-decile loss breached the -5% gate"
        )
    if any("paired_excess" in gate or "treated_mean_above" in gate for gate in failed_gates):
        return (
            "mechanism-specific control failure: extreme five-session peer laggards did not establish "
            "the frozen magnitude-and-uncertainty-bounded recovery edge over same-date neutral residuals"
        )
    if failed_gates:
        return "frozen train gate failure(s): " + ", ".join(failed_gates)
    return "none; every frozen train gate passed"


def run_lab_from_panel(
    close_panel: pd.DataFrame,
    *,
    symbols: list[str],
    provenance: dict[str, Any],
    frozen_blueprints: list[dict[str, Any]] | None = None,
    train_fraction: float = 0.60,
    feature_sessions: int = 5,
    forward_sessions: int = 5,
    rebalance_sessions: int = 5,
    group_size: int = 3,
    treated_mean_residual_max: float = -0.04,
    min_episodes: int = 40,
    min_signal_years: int = 8,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    panel = _validate_panel(close_panel)
    normalized = [str(symbol).strip().upper() for symbol in symbols]
    if normalized != list(panel.columns) or len(normalized) != len(set(normalized)):
        raise ValueError("symbols must exactly match ordered close-panel columns")
    blueprints = (
        build_residual_reversal_blueprints(
            panel,
            feature_sessions=feature_sessions,
            forward_sessions=forward_sessions,
            rebalance_sessions=rebalance_sessions,
            group_size=group_size,
            treated_mean_residual_max=treated_mean_residual_max,
        )
        if frozen_blueprints is None
        else list(frozen_blueprints)
    )
    train, holdout = _split_blueprints(blueprints, train_fraction=train_fraction)
    train_result = evaluate_train_partition(
        panel,
        train,
        feature_sessions=feature_sessions,
        forward_sessions=forward_sessions,
        group_size=group_size,
        treated_mean_residual_max=treated_mean_residual_max,
        min_episodes=min_episodes,
        min_signal_years=min_signal_years,
        bootstrap_samples=bootstrap_samples,
    )
    advanced = bool(train_result["gate_pass"])
    failed_gates = [name for name, passed in train_result["gate_checks"].items() if not passed]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD_L0_UNDERLYING_DISCOVERY",
        "paper_only": True,
        "sleeve_usd": 3000.0,
        "candidate_id": CANDIDATE_ID,
        "mechanism_family": FAMILY_ID,
        "novelty_key": (
            "direction_up|cross_section_peer_residual_reversal_5d|fixed_liquid_companies|"
            "bottom3_mean_le_-4pct|5session|same_date_neutral_residual_control|"
            "bull_call_debit_spread_21d_2wide_planned"
        ),
        "economic_mechanism": (
            "temporary issuer-specific liquidity or attention pressure can push liquid stocks below their "
            "same-date peer basket; genuine overreaction should rebound absolutely and relative to neutral peers"
        ),
        "forecast_type": "direction_up_and_relative_recovery_over_five_sessions",
        "funnel_stage_before": "F0_MECHANISM",
        "funnel_stage_after": "F1_TRAIN" if advanced else "F0_MECHANISM",
        "strategy_outcome": "STRATEGY_ADVANCED" if advanced else "FAMILY_CLOSED",
        "decision": (
            "ADVANCE_CROSS_SECTION_RESIDUAL_REVERSAL_TO_F1_TRAIN"
            if advanced
            else "CLOSE_CROSS_SECTION_RESIDUAL_REVERSAL_TRAIN_FAMILY"
        ),
        "claim_scope": (
            "split/dividend-adjusted underlying closes, fixed present-day liquid-company panel, train-only "
            "L0 discovery, and 20-bps underlying sensitivity; no option marks, IV, debit, fill, option PnL, "
            "F2, L1, capital-seat, or paper-eligibility claim"
        ),
        "f2_or_l1_claim": False,
        "funnel_claim_f2": False,
        "l1_claim": False,
        "capital_seat_claim": False,
        "all_train_rows_are_inspected_development_data": True,
        "falsifier": (
            "fewer than 40 train episodes or eight signal years; chronology/group/overlap/ranking failure; "
            "treated mean after 20 bps <=0; paired excess <0.25%; paired-excess circular-block LB90 <=0; "
            "treated positive frequency <55%; or treated worst-decile mean <-5%"
        ),
        "config": {
            "symbols": normalized,
            "feature_sessions": feature_sessions,
            "forward_sessions": forward_sessions,
            "rebalance_sessions": rebalance_sessions,
            "group_size_each": group_size,
            "treated_mean_residual_max": treated_mean_residual_max,
            "train_fraction": train_fraction,
            "minimum_train_episodes": min_episodes,
            "minimum_signal_years": min_signal_years,
            "round_trip_underlying_cost_bps_per_group_member": 20.0,
            "minimum_paired_excess_mean": 0.0025,
            "minimum_treated_positive_frequency": 0.55,
            "minimum_treated_worst_decile_mean": -0.05,
            "bootstrap_confidence": 0.90,
            "bootstrap_samples": bootstrap_samples,
            "bootstrap_block_length_episodes": 3,
            "non_overlapping_episodes": True,
        },
        "layered_edge_stack": {
            "market_underlying": "fixed 14-name liquid US operating-company panel",
            "forecast_type": "direction up and relative recovery over five completed sessions",
            "economic_mechanism": "temporary issuer-specific liquidity/attention overreaction and mean reversion",
            "option_structure": "future conditional one-lot 18-24 DTE $2-wide bull call debit spread",
            "intended_greeks": ["positive_delta", "positive_gamma", "bounded_debit"],
            "dangerous_greeks_and_exposures": [
                "negative_theta_if_recovery_stalls",
                "post_shock_implied_volatility_overpayment_and_vega_loss",
                "gap_through_risk",
                "capped_upside",
                "two_leg_liquidity",
                "short_call_assignment_and_expiry_handling",
            ],
            "regime_envelope": "completed bottom-three mean five-session peer residual <=-4%; complete panel; no overlap",
            "entry_trigger": "next regular-session decision after completed rank signal, conditional on listed package and risk gates",
            "exit_management": "+50%/-50% debit, five-session time stop, five-DTE guard, or peer residual recovery; no roll",
            "capital_fit_usd": 200.0,
            "max_loss_usd": 200.0,
            "max_loss_status": (
                "future same-expiry frictionless debit ceiling only; no observed or simulated option-path "
                "loss and closing friction is unmodeled"
            ),
            "max_lots": 1,
            "portfolio_overlap": "one global residual-reversal unit; no same-issuer or correlated positive-delta Agentic overlap",
            "evidence_falsifier": "frozen train gates above; final chronological 40% sealed",
            "confidence_stage": "F1_TRAIN/L0" if advanced else "F0_MECHANISM_CLOSED/L0",
            "stand_aside": "any feature, threshold, completeness, overlap, event, package debit/liquidity, or risk gate failure",
        },
        "structure": "conditional_bull_call_debit_spread_not_yet_priced",
        "capital_fit_usd": 200.0,
        "one_lot_max_loss_usd": 200.0,
        "max_loss_usd": 200.0,
        "max_lots": 1,
        "capital_basis": (
            "future same-expiry frictionless $2-width/debit ceiling; admission requires debit <=$200, "
            "while observed/simulated option-path loss and closing friction remain unmeasured"
        ),
        "observed_or_simulated_option_path_max_loss_usd": None,
        "provenance": provenance,
        "population_validity": {
            "population_type": "fixed present-day liquid operating companies",
            "population_pure": True,
            "ranking_complete": True,
            "survivorship_bias": True,
            "listing_bias": True,
            "historical_optionability_reconstructed": False,
            "generalization_allowed": False,
        },
        "train": train_result,
        "holdout": _holdout_identity(holdout),
        "option_stage": {
            "status": "NOT_RUN_PENDING_UNTOUCHED_HOLDOUT" if advanced else "NOT_RUN_TRAIN_GATE_FAILED",
            "pricing_run": False,
            "pricing_calls": 0,
            "planned_structure": "bull_call_debit_spread",
            "planned_dte_range": [18, 24],
            "planned_width_usd": 2.0,
            "option_mark_provenance": None,
        },
        "failed_gates": failed_gates,
        "dominant_failure_mechanism": None if advanced else _dominant_failure(failed_gates),
        "closed_family": None if advanced else FAMILY_ID,
        "quarantine": {
            "enabled": not advanced,
            "scope": [
                FAMILY_ID,
                CANDIDATE_ID,
                "same fixed 14-name present-day panel",
                "bottom-three residual laggards versus neutral-three controls",
                "nearby treated mean residual thresholds around -4%",
                "nearby five-session feature and forward-horizon retunes",
            ],
            "banned_train_salvage": [
                "delete AMD, TSLA, AAPL, or another symbol after inspecting worst episodes",
                "loosen the -5% worst-decile gate",
                "open the sealed holdout",
                "derive event exclusions or thresholds from inspected train outcomes",
            ],
            "reopen_condition": (
                "materially new economic mechanism or genuinely prior-known event evidence whose taxonomy, "
                "labels, and thresholds are frozen before outcomes; keep this holdout sealed"
            ),
        },
        "methodology_boundaries": {
            "chronology": "features end at completed signal close; outcome starts next completed close",
            "control": "same-date peer residuals closest to zero, disjoint from treated; paired outcome",
            "dependence": "globally non-overlapping episodes and circular three-episode block bootstrap",
            "costs": "20-bps underlying round-trip sensitivity per group member; not option execution cost",
            "option_alignment": "five-session rebound direction aligns with a managed 18-24 DTE bull call spread but does not validate option-path economics",
            "observed_option_marks": False,
            "proxy_option_marks": False,
            "holdout_outcomes_read": False,
            "l1_or_paper_eligibility": False,
        },
        "search_information": "new train-only overreaction mechanism decision with paired neutral-residual control and sealed holdout",
        "strategy_advancement": advanced,
        "strategy_advancement_summary": (
            "advanced F0_MECHANISM -> F1_TRAIN under discovery bar"
            if advanced
            else "none; exact mechanism family closed at F0"
        ),
        "registration_eligible": False,
        "authority": "research only; no registry, paper, shadow, funding, broker, arm, or live authority",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    parser.add_argument("--start", default="2012-06-01")
    parser.add_argument("--end", default="2026-07-16")
    parser.add_argument("--cache-dir", default=".cache/platform/cross_section_residual_reversal")
    parser.add_argument("--train-fraction", type=float, default=0.60)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    cache_dir = Path(args.cache_dir)
    histories: dict[str, pd.Series] = {}
    provenance: dict[str, Any] = {}
    for symbol in symbols:
        history, source = load_adjusted_history(
            symbol,
            cache_dir=cache_dir,
            start=args.start,
            end=args.end,
        )
        histories[symbol] = history
        provenance[symbol] = source
    panel = assemble_close_panel(histories, symbols=symbols, min_common_rows=2_500)
    provenance["common_panel"] = {
        "rows": int(len(panel)),
        "start": str(panel.index[0].date()),
        "end": str(panel.index[-1].date()),
        "join": "inner join on trading dates; no forward fill",
    }
    payload = run_lab_from_panel(
        panel,
        symbols=symbols,
        provenance=provenance,
        train_fraction=args.train_fraction,
        bootstrap_samples=args.bootstrap_samples,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "candidate_id": payload["candidate_id"],
                "strategy_outcome": payload["strategy_outcome"],
                "decision": payload["decision"],
                "funnel_stage_after": payload["funnel_stage_after"],
                "train_n": payload["train"]["n_episodes"],
                "signal_years": payload["train"]["signal_years"],
                "treated_mean_return_after_cost": payload["train"]["treated_mean_return_after_cost"],
                "paired_excess_mean": payload["train"]["paired_excess_mean"],
                "paired_excess_bootstrap_lb90": payload["train"]["paired_excess_bootstrap_lb90"],
                "failed_gates": payload["failed_gates"],
                "out": str(out),
            },
            indent=2,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Train-only monthly cross-sectional 12-minus-1 momentum discovery lab.

Research-only BUILD/L0. The underlying mechanism is evaluated before option
pricing; the chronological final 40% remains untouched in this wake.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from scripts.low_hv_cross_section_train_lab import (
        _validate_close_panel,
        assemble_close_panel,
        circular_block_bootstrap_lower_bound,
        load_adjusted_history,
        split_blueprints,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from low_hv_cross_section_train_lab import (  # type: ignore[no-redef]
        _validate_close_panel,
        assemble_close_panel,
        circular_block_bootstrap_lower_bound,
        load_adjusted_history,
        split_blueprints,
    )

DEFAULT_SYMBOLS = (
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
)


def build_monthly_momentum_blueprints(
    close_panel: pd.DataFrame,
    *,
    lookback_sessions: int = 252,
    skip_sessions: int = 21,
    forward_sessions: int = 21,
    quantile_count: int = 3,
) -> list[dict[str, Any]]:
    """Rank completed 12-minus-1 momentum and reserve non-overlapping episodes."""
    panel = _validate_close_panel(close_panel)
    if lookback_sessions < 2:
        raise ValueError("lookback sessions must be at least two")
    if not 1 <= skip_sessions < lookback_sessions:
        raise ValueError("skip sessions must be positive and smaller than lookback")
    if forward_sessions < 1 or quantile_count < 1:
        raise ValueError("forward sessions and quantile count must be positive")
    if 2 * quantile_count > panel.shape[1]:
        raise ValueError("top/bottom groups must be disjoint")

    month_keys = panel.index.to_period("M")
    rank_dates = panel.groupby(month_keys, sort=True).tail(1).index
    blueprints: list[dict[str, Any]] = []
    previous_exit_position = -1
    for raw_rank_date in rank_dates:
        rank_date = pd.Timestamp(raw_rank_date)
        rank_position = int(panel.index.get_loc(rank_date))
        feature_start_position = rank_position - lookback_sessions
        feature_end_position = rank_position - skip_sessions
        entry_position = rank_position + 1
        exit_position = entry_position + forward_sessions
        if feature_start_position < 0 or exit_position >= len(panel):
            continue
        if entry_position <= previous_exit_position:
            continue

        feature_start_date = pd.Timestamp(panel.index[feature_start_position])
        feature_end_date = pd.Timestamp(panel.index[feature_end_position])
        momentum = panel.loc[feature_end_date] / panel.loc[feature_start_date] - 1.0
        values = momentum.to_numpy(dtype=float)
        if not np.isfinite(values).all():
            continue
        ordered = sorted(
            ((float(value), str(symbol)) for symbol, value in momentum.items()),
            key=lambda item: (item[0], item[1]),
        )
        bottom = [symbol for _, symbol in ordered[:quantile_count]][::-1]
        top = [symbol for _, symbol in ordered[-quantile_count:]][::-1]
        blueprints.append(
            {
                "rank_date": rank_date,
                "feature_start_date": feature_start_date,
                "feature_end_date": feature_end_date,
                "entry_date": pd.Timestamp(panel.index[entry_position]),
                "exit_date": pd.Timestamp(panel.index[exit_position]),
                "top_momentum_symbols": top,
                "bottom_momentum_symbols": bottom,
                "top_momentum_values": {symbol: float(momentum[symbol]) for symbol in top},
                "bottom_momentum_values": {
                    symbol: float(momentum[symbol]) for symbol in bottom
                },
            }
        )
        previous_exit_position = exit_position
    return blueprints


def evaluate_train_partition(
    close_panel: pd.DataFrame,
    train_blueprints: list[dict[str, Any]],
    *,
    min_episodes: int = 24,
    round_trip_cost_bps: float = 20.0,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    panel = _validate_close_panel(close_panel)
    if min_episodes < 1 or not train_blueprints:
        raise ValueError("non-empty train blueprints and positive min_episodes are required")
    if not np.isfinite(round_trip_cost_bps) or round_trip_cost_bps < 0.0:
        raise ValueError("round-trip cost bps must be finite and non-negative")
    cost_fraction = float(round_trip_cost_bps) / 10_000.0
    rows: list[dict[str, Any]] = []
    prior_exit: pd.Timestamp | None = None
    integrity_violations: list[str] = []

    for index, blueprint in enumerate(train_blueprints):
        rank_date = pd.Timestamp(blueprint["rank_date"])
        feature_start = pd.Timestamp(blueprint["feature_start_date"])
        feature_end = pd.Timestamp(blueprint["feature_end_date"])
        entry_date = pd.Timestamp(blueprint["entry_date"])
        exit_date = pd.Timestamp(blueprint["exit_date"])
        top = list(blueprint["top_momentum_symbols"])
        bottom = list(blueprint["bottom_momentum_symbols"])
        if not (feature_start < feature_end <= rank_date < entry_date < exit_date):
            integrity_violations.append(f"chronology:{index}")
        if prior_exit is not None and entry_date <= prior_exit:
            integrity_violations.append(f"overlap:{index}")
        if set(top) & set(bottom) or not top or len(top) != len(bottom):
            integrity_violations.append(f"groups:{index}")
        missing = sorted((set(top) | set(bottom)) - set(panel.columns))
        required_dates = {feature_start, feature_end, rank_date, entry_date, exit_date}
        if missing or not required_dates.issubset(set(panel.index)):
            raise ValueError(f"blueprint {index} is outside the close panel: {missing}")

        top_returns = panel.loc[exit_date, top] / panel.loc[entry_date, top] - 1.0
        bottom_returns = panel.loc[exit_date, bottom] / panel.loc[entry_date, bottom] - 1.0
        top_mean = float(top_returns.mean()) - cost_fraction
        bottom_mean = float(bottom_returns.mean()) - cost_fraction
        rows.append(
            {
                "rank_date": str(rank_date.date()),
                "feature_start_date": str(feature_start.date()),
                "feature_end_date": str(feature_end.date()),
                "entry_date": str(entry_date.date()),
                "exit_date": str(exit_date.date()),
                "top_momentum_symbols": top,
                "bottom_momentum_symbols": bottom,
                "top_momentum_mean_return_after_cost": top_mean,
                "bottom_momentum_mean_return_after_cost": bottom_mean,
                "paired_excess_return": top_mean - bottom_mean,
            }
        )
        prior_exit = exit_date

    top_values = np.asarray(
        [row["top_momentum_mean_return_after_cost"] for row in rows], dtype=float
    )
    bottom_values = np.asarray(
        [row["bottom_momentum_mean_return_after_cost"] for row in rows], dtype=float
    )
    excess = top_values - bottom_values
    lower_bound = circular_block_bootstrap_lower_bound(
        excess,
        samples=bootstrap_samples,
        seed=20260714,
    )
    gate_checks = {
        "minimum_train_episodes": len(rows) >= min_episodes,
        "positive_top_momentum_mean_return_after_cost": float(top_values.mean()) > 0.0,
        "positive_paired_excess_mean": float(excess.mean()) > 0.0,
        "paired_excess_bootstrap_lb90_positive": lower_bound > 0.0,
        "zero_integrity_violations": not integrity_violations,
    }
    return {
        "n_episodes": len(rows),
        "round_trip_cost_bps_per_group_member": float(round_trip_cost_bps),
        "top_momentum_mean_return": float(top_values.mean()),
        "bottom_momentum_mean_return": float(bottom_values.mean()),
        "paired_excess_mean": float(excess.mean()),
        "paired_excess_median": float(np.median(excess)),
        "paired_excess_positive_frequency": float(np.mean(excess > 0.0)),
        "paired_excess_bootstrap_lb90": lower_bound,
        "bootstrap_samples": int(bootstrap_samples),
        "bootstrap_block_length": 3,
        "integrity_violations": integrity_violations,
        "gate_checks": gate_checks,
        "gate_pass": bool(all(gate_checks.values())),
        "episodes": rows,
    }


def run_lab_from_panel(
    close_panel: pd.DataFrame,
    *,
    symbols: list[str],
    provenance: dict[str, Any],
    train_fraction: float = 0.60,
    lookback_sessions: int = 252,
    skip_sessions: int = 21,
    forward_sessions: int = 21,
    quantile_count: int = 3,
    min_train_episodes: int = 24,
    round_trip_cost_bps: float = 20.0,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    panel = _validate_close_panel(close_panel)
    normalized = [str(symbol).strip().upper() for symbol in symbols]
    if normalized != list(panel.columns) or len(normalized) != len(set(normalized)):
        raise ValueError("symbols must exactly match the ordered close-panel columns")
    blueprints = build_monthly_momentum_blueprints(
        panel,
        lookback_sessions=lookback_sessions,
        skip_sessions=skip_sessions,
        forward_sessions=forward_sessions,
        quantile_count=quantile_count,
    )
    train, holdout = split_blueprints(blueprints, train_fraction=train_fraction)
    train_result = evaluate_train_partition(
        panel,
        train,
        min_episodes=min_train_episodes,
        round_trip_cost_bps=round_trip_cost_bps,
        bootstrap_samples=bootstrap_samples,
    )
    advanced = bool(train_result["gate_pass"])
    holdout_first = holdout[0]
    holdout_last = holdout[-1]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD_L0_UNDERLYING_DISCOVERY",
        "paper_only": True,
        "sleeve_usd": 3000.0,
        "candidate_id": "CROSS_SECTION_12_1_MOMENTUM_PCS_21D_V1",
        "mechanism_family": "MONTHLY_CROSS_SECTION_12_1_MOMENTUM_FORWARD_DRIFT",
        "economic_mechanism": (
            "gradual information diffusion and investor underreaction make intermediate-horizon "
            "relative strength persist, so the strongest prior completed 12-minus-1-month liquid "
            "equities should have better next-21-session drift than same-date weakest controls"
        ),
        "candidate_or_family_scope": (
            "month-end top-three versus bottom-three 252-session momentum ranks skipping the most "
            "recent 21 sessions in a fixed 14-name present-day liquid-equity panel, with "
            "non-overlapping 21-session forward episodes"
        ),
        "funnel_stage_before": "F0_MECHANISM",
        "funnel_stage_after": "F1_TRAIN" if advanced else "F0_MECHANISM",
        "falsifier": (
            "on the chronological first 60% of eligible non-overlapping monthly episodes, fewer "
            "than 24 episodes, non-positive top-momentum after-cost mean, non-positive top-minus-bottom "
            "mean, a non-positive one-sided 90% circular-block-bootstrap lower bound, or any integrity "
            "violation closes the exact family"
        ),
        "claim_scope": (
            "split/dividend-adjusted underlying closes with a labeled 20-bps round-trip sensitivity; "
            "fixed present-day universe with explicit survivorship/listing bias; train-only L0 "
            "discovery; no option marks, option costs, fills, L1, capital-seat, or paper eligibility claim"
        ),
        "all_train_rows_are_inspected_development_data": True,
        "f2_or_l1_claim": False,
        "config": {
            "symbols": normalized,
            "lookback_sessions": lookback_sessions,
            "skip_most_recent_sessions": skip_sessions,
            "forward_sessions": forward_sessions,
            "quantile_count_each_side": quantile_count,
            "train_fraction": train_fraction,
            "minimum_train_episodes": min_train_episodes,
            "round_trip_cost_bps_per_group_member": round_trip_cost_bps,
            "bootstrap_confidence": 0.90,
            "bootstrap_samples": bootstrap_samples,
            "bootstrap_block_length": 3,
            "non_overlapping_episodes": True,
        },
        "data_provenance": provenance,
        "population_validity": {
            "population_type": "fixed present-day liquid US equities only",
            "population_pure": True,
            "ranking_complete": True,
            "survivorship_bias": True,
            "listing_bias": True,
            "generalization_allowed": False,
        },
        "train": train_result,
        "untouched_holdout": {
            "n_blueprints": len(holdout),
            "first_rank_date": str(pd.Timestamp(holdout_first["rank_date"]).date()),
            "first_entry_date": str(pd.Timestamp(holdout_first["entry_date"]).date()),
            "last_rank_date": str(pd.Timestamp(holdout_last["rank_date"]).date()),
            "last_exit_date": str(pd.Timestamp(holdout_last["exit_date"]).date()),
            "outcome_metrics_read": False,
            "simulation_run": False,
        },
        "option_stage": {
            "status": "NOT_RUN_PENDING_UNTOUCHED_HOLDOUT" if advanced else "NOT_RUN_TRAIN_GATE_FAILED",
            "pricing_run": False,
            "pricing_calls": 0,
            "planned_structure": "put_credit_spread",
            "planned_width_usd": 1.0,
            "option_mark_provenance": None,
        },
        "structure": "conditional_put_credit_spread_not_yet_priced",
        "capital_fit_usd": 100.0,
        "one_lot_max_loss_usd": 100.0,
        "max_loss_usd": 100.0,
        "max_lots": 1,
        "capital_basis": (
            "structural upper bound for one future $1-wide PCS before net credit and closing friction; "
            "not an observed or simulated trade loss"
        ),
        "strategy_outcome": "STRATEGY_ADVANCED" if advanced else "FAMILY_CLOSED",
        "decision": (
            "ADVANCE_CROSS_SECTION_12_1_MOMENTUM_TO_F1_TRAIN"
            if advanced
            else "CLOSE_CROSS_SECTION_12_1_MOMENTUM_TRAIN_FAMILY"
        ),
        "closed_family": (
            None if advanced else "MONTHLY_CROSS_SECTION_12_1_MOMENTUM_FORWARD_DRIFT"
        ),
        "dominant_failure_mechanism": (
            None
            if advanced
            else "the frozen intermediate-momentum selector did not establish positive, uncertainty-bounded incremental train drift over the same-date weakest-momentum control"
        ),
        "registration_eligible": False,
        "authority": "research only; no registry, paper, shadow, funding, broker, arm, or live authority",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--end", default="2026-07-15")
    parser.add_argument("--cache-dir", default=".cache/platform/low_hv_cross_section")
    parser.add_argument("--train-fraction", type=float, default=0.60)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    histories: dict[str, pd.Series] = {}
    source_meta: dict[str, Any] = {}
    for symbol in symbols:
        history, meta = load_adjusted_history(
            symbol,
            cache_dir=Path(args.cache_dir),
            start=args.start,
            end=args.end,
        )
        histories[symbol] = history
        source_meta[symbol] = meta
    panel = assemble_close_panel(histories, symbols=symbols, min_common_rows=2_000)
    provenance = {
        "sources": source_meta,
        "common_panel": {
            "rows": int(len(panel)),
            "start": str(panel.index[0].date()),
            "end": str(panel.index[-1].date()),
            "join": "inner join on trading dates; no forward fill",
        },
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
                "train_n": payload["train"]["n_episodes"],
                "top_momentum_mean_return": payload["train"]["top_momentum_mean_return"],
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

#!/usr/bin/env python3
"""Train-only monthly-OPEX post-expiry broad-index drift discovery lab.

Research-only BUILD/L0. The underlying timing mechanism is evaluated before any
option pricing; the chronological final 40% remains untouched in this wake.
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

DEFAULT_SYMBOLS = ("SPY", "QQQ", "IWM", "DIA")


def _nth_friday(year: int, month: int, occurrence: int) -> pd.Timestamp:
    if occurrence < 1:
        raise ValueError("Friday occurrence must be positive")
    first = pd.Timestamp(year=year, month=month, day=1)
    first_friday = first + pd.Timedelta(days=(4 - first.weekday()) % 7)
    return first_friday + pd.Timedelta(days=7 * (occurrence - 1))


def _session_on_or_before(index: pd.DatetimeIndex, target: pd.Timestamp) -> pd.Timestamp | None:
    target = pd.Timestamp(target).normalize()
    candidates = index[(index <= target) & (index >= target - pd.Timedelta(days=3))]
    if len(candidates) == 0:
        return None
    session = pd.Timestamp(candidates[-1])
    return session if session.month == target.month else None


def build_monthly_opex_blueprints(
    close_panel: pd.DataFrame,
    *,
    forward_sessions: int = 5,
) -> list[dict[str, Any]]:
    """Build outcome-independent post-OPEX episodes and first-Friday controls."""
    panel = _validate_close_panel(close_panel)
    if forward_sessions < 1:
        raise ValueError("forward sessions must be positive")
    index = pd.DatetimeIndex(panel.index)
    blueprints: list[dict[str, Any]] = []
    previous_event_exit: pd.Timestamp | None = None

    for month in pd.period_range(index[0].to_period("M"), index[-1].to_period("M"), freq="M"):
        calendar_control = _nth_friday(month.year, month.month, 1)
        calendar_opex = _nth_friday(month.year, month.month, 3)
        control_session = _session_on_or_before(index, calendar_control)
        opex_session = _session_on_or_before(index, calendar_opex)
        if control_session is None or opex_session is None:
            continue
        control_pos = int(index.get_loc(control_session))
        opex_pos = int(index.get_loc(opex_session))
        control_entry_pos = control_pos + 1
        event_entry_pos = opex_pos + 1
        control_exit_pos = control_entry_pos + forward_sessions
        event_exit_pos = event_entry_pos + forward_sessions
        if event_exit_pos >= len(index) or control_exit_pos >= len(index):
            continue
        control_entry = pd.Timestamp(index[control_entry_pos])
        control_exit = pd.Timestamp(index[control_exit_pos])
        event_entry = pd.Timestamp(index[event_entry_pos])
        event_exit = pd.Timestamp(index[event_exit_pos])
        if control_entry.month != month.month or event_entry < opex_session:
            continue
        if control_exit > event_entry:
            continue
        if previous_event_exit is not None and control_entry <= previous_event_exit:
            continue
        blueprints.append(
            {
                "rank_date": opex_session,
                "month": str(month),
                "calendar_control_friday": calendar_control,
                "control_session_date": control_session,
                "control_entry_date": control_entry,
                "control_exit_date": control_exit,
                "calendar_opex_date": calendar_opex,
                "opex_session_date": opex_session,
                "event_entry_date": event_entry,
                "event_exit_date": event_exit,
            }
        )
        previous_event_exit = event_exit
    return blueprints


def evaluate_train_partition(
    close_panel: pd.DataFrame,
    train_blueprints: list[dict[str, Any]],
    *,
    min_episodes: int = 48,
    round_trip_cost_bps: float = 10.0,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    """Evaluate only the frozen train episodes against paired calendar controls."""
    panel = _validate_close_panel(close_panel)
    if min_episodes < 1 or not train_blueprints:
        raise ValueError("non-empty train blueprints and positive min_episodes are required")
    if not np.isfinite(round_trip_cost_bps) or round_trip_cost_bps < 0.0:
        raise ValueError("round-trip cost bps must be finite and non-negative")
    cost_fraction = float(round_trip_cost_bps) / 10_000.0
    rows: list[dict[str, Any]] = []
    integrity_violations: list[str] = []
    previous_event_exit: pd.Timestamp | None = None

    for position, blueprint in enumerate(train_blueprints):
        control_calendar = pd.Timestamp(blueprint["calendar_control_friday"])
        control_session = pd.Timestamp(blueprint["control_session_date"])
        control_entry = pd.Timestamp(blueprint["control_entry_date"])
        control_exit = pd.Timestamp(blueprint["control_exit_date"])
        opex_calendar = pd.Timestamp(blueprint["calendar_opex_date"])
        opex_session = pd.Timestamp(blueprint["opex_session_date"])
        event_entry = pd.Timestamp(blueprint["event_entry_date"])
        event_exit = pd.Timestamp(blueprint["event_exit_date"])
        if not (
            control_session <= control_calendar < opex_calendar
            and control_session < control_entry < control_exit
            and opex_session <= opex_calendar < event_entry < event_exit
        ):
            integrity_violations.append(f"chronology:{position}")
        if control_exit > event_entry:
            integrity_violations.append(f"control_overlaps_event:{position}")
        if previous_event_exit is not None and control_entry <= previous_event_exit:
            integrity_violations.append(f"episode_overlap:{position}")
        required_dates = {control_session, control_entry, control_exit, opex_session, event_entry, event_exit}
        if not required_dates.issubset(set(panel.index)):
            raise ValueError(f"blueprint {position} is outside the close panel")

        event_by_symbol = panel.loc[event_exit] / panel.loc[event_entry] - 1.0
        control_by_symbol = panel.loc[control_exit] / panel.loc[control_entry] - 1.0
        event_basket = float(event_by_symbol.mean()) - cost_fraction
        control_basket = float(control_by_symbol.mean()) - cost_fraction
        rows.append(
            {
                "month": str(blueprint["month"]),
                "control_session_date": str(control_session.date()),
                "control_entry_date": str(control_entry.date()),
                "control_exit_date": str(control_exit.date()),
                "opex_session_date": str(opex_session.date()),
                "event_entry_date": str(event_entry.date()),
                "event_exit_date": str(event_exit.date()),
                "event_returns_by_symbol_before_cost": {
                    symbol: float(event_by_symbol[symbol]) for symbol in panel.columns
                },
                "control_returns_by_symbol_before_cost": {
                    symbol: float(control_by_symbol[symbol]) for symbol in panel.columns
                },
                "event_basket_return_after_cost": event_basket,
                "control_basket_return_after_cost": control_basket,
                "paired_excess_return": event_basket - control_basket,
            }
        )
        previous_event_exit = event_exit

    event = np.asarray([row["event_basket_return_after_cost"] for row in rows], dtype=float)
    control = np.asarray([row["control_basket_return_after_cost"] for row in rows], dtype=float)
    paired = event - control
    lower_bound = circular_block_bootstrap_lower_bound(
        paired,
        samples=bootstrap_samples,
        seed=20260715,
    )
    gate_checks = {
        "minimum_train_episodes": len(rows) >= min_episodes,
        "positive_event_basket_mean_return_after_cost": float(event.mean()) > 0.0,
        "positive_paired_excess_mean": float(paired.mean()) > 0.0,
        "paired_excess_bootstrap_lb90_positive": lower_bound > 0.0,
        "zero_integrity_violations": not integrity_violations,
    }
    return {
        "n_episodes": len(rows),
        "round_trip_cost_bps_per_basket_episode": float(round_trip_cost_bps),
        "event_basket_mean_return_after_cost": float(event.mean()),
        "event_basket_median_return_after_cost": float(np.median(event)),
        "control_basket_mean_return_after_cost": float(control.mean()),
        "paired_excess_mean": float(paired.mean()),
        "paired_excess_median": float(np.median(paired)),
        "paired_excess_positive_frequency": float(np.mean(paired > 0.0)),
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
    forward_sessions: int = 5,
    min_train_episodes: int = 48,
    round_trip_cost_bps: float = 10.0,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    panel = _validate_close_panel(close_panel)
    normalized = [str(symbol).strip().upper() for symbol in symbols]
    if normalized != list(panel.columns) or normalized != list(DEFAULT_SYMBOLS):
        raise ValueError("symbols must exactly match the frozen SPY,QQQ,IWM,DIA panel order")
    blueprints = build_monthly_opex_blueprints(panel, forward_sessions=forward_sessions)
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
        "candidate_id": "MONTHLY_OPEX_POST_EXPIRY_BULL_CALL_14D_V1",
        "mechanism_family": "MONTHLY_OPEX_POST_EXPIRY_BROAD_INDEX_DRIFT",
        "economic_mechanism": (
            "monthly index-option expiration may unwind dealer hedges and rebalance index exposure, "
            "creating a short positive broad-index drift after third-Friday OPEX relative to an "
            "outcome-free same-month pre-OPEX Friday control"
        ),
        "candidate_or_family_scope": (
            "equal-weight SPY/QQQ/IWM/DIA five-session adjusted-close return entered on the next "
            "completed session after monthly OPEX versus the identical horizon after the first "
            "Friday of the same month"
        ),
        "funnel_stage_before": "F0_MECHANISM",
        "funnel_stage_after": "F1_TRAIN" if advanced else "F0_MECHANISM",
        "falsifier": (
            "on the chronological first 60% of eligible non-overlapping monthly episodes, fewer "
            "than 48 episodes, non-positive equal-weight basket mean after a labeled 10-bps "
            "round-trip sensitivity, non-positive paired excess versus the first-Friday control, "
            "a non-positive one-sided 90% circular-block-bootstrap lower bound, or any integrity "
            "violation closes the exact family"
        ),
        "claim_scope": (
            "split/dividend-adjusted broad-index ETF closes with a labeled underlying 10-bps "
            "round-trip sensitivity; train-only L0 discovery; no option marks, option costs, fills, "
            "L1, capital-seat, or paper eligibility claim"
        ),
        "all_train_rows_are_inspected_development_data": True,
        "f2_or_l1_claim": False,
        "config": {
            "symbols": normalized,
            "event": "next completed session after adjusted third-Friday monthly OPEX",
            "control": "next completed session after adjusted first Friday of the same month",
            "forward_sessions": forward_sessions,
            "train_fraction": train_fraction,
            "minimum_train_episodes": min_train_episodes,
            "round_trip_cost_bps_per_basket_episode": round_trip_cost_bps,
            "bootstrap_confidence": 0.90,
            "bootstrap_samples": bootstrap_samples,
            "bootstrap_block_length": 3,
            "non_overlapping_episodes": True,
        },
        "data_provenance": provenance,
        "population_validity": {
            "population_type": "fixed broad-index ETF basket",
            "population_pure": True,
            "population_pure_semantics": (
                "the frozen four-symbol basket was evaluated completely and without row mixing; "
                "this does not mean the basket is survivorship-bias-free"
            ),
            "bias_free": False,
            "ranking_complete": True,
            "survivorship_bias": True,
            "listing_bias": True,
            "generalization_allowed": False,
        },
        "train": train_result,
        "untouched_holdout": {
            "n_blueprints": len(holdout),
            "first_month": str(holdout_first["month"]),
            "first_event_entry_date": str(pd.Timestamp(holdout_first["event_entry_date"]).date()),
            "last_month": str(holdout_last["month"]),
            "last_event_exit_date": str(pd.Timestamp(holdout_last["event_exit_date"]).date()),
            "outcome_metrics_read": False,
            "simulation_run": False,
        },
        "option_stage": {
            "status": "NOT_RUN_PENDING_UNTOUCHED_HOLDOUT" if advanced else "NOT_RUN_TRAIN_GATE_FAILED",
            "pricing_run": False,
            "pricing_calls": 0,
            "planned_structure": "bull_call_debit_spread",
            "planned_dte": 14,
            "planned_width_usd": 2.0,
            "option_mark_provenance": None,
        },
        "structure": "conditional_bull_call_debit_spread_not_yet_priced",
        "capital_fit_usd": 200.0,
        "one_lot_max_loss_usd": 200.0,
        "max_loss_usd": 200.0,
        "max_lots": 1,
        "capital_basis": (
            "structural $2-wide one-lot debit-spread upper bound before closing friction; not an "
            "observed or simulated paid debit"
        ),
        "strategy_outcome": "STRATEGY_ADVANCED" if advanced else "FAMILY_CLOSED",
        "decision": (
            "ADVANCE_MONTHLY_OPEX_POST_EXPIRY_TO_F1_TRAIN"
            if advanced
            else "CLOSE_MONTHLY_OPEX_POST_EXPIRY_TRAIN_FAMILY"
        ),
        "closed_family": None if advanced else "MONTHLY_OPEX_POST_EXPIRY_BROAD_INDEX_DRIFT",
        "dominant_failure_mechanism": (
            None
            if advanced
            else "the frozen post-OPEX basket did not establish positive, uncertainty-bounded incremental train drift over the same-month first-Friday control"
        ),
        "registration_eligible": False,
        "authority": "research only; no registry, paper, shadow, funding, broker, arm, or live authority",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--end", default="2026-07-16")
    parser.add_argument("--cache-dir", default=".cache/platform/monthly_opex_broad_index")
    parser.add_argument("--train-fraction", type=float, default=0.60)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    histories: dict[str, pd.Series] = {}
    source_meta: dict[str, Any] = {}
    for symbol in symbols:
        # Materialize the cache first, then parse that persisted snapshot even on
        # the download invocation.  This prevents tiny CSV round-trip float
        # differences from making the canonical evidence irreproducible.
        load_adjusted_history(
            symbol,
            cache_dir=Path(args.cache_dir),
            start=args.start,
            end=args.end,
        )
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
                "event_basket_mean_return_after_cost": payload["train"][
                    "event_basket_mean_return_after_cost"
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

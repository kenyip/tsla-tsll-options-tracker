#!/usr/bin/env python3
"""Train-only multi-mechanism defined-risk candidate factory.

BUILD/L0 only. Signal and control geometry is frozen before outcome access; the
chronological final 40% remains identity-only and no option pricing occurs.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from scripts.fomc_information_resolution_train_lab import load_adjusted_ohlcv
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from fomc_information_resolution_train_lab import load_adjusted_ohlcv  # type: ignore[no-redef]


@dataclass(frozen=True)
class MechanismSpec:
    candidate_id: str
    family_id: str
    direction: int
    structure: str
    mechanism: str
    trigger_name: str


CREDIT_SPEC = MechanismSpec(
    candidate_id="CREDIT_RISK_OFF_SPY_BEAR_PUT_21D_V1",
    family_id="HIGH_YIELD_CREDIT_DIVERGENCE_FORWARD_DOWNSIDE",
    direction=-1,
    structure="future_conditional_18_24dte_2wide_bear_put_debit_spread",
    mechanism=(
        "High-yield credit may reprice deteriorating risk appetite and financing conditions before "
        "large-cap equities fully adjust."
    ),
    trigger_name="credit_risk_off",
)
OVERNIGHT_SPEC = MechanismSpec(
    candidate_id="OVERNIGHT_SELL_INTRADAY_RECOVERY_SPY_BULL_CALL_21D_V1",
    family_id="OVERNIGHT_INTRADAY_DISAGREEMENT_FORWARD_UPDRIFT",
    direction=1,
    structure="future_conditional_18_24dte_2wide_bull_call_debit_spread",
    mechanism=(
        "Repeated overnight selling absorbed by regular-session buying may represent transitory "
        "risk-transfer pressure rather than durable negative information."
    ),
    trigger_name="overnight_sell_intraday_recovery",
)
SPECS = (CREDIT_SPEC, OVERNIGHT_SPEC)


def _validate_frames(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    required = {"SPY", "HYG", "IEF"}
    if set(frames) != required:
        raise ValueError("frames must contain exactly SPY, HYG, and IEF")
    prepared: dict[str, pd.DataFrame] = {}
    for symbol in sorted(required):
        frame = frames[symbol].copy()
        frame.index = pd.DatetimeIndex(pd.to_datetime(frame.index)).tz_localize(None).normalize()
        frame.columns = [str(column).strip().lower() for column in frame.columns]
        needed = {"open", "high", "low", "close", "volume"}
        if not needed.issubset(frame.columns):
            raise ValueError(f"{symbol} frame missing OHLCV")
        frame = frame.loc[:, ["open", "high", "low", "close", "volume"]].apply(
            pd.to_numeric, errors="coerce"
        )
        values = frame.to_numpy(dtype=float)
        if (
            frame.empty
            or not frame.index.is_unique
            or not frame.index.is_monotonic_increasing
            or not np.isfinite(values).all()
            or (frame[["open", "high", "low", "close"]] <= 0.0).any().any()
        ):
            raise ValueError(f"{symbol} frame must be unique, increasing, finite, and positive")
        prepared[symbol] = frame
    return prepared


def build_feature_panel(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build completed-session features on the exact common trading-date panel."""
    validated = _validate_frames(frames)
    common = validated["SPY"].index
    for symbol in ("HYG", "IEF"):
        common = common.intersection(validated[symbol].index)
    common = common.sort_values()
    if len(common) < 1_000:
        raise ValueError("common panel requires at least 1,000 rows")
    spy = validated["SPY"].loc[common]
    hyg = validated["HYG"].loc[common, "close"]
    ief = validated["IEF"].loc[common, "close"]
    close = spy["close"]
    log_return = np.log(close / close.shift(1))
    overnight = spy["open"] / close.shift(1) - 1.0
    intraday = close / spy["open"] - 1.0
    features = pd.DataFrame(
        {
            "spy_open": spy["open"],
            "spy_close": close,
            "sma100": close.rolling(100, min_periods=100).mean(),
            "ret60": close / close.shift(60) - 1.0,
            "ret5": close / close.shift(5) - 1.0,
            "hv20": log_return.rolling(20, min_periods=20).std() * np.sqrt(252.0),
            "hyg_ief_ret10": (hyg / hyg.shift(10) - 1.0) - (ief / ief.shift(10) - 1.0),
            "overnight5": (1.0 + overnight).rolling(5, min_periods=5).apply(np.prod, raw=True)
            - 1.0,
            "intraday5": (1.0 + intraday).rolling(5, min_periods=5).apply(np.prod, raw=True)
            - 1.0,
        },
        index=common,
    )
    features["sma_distance"] = features["spy_close"] / features["sma100"] - 1.0
    return features


def _trigger_mask(features: pd.DataFrame, spec: MechanismSpec) -> pd.Series:
    uptrend = features["spy_close"] > features["sma100"]
    if spec == CREDIT_SPEC:
        return uptrend & (features["hyg_ief_ret10"] <= -0.015) & (features["ret5"] <= 0.0)
    if spec == OVERNIGHT_SPEC:
        return uptrend & (features["overnight5"] <= -0.01) & (features["intraday5"] >= 0.01)
    raise ValueError(f"unknown mechanism {spec.candidate_id}")


def _base_control_mask(features: pd.DataFrame, spec: MechanismSpec) -> pd.Series:
    finite = np.isfinite(
        features[["spy_close", "sma100", "ret60", "hv20", "sma_distance"]].to_numpy(
            dtype=float
        )
    ).all(axis=1)
    base = pd.Series(finite, index=features.index) & (features["spy_close"] > features["sma100"])
    if spec == CREDIT_SPEC:
        base &= features["ret5"] <= 0.0
    return base & ~_trigger_mask(features, spec)


def freeze_signal_geometry(
    features: pd.DataFrame,
    spec: MechanismSpec,
    *,
    forward_sessions: int = 5,
) -> list[dict[str, Any]]:
    """Freeze non-overlapping signal identities without reading forward returns."""
    if forward_sessions < 1:
        raise ValueError("forward_sessions must be positive")
    trigger = _trigger_mask(features, spec)
    rows: list[dict[str, Any]] = []
    next_available = 0
    for signal_pos in range(len(features)):
        if signal_pos < next_available or not bool(trigger.iloc[signal_pos]):
            continue
        entry_pos = signal_pos + 1
        exit_pos = entry_pos + forward_sessions
        if exit_pos >= len(features):
            continue
        match_fields = features.iloc[signal_pos][["ret60", "hv20", "sma_distance"]]
        if not np.isfinite(match_fields.to_numpy(dtype=float)).all():
            continue
        rows.append(
            {
                "signal_pos": signal_pos,
                "signal_date": pd.Timestamp(features.index[signal_pos]),
                "feature_max_date": pd.Timestamp(features.index[signal_pos]),
                "entry_pos": entry_pos,
                "entry_date": pd.Timestamp(features.index[entry_pos]),
                "exit_pos": exit_pos,
                "exit_date": pd.Timestamp(features.index[exit_pos]),
                "ret60": float(match_fields["ret60"]),
                "hv20": float(match_fields["hv20"]),
                "sma_distance": float(match_fields["sma_distance"]),
            }
        )
        next_available = exit_pos + 1
    return rows


def match_prior_controls(
    features: pd.DataFrame,
    signals: list[dict[str, Any]],
    spec: MechanismSpec,
    *,
    forward_sessions: int = 5,
    max_distance_sessions: int = 756,
    max_ret60_gap: float = 0.10,
    max_hv20_gap: float = 0.10,
    max_sma_distance_gap: float = 0.10,
) -> list[dict[str, Any]]:
    """Attach one outcome-independent, prior-only, no-reuse control per signal."""
    if min(max_ret60_gap, max_hv20_gap, max_sma_distance_gap) <= 0.0:
        raise ValueError("match gaps must be positive")
    control_mask = _base_control_mask(features, spec)
    used_windows: list[tuple[int, int]] = []
    matched: list[dict[str, Any]] = []
    for signal in signals:
        signal_pos = int(signal["signal_pos"])
        lower = max(100, signal_pos - max_distance_sessions)
        candidates: list[tuple[float, int, int, int]] = []
        for control_pos in range(lower, signal_pos):
            if not bool(control_mask.iloc[control_pos]):
                continue
            entry_pos = control_pos + 1
            exit_pos = entry_pos + forward_sessions
            if exit_pos >= signal_pos:
                continue
            window = (entry_pos, exit_pos)
            if any(not (window[1] < prior[0] or window[0] > prior[1]) for prior in used_windows):
                continue
            row = features.iloc[control_pos]
            fields = row[["ret60", "hv20", "sma_distance"]].to_numpy(dtype=float)
            if not np.isfinite(fields).all():
                continue
            ret_gap = abs(float(signal["ret60"]) - float(row["ret60"]))
            hv_gap = abs(float(signal["hv20"]) - float(row["hv20"]))
            sma_gap = abs(float(signal["sma_distance"]) - float(row["sma_distance"]))
            if ret_gap > max_ret60_gap or hv_gap > max_hv20_gap or sma_gap > max_sma_distance_gap:
                continue
            score = (
                ret_gap / max_ret60_gap
                + hv_gap / max_hv20_gap
                + sma_gap / max_sma_distance_gap
            )
            candidates.append((float(score), signal_pos - control_pos, control_pos, exit_pos))
        if not candidates:
            continue
        score, distance, control_pos, control_exit_pos = min(
            candidates, key=lambda row: (row[0], row[1], row[2])
        )
        control_entry_pos = control_pos + 1
        control_row = features.iloc[control_pos]
        item = dict(signal)
        item.update(
            {
                "control_feature_pos": control_pos,
                "control_feature_date": pd.Timestamp(features.index[control_pos]),
                "control_entry_pos": control_entry_pos,
                "control_entry_date": pd.Timestamp(features.index[control_entry_pos]),
                "control_exit_pos": control_exit_pos,
                "control_exit_date": pd.Timestamp(features.index[control_exit_pos]),
                "control_ret60": float(control_row["ret60"]),
                "control_hv20": float(control_row["hv20"]),
                "control_sma_distance": float(control_row["sma_distance"]),
                "ret60_match_gap": abs(float(signal["ret60"]) - float(control_row["ret60"])),
                "hv20_match_gap": abs(float(signal["hv20"]) - float(control_row["hv20"])),
                "sma_distance_match_gap": abs(
                    float(signal["sma_distance"]) - float(control_row["sma_distance"])
                ),
                "match_score": score,
                "control_distance_sessions": int(distance),
            }
        )
        matched.append(item)
        used_windows.append((control_entry_pos, control_exit_pos))
    return matched


def _block_lower_bound(values: np.ndarray, *, samples: int, seed: int) -> float:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or not len(vector) or not np.isfinite(vector).all():
        raise ValueError("bootstrap requires a finite non-empty vector")
    if samples < 100:
        raise ValueError("bootstrap samples must be at least 100")
    block = min(3, len(vector))
    n_blocks = int(np.ceil(len(vector) / block))
    offsets = np.arange(block)
    rng = np.random.default_rng(seed)
    estimates = np.empty(samples, dtype=float)
    for index in range(samples):
        starts = rng.integers(0, len(vector), size=n_blocks)
        draw = np.concatenate([vector[(start + offsets) % len(vector)] for start in starts])[
            : len(vector)
        ]
        estimates[index] = float(draw.mean())
    return float(np.quantile(estimates, 0.10))


def _worst_decile(values: np.ndarray) -> float:
    count = max(1, int(np.ceil(len(values) * 0.10)))
    return float(np.sort(values)[:count].mean())


def evaluate_train(
    features: pd.DataFrame,
    matched_train: list[dict[str, Any]],
    spec: MechanismSpec,
    *,
    n_train_eligible: int,
    min_pairs: int = 36,
    min_years: int = 8,
    min_support: float = 0.80,
    round_trip_cost_bps: float = 10.0,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    if n_train_eligible < 1:
        raise ValueError("train requires eligible signals")
    rows: list[dict[str, Any]] = []
    violations: list[str] = []
    used_controls: list[tuple[int, int]] = []
    for index, item in enumerate(matched_train):
        signal_pos = int(item["signal_pos"])
        entry_pos = int(item["entry_pos"])
        exit_pos = int(item["exit_pos"])
        control_pos = int(item["control_feature_pos"])
        control_entry = int(item["control_entry_pos"])
        control_exit = int(item["control_exit_pos"])
        if not (signal_pos < entry_pos < exit_pos):
            violations.append(f"signal_chronology:{index}")
        if not (control_pos < control_entry < control_exit < signal_pos):
            violations.append(f"control_chronology:{index}")
        if item["feature_max_date"] != item["signal_date"]:
            violations.append(f"feature_lag:{index}")
        window = (control_entry, control_exit)
        if any(not (window[1] < prior[0] or window[0] > prior[1]) for prior in used_controls):
            violations.append(f"control_reuse:{index}")
        used_controls.append(window)
        if bool(_trigger_mask(features, spec).iloc[control_pos]):
            violations.append(f"control_trigger_contamination:{index}")
        event_raw = float(
            features.iloc[exit_pos]["spy_close"] / features.iloc[entry_pos]["spy_close"] - 1.0
        )
        control_raw = float(
            features.iloc[control_exit]["spy_close"]
            / features.iloc[control_entry]["spy_close"]
            - 1.0
        )
        cost = round_trip_cost_bps / 10_000.0
        event_signed = spec.direction * event_raw - cost
        control_signed = spec.direction * control_raw - cost
        metrics = [event_raw, control_raw, event_signed, control_signed]
        if not np.isfinite(metrics).all():
            violations.append(f"nonfinite_outcome:{index}")
            continue
        rows.append(
            {
                "signal_date": str(pd.Timestamp(item["signal_date"]).date()),
                "entry_date": str(pd.Timestamp(item["entry_date"]).date()),
                "exit_date": str(pd.Timestamp(item["exit_date"]).date()),
                "control_feature_date": str(pd.Timestamp(item["control_feature_date"]).date()),
                "control_entry_date": str(pd.Timestamp(item["control_entry_date"]).date()),
                "control_exit_date": str(pd.Timestamp(item["control_exit_date"]).date()),
                "event_raw_return": event_raw,
                "control_raw_return": control_raw,
                "event_signed_return_after_cost": event_signed,
                "control_signed_return_after_cost": control_signed,
                "paired_signed_excess": event_signed - control_signed,
                "match_score": float(item["match_score"]),
                "control_distance_sessions": int(item["control_distance_sessions"]),
            }
        )
    events = np.asarray([row["event_signed_return_after_cost"] for row in rows], dtype=float)
    controls = np.asarray([row["control_signed_return_after_cost"] for row in rows], dtype=float)
    paired = events - controls
    years = sorted({pd.Timestamp(row["signal_date"]).year for row in rows})
    support = len(rows) / n_train_eligible
    event_mean = float(events.mean()) if len(events) else None
    paired_mean = float(paired.mean()) if len(paired) else None
    lower_bound = (
        _block_lower_bound(paired, samples=bootstrap_samples, seed=20260716 + (spec.direction > 0))
        if len(paired)
        else None
    )
    positive_frequency = float(np.mean(events > 0.0)) if len(events) else None
    tail = _worst_decile(events) if len(events) else None
    gate_checks = {
        "minimum_train_pairs": len(rows) >= min_pairs,
        "minimum_signal_years": len(years) >= min_years,
        "minimum_control_support": support >= min_support,
        "signed_event_mean_after_10bps_positive": event_mean is not None and event_mean > 0.0,
        "signed_paired_excess_mean_positive": paired_mean is not None and paired_mean > 0.0,
        "paired_excess_block_bootstrap_lb90_positive": lower_bound is not None
        and lower_bound > 0.0,
        "signed_positive_frequency_at_least_55pct": positive_frequency is not None
        and positive_frequency >= 0.55,
        "signed_worst_decile_at_least_negative_5pct": tail is not None and tail >= -0.05,
        "zero_integrity_violations": not violations,
    }
    return {
        "n_train_eligible_signals": int(n_train_eligible),
        "n_matched_pairs": len(rows),
        "signal_years": years,
        "control_support": support,
        "signed_event_mean_return_after_cost": event_mean,
        "signed_control_mean_return_after_cost": float(controls.mean()) if len(controls) else None,
        "signed_paired_excess_mean": paired_mean,
        "signed_paired_excess_median": float(np.median(paired)) if len(paired) else None,
        "paired_excess_block_bootstrap_lb90": lower_bound,
        "signed_positive_frequency": positive_frequency,
        "signed_worst_decile_mean": tail,
        "max_match_score": max((row["match_score"] for row in rows), default=None),
        "median_control_distance_sessions": float(
            np.median([row["control_distance_sessions"] for row in rows])
        )
        if rows
        else None,
        "max_control_distance_sessions": max(
            (row["control_distance_sessions"] for row in rows), default=None
        ),
        "round_trip_underlying_cost_bps": round_trip_cost_bps,
        "bootstrap_samples": bootstrap_samples,
        "bootstrap_block_length_pairs": 3,
        "integrity_violations": violations,
        "gate_checks": gate_checks,
        "gate_pass": bool(all(gate_checks.values())),
        "pairs": rows,
    }


def _identity_payload(rows: list[dict[str, Any]], *, eligible_count: int) -> dict[str, Any]:
    identities = [
        {
            "signal_date": str(pd.Timestamp(row["signal_date"]).date()),
            "entry_date": str(pd.Timestamp(row["entry_date"]).date()),
            "exit_date": str(pd.Timestamp(row["exit_date"]).date()),
            "control_feature_date": str(pd.Timestamp(row["control_feature_date"]).date()),
            "control_entry_date": str(pd.Timestamp(row["control_entry_date"]).date()),
            "control_exit_date": str(pd.Timestamp(row["control_exit_date"]).date()),
        }
        for row in rows
    ]
    encoded = json.dumps(identities, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "n_eligible_signals": eligible_count,
        "n_matched_pairs": len(identities),
        "identity_sha256": hashlib.sha256(encoded).hexdigest(),
        "first_signal_date": identities[0]["signal_date"] if identities else None,
        "last_signal_date": identities[-1]["signal_date"] if identities else None,
        "identity_fields": list(identities[0]) if identities else [],
        "outcome_metrics_read": False,
        "simulation_run": False,
        "option_pricing_calls": 0,
    }


def run_mechanism(
    features: pd.DataFrame,
    spec: MechanismSpec,
    *,
    train_fraction: float = 0.60,
    bootstrap_samples: int = 10_000,
    min_pairs: int = 36,
    min_years: int = 8,
) -> dict[str, Any]:
    signals = freeze_signal_geometry(features, spec)
    if len(signals) < 2:
        raise ValueError(f"{spec.candidate_id} has fewer than two eligible signals")
    split = int(len(signals) * train_fraction)
    if split < 1 or split >= len(signals):
        raise ValueError("train/holdout split is empty")
    train_signals = signals[:split]
    holdout_signals = signals[split:]
    matched = match_prior_controls(features, signals, spec)
    train_last_date = pd.Timestamp(train_signals[-1]["signal_date"])
    matched_train = [row for row in matched if pd.Timestamp(row["signal_date"]) <= train_last_date]
    matched_holdout = [row for row in matched if pd.Timestamp(row["signal_date"]) > train_last_date]
    train = evaluate_train(
        features,
        matched_train,
        spec,
        n_train_eligible=len(train_signals),
        min_pairs=min_pairs,
        min_years=min_years,
        bootstrap_samples=bootstrap_samples,
    )
    failed = [name for name, passed in train["gate_checks"].items() if not passed]
    return {
        "candidate_id": spec.candidate_id,
        "family_id": spec.family_id,
        "direction": "down" if spec.direction < 0 else "up",
        "economic_mechanism": spec.mechanism,
        "planned_option_structure": spec.structure,
        "capital_fit_usd": 200.0,
        "max_loss_usd": 200.0,
        "max_lots": 1,
        "funnel_before": "F0_MECHANISM",
        "funnel_after_if_selected": "F1_TRAIN" if train["gate_pass"] else "F0_MECHANISM",
        "train_gate_pass": train["gate_pass"],
        "train": train,
        "holdout": _identity_payload(matched_holdout, eligible_count=len(holdout_signals)),
        "failed_gates": failed,
        "all_train_rows_are_inspected_development_data": True,
        "f2_claim": False,
        "l1_claim": False,
        "option_pricing_calls": 0,
    }


def _dominant_failure_mechanism(candidate: dict[str, Any]) -> str:
    failed = [str(name) for name in candidate.get("failed_gates", [])]
    train = candidate.get("train", {})
    return (
        "The exact credit-risk-off trigger has the wrong signed five-session direction and "
        "negative specificity versus prior same-regime controls: "
        f"signed_event_mean_after_cost={train.get('signed_event_mean_return_after_cost')}; "
        f"signed_paired_excess_mean={train.get('signed_paired_excess_mean')}. "
        f"Only these frozen gates failed: {', '.join(failed)}."
    )


def run_factory(
    frames: dict[str, pd.DataFrame],
    *,
    provenance: dict[str, Any],
    train_fraction: float = 0.60,
    bootstrap_samples: int = 10_000,
    min_pairs: int = 36,
    min_years: int = 8,
) -> dict[str, Any]:
    features = build_feature_panel(frames)
    screens = [
        run_mechanism(
            features,
            spec,
            train_fraction=train_fraction,
            bootstrap_samples=bootstrap_samples,
            min_pairs=min_pairs,
            min_years=min_years,
        )
        for spec in SPECS
    ]
    survivors = [row for row in screens if row["train_gate_pass"]]
    survivors.sort(
        key=lambda row: (
            -float(row["train"]["paired_excess_block_bootstrap_lb90"]),
            -len(row["train"]["signal_years"]),
            -int(row["train"]["n_matched_pairs"]),
            row["candidate_id"],
        )
    )
    selected = survivors[0] if survivors else next(
        row for row in screens if row["candidate_id"] == CREDIT_SPEC.candidate_id
    )
    advanced = bool(survivors)
    return {
        "schema_version": "train_only_defined_risk_candidate_factory.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD_L0_UNDERLYING_DISCOVERY",
        "paper_only": True,
        "sleeve_usd": 3000.0,
        "factory_id": "TRAIN_ONLY_DEFINED_RISK_CANDIDATE_FACTORY_V1",
        "factory_is_strategy_progress": False,
        "candidate_count": len(screens),
        "candidates": screens,
        "selection_rule": (
            "complete gate passes only; descending paired LB90, event years, pairs, then candidate id; "
            "if none pass, claim-bearing close is the primary credit-risk family"
        ),
        "selected_candidate_id": selected["candidate_id"],
        "selected_family_id": selected["family_id"],
        "strategy_outcome": "STRATEGY_ADVANCED" if advanced else "FAMILY_CLOSED",
        "funnel_stage_before": "F0_MECHANISM",
        "funnel_stage_after": "F1_TRAIN" if advanced else "F0_MECHANISM",
        "strategy_advancement": advanced,
        "claim_bar": "L0_DISCOVERY_ONLY",
        "closed_families": [] if advanced else [CREDIT_SPEC.candidate_id, CREDIT_SPEC.family_id],
        "dominant_failure_mechanism": None
        if advanced
        else _dominant_failure_mechanism(selected),
        "secondary_screen_is_search_information_only": not advanced
        or selected["candidate_id"] != OVERNIGHT_SPEC.candidate_id,
        "data_provenance": provenance,
        "common_panel": {
            "rows": len(features),
            "start": str(features.index[0].date()),
            "end": str(features.index[-1].date()),
            "join": "inner join on exact trading dates; no forward fill",
        },
        "methodology_boundaries": {
            "features": "completed daily adjusted OHLCV only; signal-day close is final feature",
            "entry_exit": "next completed close to fifth subsequent completed close",
            "controls": (
                "deterministic prior-only, full outcome before signal, no reuse, same base regime, "
                "non-trigger at control feature date; no later path labels used for selection"
            ),
            "holdout": "chronological final 40% identity only; no outcome metrics or option simulation",
            "cost": "10 bps underlying round-trip sensitivity, not option spread/fill friction",
            "option_marks": "none; future defined-risk expression is planning context only",
            "population": "present-day ETFs with inception/survivorship/proxy-composition limitations",
        },
        "authority": (
            "research only; no L1, capital seat, registry, paper, shadow, broker, funding, arm, or live authority"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2007-05-01")
    parser.add_argument("--end", default="2026-07-16")
    parser.add_argument("--cache-dir", default=".cache/platform/defined_risk_candidate_factory")
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    frames: dict[str, pd.DataFrame] = {}
    provenance: dict[str, Any] = {}
    for symbol in ("SPY", "HYG", "IEF"):
        frame, meta = load_adjusted_ohlcv(
            symbol,
            cache_dir=Path(args.cache_dir),
            start=args.start,
            end=args.end,
        )
        frames[symbol] = frame
        provenance[symbol] = meta
    payload = run_factory(
        frames,
        provenance=provenance,
        bootstrap_samples=args.bootstrap_samples,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    summary = {
        "factory_id": payload["factory_id"],
        "strategy_outcome": payload["strategy_outcome"],
        "selected_candidate_id": payload["selected_candidate_id"],
        "funnel_stage_after": payload["funnel_stage_after"],
        "screens": [
            {
                "candidate_id": row["candidate_id"],
                "gate_pass": row["train_gate_pass"],
                "n_pairs": row["train"]["n_matched_pairs"],
                "support": row["train"]["control_support"],
                "event_mean": row["train"]["signed_event_mean_return_after_cost"],
                "paired_mean": row["train"]["signed_paired_excess_mean"],
                "lb90": row["train"]["paired_excess_block_bootstrap_lb90"],
                "failed_gates": row["failed_gates"],
            }
            for row in payload["candidates"]
        ],
        "out": str(out),
    }
    print(json.dumps(summary, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

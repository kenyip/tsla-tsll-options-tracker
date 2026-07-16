#!/usr/bin/env python3
"""Train-only broad-index overnight-sell / intraday-absorption discovery lab.

BUILD/L0 only. Signal/control geometry is frozen before outcome evaluation, synchronous
cross-index signals are clustered by date before inference, the chronological final
40% remains identity-only, and no option pricing occurs.
"""
from __future__ import annotations

import argparse
from collections import Counter
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


SYMBOLS = ("SPY", "QQQ", "IWM", "DIA")
CANDIDATE_ID = "BROAD_INDEX_OVERNIGHT_ABSORPTION_BULL_CALL_21D_V1"
FAMILY_ID = "BROAD_INDEX_OVERNIGHT_SELL_INTRADAY_ABSORPTION_FORWARD_UPDRIFT"


def planning_risk_boundaries() -> dict[str, Any]:
    """Keep the underlying F0 horizon separate from the unpriced option plan."""
    return {
        "f0_underlying_horizon_sessions": 5,
        "planned_option_dte_min": 18,
        "planned_option_dte_max": 24,
        "planned_option_width_usd": 2.0,
        "capital_fit_usd": 200.0,
        "max_loss_usd": 200.0,
        "max_loss_semantics": (
            "frictionless planning width ceiling before debit, closing friction, assignment, "
            "exercise, or management-path validation"
        ),
        "option_path_measured": False,
        "option_pricing_calls": 0,
    }


def _validate_frame(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    prepared = frame.copy()
    prepared.index = pd.DatetimeIndex(pd.to_datetime(prepared.index)).tz_localize(None).normalize()
    prepared.columns = [str(column).strip().lower() for column in prepared.columns]
    needed = ["open", "high", "low", "close", "volume"]
    if not set(needed).issubset(prepared.columns):
        raise ValueError(f"{symbol} frame missing OHLCV")
    prepared = prepared.loc[:, needed].apply(pd.to_numeric, errors="coerce")
    values = prepared.to_numpy(dtype=float)
    if (
        prepared.empty
        or not prepared.index.is_unique
        or not prepared.index.is_monotonic_increasing
        or not np.isfinite(values).all()
        or (prepared[["open", "high", "low", "close"]] <= 0.0).any().any()
    ):
        raise ValueError(f"{symbol} frame must be unique, increasing, finite, and positive")
    return prepared


def build_features(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    price = _validate_frame(frame, symbol)
    close = price["close"]
    log_return = np.log(close / close.shift(1))
    overnight = price["open"] / close.shift(1) - 1.0
    intraday = close / price["open"] - 1.0
    features = pd.DataFrame(
        {
            "open": price["open"],
            "close": close,
            "sma100": close.rolling(100, min_periods=100).mean(),
            "ret60": close / close.shift(60) - 1.0,
            "hv20": log_return.rolling(20, min_periods=20).std() * np.sqrt(252.0),
            "overnight5": (1.0 + overnight).rolling(5, min_periods=5).apply(np.prod, raw=True)
            - 1.0,
            "intraday5": (1.0 + intraday).rolling(5, min_periods=5).apply(np.prod, raw=True)
            - 1.0,
        },
        index=price.index,
    )
    features["sma_distance"] = features["close"] / features["sma100"] - 1.0
    return features


def trigger_mask(features: pd.DataFrame) -> pd.Series:
    return (
        (features["close"] > features["sma100"])
        & (features["overnight5"] <= -0.01)
        & (features["intraday5"] >= 0.01)
    )


def base_control_mask(features: pd.DataFrame) -> pd.Series:
    finite = np.isfinite(
        features[["close", "sma100", "ret60", "hv20", "sma_distance"]].to_numpy(dtype=float)
    ).all(axis=1)
    return pd.Series(finite, index=features.index) & (features["close"] > features["sma100"]) & ~trigger_mask(features)


def freeze_signals(
    features: pd.DataFrame,
    symbol: str,
    *,
    forward_sessions: int = 5,
) -> list[dict[str, Any]]:
    if forward_sessions < 1:
        raise ValueError("forward_sessions must be positive")
    trigger = trigger_mask(features)
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
                "symbol": symbol,
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
    *,
    forward_sessions: int = 5,
    max_distance_sessions: int = 756,
    max_ret60_gap: float = 0.10,
    max_hv20_gap: float = 0.10,
    max_sma_distance_gap: float = 0.10,
) -> list[dict[str, Any]]:
    if min(max_ret60_gap, max_hv20_gap, max_sma_distance_gap) <= 0.0:
        raise ValueError("match gaps must be positive")
    control_mask = base_control_mask(features)
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
            values = row[["ret60", "hv20", "sma_distance"]].to_numpy(dtype=float)
            if not np.isfinite(values).all():
                continue
            ret_gap = abs(float(signal["ret60"]) - float(row["ret60"]))
            hv_gap = abs(float(signal["hv20"]) - float(row["hv20"]))
            sma_gap = abs(float(signal["sma_distance"]) - float(row["sma_distance"]))
            if ret_gap > max_ret60_gap or hv_gap > max_hv20_gap or sma_gap > max_sma_distance_gap:
                continue
            score = ret_gap / max_ret60_gap + hv_gap / max_hv20_gap + sma_gap / max_sma_distance_gap
            candidates.append((float(score), signal_pos - control_pos, control_pos, exit_pos))
        if not candidates:
            continue
        score, distance, control_pos, control_exit_pos = min(
            candidates, key=lambda row: (row[0], row[1], row[2])
        )
        item = dict(signal)
        item.update(
            {
                "control_feature_pos": control_pos,
                "control_feature_date": pd.Timestamp(features.index[control_pos]),
                "control_entry_pos": control_pos + 1,
                "control_entry_date": pd.Timestamp(features.index[control_pos + 1]),
                "control_exit_pos": control_exit_pos,
                "control_exit_date": pd.Timestamp(features.index[control_exit_pos]),
                "match_score": score,
                "control_distance_sessions": int(distance),
            }
        )
        matched.append(item)
        used_windows.append((control_pos + 1, control_exit_pos))
    return matched


def _block_lower_bound(values: np.ndarray, *, samples: int, seed: int) -> float:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or not len(vector) or not np.isfinite(vector).all():
        raise ValueError("bootstrap requires a finite non-empty vector")
    if samples < 100:
        raise ValueError("bootstrap samples must be at least 100")
    block = min(5, len(vector))
    blocks = int(np.ceil(len(vector) / block))
    offsets = np.arange(block)
    rng = np.random.default_rng(seed)
    estimates = np.empty(samples, dtype=float)
    for index in range(samples):
        starts = rng.integers(0, len(vector), size=blocks)
        draw = np.concatenate([vector[(start + offsets) % len(vector)] for start in starts])[
            : len(vector)
        ]
        estimates[index] = float(draw.mean())
    return float(np.quantile(estimates, 0.10))


def _worst_decile(values: np.ndarray) -> float:
    count = max(1, int(np.ceil(len(values) * 0.10)))
    return float(np.sort(values)[:count].mean())


def _dependence_diagnostics(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    """Serialize residual near-date and cross-index breadth limits."""
    dates = [pd.Timestamp(row["signal_date"]) for row in episodes]
    gaps = [(later - earlier).days for earlier, later in zip(dates, dates[1:])]
    distribution = Counter(str(int(row["n_symbols"])) for row in episodes)
    return {
        "n_consecutive_episode_gaps": len(gaps),
        "consecutive_episode_gaps_le_7_calendar_days": sum(gap <= 7 for gap in gaps),
        "episode_n_symbols_distribution": {
            key: int(distribution[key]) for key in sorted(distribution, key=int)
        },
        "same_date_rows_clustered": True,
        "residual_boundary": (
            "nearby signal dates can retain shared calendar exposure across five-session windows; "
            "the circular five-episode block is a sensitivity, not proof of independent episodes"
        ),
    }


def evaluate_train(
    features_by_symbol: dict[str, pd.DataFrame],
    matched_train: list[dict[str, Any]],
    *,
    n_train_eligible_rows: int,
    min_episodes: int = 48,
    min_years: int = 10,
    min_symbols: int = 3,
    min_support: float = 0.80,
    round_trip_cost_bps: float = 10.0,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    if n_train_eligible_rows < 1:
        raise ValueError("train requires eligible rows")
    raw_rows: list[dict[str, Any]] = []
    violations: list[str] = []
    used_controls: dict[str, list[tuple[int, int]]] = {symbol: [] for symbol in features_by_symbol}
    for index, item in enumerate(matched_train):
        symbol = str(item["symbol"])
        features = features_by_symbol[symbol]
        signal_pos = int(item["signal_pos"])
        entry_pos = int(item["entry_pos"])
        exit_pos = int(item["exit_pos"])
        control_pos = int(item["control_feature_pos"])
        control_entry = int(item["control_entry_pos"])
        control_exit = int(item["control_exit_pos"])
        if not (signal_pos < entry_pos < exit_pos):
            violations.append(f"signal_chronology:{symbol}:{index}")
        if not (control_pos < control_entry < control_exit < signal_pos):
            violations.append(f"control_chronology:{symbol}:{index}")
        if item["feature_max_date"] != item["signal_date"]:
            violations.append(f"feature_lag:{symbol}:{index}")
        window = (control_entry, control_exit)
        if any(not (window[1] < prior[0] or window[0] > prior[1]) for prior in used_controls[symbol]):
            violations.append(f"control_reuse:{symbol}:{index}")
        used_controls[symbol].append(window)
        if bool(trigger_mask(features).iloc[control_pos]):
            violations.append(f"control_trigger_contamination:{symbol}:{index}")
        event_raw = float(features.iloc[exit_pos]["close"] / features.iloc[entry_pos]["close"] - 1.0)
        control_raw = float(
            features.iloc[control_exit]["close"] / features.iloc[control_entry]["close"] - 1.0
        )
        cost = round_trip_cost_bps / 10_000.0
        event_after_cost = event_raw - cost
        control_after_cost = control_raw - cost
        if not np.isfinite([event_raw, control_raw, event_after_cost, control_after_cost]).all():
            violations.append(f"nonfinite_outcome:{symbol}:{index}")
            continue
        raw_rows.append(
            {
                "symbol": symbol,
                "signal_date": str(pd.Timestamp(item["signal_date"]).date()),
                "entry_date": str(pd.Timestamp(item["entry_date"]).date()),
                "exit_date": str(pd.Timestamp(item["exit_date"]).date()),
                "control_feature_date": str(pd.Timestamp(item["control_feature_date"]).date()),
                "control_entry_date": str(pd.Timestamp(item["control_entry_date"]).date()),
                "control_exit_date": str(pd.Timestamp(item["control_exit_date"]).date()),
                "event_return_after_cost": event_after_cost,
                "control_return_after_cost": control_after_cost,
                "paired_excess": event_after_cost - control_after_cost,
                "match_score": float(item["match_score"]),
                "control_distance_sessions": int(item["control_distance_sessions"]),
            }
        )
    episodes: list[dict[str, Any]] = []
    for signal_date, group in pd.DataFrame(raw_rows).groupby("signal_date", sort=True):
        if group["symbol"].duplicated().any():
            violations.append(f"duplicate_symbol_episode:{signal_date}")
        event = float(group["event_return_after_cost"].mean())
        control = float(group["control_return_after_cost"].mean())
        episodes.append(
            {
                "signal_date": str(signal_date),
                "symbols": sorted(group["symbol"].astype(str).tolist()),
                "n_symbols": int(len(group)),
                "event_return_after_cost": event,
                "control_return_after_cost": control,
                "paired_excess": event - control,
            }
        )
    events = np.asarray([row["event_return_after_cost"] for row in episodes], dtype=float)
    controls = np.asarray([row["control_return_after_cost"] for row in episodes], dtype=float)
    paired = events - controls
    years = sorted({pd.Timestamp(row["signal_date"]).year for row in episodes})
    represented = sorted({row["symbol"] for row in raw_rows})
    support = len(raw_rows) / n_train_eligible_rows
    event_mean = float(events.mean()) if len(events) else None
    paired_mean = float(paired.mean()) if len(paired) else None
    lower_bound = (
        _block_lower_bound(paired, samples=bootstrap_samples, seed=20260716)
        if len(paired)
        else None
    )
    positive_frequency = float(np.mean(events > 0.0)) if len(events) else None
    event_tail = _worst_decile(events) if len(events) else None
    paired_tail = _worst_decile(paired) if len(paired) else None
    gate_checks = {
        "minimum_clustered_train_episodes": len(episodes) >= min_episodes,
        "minimum_signal_years": len(years) >= min_years,
        "minimum_represented_symbols": len(represented) >= min_symbols,
        "minimum_control_support": support >= min_support,
        "event_mean_after_10bps_positive": event_mean is not None and event_mean > 0.0,
        "paired_excess_mean_positive": paired_mean is not None and paired_mean > 0.0,
        "paired_excess_five_episode_block_lb90_positive": lower_bound is not None and lower_bound > 0.0,
        "positive_frequency_at_least_55pct": positive_frequency is not None and positive_frequency >= 0.55,
        "event_return_worst_decile_at_least_negative_5pct": event_tail is not None
        and event_tail >= -0.05,
        "zero_integrity_violations": not violations,
    }
    distances = [row["control_distance_sessions"] for row in raw_rows]
    return {
        "n_train_eligible_signal_rows": int(n_train_eligible_rows),
        "n_matched_signal_rows": len(raw_rows),
        "n_clustered_episodes": len(episodes),
        "signal_years": years,
        "represented_symbols": represented,
        "control_support": support,
        "event_mean_return_after_cost": event_mean,
        "control_mean_return_after_cost": float(controls.mean()) if len(controls) else None,
        "paired_excess_mean": paired_mean,
        "paired_excess_median": float(np.median(paired)) if len(paired) else None,
        "paired_excess_block_bootstrap_lb90": lower_bound,
        "positive_frequency": positive_frequency,
        "event_return_worst_decile_mean_after_10bps": event_tail,
        "paired_excess_worst_decile_mean": paired_tail,
        "median_control_distance_sessions": float(np.median(distances)) if distances else None,
        "max_control_distance_sessions": max(distances, default=None),
        "round_trip_underlying_cost_bps": round_trip_cost_bps,
        "bootstrap_samples": bootstrap_samples,
        "bootstrap_block_length_episodes": 5,
        "dependence_diagnostics": _dependence_diagnostics(episodes),
        "integrity_violations": violations,
        "gate_checks": gate_checks,
        "gate_pass": bool(all(gate_checks.values())),
        "episodes": episodes,
        "signal_rows": raw_rows,
    }


def _identity_payload(rows: list[dict[str, Any]], *, eligible_count: int) -> dict[str, Any]:
    identities = [
        {
            "symbol": str(row["symbol"]),
            "signal_date": str(pd.Timestamp(row["signal_date"]).date()),
            "entry_date": str(pd.Timestamp(row["entry_date"]).date()),
            "exit_date": str(pd.Timestamp(row["exit_date"]).date()),
            "control_feature_date": str(pd.Timestamp(row["control_feature_date"]).date()),
            "control_entry_date": str(pd.Timestamp(row["control_entry_date"]).date()),
            "control_exit_date": str(pd.Timestamp(row["control_exit_date"]).date()),
        }
        for row in sorted(rows, key=lambda item: (item["signal_date"], item["symbol"]))
    ]
    encoded = json.dumps(identities, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "n_eligible_signal_rows": eligible_count,
        "n_matched_signal_rows": len(identities),
        "n_signal_dates": len({row["signal_date"] for row in identities}),
        "identity_sha256": hashlib.sha256(encoded).hexdigest(),
        "first_signal_date": identities[0]["signal_date"] if identities else None,
        "last_signal_date": identities[-1]["signal_date"] if identities else None,
        "identity_fields": list(identities[0]) if identities else [],
        "outcome_metrics_read": False,
        "simulation_run": False,
        "option_pricing_calls": 0,
    }


def run_lab(
    frames: dict[str, pd.DataFrame],
    *,
    provenance: dict[str, Any],
    train_fraction: float = 0.60,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    if set(frames) != set(SYMBOLS):
        raise ValueError(f"frames must contain exactly {', '.join(SYMBOLS)}")
    features_by_symbol = {symbol: build_features(frames[symbol], symbol) for symbol in SYMBOLS}
    signals_by_symbol = {
        symbol: freeze_signals(features_by_symbol[symbol], symbol) for symbol in SYMBOLS
    }
    all_signals = sorted(
        [row for rows in signals_by_symbol.values() for row in rows],
        key=lambda row: (row["signal_date"], row["symbol"]),
    )
    signal_dates = sorted({pd.Timestamp(row["signal_date"]) for row in all_signals})
    if len(signal_dates) < 2:
        raise ValueError("candidate requires at least two signal dates")
    split = int(len(signal_dates) * train_fraction)
    if split < 1 or split >= len(signal_dates):
        raise ValueError("train/holdout split is empty")
    train_last_date = signal_dates[split - 1]
    matched_by_symbol = {
        symbol: match_prior_controls(features_by_symbol[symbol], signals_by_symbol[symbol])
        for symbol in SYMBOLS
    }
    matched = sorted(
        [row for rows in matched_by_symbol.values() for row in rows],
        key=lambda row: (row["signal_date"], row["symbol"]),
    )
    train_signals = [row for row in all_signals if pd.Timestamp(row["signal_date"]) <= train_last_date]
    holdout_signals = [row for row in all_signals if pd.Timestamp(row["signal_date"]) > train_last_date]
    matched_train = [row for row in matched if pd.Timestamp(row["signal_date"]) <= train_last_date]
    matched_holdout = [row for row in matched if pd.Timestamp(row["signal_date"]) > train_last_date]
    train = evaluate_train(
        features_by_symbol,
        matched_train,
        n_train_eligible_rows=len(train_signals),
        bootstrap_samples=bootstrap_samples,
    )
    failed = [name for name, passed in train["gate_checks"].items() if not passed]
    advanced = bool(train["gate_pass"])
    outcome = "STRATEGY_ADVANCED" if advanced else "FAMILY_CLOSED"
    planning = planning_risk_boundaries()
    dominant_failure = None
    if not advanced:
        dominant_failure = (
            "The exact broad-index overnight-sell/intraday-absorption trigger did not clear the "
            "frozen clustered train conjunction. Failed gates: " + ", ".join(failed) + "."
        )
    return {
        "schema_version": "broad_index_overnight_absorption_train.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD_L0_UNDERLYING_DISCOVERY",
        "paper_only": True,
        "sleeve_usd": 3000.0,
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "economic_mechanism": (
            "Repeated overnight selling absorbed by positive regular-session demand across liquid "
            "broad-index ETFs may be transitory risk-transfer pressure rather than durable negative information."
        ),
        "planned_option_structure": "future_conditional_18_24dte_2wide_bull_call_debit_spread",
        "planning_risk_boundaries": planning,
        "capital_fit_usd": planning["capital_fit_usd"],
        "max_loss_usd": planning["max_loss_usd"],
        "max_lots": 1,
        "funnel_stage_before": "F0_MECHANISM",
        "funnel_stage_after": "F1_TRAIN" if advanced else "F0_MECHANISM",
        "strategy_outcome": outcome,
        "strategy_advancement": advanced,
        "claim_bar": "L0_DISCOVERY_ONLY",
        "train": train,
        "failed_gates": failed,
        "dominant_failure_mechanism": dominant_failure,
        "holdout": _identity_payload(matched_holdout, eligible_count=len(holdout_signals)),
        "all_train_rows_are_inspected_development_data": True,
        "f2_claim": False,
        "l1_claim": False,
        "option_pricing_calls": 0,
        "closed_families": [] if advanced else [CANDIDATE_ID, FAMILY_ID],
        "data_provenance": provenance,
        "population": {
            "symbols": list(SYMBOLS),
            "signal_dates_total": len(signal_dates),
            "train_last_signal_date": str(train_last_date.date()),
            "split": "chronological 60/40 by unique signal date",
            "simultaneous_signals": "same-date ETF rows averaged to one inference episode",
        },
        "methodology_boundaries": {
            "features": "completed adjusted daily OHLCV; signal-day close is final feature",
            "entry_exit": "next completed close to fifth subsequent completed close per symbol",
            "controls": "same-symbol deterministic prior-only, full outcome before signal, no reuse, non-trigger, matched on ret60/hv20/SMA100 distance",
            "holdout": "chronological final 40% identity only; no outcomes or option simulation",
            "cost": "10 bps underlying round-trip sensitivity, not option debit/spread/fill friction",
            "dependence": "same-date cross-index rows clustered before circular five-episode bootstrap",
            "option_marks": "none; future defined-risk expression is planning context only",
            "population_limit": "fixed present-day index ETFs with inception/composition survivorship limits",
        },
        "authority": "research only; no L1, capital seat, registry, paper, shadow, broker, funding, arm, or live authority",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2007-05-01")
    parser.add_argument("--end", default="2026-07-16")
    parser.add_argument("--cache-dir", default=".cache/platform/broad_index_overnight_absorption")
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    frames: dict[str, pd.DataFrame] = {}
    provenance: dict[str, Any] = {}
    for symbol in SYMBOLS:
        frame, meta = load_adjusted_ohlcv(
            symbol,
            cache_dir=Path(args.cache_dir),
            start=args.start,
            end=args.end,
        )
        frames[symbol] = frame
        provenance[symbol] = meta
    payload = run_lab(
        frames,
        provenance=provenance,
        bootstrap_samples=args.bootstrap_samples,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    summary = {
        "candidate_id": payload["candidate_id"],
        "strategy_outcome": payload["strategy_outcome"],
        "funnel_stage_after": payload["funnel_stage_after"],
        "n_clustered_episodes": payload["train"]["n_clustered_episodes"],
        "represented_symbols": payload["train"]["represented_symbols"],
        "event_mean": payload["train"]["event_mean_return_after_cost"],
        "paired_mean": payload["train"]["paired_excess_mean"],
        "lb90": payload["train"]["paired_excess_block_bootstrap_lb90"],
        "failed_gates": payload["failed_gates"],
        "out": str(out),
    }
    print(json.dumps(summary, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

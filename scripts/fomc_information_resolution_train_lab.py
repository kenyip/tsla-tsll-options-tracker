#!/usr/bin/env python3
"""Train-only FOMC policy-information-resolution discovery lab.

BUILD/L0 only. Official prior-known release timestamps define events. The lab
keeps the chronological final 40% of eligible blueprints outcome-unread and
performs no option pricing.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import re

import numpy as np
import pandas as pd
import yfinance as yf


FED_BASE_URL = "https://www.federalreserve.gov"
FED_PRESS_JSON_URL = f"{FED_BASE_URL}/json/ne-press.json"
EVENT_TITLE = "Federal Reserve issues FOMC statement"
PRESS_TYPE = "Monetary Policy"
STATEMENT_PATH = re.compile(r"^/newsevents/pressreleases/monetary\d{8}a\.htm$")
NEW_YORK = "America/New_York"
CANDIDATE_ID = "FOMC_INFORMATION_RESOLUTION_SPY_BULL_CALL_21D_V1"
FAMILY_ID = "FOMC_POLICY_INFORMATION_RESOLUTION_DRIFT"


def _fetch_url_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "TraderResearch/1.0"})
    with urlopen(request, timeout=45) as response:
        return response.read()


def load_official_press_records(
    cache_path: Path,
    *,
    fetch_bytes: Callable[[str], bytes] = _fetch_url_bytes,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Persist and replay exact bytes from the Federal Reserve press index."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if not cache_path.exists():
        payload = fetch_bytes(FED_PRESS_JSON_URL)
        if not payload:
            raise ValueError("Federal Reserve press source returned no bytes")
        cache_path.write_bytes(payload)
    raw = cache_path.read_bytes()
    try:
        decoded = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Federal Reserve press cache is not valid UTF-8 JSON") from exc
    if not isinstance(decoded, list) or not decoded or not all(
        isinstance(record, dict) for record in decoded
    ):
        raise ValueError("Federal Reserve press cache must be a non-empty record list")
    records = [dict(record) for record in decoded]
    return records, {
        "url": FED_PRESS_JSON_URL,
        "path": str(cache_path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "records": len(records),
        "timestamp_semantics": "feed-local timestamps interpreted as America/New_York",
    }


def parse_official_fomc_events(
    records: Iterable[dict[str, Any]], *, start: str, end: str
) -> pd.DataFrame:
    """Select exact regular 14:00 ET FOMC statement records from the Fed feed."""
    start_date = pd.Timestamp(start).normalize()
    end_date = pd.Timestamp(end).normalize()
    if start_date > end_date:
        raise ValueError("event start must not exceed end")
    excluded = {
        "excluded_non_2pm": 0,
        "excluded_wrong_title": 0,
        "excluded_wrong_press_type": 0,
        "excluded_bad_url": 0,
        "excluded_outside_window": 0,
    }
    rows: list[dict[str, Any]] = []
    for record in records:
        title = str(record.get("t", ""))
        if title != EVENT_TITLE:
            excluded["excluded_wrong_title"] += 1
            continue
        if str(record.get("pt", "")) != PRESS_TYPE:
            excluded["excluded_wrong_press_type"] += 1
            continue
        path = str(record.get("l", ""))
        if not STATEMENT_PATH.fullmatch(path):
            excluded["excluded_bad_url"] += 1
            continue
        try:
            naive = pd.Timestamp(str(record.get("d", "")))
        except (TypeError, ValueError) as exc:
            raise ValueError("Fed release timestamp is malformed") from exc
        if naive.tzinfo is not None:
            raise ValueError("Fed release timestamps must use feed-local naive time")
        decision_date = naive.normalize()
        if not start_date <= decision_date <= end_date:
            excluded["excluded_outside_window"] += 1
            continue
        if naive.time().isoformat() != "14:00:00":
            excluded["excluded_non_2pm"] += 1
            continue
        release_at = naive.tz_localize(NEW_YORK, ambiguous="raise", nonexistent="raise")
        rows.append(
            {
                "decision_date": decision_date,
                "release_at_new_york": release_at,
                "statement_url": urljoin(FED_BASE_URL, path),
                "source_title": title,
                "source_press_type": PRESS_TYPE,
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise ValueError("no exact 14:00 ET FOMC statement events remain")
    frame = frame.sort_values(["decision_date", "statement_url"]).drop_duplicates(
        ["decision_date"], keep=False
    )
    if frame.empty:
        raise ValueError("event dates are duplicated or absent")
    frame = frame.reset_index(drop=True)
    frame.attrs.update(excluded)
    frame.attrs["source_url"] = FED_PRESS_JSON_URL
    return frame


def load_adjusted_ohlcv(
    symbol: str,
    *,
    cache_dir: Path,
    start: str,
    end: str,
    downloader: Any = yf.download,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load and hash the exact persisted auto-adjusted OHLCV representation."""
    normalized = str(symbol).strip().upper()
    if not normalized or not re.fullmatch(r"[A-Z][A-Z0-9.-]*", normalized):
        raise ValueError("valid symbol is required")
    if pd.Timestamp(start) >= pd.Timestamp(end):
        raise ValueError("history start must precede end")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{normalized}_{start}_{end}_auto_adjust_ohlcv.csv"
    if not cache_path.exists():
        downloaded = downloader(
            normalized,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
        )
        if isinstance(downloaded.columns, pd.MultiIndex):
            downloaded.columns = downloaded.columns.get_level_values(0)
        required = ["Open", "High", "Low", "Close", "Volume"]
        if downloaded.empty or not set(required).issubset(downloaded.columns):
            raise ValueError(f"{normalized} adjusted download missing OHLCV")
        persisted = downloaded.loc[:, required].copy()
        persisted.columns = [column.lower() for column in required]
        persisted.to_csv(cache_path)
    raw = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    raw.columns = [str(column).strip().lower() for column in raw.columns]
    if list(raw.columns) != ["open", "high", "low", "close", "volume"]:
        raise ValueError(f"{normalized} cache must contain exact OHLCV columns")
    while len(raw) and raw.iloc[-1].isna().any():
        raw = raw.iloc[:-1]
    prepared = _validate_price_frame(raw)
    return prepared, {
        "path": str(cache_path),
        "sha256": hashlib.sha256(cache_path.read_bytes()).hexdigest(),
        "rows": int(len(prepared)),
        "start": str(prepared.index[0].date()),
        "end": str(prepared.index[-1].date()),
        "adjustment_semantics": "yfinance auto_adjust=True",
        "requested_start": start,
        "requested_end_exclusive": end,
    }


def _validate_price_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"open", "high", "low", "close", "volume"}
    if not required.issubset(frame.columns):
        raise ValueError("price frame requires open/high/low/close/volume")
    prepared = frame.copy()
    prepared.index = pd.DatetimeIndex(pd.to_datetime(prepared.index)).tz_localize(None).normalize()
    prepared = prepared.loc[:, ["open", "high", "low", "close", "volume"]].apply(
        pd.to_numeric, errors="coerce"
    )
    if (
        prepared.empty
        or not prepared.index.is_unique
        or not prepared.index.is_monotonic_increasing
        or not np.isfinite(prepared.to_numpy(dtype=float)).all()
        or (prepared[["open", "high", "low", "close"]] <= 0.0).any().any()
    ):
        raise ValueError("price frame must be finite, positive, unique, and increasing")
    if (prepared["high"] < prepared[["open", "close"]].max(axis=1)).any() or (
        prepared["low"] > prepared[["open", "close"]].min(axis=1)
    ).any():
        raise ValueError("price frame OHLC geometry is invalid")
    return prepared


def _feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    close = frame["close"].astype(float)
    log_return = np.log(close / close.shift(1))
    return pd.DataFrame(
        {
            "sma100": close.rolling(100, min_periods=100).mean(),
            "ret60": close / close.shift(60) - 1.0,
            "hv20": log_return.rolling(20, min_periods=20).std() * np.sqrt(252.0),
        },
        index=frame.index,
    )


def _windows_overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return not (left[1] < right[0] or left[0] > right[1])


def build_fomc_matched_blueprints(
    price_frame: pd.DataFrame,
    events: pd.DataFrame,
    *,
    control_exclusion_events: pd.DataFrame | None = None,
    forward_sessions: int = 5,
    max_distance_sessions: int = 756,
    max_hv20_gap: float = 0.10,
    max_ret60_gap: float = 0.10,
    event_exclusion_sessions: int = 5,
) -> list[dict[str, Any]]:
    """Freeze outcome-independent event/control geometry from prior-completed features."""
    frame = _validate_price_frame(price_frame)
    if forward_sessions < 1 or max_distance_sessions <= forward_sessions:
        raise ValueError("forward and matching distances are invalid")
    if min(max_hv20_gap, max_ret60_gap) <= 0.0 or event_exclusion_sessions < 0:
        raise ValueError("feature gaps must be positive and exclusion non-negative")
    required = {"decision_date", "release_at_new_york", "statement_url"}
    if not required.issubset(events.columns) or events.empty:
        raise ValueError("events require decision_date, release_at_new_york, and statement_url")
    event_table = events.copy()
    event_table["decision_date"] = pd.to_datetime(event_table["decision_date"]).dt.tz_localize(None).dt.normalize()
    if event_table["decision_date"].duplicated().any():
        raise ValueError("event decision dates must be unique")
    event_table = event_table.sort_values("decision_date").reset_index(drop=True)
    exclusion_table = event_table if control_exclusion_events is None else control_exclusion_events.copy()
    if "decision_date" not in exclusion_table.columns or exclusion_table.empty:
        raise ValueError("control exclusion events require decision_date")
    exclusion_table["decision_date"] = (
        pd.to_datetime(exclusion_table["decision_date"]).dt.tz_localize(None).dt.normalize()
    )
    if exclusion_table["decision_date"].duplicated().any():
        raise ValueError("control exclusion event dates must be unique")
    index = frame.index
    positions = {pd.Timestamp(value): position for position, value in enumerate(index)}
    features = _feature_frame(frame)
    event_positions = [
        positions[date]
        for date in exclusion_table["decision_date"]
        if date in positions
    ]
    source_coverage_start_pos = (
        0
        if control_exclusion_events is None
        else (min(event_positions) if event_positions else len(index))
    )
    excluded_control_features: set[int] = set()
    for position in event_positions:
        excluded_control_features.update(
            range(
                max(0, position - event_exclusion_sessions),
                min(len(index), position + event_exclusion_sessions + 1),
            )
        )
    used_control_windows: list[tuple[int, int]] = []
    occupied_event_windows: list[tuple[int, int]] = []
    blueprints: list[dict[str, Any]] = []
    for event in event_table.itertuples(index=False):
        decision_date = pd.Timestamp(event.decision_date)
        decision_pos = positions.get(decision_date)
        if decision_pos is None:
            continue
        feature_pos = decision_pos - 1
        entry_pos = decision_pos + 1
        exit_pos = entry_pos + forward_sessions - 1
        if feature_pos < 99 or exit_pos >= len(index):
            continue
        event_feature = features.iloc[feature_pos]
        if not np.isfinite(event_feature.to_numpy(dtype=float)).all():
            continue
        event_close = float(frame.iloc[feature_pos]["close"])
        if not (
            event_close > float(event_feature["sma100"])
            and float(event_feature["ret60"]) > 0.0
        ):
            continue
        event_window = (entry_pos, exit_pos)
        if any(_windows_overlap(event_window, prior) for prior in occupied_event_windows):
            continue
        lower = max(99, source_coverage_start_pos, feature_pos - max_distance_sessions)
        candidates: list[tuple[float, int, int, int]] = []
        for control_feature_pos in range(lower, feature_pos):
            if control_feature_pos in excluded_control_features:
                continue
            control_entry_pos = control_feature_pos + 1
            control_exit_pos = control_entry_pos + forward_sessions - 1
            if any(
                position in excluded_control_features
                for position in range(control_feature_pos, control_exit_pos + 1)
            ):
                continue
            if control_exit_pos >= decision_pos:
                continue
            control_window = (control_entry_pos, control_exit_pos)
            if any(_windows_overlap(control_window, prior) for prior in used_control_windows):
                continue
            if any(_windows_overlap(control_window, prior) for prior in occupied_event_windows):
                continue
            control_feature = features.iloc[control_feature_pos]
            if not np.isfinite(control_feature.to_numpy(dtype=float)).all():
                continue
            control_close = float(frame.iloc[control_feature_pos]["close"])
            if not (
                control_close > float(control_feature["sma100"])
                and float(control_feature["ret60"]) > 0.0
            ):
                continue
            hv_gap = abs(float(event_feature["hv20"]) - float(control_feature["hv20"]))
            ret_gap = abs(float(event_feature["ret60"]) - float(control_feature["ret60"]))
            if hv_gap > max_hv20_gap or ret_gap > max_ret60_gap:
                continue
            distance = feature_pos - control_feature_pos
            score = hv_gap / max_hv20_gap + ret_gap / max_ret60_gap
            candidates.append((float(score), distance, control_feature_pos, control_exit_pos))
        if not candidates:
            continue
        score, distance, control_feature_pos, control_exit_pos = min(
            candidates, key=lambda row: (row[0], row[1], row[2])
        )
        control_entry_pos = control_feature_pos + 1
        control_feature = features.iloc[control_feature_pos]
        blueprints.append(
            {
                "decision_date": decision_date,
                "release_at_new_york": str(event.release_at_new_york),
                "statement_url": str(event.statement_url),
                "feature_date": pd.Timestamp(index[feature_pos]),
                "event_entry_date": pd.Timestamp(index[entry_pos]),
                "event_exit_date": pd.Timestamp(index[exit_pos]),
                "event_ret60": float(event_feature["ret60"]),
                "event_hv20": float(event_feature["hv20"]),
                "control_feature_date": pd.Timestamp(index[control_feature_pos]),
                "control_entry_date": pd.Timestamp(index[control_entry_pos]),
                "control_exit_date": pd.Timestamp(index[control_exit_pos]),
                "control_ret60": float(control_feature["ret60"]),
                "control_hv20": float(control_feature["hv20"]),
                "ret60_match_gap": abs(
                    float(event_feature["ret60"]) - float(control_feature["ret60"])
                ),
                "hv20_match_gap": abs(
                    float(event_feature["hv20"]) - float(control_feature["hv20"])
                ),
                "match_score": score,
                "calendar_distance_sessions": int(distance),
            }
        )
        used_control_windows.append((control_entry_pos, control_exit_pos))
        occupied_event_windows.append(event_window)
    return blueprints


def _eligible_event_geometry(
    frame: pd.DataFrame, events: pd.DataFrame, *, forward_sessions: int
) -> list[dict[str, Any]]:
    index = frame.index
    positions = {pd.Timestamp(value): position for position, value in enumerate(index)}
    features = _feature_frame(frame)
    geometry: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    for event in events.sort_values("decision_date").itertuples(index=False):
        decision_date = pd.Timestamp(event.decision_date).tz_localize(None).normalize()
        decision_pos = positions.get(decision_date)
        if decision_pos is None:
            continue
        feature_pos = decision_pos - 1
        entry_pos = decision_pos + 1
        exit_pos = entry_pos + forward_sessions - 1
        if feature_pos < 99 or exit_pos >= len(index):
            continue
        feature = features.iloc[feature_pos]
        if not np.isfinite(feature.to_numpy(dtype=float)).all():
            continue
        if not (
            float(frame.iloc[feature_pos]["close"]) > float(feature["sma100"])
            and float(feature["ret60"]) > 0.0
        ):
            continue
        window = (entry_pos, exit_pos)
        if any(_windows_overlap(window, prior) for prior in occupied):
            continue
        geometry.append(
            {
                "decision_date": decision_date,
                "feature_date": pd.Timestamp(index[feature_pos]),
                "event_entry_date": pd.Timestamp(index[entry_pos]),
                "event_exit_date": pd.Timestamp(index[exit_pos]),
                "statement_url": str(event.statement_url),
            }
        )
        occupied.append(window)
    return geometry


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False, default=str
    ).encode("utf-8")


def _finite_or_none(value: float) -> float | None:
    return float(value) if math.isfinite(float(value)) else None


def _year_block_bootstrap_lower_bound(
    differences: np.ndarray,
    years: np.ndarray,
    *,
    samples: int,
    seed: int,
    alpha: float = 0.10,
) -> float | None:
    if len(differences) == 0 or samples < 100:
        return None
    unique_years = np.array(sorted(set(int(year) for year in years)), dtype=int)
    if len(unique_years) == 0:
        return None
    grouped = {year: differences[years == year] for year in unique_years}
    rng = np.random.default_rng(seed)
    draws = np.empty(samples, dtype=float)
    for draw in range(samples):
        sampled_years = rng.choice(unique_years, size=len(unique_years), replace=True)
        sampled = np.concatenate([grouped[int(year)] for year in sampled_years])
        draws[draw] = float(np.mean(sampled))
    return float(np.quantile(draws, alpha))


def run_lab_from_frame(
    price_frame: pd.DataFrame,
    events: pd.DataFrame,
    *,
    provenance: dict[str, Any],
    control_exclusion_events: pd.DataFrame | None = None,
    train_fraction: float = 0.60,
    forward_sessions: int = 5,
    round_trip_cost_bps: float = 10.0,
    max_distance_sessions: int = 756,
    max_hv20_gap: float = 0.10,
    max_ret60_gap: float = 0.10,
    event_exclusion_sessions: int = 5,
    min_train_pairs: int = 36,
    min_event_years: int = 6,
    min_control_support: float = 0.80,
    min_positive_frequency: float = 0.55,
    worst_decile_floor: float = -0.05,
    bootstrap_samples: int = 20_000,
    bootstrap_seed: int = 20260716,
) -> dict[str, Any]:
    """Evaluate only the chronological train partition; seal holdout outcomes."""
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be strictly between zero and one")
    if round_trip_cost_bps < 0.0:
        raise ValueError("round-trip cost must be non-negative")
    frame = _validate_price_frame(price_frame)
    exclusion_events = events if control_exclusion_events is None else control_exclusion_events
    if "decision_date" not in exclusion_events.columns or exclusion_events.empty:
        raise ValueError("control exclusion events require decision_date")
    eligible = _eligible_event_geometry(frame, events, forward_sessions=forward_sessions)
    if len(eligible) < 2:
        raise ValueError("fewer than two eligible event blueprints")
    split_index = int(math.floor(len(eligible) * train_fraction))
    if split_index <= 0 or split_index >= len(eligible):
        raise ValueError("chronological split produced an empty partition")
    train_eligible = eligible[:split_index]
    holdout_eligible = eligible[split_index:]
    matched = build_fomc_matched_blueprints(
        frame,
        events,
        control_exclusion_events=exclusion_events,
        forward_sessions=forward_sessions,
        max_distance_sessions=max_distance_sessions,
        max_hv20_gap=max_hv20_gap,
        max_ret60_gap=max_ret60_gap,
        event_exclusion_sessions=event_exclusion_sessions,
    )
    matched_by_date = {pd.Timestamp(row["decision_date"]): row for row in matched}
    train_rows = [
        matched_by_date[row["decision_date"]]
        for row in train_eligible
        if row["decision_date"] in matched_by_date
    ]
    holdout_rows = [
        matched_by_date[row["decision_date"]]
        for row in holdout_eligible
        if row["decision_date"] in matched_by_date
    ]
    train_dates = {pd.Timestamp(row["decision_date"]) for row in train_eligible}
    if any(pd.Timestamp(row["decision_date"]) not in train_dates for row in train_rows):
        raise AssertionError("holdout row entered train evaluation")
    event_returns: list[float] = []
    control_returns: list[float] = []
    pair_audit: list[dict[str, Any]] = []
    years: list[int] = []
    cost = round_trip_cost_bps / 10_000.0
    for row in train_rows:
        event_entry = float(frame.loc[row["event_entry_date"], "open"])
        event_exit = float(frame.loc[row["event_exit_date"], "close"])
        control_entry = float(frame.loc[row["control_entry_date"], "open"])
        control_exit = float(frame.loc[row["control_exit_date"], "close"])
        event_net = event_exit / event_entry - 1.0 - cost
        control_net = control_exit / control_entry - 1.0 - cost
        event_returns.append(event_net)
        control_returns.append(control_net)
        years.append(pd.Timestamp(row["decision_date"]).year)
        pair_audit.append(
            {
                "decision_date": str(pd.Timestamp(row["decision_date"]).date()),
                "feature_date": str(pd.Timestamp(row["feature_date"]).date()),
                "event_entry_date": str(pd.Timestamp(row["event_entry_date"]).date()),
                "event_exit_date": str(pd.Timestamp(row["event_exit_date"]).date()),
                "control_feature_date": str(
                    pd.Timestamp(row["control_feature_date"]).date()
                ),
                "control_entry_date": str(pd.Timestamp(row["control_entry_date"]).date()),
                "control_exit_date": str(pd.Timestamp(row["control_exit_date"]).date()),
                "event_return_after_cost": event_net,
                "control_return_after_cost": control_net,
                "paired_excess": event_net - control_net,
                "event_ret60": float(row["event_ret60"]),
                "control_ret60": float(row["control_ret60"]),
                "event_hv20": float(row["event_hv20"]),
                "control_hv20": float(row["control_hv20"]),
                "ret60_match_gap": float(row["ret60_match_gap"]),
                "hv20_match_gap": float(row["hv20_match_gap"]),
                "calendar_distance_sessions": int(row["calendar_distance_sessions"]),
                "statement_url": str(row["statement_url"]),
            }
        )
    event_array = np.asarray(event_returns, dtype=float)
    control_array = np.asarray(control_returns, dtype=float)
    year_array = np.asarray(years, dtype=int)
    paired = event_array - control_array
    pair_count = len(train_rows)
    event_years = len(set(years))
    support = pair_count / len(train_eligible) if train_eligible else 0.0
    mean_event = float(np.mean(event_array)) if pair_count else float("nan")
    mean_control = float(np.mean(control_array)) if pair_count else float("nan")
    mean_paired = float(np.mean(paired)) if pair_count else float("nan")
    positive_frequency = float(np.mean(paired > 0.0)) if pair_count else float("nan")
    worst_decile = float(np.quantile(event_array, 0.10)) if pair_count else float("nan")
    bootstrap_lb = _year_block_bootstrap_lower_bound(
        paired,
        year_array,
        samples=bootstrap_samples,
        seed=bootstrap_seed,
    )
    control_exit_dates = [pd.Timestamp(row["control_exit_date"]) for row in train_rows]
    decision_dates = [pd.Timestamp(row["decision_date"]) for row in train_rows]
    control_windows = [
        (pd.Timestamp(row["control_entry_date"]), pd.Timestamp(row["control_exit_date"]))
        for row in train_rows
    ]
    frame_positions = {
        pd.Timestamp(value): position for position, value in enumerate(frame.index)
    }
    official_event_positions = [
        frame_positions[date]
        for date in pd.to_datetime(exclusion_events["decision_date"])
        .dt.tz_localize(None)
        .dt.normalize()
        if date in frame_positions
    ]
    exclusion_positions: set[int] = set()
    for event_position in official_event_positions:
        exclusion_positions.update(
            range(
                max(0, event_position - event_exclusion_sessions),
                min(len(frame), event_position + event_exclusion_sessions + 1),
            )
        )
    controls_outside_exclusion = all(
        all(
            position not in exclusion_positions
            for position in range(
                frame_positions[pd.Timestamp(row["control_feature_date"])],
                frame_positions[pd.Timestamp(row["control_exit_date"])] + 1,
            )
        )
        for row in train_rows
    )
    source_coverage_start = (
        pd.to_datetime(exclusion_events["decision_date"])
        .dt.tz_localize(None)
        .dt.normalize()
        .min()
    )
    integrity = {
        "control_outcomes_complete_before_event": all(
            control_exit < decision
            for control_exit, decision in zip(control_exit_dates, decision_dates)
        ),
        "control_windows_unique": len(control_windows) == len(set(control_windows)),
        "control_windows_nonoverlapping": all(
            not (left[0] <= right[1] and right[0] <= left[1])
            for index, left in enumerate(control_windows)
            for right in control_windows[index + 1 :]
        ),
        "control_windows_outside_event_exclusion_bands": controls_outside_exclusion,
        "control_windows_within_source_coverage": all(
            pd.Timestamp(row["control_feature_date"]) >= source_coverage_start
            for row in train_rows
        ),
        "match_gaps_within_bounds": all(
            float(row["hv20_match_gap"]) <= max_hv20_gap
            and float(row["ret60_match_gap"]) <= max_ret60_gap
            for row in train_rows
        ),
        "train_precedes_holdout": train_eligible[-1]["decision_date"]
        < holdout_eligible[0]["decision_date"],
        "holdout_outcomes_unread": True,
        "option_pricing_calls_zero": True,
    }
    gates = {
        "minimum_train_pairs": pair_count >= min_train_pairs,
        "minimum_event_years": event_years >= min_event_years,
        "minimum_control_support": support >= min_control_support,
        "event_mean_after_cost_positive": math.isfinite(mean_event) and mean_event > 0.0,
        "paired_excess_mean_positive": math.isfinite(mean_paired) and mean_paired > 0.0,
        "paired_excess_year_block_bootstrap_lb90_positive": bootstrap_lb is not None
        and bootstrap_lb > 0.0,
        "paired_excess_positive_frequency": math.isfinite(positive_frequency)
        and positive_frequency >= min_positive_frequency,
        "event_return_worst_decile": math.isfinite(worst_decile)
        and worst_decile >= worst_decile_floor,
        "zero_integrity_violations": all(integrity.values()),
    }
    gate_pass = all(gates.values())
    holdout_identity = [
        {
            "decision_date": str(row["decision_date"].date()),
            "feature_date": str(row["feature_date"].date()),
            "event_entry_date": str(row["event_entry_date"].date()),
            "event_exit_date": str(row["event_exit_date"].date()),
            "statement_url": row["statement_url"],
            "matched": row["decision_date"] in matched_by_date,
        }
        for row in holdout_eligible
    ]
    payload: dict[str, Any] = {
        "schema_version": 1,
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "strategy_outcome": "STRATEGY_ADVANCED" if gate_pass else "FAMILY_CLOSED",
        "funnel_transition": "F0_MECHANISM->F1_TRAIN"
        if gate_pass
        else "F0_MECHANISM->F0_MECHANISM_CLOSED",
        "authority": "L0_DISCOVERY_ONLY",
        "provenance": provenance,
        "population": {
            "official_source_events": int(len(events)),
            "control_exclusion_official_events": int(len(exclusion_events)),
            "control_source_coverage_start": str(pd.Timestamp(source_coverage_start).date()),
            "regime_eligible_events": len(eligible),
            "matched_events": len(matched),
            "train_fraction": train_fraction,
            "train_eligible_events": len(train_eligible),
            "train_matched_pairs": pair_count,
            "holdout_eligible_events": len(holdout_eligible),
            "holdout_matched_blueprints": len(holdout_rows),
        },
        "train": {
            "gate_pass": gate_pass,
            "gates": gates,
            "metrics": {
                "pair_count": pair_count,
                "event_year_count": event_years,
                "control_support": support,
                "round_trip_cost_bps_each_path": round_trip_cost_bps,
                "mean_event_return_after_cost": _finite_or_none(mean_event),
                "mean_control_return_after_cost": _finite_or_none(mean_control),
                "mean_paired_excess": _finite_or_none(mean_paired),
                "paired_excess_positive_frequency": _finite_or_none(positive_frequency),
                "paired_excess_year_block_bootstrap_lb90": bootstrap_lb,
                "event_return_worst_decile": _finite_or_none(worst_decile),
            },
            "integrity": integrity,
            "decision_dates": [str(date.date()) for date in decision_dates],
            "pairs": pair_audit,
        },
        "untouched_holdout": {
            "eligible_blueprints": len(holdout_eligible),
            "matched_blueprints": len(holdout_rows),
            "identity_sha256": hashlib.sha256(
                _canonical_json_bytes(holdout_identity)
            ).hexdigest(),
            "outcome_metrics_read": False,
            "simulation_run": False,
            "option_pricing_run": False,
        },
        "option_stage": {
            "pricing_calls": 0,
            "structure": "conditional_future_18_24_dte_2wide_bull_call",
            "capital_fit_usd": 200,
            "max_loss_usd": 200,
            "max_lots": 1,
            "risk_semantics": "planning width bound only; no paid debit observed",
        },
        "l1_claim": False,
        "capital_seat_claim": False,
        "paper_watch_claim": False,
    }
    _canonical_json_bytes(payload)
    return payload


def _event_manifest(
    events: pd.DataFrame,
    source: dict[str, Any],
    *,
    control_exclusion_events: pd.DataFrame | None = None,
) -> dict[str, Any]:
    exclusion_events = events if control_exclusion_events is None else control_exclusion_events

    def manifest_rows(frame: pd.DataFrame) -> list[dict[str, str]]:
        return [
            {
                "decision_date": str(pd.Timestamp(row["decision_date"]).date()),
                "release_at_new_york": str(row["release_at_new_york"]),
                "statement_url": str(row["statement_url"]),
                "source_title": str(row["source_title"]),
                "source_press_type": str(row["source_press_type"]),
            }
            for row in frame.to_dict(orient="records")
        ]

    return {
        "schema_version": 2,
        "source": source,
        "filter": {
            "title": EVENT_TITLE,
            "press_type": PRESS_TYPE,
            "release_time_new_york": "14:00:00",
            "statement_path_regex": STATEMENT_PATH.pattern,
            "event_start": "2013-01-01",
            "event_end": "2025-12-31",
        },
        "filter_counts": {
            key: value
            for key, value in events.attrs.items()
            if key.startswith("excluded_")
        },
        "events": manifest_rows(events),
        "control_exclusion_events": manifest_rows(exclusion_events),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run train-only SPY FOMC information-resolution discovery lab"
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest-out", type=Path, required=True)
    parser.add_argument(
        "--cache-dir", type=Path, default=Path(".cache/platform/fomc_information_resolution")
    )
    parser.add_argument("--history-start", default="2012-01-01")
    parser.add_argument("--history-end", default="2026-01-15")
    parser.add_argument("--event-start", default="2013-01-01")
    parser.add_argument("--event-end", default="2025-12-31")
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    args = parser.parse_args()

    fed_cache = args.cache_dir / "fed_ne_press.json"
    records, fed_meta = load_official_press_records(fed_cache)
    events = parse_official_fomc_events(
        records, start=args.event_start, end=args.event_end
    )
    control_exclusion_events = parse_official_fomc_events(
        records, start=args.history_start, end=args.event_end
    )
    manifest = _event_manifest(
        events,
        fed_meta,
        control_exclusion_events=control_exclusion_events,
    )
    manifest["filter"]["event_start"] = args.event_start
    manifest["filter"]["event_end"] = args.event_end
    manifest["filter"]["control_exclusion_start"] = args.history_start
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    manifest_meta = {
        "path": str(args.manifest_out),
        "sha256": hashlib.sha256(args.manifest_out.read_bytes()).hexdigest(),
        "event_count": len(events),
        "control_exclusion_event_count": len(control_exclusion_events),
    }

    prices, price_meta = load_adjusted_ohlcv(
        "SPY",
        cache_dir=args.cache_dir,
        start=args.history_start,
        end=args.history_end,
    )
    payload = run_lab_from_frame(
        prices,
        events,
        control_exclusion_events=control_exclusion_events,
        provenance={
            "federal_reserve_press_index": fed_meta,
            "official_event_manifest": manifest_meta,
            "spy_adjusted_ohlcv": price_meta,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        bootstrap_samples=args.bootstrap_samples,
    )
    payload["predeclared_geometry"] = {
        "event_start": args.event_start,
        "event_end": args.event_end,
        "history_start": args.history_start,
        "history_end_exclusive": args.history_end,
        "regime": "prior close > fully warmed SMA100 and prior trailing 60-session return > 0",
        "entry": "next completed regular session open after exact 14:00 ET statement",
        "exit": "fifth session close including entry session",
        "control": {
            "prior_only": True,
            "max_distance_sessions": 756,
            "max_hv20_gap": 0.10,
            "max_ret60_gap": 0.10,
            "event_exclusion_sessions_each_side": 5,
            "event_exclusion_scope": "all source-covered exact 14:00 ET statements; controls before first source-covered event forbidden",
            "reuse": False,
            "full_outcome_before_event": True,
        },
        "train_fraction": 0.60,
        "round_trip_cost_bps_each_path": 10.0,
        "bootstrap": "one-sided 90% lower bound, resample whole decision years",
    }
    payload["predeclared_falsifier"] = {
        "minimum_train_pairs": 36,
        "minimum_event_years": 6,
        "minimum_control_support": 0.80,
        "event_mean_after_cost_positive": True,
        "paired_excess_mean_positive": True,
        "paired_excess_year_block_bootstrap_lb90_positive": True,
        "paired_excess_positive_frequency_min": 0.55,
        "event_return_worst_decile_min": -0.05,
        "zero_integrity_violations": True,
    }
    payload["search_information"] = (
        "Official prior-known scheduled-macro labels plus outcome-independent prior-only "
        "same-regime matching; final 40% sealed; no option pricing."
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out": str(args.out),
                "manifest": str(args.manifest_out),
                "strategy_outcome": payload["strategy_outcome"],
                "train_gate_pass": payload["train"]["gate_pass"],
                "train_pairs": payload["population"]["train_matched_pairs"],
                "holdout_outcomes_read": payload["untouched_holdout"][
                    "outcome_metrics_read"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

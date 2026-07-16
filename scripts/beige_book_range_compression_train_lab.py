#!/usr/bin/env python3
"""Train-only Beige Book range-compression discovery lab.

BUILD/L0 only. Official prior-known publication dates define events. The lab
keeps the chronological final 40% of eligible blueprints outcome-unread and
performs no option pricing.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import sys

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fomc_information_resolution_train_lab import (
    _canonical_json_bytes,
    _fetch_url_bytes,
    _finite_or_none,
    _validate_price_frame,
    _windows_overlap,
    _year_block_bootstrap_lower_bound,
    load_adjusted_ohlcv,
)


FED_BASE_URL = "https://www.federalreserve.gov"
FED_CALENDAR_JSON_URL = f"{FED_BASE_URL}/json/calendar.json"
BEIGE_PDF_DATE = re.compile(r"BeigeBook_(\d{8})\.pdf$", re.IGNORECASE)
NEW_YORK = "America/New_York"


def load_official_beige_sources(
    cache_dir: Path,
    *,
    start_year: int,
    end_year: int,
    fetch_bytes: Callable[[str], bytes] = _fetch_url_bytes,
) -> tuple[dict[int, bytes], bytes, dict[str, Any]]:
    """Persist and replay exact Federal Reserve archive and calendar bytes."""
    if start_year > end_year:
        raise ValueError("start year must not exceed end year")
    cache_dir.mkdir(parents=True, exist_ok=True)
    annual_pages: dict[int, bytes] = {}
    annual_meta: dict[str, dict[str, Any]] = {}
    for year in range(start_year, end_year + 1):
        url = f"{FED_BASE_URL}/monetarypolicy/beigebook{year}.htm"
        path = cache_dir / f"beigebook{year}.html"
        if not path.exists():
            payload = fetch_bytes(url)
            if not payload:
                raise ValueError(f"official Beige Book {year} source returned no bytes")
            path.write_bytes(payload)
        raw = path.read_bytes()
        annual_pages[year] = raw
        annual_meta[str(year)] = {
            "url": url,
            "path": str(path),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }
    calendar_path = cache_dir / "calendar.json"
    if not calendar_path.exists():
        payload = fetch_bytes(FED_CALENDAR_JSON_URL)
        if not payload:
            raise ValueError("official Federal Reserve calendar returned no bytes")
        calendar_path.write_bytes(payload)
    calendar_raw = calendar_path.read_bytes()
    return annual_pages, calendar_raw, {
        "annual_pages": annual_meta,
        "calendar": {
            "url": FED_CALENDAR_JSON_URL,
            "path": str(calendar_path),
            "sha256": hashlib.sha256(calendar_raw).hexdigest(),
            "bytes": len(calendar_raw),
        },
    }


def parse_official_beige_book_events(
    annual_pages: dict[int, bytes],
    calendar_payload: bytes,
    *,
    start: str,
    end: str,
) -> pd.DataFrame:
    """Parse exact archive PDF dates and corroborate official 14:00 calendar rows."""
    start_date = pd.Timestamp(start).normalize()
    end_date = pd.Timestamp(end).normalize()
    calendar = json.loads(calendar_payload.decode("utf-8-sig"))
    calendar_rows: dict[pd.Timestamp, str] = {}
    for item in calendar.get("events", []):
        if (
            item.get("title") != "Beige Book"
            or item.get("type") != "Beige"
            or not item.get("month")
        ):
            continue
        for day in str(item.get("days", "")).split(","):
            day = day.strip()
            if day:
                calendar_rows[pd.Timestamp(f"{item['month']}-{int(day):02d}")] = str(
                    item.get("time", "")
                )
    rows: list[dict[str, Any]] = []
    for year, payload in sorted(annual_pages.items()):
        soup = BeautifulSoup(payload.decode("utf-8-sig"), "html.parser")
        for anchor in soup.find_all("a", href=True):
            href = str(anchor["href"])
            match = BEIGE_PDF_DATE.search(href)
            if not match:
                continue
            date = pd.Timestamp(match.group(1)).normalize()
            if date.year != int(year) or not start_date <= date <= end_date:
                continue
            calendar_time = calendar_rows.get(date, "")
            corroborated = date in calendar_rows
            rows.append(
                {
                    "decision_date": date,
                    "release_at_new_york": date.tz_localize(NEW_YORK)
                    + pd.Timedelta(hours=14),
                    "source_url": urljoin(FED_BASE_URL, href),
                    "calendar_time_corroborated": corroborated,
                    "calendar_time": calendar_time,
                }
            )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise ValueError("no official Beige Book archive dates remain")
    conflicts = int(
        sum(
            bool(row["calendar_time_corroborated"])
            and row["calendar_time"] != "2:00 p.m."
            for row in rows
        )
    )
    if conflicts:
        raise ValueError("official Beige Book calendar time conflict")
    if frame["decision_date"].duplicated().any():
        raise ValueError("official Beige Book archive dates must be unique")
    frame = frame.sort_values("decision_date").reset_index(drop=True)
    frame.attrs["calendar_overlap_events"] = int(
        frame["calendar_time_corroborated"].sum()
    )
    frame.attrs["calendar_time_conflicts"] = conflicts
    return frame


def _feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    close = frame["close"].astype(float)
    log_return = np.log(close / close.shift(1))
    return pd.DataFrame(
        {
            "ret60": close / close.shift(60) - 1.0,
            "hv20": log_return.rolling(20, min_periods=20).std() * np.sqrt(252.0),
        },
        index=frame.index,
    )


def _neutral_nonstress(feature: pd.Series) -> bool:
    values = feature.to_numpy(dtype=float)
    return bool(
        np.isfinite(values).all()
        and abs(float(feature["ret60"])) <= 0.12
        and float(feature["hv20"]) <= 0.30
    )


def build_beige_book_matched_blueprints(
    price_frame: pd.DataFrame,
    events: pd.DataFrame,
    *,
    control_exclusion_events: pd.DataFrame | None = None,
    forward_sessions: int = 5,
    max_distance_sessions: int = 756,
    max_hv20_gap: float = 0.08,
    max_ret60_gap: float = 0.08,
    event_exclusion_sessions: int = 5,
) -> list[dict[str, Any]]:
    """Freeze neutral-regime event/control geometry without reading outcomes."""
    frame = _validate_price_frame(price_frame)
    if forward_sessions < 1 or max_distance_sessions <= forward_sessions:
        raise ValueError("forward and matching distances are invalid")
    if min(max_hv20_gap, max_ret60_gap) <= 0.0 or event_exclusion_sessions < 0:
        raise ValueError("feature gaps must be positive and exclusion non-negative")
    required = {"decision_date", "release_at_new_york", "source_url"}
    if not required.issubset(events.columns) or events.empty:
        raise ValueError("events require decision_date, release_at_new_york, and source_url")
    event_table = events.copy()
    event_table["decision_date"] = (
        pd.to_datetime(event_table["decision_date"]).dt.tz_localize(None).dt.normalize()
    )
    if event_table["decision_date"].duplicated().any():
        raise ValueError("event decision dates must be unique")
    event_table = event_table.sort_values("decision_date").reset_index(drop=True)
    exclusion_table = (
        event_table if control_exclusion_events is None else control_exclusion_events.copy()
    )
    if "decision_date" not in exclusion_table.columns or exclusion_table.empty:
        raise ValueError("control exclusion events require decision_date")
    exclusion_table["decision_date"] = (
        pd.to_datetime(exclusion_table["decision_date"])
        .dt.tz_localize(None)
        .dt.normalize()
    )
    if exclusion_table["decision_date"].duplicated().any():
        raise ValueError("control exclusion event dates must be unique")

    index = frame.index
    positions = {pd.Timestamp(value): position for position, value in enumerate(index)}
    features = _feature_frame(frame)
    official_positions = [
        positions[date]
        for date in exclusion_table["decision_date"]
        if date in positions
    ]
    source_coverage_start_pos = (
        0
        if control_exclusion_events is None
        else (min(official_positions) if official_positions else len(index))
    )
    excluded_positions: set[int] = set()
    for position in official_positions:
        excluded_positions.update(
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
        if feature_pos < 60 or exit_pos >= len(index):
            continue
        event_feature = features.iloc[feature_pos]
        if not _neutral_nonstress(event_feature):
            continue
        event_window = (entry_pos, exit_pos)
        if any(_windows_overlap(event_window, prior) for prior in occupied_event_windows):
            continue
        lower = max(60, source_coverage_start_pos, feature_pos - max_distance_sessions)
        candidates: list[tuple[float, int, int, int]] = []
        for control_feature_pos in range(lower, feature_pos):
            control_entry_pos = control_feature_pos + 1
            control_exit_pos = control_entry_pos + forward_sessions - 1
            if any(
                position in excluded_positions
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
            if not _neutral_nonstress(control_feature):
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
                "source_url": str(event.source_url),
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
        if feature_pos < 60 or exit_pos >= len(index):
            continue
        if not _neutral_nonstress(features.iloc[feature_pos]):
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
                "source_url": str(event.source_url),
            }
        )
        occupied.append(window)
    return geometry


def _window_range(frame: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> float:
    window = frame.loc[start:end]
    if window.empty:
        raise ValueError("range window is empty")
    return float(window["high"].max() / window["low"].min() - 1.0)


def _distance_summary(values: list[float | int]) -> dict[str, float | int]:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or not len(vector) or not np.isfinite(vector).all():
        raise ValueError("match-distance summary requires non-empty finite values")
    return {
        "count": int(len(vector)),
        "min": float(vector.min()),
        "median": float(np.median(vector)),
        "max": float(vector.max()),
    }


def run_lab_from_frame(
    price_frame: pd.DataFrame,
    events: pd.DataFrame,
    *,
    provenance: dict[str, Any],
    control_exclusion_events: pd.DataFrame | None = None,
    train_fraction: float = 0.60,
    forward_sessions: int = 5,
    range_hurdle_bps: float = 20.0,
    max_distance_sessions: int = 756,
    max_hv20_gap: float = 0.08,
    max_ret60_gap: float = 0.08,
    event_exclusion_sessions: int = 5,
    min_train_pairs: int = 30,
    min_event_years: int = 6,
    min_control_support: float = 0.80,
    min_positive_frequency: float = 0.55,
    max_event_range_p90: float = 0.07,
    bootstrap_samples: int = 20_000,
    bootstrap_seed: int = 20260716,
) -> dict[str, Any]:
    """Evaluate range compression on train only and seal holdout outcomes."""
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be strictly between zero and one")
    if range_hurdle_bps < 0.0 or max_event_range_p90 <= 0.0:
        raise ValueError("range hurdle and tail ceiling are invalid")
    frame = _validate_price_frame(price_frame)
    exclusion_events = events if control_exclusion_events is None else control_exclusion_events
    if "decision_date" not in exclusion_events.columns or exclusion_events.empty:
        raise ValueError("control exclusion events require decision_date")
    eligible = _eligible_event_geometry(frame, events, forward_sessions=forward_sessions)
    if len(eligible) < 2:
        raise ValueError("fewer than two eligible event blueprints")
    split_index = int(np.floor(len(eligible) * train_fraction))
    if split_index <= 0 or split_index >= len(eligible):
        raise ValueError("chronological split produced an empty partition")
    train_eligible = eligible[:split_index]
    holdout_eligible = eligible[split_index:]
    matched = build_beige_book_matched_blueprints(
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

    hurdle = range_hurdle_bps / 10_000.0
    event_ranges: list[float] = []
    control_ranges: list[float] = []
    years: list[int] = []
    pair_audit: list[dict[str, Any]] = []
    for row in train_rows:
        event_range = _window_range(
            frame, row["event_entry_date"], row["event_exit_date"]
        )
        control_range = _window_range(
            frame, row["control_entry_date"], row["control_exit_date"]
        )
        compression = control_range - event_range - hurdle
        event_ranges.append(event_range)
        control_ranges.append(control_range)
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
                "event_range": event_range,
                "control_range": control_range,
                "paired_compression_after_hurdle": compression,
                "event_ret60": float(row["event_ret60"]),
                "control_ret60": float(row["control_ret60"]),
                "event_hv20": float(row["event_hv20"]),
                "control_hv20": float(row["control_hv20"]),
                "ret60_match_gap": float(row["ret60_match_gap"]),
                "hv20_match_gap": float(row["hv20_match_gap"]),
                "calendar_distance_sessions": int(row["calendar_distance_sessions"]),
                "source_url": str(row["source_url"]),
            }
        )
    event_array = np.asarray(event_ranges, dtype=float)
    control_array = np.asarray(control_ranges, dtype=float)
    year_array = np.asarray(years, dtype=int)
    compression_array = control_array - event_array - hurdle
    pair_count = len(train_rows)
    event_years = len(set(years))
    support = pair_count / len(train_eligible) if train_eligible else 0.0
    mean_event = float(np.mean(event_array)) if pair_count else float("nan")
    mean_control = float(np.mean(control_array)) if pair_count else float("nan")
    mean_compression = (
        float(np.mean(compression_array)) if pair_count else float("nan")
    )
    positive_frequency = (
        float(np.mean(compression_array > 0.0)) if pair_count else float("nan")
    )
    event_range_p90 = (
        float(np.quantile(event_array, 0.90)) if pair_count else float("nan")
    )
    bootstrap_lb = _year_block_bootstrap_lower_bound(
        compression_array,
        year_array,
        samples=bootstrap_samples,
        seed=bootstrap_seed,
    )
    match_quality = (
        {
            "calendar_distance_sessions": _distance_summary(
                [row["calendar_distance_sessions"] for row in pair_audit]
            ),
            "hv20_match_gap": _distance_summary(
                [row["hv20_match_gap"] for row in pair_audit]
            ),
            "ret60_match_gap": _distance_summary(
                [row["ret60_match_gap"] for row in pair_audit]
            ),
            "calendar_distance_over_252_sessions_count": int(
                sum(row["calendar_distance_sessions"] > 252 for row in pair_audit)
            ),
            "absolute_paired_compression_over_5pct_count": int(
                np.sum(np.abs(compression_array) > 0.05)
            ),
            "diagnostic_only": True,
        }
        if pair_count
        else None
    )

    frame_positions = {
        pd.Timestamp(value): position for position, value in enumerate(frame.index)
    }
    official_positions = [
        frame_positions[date]
        for date in pd.to_datetime(exclusion_events["decision_date"])
        .dt.tz_localize(None)
        .dt.normalize()
        if date in frame_positions
    ]
    excluded_positions: set[int] = set()
    for position in official_positions:
        excluded_positions.update(
            range(
                max(0, position - event_exclusion_sessions),
                min(len(frame), position + event_exclusion_sessions + 1),
            )
        )
    control_windows = [
        (
            frame_positions[pd.Timestamp(row["control_entry_date"])],
            frame_positions[pd.Timestamp(row["control_exit_date"])],
        )
        for row in train_rows
    ]
    event_windows = [
        (
            frame_positions[pd.Timestamp(row["event_entry_date"])],
            frame_positions[pd.Timestamp(row["event_exit_date"])],
        )
        for row in train_rows
    ]
    source_coverage_start = (
        pd.to_datetime(exclusion_events["decision_date"])
        .dt.tz_localize(None)
        .dt.normalize()
        .min()
    )
    integrity = {
        "official_event_dates_unique": not events["decision_date"].duplicated().any(),
        "calendar_time_conflicts_zero": int(events.attrs.get("calendar_time_conflicts", 0))
        == 0,
        "control_outcomes_complete_before_event": all(
            pd.Timestamp(row["control_exit_date"]) < pd.Timestamp(row["decision_date"])
            for row in train_rows
        ),
        "control_windows_unique": len(control_windows) == len(set(control_windows)),
        "control_windows_nonoverlapping": all(
            not _windows_overlap(left, right)
            for index, left in enumerate(control_windows)
            for right in control_windows[index + 1 :]
        ),
        "controls_do_not_overlap_train_events": all(
            not _windows_overlap(control, event)
            for control in control_windows
            for event in event_windows
        ),
        "control_windows_outside_event_exclusion_bands": all(
            all(position not in excluded_positions for position in range(start, end + 1))
            for start, end in control_windows
        ),
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
        "mean_paired_compression_after_hurdle_positive": np.isfinite(mean_compression)
        and mean_compression > 0.0,
        "year_block_bootstrap_lb90_positive": bootstrap_lb is not None
        and bootstrap_lb > 0.0,
        "positive_frequency": np.isfinite(positive_frequency)
        and positive_frequency >= min_positive_frequency,
        "event_range_p90_within_ceiling": np.isfinite(event_range_p90)
        and event_range_p90 <= max_event_range_p90,
        "zero_integrity_violations": all(integrity.values()),
    }
    gate_pass = all(gates.values())
    holdout_identity = [
        {
            "decision_date": str(row["decision_date"].date()),
            "feature_date": str(row["feature_date"].date()),
            "event_entry_date": str(row["event_entry_date"].date()),
            "event_exit_date": str(row["event_exit_date"].date()),
            "source_url": str(row["source_url"]),
            "matched": row["decision_date"] in matched_by_date,
        }
        for row in holdout_eligible
    ]
    payload: dict[str, Any] = {
        "schema_version": 1,
        "candidate_id": "BEIGE_BOOK_RANGE_COMPRESSION_SPY_IC_21D_V1",
        "family_id": "BEIGE_BOOK_INFORMATION_RESOLUTION_RANGE_COMPRESSION",
        "strategy_outcome": "STRATEGY_ADVANCED" if gate_pass else "FAMILY_CLOSED",
        "funnel_transition": (
            "F0_MECHANISM->F1_TRAIN"
            if gate_pass
            else "F0_MECHANISM->F0_MECHANISM_CLOSED"
        ),
        "authority": "L0_DISCOVERY_ONLY",
        "provenance": provenance,
        "population": {
            "official_source_events": int(len(events)),
            "control_exclusion_official_events": int(len(exclusion_events)),
            "calendar_overlap_events": int(events.attrs.get("calendar_overlap_events", 0)),
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
                "range_hurdle_bps": range_hurdle_bps,
                "mean_event_range": _finite_or_none(mean_event),
                "mean_control_range": _finite_or_none(mean_control),
                "mean_paired_compression_after_hurdle": _finite_or_none(
                    mean_compression
                ),
                "paired_compression_positive_frequency": _finite_or_none(
                    positive_frequency
                ),
                "paired_compression_year_block_bootstrap_lb90": bootstrap_lb,
                "event_range_p90": _finite_or_none(event_range_p90),
                "match_quality": match_quality,
            },
            "integrity": integrity,
            "decision_dates": [
                str(pd.Timestamp(row["decision_date"]).date()) for row in train_rows
            ],
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
            "structure": "conditional_future_18_24_dte_2wide_iron_condor",
            "capital_fit_usd": 200,
            "max_loss_usd": 200,
            "max_lots": 1,
            "risk_semantics": "planning width bound only; no credit or option marks observed",
        },
        "l1_claim": False,
        "capital_seat_claim": False,
        "paper_watch_claim": False,
    }
    _canonical_json_bytes(payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run train-only SPY Beige Book range-compression discovery lab"
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest-out", type=Path, required=True)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".cache/platform/beige_book_range_compression"),
    )
    parser.add_argument("--history-start", default="2013-01-01")
    parser.add_argument("--history-end", default="2026-01-15")
    parser.add_argument("--event-start", default="2013-01-01")
    parser.add_argument("--event-end", default="2025-12-31")
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    args = parser.parse_args(argv)

    start_year = pd.Timestamp(args.event_start).year
    end_year = pd.Timestamp(args.event_end).year
    annual_pages, calendar_payload, source_meta = load_official_beige_sources(
        args.cache_dir / "official_sources",
        start_year=start_year,
        end_year=end_year,
    )
    events = parse_official_beige_book_events(
        annual_pages,
        calendar_payload,
        start=args.event_start,
        end=args.event_end,
    )
    manifest = {
        "schema_version": 1,
        "source": source_meta,
        "filter": {
            "archive_pdf_regex": BEIGE_PDF_DATE.pattern,
            "event_start": args.event_start,
            "event_end": args.event_end,
            "calendar_exact_title": "Beige Book",
            "calendar_exact_type": "Beige",
            "calendar_release_time_new_york": "14:00:00",
            "nonoverlap_time_semantics": (
                "archive PDF date defines publication day; next-session entry does not "
                "depend on an intraday timestamp; official calendar rows corroborate "
                "14:00 America/New_York wherever structured history overlaps"
            ),
        },
        "filter_counts": {
            "official_events": int(len(events)),
            "calendar_overlap_events": int(
                events.attrs.get("calendar_overlap_events", 0)
            ),
            "calendar_time_conflicts": int(
                events.attrs.get("calendar_time_conflicts", 0)
            ),
        },
        "events": [
            {
                "decision_date": str(pd.Timestamp(row["decision_date"]).date()),
                "release_at_new_york": str(row["release_at_new_york"]),
                "source_url": str(row["source_url"]),
                "calendar_time_corroborated": bool(
                    row["calendar_time_corroborated"]
                ),
                "calendar_time": row["calendar_time"],
            }
            for row in events.to_dict(orient="records")
        ],
    }
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    manifest_meta = {
        "path": str(args.manifest_out),
        "sha256": hashlib.sha256(args.manifest_out.read_bytes()).hexdigest(),
        "event_count": len(events),
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
        control_exclusion_events=events,
        provenance={
            "federal_reserve_beige_book_sources": source_meta,
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
        "regime": "prior completed HV20 <= 0.30 and abs trailing 60-session return <= 0.12",
        "entry": "next completed regular session open after official publication date",
        "exit": "fifth session close including entry session",
        "endpoint": "maximum high / minimum low - 1 over five completed sessions",
        "control": {
            "prior_only": True,
            "max_distance_sessions": 756,
            "max_hv20_gap": 0.08,
            "max_ret60_gap": 0.08,
            "event_exclusion_sessions_each_side": 5,
            "event_exclusion_scope": "all source-covered official Beige Book dates",
            "reuse": False,
            "full_outcome_before_event": True,
        },
        "train_fraction": 0.60,
        "range_hurdle_bps": 20.0,
        "bootstrap": "one-sided 90% lower bound, resample whole release years",
    }
    payload["predeclared_falsifier"] = {
        "minimum_train_pairs": 30,
        "minimum_event_years": 6,
        "minimum_control_support": 0.80,
        "mean_paired_compression_after_20bps_hurdle_positive": True,
        "year_block_bootstrap_lb90_positive": True,
        "paired_compression_positive_frequency_min": 0.55,
        "event_range_p90_max": 0.07,
        "zero_integrity_violations": True,
    }
    failed_gates = [
        name for name, passed in payload["train"]["gates"].items() if not passed
    ]
    payload["dominant_failure_mechanism"] = (
        None
        if payload["train"]["gate_pass"]
        else "The scheduled qualitative release did not produce robust hurdle-adjusted "
        "five-session SPY range compression versus frozen prior-only neutral controls; "
        f"failed gates: {', '.join(failed_gates)}."
    )
    payload["search_information"] = (
        "Official prior-known Beige Book publication dates plus official calendar-time "
        "corroboration, train-only range endpoint, prior-only neutral-regime controls, "
        "sealed final 40%, and zero option pricing."
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

"""Archived, announcement-time-aware cash-dividend events for research sims."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import tempfile
from typing import Any, Optional, Sequence, cast
from urllib.request import Request, urlopen

import pandas as pd

from trader_platform.research.corporate_action_risk import DividendEvent


_SOURCE = "nasdaq_dividend_history"
_SCHEMA_VERSION = 1
_MISSING = {"", "n/a", "na", "--", "none", "null"}


@dataclass(frozen=True)
class DividendEventArchive:
    symbol: str
    observed_at: pd.Timestamp
    coverage_start: pd.Timestamp
    source: str
    events: tuple[DividendEvent, ...]
    source_rows: int
    retained_rows: int
    truncated_at_missing_known_at: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": _SCHEMA_VERSION,
            "symbol": self.symbol,
            "observed_at": self.observed_at.tz_localize("UTC").isoformat(),
            "coverage_start": self.coverage_start.isoformat(),
            "source": self.source,
            "source_rows": self.source_rows,
            "retained_rows": self.retained_rows,
            "truncated_at_missing_known_at": self.truncated_at_missing_known_at,
            "events": [
                {
                    "symbol": event.symbol,
                    "ex_date": event.ex_date.isoformat(),
                    "amount_per_share": event.amount_per_share,
                    "known_at": event.known_at.isoformat(),
                }
                for event in self.events
            ],
        }


class ArchivedDividendEventProvider:
    """Serve only as-of dates covered by one immutable source snapshot."""

    def __init__(self, archive: DividendEventArchive):
        self.archive = archive

    def __call__(
        self, symbol: str, as_of: pd.Timestamp, through: pd.Timestamp
    ) -> Optional[Sequence[DividendEvent]]:
        as_of_ts = _timestamp(as_of)
        through_ts = _timestamp(through)
        if through_ts < as_of_ts:
            raise ValueError("dividend query through date precedes as_of")
        if symbol.strip().upper() != self.archive.symbol:
            return None
        if not self.archive.coverage_start <= as_of_ts <= self.archive.observed_at:
            return None
        return self.archive.events


def _timestamp(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        raise ValueError("dividend timestamp cannot be missing")
    if ts.tzinfo is not None:
        ts = ts.tz_convert("UTC").tz_localize(None)
    return cast(pd.Timestamp, ts).normalize()


def _observed_timestamp(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if pd.isna(ts) or ts.tzinfo is None:
        raise ValueError("observed_at must include a timezone")
    return cast(pd.Timestamp, ts.tz_convert("UTC").tz_localize(None))


def _date(value: Any, field: str) -> pd.Timestamp:
    text = str(value or "").strip()
    if text.lower() in _MISSING:
        raise ValueError(f"missing {field}")
    try:
        return _timestamp(pd.to_datetime(text, format="%m/%d/%Y"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field}: {text!r}") from exc


def _cash_amount(value: Any) -> float:
    text = re.sub(r"[^0-9.+-]", "", str(value or ""))
    try:
        amount = float(text)
    except ValueError as exc:
        raise ValueError(f"invalid dividend amount: {value!r}") from exc
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError(f"invalid dividend amount: {value!r}")
    return amount


def archive_from_nasdaq_payload(
    symbol: str,
    payload: dict[str, Any],
    *,
    observed_at: datetime | pd.Timestamp,
) -> DividendEventArchive:
    """Normalize a Nasdaq history response without inventing declaration dates.

    The public page may contain old rows with ``N/A`` declaration dates. Those rows
    and all older history are excluded, creating a conservative recent coverage
    boundary instead of backfilling ``known_at`` from ex-date.
    """
    sym = symbol.strip().upper()
    status = payload.get("status") or {}
    if int(status.get("rCode") or 0) != 200:
        raise ValueError(f"Nasdaq dividend source unsupported for {sym}")
    data = payload.get("data")
    dividends = data.get("dividends") if isinstance(data, dict) else None
    rows = dividends.get("rows") if isinstance(dividends, dict) else None
    if not isinstance(rows, list) or not rows:
        message = str(payload.get("message") or "").strip()
        raise ValueError(
            f"Nasdaq dividend coverage ambiguous for {sym}: {message or 'no rows'}"
        )

    observed_ts = _observed_timestamp(observed_at)
    events: list[DividendEvent] = []
    truncated = False
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"invalid Nasdaq dividend row at index {index}")
        declaration_text = str(row.get("declarationDate") or "").strip()
        if declaration_text.lower() in _MISSING:
            if not events:
                raise ValueError("latest Nasdaq dividend row lacks declarationDate")
            truncated = True
            break
        if str(row.get("type") or "").strip().lower() != "cash":
            raise ValueError(f"unsupported Nasdaq dividend type at index {index}")
        currency = str(row.get("currency") or "").strip().upper()
        if currency not in {"", "USD"}:
            raise ValueError(f"unsupported Nasdaq dividend currency at index {index}")
        ex_date = _date(row.get("exOrEffDate"), "exOrEffDate")
        known_at = _date(declaration_text, "declarationDate")
        if known_at > ex_date:
            raise ValueError("dividend declarationDate is after exOrEffDate")
        if known_at > observed_ts:
            raise ValueError("dividend declarationDate is after snapshot observed_at")
        events.append(
            DividendEvent(
                symbol=sym,
                ex_date=ex_date,
                amount_per_share=_cash_amount(row.get("amount")),
                known_at=known_at,
            )
        )

    if not events:
        raise ValueError(f"no usable announcement-time dividend rows for {sym}")
    events.sort(key=lambda event: (event.ex_date, event.known_at))
    return DividendEventArchive(
        symbol=sym,
        observed_at=observed_ts,
        coverage_start=min(event.known_at for event in events),
        source=_SOURCE,
        events=tuple(events),
        source_rows=len(rows),
        retained_rows=len(events),
        truncated_at_missing_known_at=truncated,
    )


def snapshot_nasdaq_dividend_history(symbol: str) -> DividendEventArchive:
    sym = symbol.strip().upper()
    url = f"https://api.nasdaq.com/api/quote/{sym}/dividends?assetclass=stocks"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 TraderResearch/1.0",
        },
    )
    with urlopen(request, timeout=20) as response:  # noqa: S310 - fixed HTTPS host
        payload = json.load(response)
    return archive_from_nasdaq_payload(
        sym, payload, observed_at=datetime.now(timezone.utc)
    )


def archive_from_mapping(payload: dict[str, Any]) -> DividendEventArchive:
    if int(payload.get("schema_version") or 0) != _SCHEMA_VERSION:
        raise ValueError("unsupported dividend archive schema")
    symbol = str(payload.get("symbol") or "").strip().upper()
    source = str(payload.get("source") or "").strip()
    if not symbol or source != _SOURCE:
        raise ValueError("invalid dividend archive identity")
    observed_at = _observed_timestamp(payload.get("observed_at"))
    coverage_start = _timestamp(payload.get("coverage_start"))
    if coverage_start > observed_at:
        raise ValueError("dividend archive coverage starts after observation")
    raw_events = payload.get("events")
    if not isinstance(raw_events, list) or not raw_events:
        raise ValueError("dividend archive has no events")
    events = []
    for row in raw_events:
        if not isinstance(row, dict):
            raise ValueError("invalid dividend archive event")
        event_symbol = str(row.get("symbol") or "").strip().upper()
        ex_date = _timestamp(row.get("ex_date"))
        known_at = _timestamp(row.get("known_at"))
        amount_raw = row.get("amount_per_share")
        if amount_raw is None:
            raise ValueError("dividend archive amount is missing")
        amount = float(amount_raw)
        if event_symbol != symbol or known_at > ex_date or known_at > observed_at:
            raise ValueError("invalid dividend archive event identity or timing")
        if not math.isfinite(amount) or amount <= 0:
            raise ValueError("invalid dividend archive amount")
        events.append(DividendEvent(symbol, ex_date, amount, known_at))
    retained_rows = int(payload.get("retained_rows") or len(events))
    source_rows = int(payload.get("source_rows") or len(events))
    if retained_rows != len(events) or source_rows < retained_rows:
        raise ValueError("dividend archive row counts do not match events")
    if len(set(events)) != len(events):
        raise ValueError("dividend archive contains duplicate events")
    if min(event.known_at for event in events) != coverage_start:
        raise ValueError("dividend archive coverage boundary does not match events")
    return DividendEventArchive(
        symbol=symbol,
        observed_at=observed_at,
        coverage_start=coverage_start,
        source=source,
        events=tuple(sorted(events, key=lambda event: (event.ex_date, event.known_at))),
        source_rows=source_rows,
        retained_rows=retained_rows,
        truncated_at_missing_known_at=bool(
            payload.get("truncated_at_missing_known_at", False)
        ),
    )


def load_dividend_event_archive(path: str | Path) -> DividendEventArchive:
    return archive_from_mapping(json.loads(Path(path).read_text()))


def write_dividend_event_archive(
    path: str | Path, archive: DividendEventArchive
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=target.parent, prefix=f".{target.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        json.dump(archive.to_dict(), handle, indent=2)
        handle.write("\n")
    temporary.replace(target)


def summarize_dividend_event_archive(archive: DividendEventArchive) -> dict[str, Any]:
    return {
        "schema_version": _SCHEMA_VERSION,
        "symbol": archive.symbol,
        "source": archive.source,
        "observed_at": archive.observed_at.tz_localize("UTC").isoformat(),
        "coverage_start": archive.coverage_start.isoformat(),
        "coverage_end_asof": archive.observed_at.tz_localize("UTC").isoformat(),
        "source_rows": archive.source_rows,
        "retained_rows": archive.retained_rows,
        "truncated_at_missing_known_at": archive.truncated_at_missing_known_at,
        "provider_eligible": archive.retained_rows > 0,
        "claim_limit": "cash-dividend assignment guard only; not option-surface or edge evidence",
    }

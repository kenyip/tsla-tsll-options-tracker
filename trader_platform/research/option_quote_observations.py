"""Normalize current or archived option bid/ask observations for cost research."""

from __future__ import annotations

import csv
import tempfile
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any, Iterable
from zoneinfo import ZoneInfo


_REQUIRED_COLUMNS = {
    "observed_at",
    "symbol",
    "expiration",
    "option_type",
    "strike",
    "bid",
    "ask",
    "source",
    "is_observed",
}


@dataclass(frozen=True)
class OptionQuoteObservation:
    observed_at: datetime
    symbol: str
    expiration: date
    option_type: str
    strike: float
    bid: float
    ask: float
    source: str
    is_observed: bool
    contract_symbol: str = ""
    last_price: float | None = None
    implied_volatility: float | None = None

    @property
    def half_spread(self) -> float:
        return (self.ask - self.bid) / 2.0

    @property
    def mid(self) -> float:
        return (self.ask + self.bid) / 2.0

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["observed_at"] = self.observed_at.isoformat()
        row["expiration"] = self.expiration.isoformat()
        row["half_spread"] = self.half_spread
        row["mid"] = self.mid
        return row


@dataclass(frozen=True)
class StrategyLegRequirement:
    event_id: str
    event_kind: str
    event_at: datetime
    symbol: str
    expiration: date
    option_type: str
    strike: float


@dataclass(frozen=True)
class StrategyLegQuoteMatch:
    requirement: StrategyLegRequirement
    observation: OptionQuoteObservation | None
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.requirement.event_id,
            "event_kind": self.requirement.event_kind,
            "event_at": self.requirement.event_at.isoformat(),
            "symbol": self.requirement.symbol,
            "expiration": self.requirement.expiration.isoformat(),
            "option_type": self.requirement.option_type,
            "strike": self.requirement.strike,
            "reason": self.reason,
            "observation": self.observation.to_dict() if self.observation else None,
            "quote_age_seconds": (
                (self.requirement.event_at - self.observation.observed_at).total_seconds()
                if self.observation
                else None
            ),
        }


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no"}:
        return False
    raise ValueError(f"invalid is_observed value: {value!r}")


def _parse_optional_float(value: Any) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return float(value)


def _normalize_timestamp(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("observed_at must include a timezone")
    return parsed.astimezone(timezone.utc)


def observation_from_mapping(row: dict[str, Any]) -> OptionQuoteObservation:
    missing = sorted(_REQUIRED_COLUMNS - set(row))
    if missing:
        raise ValueError(f"missing quote columns: {', '.join(missing)}")
    option_type = str(row["option_type"]).strip().lower()
    if option_type not in {"call", "put"}:
        raise ValueError(f"invalid option_type: {option_type!r}")
    bid = float(row["bid"])
    ask = float(row["ask"])
    strike = float(row["strike"])
    if bid < 0 or ask < 0 or ask < bid:
        raise ValueError(f"invalid quote bid={bid} ask={ask}")
    if strike <= 0:
        raise ValueError(f"invalid strike: {strike}")
    return OptionQuoteObservation(
        observed_at=_normalize_timestamp(row["observed_at"]),
        symbol=str(row["symbol"]).strip().upper(),
        expiration=date.fromisoformat(str(row["expiration"])),
        option_type=option_type,
        strike=strike,
        bid=bid,
        ask=ask,
        source=str(row["source"]).strip(),
        is_observed=_parse_bool(row["is_observed"]),
        contract_symbol=str(row.get("contract_symbol") or "").strip(),
        last_price=_parse_optional_float(row.get("last_price")),
        implied_volatility=_parse_optional_float(row.get("implied_volatility")),
    )


def load_observations_csv(
    path: str | Path, *, require_observed: bool = True
) -> list[OptionQuoteObservation]:
    with Path(path).open(newline="") as handle:
        rows = [observation_from_mapping(dict(row)) for row in csv.DictReader(handle)]
    if not rows:
        raise ValueError(f"no quote observations in {path}")
    if require_observed and any(not row.is_observed for row in rows):
        raise ValueError("synthetic/non-observed rows cannot calibrate execution costs")
    return rows


def summarize_half_spreads(rows: Iterable[OptionQuoteObservation]) -> dict[str, Any]:
    observations = list(rows)
    if not observations:
        raise ValueError("cannot summarize an empty quote set")
    spreads = [row.half_spread for row in observations]
    return {
        "n_quotes": len(observations),
        "n_observed": sum(row.is_observed for row in observations),
        "symbols": sorted({row.symbol for row in observations}),
        "median_half_spread": float(median(spreads)),
        "max_half_spread": float(max(spreads)),
        "observed_at_min": min(row.observed_at for row in observations).isoformat(),
        "observed_at_max": max(row.observed_at for row in observations).isoformat(),
        "calibration_eligible": all(row.is_observed for row in observations),
    }


def summarize_archive_density(
    rows: Iterable[OptionQuoteObservation],
    *,
    minimum_market_dates: int = 3,
    market_timezone: str = "America/New_York",
) -> dict[str, Any]:
    """Report whether observed weekday RTH quotes clear the historical replay floor."""
    observations = list(rows)
    if not observations:
        raise ValueError("cannot summarize an empty quote archive")
    timezone_info = ZoneInfo(market_timezone)
    localized = [(row, row.observed_at.astimezone(timezone_info)) for row in observations]
    archive_dates = sorted({local.date() for _, local in localized})
    rth_observations = [
        (row, local)
        for row, local in localized
        if local.weekday() < 5 and time(9, 30) <= local.time() <= time(16, 0)
    ]
    market_dates = sorted({local.date() for _, local in rth_observations})
    dates_with_non_rth_quotes = sorted(
        {
            local.date()
            for _, local in localized
            if local.weekday() >= 5 or not time(9, 30) <= local.time() <= time(16, 0)
        }
    )
    fully_excluded_dates = sorted(set(archive_dates) - set(market_dates))
    expirations_by_date = {
        market_date.isoformat(): sorted(
            {
                row.expiration.isoformat()
                for row, local in rth_observations
                if local.date() == market_date
            }
        )
        for market_date in market_dates
    }
    rejection_reasons = []
    if any(not row.is_observed for row in observations):
        rejection_reasons.append("synthetic_rows_present")
    if len(market_dates) < minimum_market_dates:
        rejection_reasons.append("insufficient_market_date_density")
    return {
        "n_quotes": len(observations),
        "n_rth_quotes": len(rth_observations),
        "n_non_rth_quotes": len(observations) - len(rth_observations),
        "n_archive_dates": len(archive_dates),
        "archive_dates": [value.isoformat() for value in archive_dates],
        "n_market_dates": len(market_dates),
        "market_dates": [value.isoformat() for value in market_dates],
        "dates_with_non_rth_quotes": [
            value.isoformat() for value in dates_with_non_rth_quotes
        ],
        "fully_excluded_dates": [value.isoformat() for value in fully_excluded_dates],
        "minimum_market_dates": minimum_market_dates,
        "n_expirations": len({row.expiration for row, _ in rth_observations}),
        "expirations_by_market_date": expirations_by_date,
        "market_timezone": market_timezone,
        "provider_backtest_eligible": not rejection_reasons,
        "rejection_reasons": rejection_reasons,
    }


def join_strategy_leg_requirements(
    requirements: Iterable[StrategyLegRequirement],
    observations: Iterable[OptionQuoteObservation],
    *,
    max_quote_age: timedelta,
) -> list[StrategyLegQuoteMatch]:
    """As-of join exact contracts to the latest non-future observed quote."""
    quotes = list(observations)
    matches: list[StrategyLegQuoteMatch] = []
    for requirement in requirements:
        candidates = [
            quote
            for quote in quotes
            if quote.symbol == requirement.symbol.upper()
            and quote.expiration == requirement.expiration
            and quote.option_type == requirement.option_type.lower()
            and abs(quote.strike - requirement.strike) < 1e-9
            and quote.observed_at <= requirement.event_at
        ]
        if not candidates:
            matches.append(StrategyLegQuoteMatch(requirement, None, "missing_exact_contract_asof"))
            continue
        latest = max(candidates, key=lambda quote: quote.observed_at)
        if requirement.event_at - latest.observed_at > max_quote_age:
            matches.append(StrategyLegQuoteMatch(requirement, None, "stale_exact_contract_quote"))
            continue
        if not latest.is_observed:
            matches.append(StrategyLegQuoteMatch(requirement, None, "synthetic_quote_rejected"))
            continue
        matches.append(StrategyLegQuoteMatch(requirement, latest, "matched"))
    return matches


def summarize_join_coverage(matches: Iterable[StrategyLegQuoteMatch]) -> dict[str, Any]:
    rows = list(matches)
    if not rows:
        raise ValueError("cannot summarize empty strategy-leg requirements")
    matched = [row for row in rows if row.observation is not None]
    by_kind: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = by_kind.setdefault(row.requirement.event_kind, {"required": 0, "matched": 0})
        bucket["required"] += 1
        bucket["matched"] += int(row.observation is not None)
    rejection_reasons = []
    for kind in ("entry", "exit"):
        bucket = by_kind.get(kind, {"required": 0, "matched": 0})
        if bucket["required"] == 0 or bucket["matched"] < bucket["required"]:
            rejection_reasons.append(f"missing_{kind}_coverage")
    if any(row.observation is None for row in rows):
        rejection_reasons.append("incomplete_exact_leg_coverage")
    matched_observations = [row.observation for row in matched if row.observation is not None]
    return {
        "required_legs": len(rows),
        "matched_legs": len(matched),
        "coverage_ratio": len(matched) / len(rows),
        "by_event_kind": by_kind,
        "median_matched_half_spread": (
            float(median(observation.half_spread for observation in matched_observations))
            if matched_observations
            else None
        ),
        "calibration_eligible": not rejection_reasons,
        "rejection_reasons": rejection_reasons,
    }


def snapshot_yfinance_option_quotes(
    symbol: str, expiration: str | None = None
) -> list[OptionQuoteObservation]:
    """Fetch all current yfinance chains, or one explicit expiration."""
    import yfinance as yf

    ticker = yf.Ticker(symbol.upper())
    expirations = list(ticker.options)
    if not expirations:
        raise ValueError(f"no current option expirations returned for {symbol.upper()}")
    if expiration and expiration not in expirations:
        raise ValueError(f"expiration {expiration} is unavailable for {symbol.upper()}")
    chosen_expirations = [expiration] if expiration else expirations
    observed_at = datetime.now(timezone.utc)
    rows: list[OptionQuoteObservation] = []
    for chosen in chosen_expirations:
        chain = ticker.option_chain(chosen)
        for option_type, frame in (("call", chain.calls), ("put", chain.puts)):
            for record in frame.to_dict(orient="records"):
                bid = float(record.get("bid") or 0.0)
                ask = float(record.get("ask") or 0.0)
                if ask < bid or ask <= 0:
                    continue
                rows.append(
                    OptionQuoteObservation(
                        observed_at=observed_at,
                        symbol=symbol.upper(),
                        expiration=date.fromisoformat(chosen),
                        option_type=option_type,
                        strike=float(record["strike"]),
                        bid=bid,
                        ask=ask,
                        source="yfinance_current_chain",
                        is_observed=True,
                        contract_symbol=str(record.get("contractSymbol") or ""),
                        last_price=_parse_optional_float(record.get("lastPrice")),
                        implied_volatility=_parse_optional_float(record.get("impliedVolatility")),
                    )
                )
    if not rows:
        scope = expiration or "all expirations"
        raise ValueError(f"no valid bid/ask rows returned for {symbol.upper()} {scope}")
    return rows


def write_observations_csv(
    path: str | Path,
    rows: Iterable[OptionQuoteObservation],
    *,
    append: bool = False,
) -> None:
    observations = list(rows)
    if not observations:
        raise ValueError("cannot write an empty quote set")
    fields = [
        "observed_at",
        "symbol",
        "expiration",
        "option_type",
        "strike",
        "bid",
        "ask",
        "source",
        "is_observed",
        "contract_symbol",
        "last_price",
        "implied_volatility",
    ]
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    combined = (
        load_observations_csv(target, require_observed=False)
        if append and target.exists()
        else []
    )
    seen = set(combined)
    for observation in observations:
        if observation not in seen:
            combined.append(observation)
            seen.add(observation)
    output_rows = combined if append else observations
    with tempfile.NamedTemporaryFile(
        "w", newline="", dir=target.parent, prefix=f".{target.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for observation in output_rows:
            row = observation.to_dict()
            writer.writerow({field: row.get(field) for field in fields})
    temporary.replace(target)

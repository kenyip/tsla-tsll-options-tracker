"""Schwab developer API → normalized option quote observations (research only).

Ken-authorized market-data path. Never places orders. Fail closed without
credentials. Rows map into OptionQuoteObservation for the shared archive
boundary used by yfinance/CSV sources.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from trader_platform.research.option_quote_observations import OptionQuoteObservation

DEFAULT_API_BASE = "https://api.schwabapi.com"
SOURCE_NAME = "schwab_trader_api"


@dataclass(frozen=True)
class SchwabCredentialStatus:
    ready: bool
    reason: str
    app_key_present: bool
    app_secret_present: bool
    token_present: bool
    token_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ready": self.ready,
            "reason": self.reason,
            "app_key_present": self.app_key_present,
            "app_secret_present": self.app_secret_present,
            "token_present": self.token_present,
            "token_path": self.token_path,
            "trading_authority": False,
            "order_placement": False,
        }


def credential_status(
    *,
    env: Mapping[str, str] | None = None,
) -> SchwabCredentialStatus:
    """Inspect local env for research credentials without printing secrets."""
    environ = env if env is not None else os.environ
    app_key = bool(str(environ.get("SCHWAB_APP_KEY") or "").strip())
    app_secret = bool(str(environ.get("SCHWAB_APP_SECRET") or "").strip())
    token_path_raw = str(environ.get("SCHWAB_TOKEN_PATH") or "").strip()
    refresh = bool(str(environ.get("SCHWAB_REFRESH_TOKEN") or "").strip())
    token_path: str | None = token_path_raw or None
    token_file_ok = bool(token_path and Path(token_path).is_file())
    token_present = refresh or token_file_ok

    if not app_key or not app_secret:
        return SchwabCredentialStatus(
            ready=False,
            reason="credentials_missing: set SCHWAB_APP_KEY and SCHWAB_APP_SECRET",
            app_key_present=app_key,
            app_secret_present=app_secret,
            token_present=token_present,
            token_path=token_path,
        )
    if not token_present:
        return SchwabCredentialStatus(
            ready=False,
            reason="credentials_missing: set SCHWAB_TOKEN_PATH or SCHWAB_REFRESH_TOKEN",
            app_key_present=app_key,
            app_secret_present=app_secret,
            token_present=False,
            token_path=token_path,
        )
    return SchwabCredentialStatus(
        ready=True,
        reason="ready_for_read_only_market_data",
        app_key_present=True,
        app_secret_present=True,
        token_present=True,
        token_path=token_path,
    )


def api_base(env: Mapping[str, str] | None = None) -> str:
    environ = env if env is not None else os.environ
    base = str(environ.get("SCHWAB_API_BASE") or DEFAULT_API_BASE).strip().rstrip("/")
    return base or DEFAULT_API_BASE


def _parse_expiration(raw: Any) -> date:
    text = str(raw or "").strip()
    if not text:
        raise ValueError("missing expiration")
    # Schwab often uses YYYY-MM-DD or epoch-ms style strings depending on endpoint.
    if text.isdigit() and len(text) >= 12:
        # milliseconds since epoch
        return datetime.fromtimestamp(int(text) / 1000.0, tz=timezone.utc).date()
    return date.fromisoformat(text[:10])


def _parse_observed_at(raw: Any) -> datetime:
    if raw is None or raw == "":
        return datetime.now(timezone.utc)
    if isinstance(raw, datetime):
        return raw if raw.tzinfo is not None else raw.replace(tzinfo=timezone.utc)
    text = str(raw).strip()
    if text.isdigit() and len(text) >= 12:
        return datetime.fromtimestamp(int(text) / 1000.0, tz=timezone.utc)
    # ISO-8601
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _as_float(raw: Any) -> float | None:
    if raw is None or raw == "":
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if value != value:  # NaN
        return None
    return value


def normalize_schwab_option_chain(
    payload: Mapping[str, Any],
    *,
    underlying: str,
    observed_at: datetime | None = None,
    source: str = SOURCE_NAME,
) -> list[OptionQuoteObservation]:
    """Normalize a Schwab-like option chain payload into observations.

    Accepts either:
    - already-flat ``rows`` list of dicts with bid/ask/strike/expiration/type, or
    - a dict containing callExpDateMap / putExpDateMap style maps (common Schwab shape).
    """
    symbol = str(underlying or payload.get("symbol") or "").strip().upper()
    if not symbol:
        raise ValueError("underlying symbol required")

    stamp = observed_at or _parse_observed_at(payload.get("observed_at") or payload.get("quoteTime"))
    rows: list[OptionQuoteObservation] = []

    flat_rows = payload.get("rows")
    if isinstance(flat_rows, Sequence) and not isinstance(flat_rows, (str, bytes)):
        for item in flat_rows:
            if not isinstance(item, Mapping):
                continue
            rows.append(_row_to_observation(item, symbol=symbol, default_observed_at=stamp, source=source))
        return rows

    for option_type, map_key in (("call", "callExpDateMap"), ("put", "putExpDateMap")):
        exp_map = payload.get(map_key) or {}
        if not isinstance(exp_map, Mapping):
            continue
        for exp_key, strike_map in exp_map.items():
            # Keys often look like "2026-08-15:32" (date:dte)
            exp = _parse_expiration(str(exp_key).split(":", 1)[0])
            if not isinstance(strike_map, Mapping):
                continue
            for _strike_key, contracts in strike_map.items():
                contract_list = contracts if isinstance(contracts, Sequence) else [contracts]
                for contract in contract_list:
                    if not isinstance(contract, Mapping):
                        continue
                    merged = {
                        "expiration": exp.isoformat(),
                        "option_type": option_type,
                        "strike": contract.get("strikePrice", contract.get("strike")),
                        "bid": contract.get("bid"),
                        "ask": contract.get("ask"),
                        "last_price": contract.get("last") or contract.get("lastPrice"),
                        "implied_volatility": contract.get("volatility")
                        or contract.get("impliedVolatility"),
                        "contract_symbol": contract.get("symbol") or contract.get("contractSymbol"),
                        "observed_at": contract.get("quoteTimeInLong")
                        or contract.get("quoteTime")
                        or stamp,
                    }
                    rows.append(
                        _row_to_observation(
                            merged,
                            symbol=symbol,
                            default_observed_at=stamp,
                            source=source,
                        )
                    )
    return rows


def _row_to_observation(
    row: Mapping[str, Any],
    *,
    symbol: str,
    default_observed_at: datetime,
    source: str,
) -> OptionQuoteObservation:
    bid = _as_float(row.get("bid"))
    ask = _as_float(row.get("ask"))
    strike = _as_float(row.get("strike") if row.get("strike") is not None else row.get("strikePrice"))
    if bid is None or ask is None or strike is None:
        raise ValueError("schwab row missing bid/ask/strike")
    if ask < bid:
        raise ValueError("invalid quote: ask < bid")
    option_type = str(row.get("option_type") or row.get("putCall") or "").strip().lower()
    if option_type in {"c", "call", "calls"}:
        option_type = "call"
    elif option_type in {"p", "put", "puts"}:
        option_type = "put"
    else:
        raise ValueError(f"invalid option_type: {option_type!r}")
    expiration = _parse_expiration(row.get("expiration") or row.get("expirationDate"))
    observed_at = (
        _parse_observed_at(row.get("observed_at"))
        if row.get("observed_at") is not None
        else default_observed_at
    )
    last_price = _as_float(row.get("last_price") if row.get("last_price") is not None else row.get("last"))
    iv = _as_float(
        row.get("implied_volatility")
        if row.get("implied_volatility") is not None
        else row.get("volatility")
    )
    return OptionQuoteObservation(
        observed_at=observed_at,
        symbol=symbol,
        expiration=expiration,
        option_type=option_type,
        strike=float(strike),
        bid=float(bid),
        ask=float(ask),
        source=source,
        is_observed=True,
        contract_symbol=str(row.get("contract_symbol") or row.get("symbol") or ""),
        last_price=last_price,
        implied_volatility=iv,
    )


def snapshot_schwab_option_quotes(
    symbol: str,
    *,
    env: Mapping[str, str] | None = None,
    transport: Any | None = None,
) -> dict[str, Any]:
    """Fetch a current chain if credentials + transport are available.

    ``transport`` is an injectable callable ``(symbol, headers, base) -> mapping``
    so unit tests never hit the network. Production wiring can supply an HTTP
    client later without changing the normalize/archive boundary.
    """
    status = credential_status(env=env)
    if not status.ready:
        return {
            "ok": False,
            "symbol": str(symbol).upper(),
            "status": status.to_dict(),
            "n_quotes": 0,
            "observations": [],
            "trading_authority": False,
        }
    if transport is None:
        return {
            "ok": False,
            "symbol": str(symbol).upper(),
            "status": {
                **status.to_dict(),
                "reason": "transport_not_configured: inject HTTP transport or install schwab client wiring",
            },
            "n_quotes": 0,
            "observations": [],
            "trading_authority": False,
        }

    payload = transport(str(symbol).upper(), api_base(env=env))
    if not isinstance(payload, Mapping):
        raise TypeError("schwab transport must return a mapping payload")
    observations = normalize_schwab_option_chain(payload, underlying=str(symbol).upper())
    return {
        "ok": True,
        "symbol": str(symbol).upper(),
        "status": status.to_dict(),
        "n_quotes": len(observations),
        "observations": [row.to_dict() for row in observations],
        "trading_authority": False,
    }


def write_status_report(path: Path, *, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Write a non-secret readiness report for ops / Ken."""
    status = credential_status(env=env)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": "schwab_trader_api",
        "purpose": "research_option_quotes_only",
        "status": status.to_dict(),
        "next_step": (
            "ready_to_wire_read_only_transport"
            if status.ready
            else "configure_local_schwab_developer_credentials"
        ),
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report

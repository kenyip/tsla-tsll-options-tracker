"""Date-aware PCS/CCS/IC contract grids from observed option quote archives."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Iterable, cast
from zoneinfo import ZoneInfo

from trader_platform.research.option_quote_observations import OptionQuoteObservation
from trader_platform.research.pcs_sim import ContractGrid


class ArchivedContractGridProvider:
    """Return only expiry/strike grids observed for the requested market date."""

    def __init__(
        self,
        observations: Iterable[OptionQuoteObservation],
        *,
        market_timezone: str = "America/New_York",
    ) -> None:
        self._observations = [row for row in observations if row.is_observed]
        self._timezone = ZoneInfo(market_timezone)
        self._counters = {
            "requests": 0,
            "covered_requests": 0,
            "missing_symbol_date": 0,
            "observations_selected": 0,
        }

    @staticmethod
    def _entry_date(value: Any) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        converted = value.date()
        if not isinstance(converted, date):
            raise TypeError(f"entry_date must resolve to date, got {type(value).__name__}")
        return converted

    def __call__(self, symbol: str, entry_date: Any) -> ContractGrid | None:
        requested_date = self._entry_date(entry_date)
        normalized_symbol = symbol.strip().upper()
        self._counters["requests"] += 1
        selected = [
            row
            for row in self._observations
            if row.symbol == normalized_symbol
            and row.observed_at.astimezone(self._timezone).date() == requested_date
            and row.expiration >= requested_date
        ]
        if not selected:
            self._counters["missing_symbol_date"] += 1
            return None

        grid: dict[str, dict[str, list[float]]] = {}
        for row in selected:
            rights = grid.setdefault(row.expiration.isoformat(), {})
            rights.setdefault(row.option_type, []).append(float(row.strike))
        for rights in grid.values():
            for option_type, strikes in rights.items():
                rights[option_type] = sorted(set(strikes))
        self._counters["covered_requests"] += 1
        self._counters["observations_selected"] += len(selected)
        return cast(ContractGrid, grid)

    def coverage_counters(self) -> dict[str, Any]:
        requests = self._counters["requests"]
        return {
            **self._counters,
            "coverage_ratio": self._counters["covered_requests"] / requests if requests else 0.0,
            "market_timezone": str(self._timezone),
        }

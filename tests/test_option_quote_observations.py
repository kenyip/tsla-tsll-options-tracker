import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from trader_platform.research.option_quote_observations import (
    OptionQuoteObservation,
    StrategyLegRequirement,
    join_strategy_leg_requirements,
    load_observations_csv,
    observation_from_mapping,
    snapshot_yfinance_option_quotes,
    summarize_archive_density,
    summarize_join_coverage,
    summarize_half_spreads,
    write_observations_csv,
)


_FIXTURE = Path(__file__).parent / "fixtures/option_quote_observations.csv"


class OptionQuoteObservationsTest(unittest.TestCase):
    @staticmethod
    def _quote(
        *, observed_at: datetime, expiration: date, strike: float = 12.0
    ) -> OptionQuoteObservation:
        return OptionQuoteObservation(
            observed_at=observed_at,
            symbol="TSLL",
            expiration=expiration,
            option_type="put",
            strike=strike,
            bid=0.20,
            ask=0.24,
            source="test_observed",
            is_observed=True,
        )

    def test_fixture_smoke_is_explicitly_not_calibration_eligible(self):
        rows = load_observations_csv(_FIXTURE, require_observed=False)
        summary = summarize_half_spreads(rows)

        self.assertEqual(summary["n_quotes"], 2)
        self.assertEqual(summary["n_observed"], 0)
        self.assertAlmostEqual(summary["median_half_spread"], 0.025)
        self.assertFalse(summary["calibration_eligible"])

    def test_default_loader_rejects_synthetic_rows(self):
        with self.assertRaisesRegex(ValueError, "cannot calibrate"):
            load_observations_csv(_FIXTURE)

    def test_invalid_crossed_quote_is_rejected(self):
        row = {
            "observed_at": "2026-07-11T20:00:00-07:00",
            "symbol": "TEST",
            "expiration": "2026-08-21",
            "option_type": "put",
            "strike": "100",
            "bid": "1.30",
            "ask": "1.20",
            "source": "test",
            "is_observed": "true",
        }
        with self.assertRaisesRegex(ValueError, "invalid quote"):
            observation_from_mapping(row)

    def test_exact_contract_asof_join_uses_latest_non_future_quote(self):
        event_at = datetime(2026, 7, 11, 20, 0, tzinfo=timezone.utc)
        requirement = StrategyLegRequirement(
            event_id="trade-1:entry:short_put",
            event_kind="entry",
            event_at=event_at,
            symbol="TSLL",
            expiration=date(2026, 7, 17),
            option_type="put",
            strike=12.0,
        )
        older = OptionQuoteObservation(
            observed_at=event_at - timedelta(minutes=10),
            symbol="TSLL",
            expiration=date(2026, 7, 17),
            option_type="put",
            strike=12.0,
            bid=0.20,
            ask=0.24,
            source="test",
            is_observed=True,
        )
        latest = OptionQuoteObservation(
            observed_at=event_at - timedelta(minutes=2),
            symbol="TSLL",
            expiration=date(2026, 7, 17),
            option_type="put",
            strike=12.0,
            bid=0.21,
            ask=0.23,
            source="test",
            is_observed=True,
        )
        future = OptionQuoteObservation(
            observed_at=event_at + timedelta(seconds=1),
            symbol="TSLL",
            expiration=date(2026, 7, 17),
            option_type="put",
            strike=12.0,
            bid=0.22,
            ask=0.24,
            source="test",
            is_observed=True,
        )

        joined = join_strategy_leg_requirements(
            [requirement], [older, latest, future], max_quote_age=timedelta(minutes=5)
        )

        self.assertEqual(joined[0].observation, latest)
        self.assertEqual(joined[0].reason, "matched")

    def test_join_coverage_rejects_missing_exit_and_stale_entry(self):
        event_at = datetime(2026, 7, 11, 20, 0, tzinfo=timezone.utc)
        requirements = [
            StrategyLegRequirement(
                event_id=f"trade-1:{kind}:short_put",
                event_kind=kind,
                event_at=event_at,
                symbol="TSLL",
                expiration=date(2026, 7, 17),
                option_type="put",
                strike=12.0,
            )
            for kind in ("entry", "exit")
        ]
        stale = OptionQuoteObservation(
            observed_at=event_at - timedelta(hours=2),
            symbol="TSLL",
            expiration=date(2026, 7, 17),
            option_type="put",
            strike=12.0,
            bid=0.20,
            ask=0.24,
            source="test",
            is_observed=True,
        )

        joined = join_strategy_leg_requirements(
            requirements, [stale], max_quote_age=timedelta(minutes=30)
        )
        summary = summarize_join_coverage(joined)

        self.assertEqual(summary["matched_legs"], 0)
        self.assertFalse(summary["calibration_eligible"])
        self.assertIn("missing_entry_coverage", summary["rejection_reasons"])
        self.assertIn("missing_exit_coverage", summary["rejection_reasons"])

    def test_snapshot_captures_every_available_expiration_by_default(self):
        class Frame:
            def __init__(self, records):
                self._records = records

            def to_dict(self, *, orient):
                self.assert_orient = orient
                return self._records

        class Ticker:
            options = ("2026-07-17", "2026-07-24")

            def __init__(self):
                self.requested = []

            def option_chain(self, expiration):
                self.requested.append(expiration)
                strike = 17.0 if expiration.endswith("17") else 24.0
                record = {
                    "strike": strike,
                    "bid": 0.20,
                    "ask": 0.24,
                    "contractSymbol": f"TSLL{expiration}",
                }
                return SimpleNamespace(calls=Frame([record]), puts=Frame([record]))

        ticker = Ticker()
        fake_yfinance = SimpleNamespace(Ticker=lambda _symbol: ticker)
        with patch.dict("sys.modules", {"yfinance": fake_yfinance}):
            rows = snapshot_yfinance_option_quotes("TSLL")

        self.assertEqual(ticker.requested, list(ticker.options))
        self.assertEqual({row.expiration.isoformat() for row in rows}, set(ticker.options))
        self.assertEqual(len(rows), 4)
        self.assertEqual(len({row.observed_at for row in rows}), 1)

    def test_append_write_preserves_history_and_is_idempotent(self):
        first_at = datetime(2026, 7, 11, 20, 0, tzinfo=timezone.utc)
        second_at = datetime(2026, 7, 13, 20, 0, tzinfo=timezone.utc)
        first = self._quote(observed_at=first_at, expiration=date(2026, 7, 17))
        second = self._quote(observed_at=second_at, expiration=date(2026, 7, 24))

        with TemporaryDirectory() as directory:
            archive = Path(directory) / "TSLL.csv"
            write_observations_csv(archive, [first])
            write_observations_csv(archive, [second], append=True)
            write_observations_csv(archive, [second], append=True)
            loaded = load_observations_csv(archive)

        self.assertEqual(loaded, [first, second])

    def test_archive_density_fails_closed_below_three_market_dates(self):
        rows = [
            self._quote(
                observed_at=datetime(2026, 7, day, 20, 0, tzinfo=timezone.utc),
                expiration=date(2026, 7, 24),
                strike=float(day),
            )
            for day in (11, 12)
        ]

        summary = summarize_archive_density(rows, minimum_market_dates=3)

        self.assertEqual(summary["n_market_dates"], 2)
        self.assertEqual(summary["minimum_market_dates"], 3)
        self.assertFalse(summary["provider_backtest_eligible"])
        self.assertEqual(summary["rejection_reasons"], ["insufficient_market_date_density"])


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from trader_platform.research.corporate_action_risk import (
    assess_short_call_assignment_risk,
)
from trader_platform.research.dividend_event_archive import (
    ArchivedDividendEventProvider,
    archive_from_mapping,
    archive_from_nasdaq_payload,
    load_dividend_event_archive,
    write_dividend_event_archive,
)


def _payload(rows, *, code=200, message=None):
    return {
        "data": {"dividends": {"rows": rows}} if code == 200 else None,
        "message": message,
        "status": {"rCode": code},
    }


def _row(ex_date, declaration_date, amount="$0.25"):
    return {
        "exOrEffDate": ex_date,
        "type": "Cash",
        "amount": amount,
        "declarationDate": declaration_date,
        "recordDate": ex_date,
        "paymentDate": ex_date,
        "currency": "USD",
    }


class DividendEventArchiveTest(unittest.TestCase):
    observed_at = datetime(2026, 7, 12, 23, 0, tzinfo=timezone.utc)

    def test_nasdaq_rows_preserve_declaration_date_as_known_at(self):
        archive = archive_from_nasdaq_payload(
            "aapl",
            _payload(
                [
                    _row("05/11/2026", "04/30/2026", "$0.27"),
                    _row("02/09/2026", "01/29/2026", "$0.26"),
                    _row("11/21/1988", "N/A", "$0.10"),
                ]
            ),
            observed_at=self.observed_at,
        )

        self.assertEqual(archive.symbol, "AAPL")
        self.assertEqual(archive.source_rows, 3)
        self.assertEqual(archive.retained_rows, 2)
        self.assertTrue(archive.truncated_at_missing_known_at)
        self.assertEqual(archive.events[-1].known_at, pd.Timestamp("2026-04-30"))
        self.assertEqual(archive.coverage_start, pd.Timestamp("2026-01-29"))

    def test_provider_enforces_symbol_and_asof_coverage_but_allows_future_through(self):
        archive = archive_from_nasdaq_payload(
            "AAPL",
            _payload([_row("05/11/2026", "04/30/2026", "$0.27")]),
            observed_at=self.observed_at,
        )
        provider = ArchivedDividendEventProvider(archive)

        self.assertIsNone(
            provider("MSFT", pd.Timestamp("2026-06-01"), pd.Timestamp("2026-07-01"))
        )
        self.assertIsNone(
            provider("AAPL", pd.Timestamp("2026-04-29"), pd.Timestamp("2026-05-30"))
        )
        covered = provider(
            "AAPL", pd.Timestamp("2026-05-01"), pd.Timestamp("2026-08-01")
        )
        self.assertEqual(covered, archive.events)

    def test_first_announced_event_is_servable_before_ex_date(self):
        archive = archive_from_nasdaq_payload(
            "AAPL",
            _payload([_row("05/11/2026", "04/30/2026", "$0.27")]),
            observed_at=self.observed_at,
        )
        provider = ArchivedDividendEventProvider(archive)

        self.assertEqual(archive.coverage_start, pd.Timestamp("2026-04-30"))
        self.assertEqual(
            provider("AAPL", pd.Timestamp("2026-05-01"), pd.Timestamp("2026-05-11")),
            archive.events,
        )

    def test_future_announcement_remains_invisible_after_archive_load(self):
        payload = {
            "schema_version": 1,
            "symbol": "TEST",
            "observed_at": "2026-07-12T23:00:00+00:00",
            "coverage_start": "2026-01-12T00:00:00",
            "source": "nasdaq_dividend_history",
            "source_rows": 1,
            "retained_rows": 1,
            "truncated_at_missing_known_at": False,
            "events": [
                {
                    "symbol": "TEST",
                    "ex_date": "2026-01-20T00:00:00",
                    "amount_per_share": 5.0,
                    "known_at": "2026-01-12T00:00:00",
                }
            ],
        }
        archive = archive_from_mapping(payload)
        before = assess_short_call_assignment_risk(
            symbol="TEST",
            as_of=pd.Timestamp("2026-01-09"),
            expiration=pd.Timestamp("2026-01-30"),
            spot=60.0,
            short_strike=50.0,
            short_call_mark=10.25,
            events=archive.events,
        )
        after = assess_short_call_assignment_risk(
            symbol="TEST",
            as_of=pd.Timestamp("2026-01-13"),
            expiration=pd.Timestamp("2026-01-30"),
            spot=60.0,
            short_strike=50.0,
            short_call_mark=10.25,
            events=archive.events,
        )

        self.assertFalse(before.at_risk)
        self.assertTrue(after.at_risk)

    def test_ambiguous_empty_or_unsupported_source_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "coverage ambiguous"):
            archive_from_nasdaq_payload(
                "SMCI",
                _payload([], message="never paid or dividend pending"),
                observed_at=self.observed_at,
            )
        with self.assertRaisesRegex(ValueError, "unsupported"):
            archive_from_nasdaq_payload(
                "TSLL", _payload([], code=400), observed_at=self.observed_at
            )

    def test_missing_latest_declaration_or_future_declaration_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "latest.*lacks declarationDate"):
            archive_from_nasdaq_payload(
                "AAPL",
                _payload([_row("05/11/2026", "N/A")]),
                observed_at=self.observed_at,
            )
        with self.assertRaisesRegex(ValueError, "after snapshot"):
            archive_from_nasdaq_payload(
                "AAPL",
                _payload([_row("08/11/2026", "07/30/2026")]),
                observed_at=self.observed_at,
            )

    def test_atomic_archive_round_trip_and_tamper_boundary(self):
        archive = archive_from_nasdaq_payload(
            "AAPL",
            _payload([_row("05/11/2026", "04/30/2026", "$0.27")]),
            observed_at=self.observed_at,
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "AAPL.json"
            write_dividend_event_archive(path, archive)
            loaded = load_dividend_event_archive(path)
            tampered = json.loads(path.read_text())
            tampered["coverage_start"] = "2020-01-01T00:00:00"

        self.assertEqual(loaded, archive)
        with self.assertRaisesRegex(ValueError, "coverage boundary"):
            archive_from_mapping(tampered)

        future_known_at = archive.to_dict()
        future_known_at["events"][0]["known_at"] = "2026-07-13T00:00:00"
        future_known_at["events"][0]["ex_date"] = "2026-07-14T00:00:00"
        with self.assertRaisesRegex(ValueError, "identity or timing"):
            archive_from_mapping(future_known_at)

    def test_archive_row_count_tampering_fails_closed(self):
        archive = archive_from_nasdaq_payload(
            "AAPL",
            _payload([_row("05/11/2026", "04/30/2026", "$0.27")]),
            observed_at=self.observed_at,
        )
        payload = archive.to_dict()
        payload["retained_rows"] = 2

        with self.assertRaisesRegex(ValueError, "row counts"):
            archive_from_mapping(payload)


if __name__ == "__main__":
    unittest.main()

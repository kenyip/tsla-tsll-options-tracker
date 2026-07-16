import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

from scripts.beige_book_range_compression_train_lab import (
    build_beige_book_matched_blueprints,
    load_official_beige_sources,
    parse_official_beige_book_events,
    run_lab_from_frame,
)


class BeigeBookRangeCompressionTrainLabTest(unittest.TestCase):
    def test_official_parser_uses_pdf_date_and_corroborates_calendar_time(self):
        page = b'''<html><body>
        <a href="/monetarypolicy/files/BeigeBook_20240117.pdf">PDF</a>
        <a href="/monetarypolicy/files/not-beige-20240306.pdf">other</a>
        </body></html>'''
        calendar = json.dumps(
            {
                "events": [
                    {
                        "title": "Beige Book",
                        "time": "2:00 p.m.",
                        "month": "2024-01",
                        "days": "17",
                        "type": "Beige",
                    }
                ],
                "announcement": [],
            }
        ).encode()

        events = parse_official_beige_book_events(
            {2024: page}, calendar, start="2024-01-01", end="2024-12-31"
        )

        self.assertEqual(len(events), 1)
        row = events.iloc[0]
        self.assertEqual(row["decision_date"], pd.Timestamp("2024-01-17"))
        self.assertEqual(str(row["release_at_new_york"]), "2024-01-17 14:00:00-05:00")
        self.assertEqual(
            row["source_url"],
            "https://www.federalreserve.gov/monetarypolicy/files/BeigeBook_20240117.pdf",
        )
        self.assertTrue(row["calendar_time_corroborated"])
        self.assertEqual(events.attrs["calendar_overlap_events"], 1)
        self.assertEqual(events.attrs["calendar_time_conflicts"], 0)

    def test_uncorroborated_archive_time_is_strict_json_safe(self):
        page = b'''<html><body>
        <a href="/monetarypolicy/files/BeigeBook_20240117.pdf">PDF</a>
        <a href="/monetarypolicy/files/BeigeBook_20240306.pdf">PDF</a>
        </body></html>'''
        calendar = json.dumps(
            {
                "events": [
                    {
                        "title": "Beige Book",
                        "time": "2:00 p.m.",
                        "month": "2024-01",
                        "days": "17",
                        "type": "Beige",
                    }
                ],
                "announcement": [],
            }
        ).encode()

        events = parse_official_beige_book_events(
            {2024: page}, calendar, start="2024-01-01", end="2024-12-31"
        )
        rows = events.to_dict(orient="records")

        self.assertEqual(rows[1]["calendar_time"], "")
        json.dumps(rows, allow_nan=False, default=str)

    def test_official_calendar_time_conflict_fails_closed(self):
        page = b'<a href="/monetarypolicy/files/BeigeBook_20240117.pdf">PDF</a>'
        calendar = json.dumps(
            {
                "events": [
                    {
                        "title": "Beige Book",
                        "time": "3:00 p.m.",
                        "month": "2024-01",
                        "days": "17",
                        "type": "Beige",
                    }
                ],
                "announcement": [],
            }
        ).encode()

        with self.assertRaisesRegex(ValueError, "calendar time conflict"):
            parse_official_beige_book_events(
                {2024: page}, calendar, start="2024-01-01", end="2024-12-31"
            )

    def test_blueprint_uses_prior_features_and_ignores_future_outcomes(self):
        index = pd.bdate_range("2018-01-02", periods=700)
        close = 100.0 * np.exp(np.linspace(0.0, 0.08, len(index)))
        frame = pd.DataFrame(
            {
                "open": close,
                "high": close * 1.005,
                "low": close * 0.995,
                "close": close,
                "volume": 1_000_000,
            },
            index=index,
        )
        decision_date = index[520]
        events = pd.DataFrame(
            {
                "decision_date": [decision_date],
                "release_at_new_york": [
                    pd.Timestamp(decision_date).tz_localize("America/New_York")
                    + pd.Timedelta(hours=14)
                ],
                "source_url": ["https://www.federalreserve.gov/beige.pdf"],
            }
        )

        baseline = build_beige_book_matched_blueprints(
            frame,
            events,
            max_distance_sessions=300,
            max_hv20_gap=0.08,
            max_ret60_gap=0.08,
        )
        shocked = frame.copy()
        shocked.loc[index[521:526], ["open", "high", "low", "close"]] *= 1.25
        changed = build_beige_book_matched_blueprints(
            shocked,
            events,
            max_distance_sessions=300,
            max_hv20_gap=0.08,
            max_ret60_gap=0.08,
        )

        self.assertEqual(baseline, changed)
        self.assertEqual(len(baseline), 1)
        row = baseline[0]
        self.assertEqual(row["feature_date"], index[519])
        self.assertEqual(row["event_entry_date"], index[521])
        self.assertEqual(row["event_exit_date"], index[525])
        self.assertLess(row["control_exit_date"], decision_date)
        self.assertLessEqual(abs(row["event_ret60"]), 0.12)
        self.assertLessEqual(row["event_hv20"], 0.30)

    def test_train_only_lab_fails_closed_when_range_does_not_compress(self):
        index = pd.bdate_range("2012-01-03", periods=2_400)
        close = 100.0 * np.exp(np.linspace(0.0, 0.12, len(index)))
        frame = pd.DataFrame(
            {
                "open": close,
                "high": close * 1.01,
                "low": close * 0.99,
                "close": close,
                "volume": 1_000_000,
            },
            index=index,
        )
        event_positions = list(range(300, 2_200, 120))
        events = pd.DataFrame(
            {
                "decision_date": [index[position] for position in event_positions],
                "release_at_new_york": [
                    pd.Timestamp(index[position]).tz_localize("America/New_York")
                    + pd.Timedelta(hours=14)
                    for position in event_positions
                ],
                "source_url": [
                    f"https://www.federalreserve.gov/BeigeBook_{index[position]:%Y%m%d}.pdf"
                    for position in event_positions
                ],
            }
        )

        payload = run_lab_from_frame(
            frame,
            events,
            control_exclusion_events=events,
            provenance={"fixture": True},
            min_train_pairs=1,
            min_event_years=1,
            min_control_support=0.0,
            min_positive_frequency=0.0,
            max_event_range_p90=1.0,
            bootstrap_samples=400,
        )

        self.assertEqual(payload["strategy_outcome"], "FAMILY_CLOSED")
        self.assertEqual(
            payload["candidate_id"], "BEIGE_BOOK_RANGE_COMPRESSION_SPY_IC_21D_V1"
        )
        self.assertEqual(
            payload["family_id"], "BEIGE_BOOK_INFORMATION_RESOLUTION_RANGE_COMPRESSION"
        )
        self.assertFalse(payload["train"]["gate_pass"])
        self.assertLess(payload["train"]["metrics"]["mean_paired_compression_after_hurdle"], 0.0)
        self.assertFalse(payload["untouched_holdout"]["outcome_metrics_read"])
        self.assertFalse(payload["untouched_holdout"]["simulation_run"])
        self.assertNotIn("mean_range", payload["untouched_holdout"])
        self.assertEqual(payload["option_stage"]["pricing_calls"], 0)
        self.assertFalse(payload["l1_claim"])
        match_quality = payload["train"]["metrics"]["match_quality"]
        pairs = payload["train"]["pairs"]
        distances = [row["calendar_distance_sessions"] for row in pairs]
        compressions = [row["paired_compression_after_hurdle"] for row in pairs]
        self.assertEqual(match_quality["calendar_distance_sessions"]["count"], len(pairs))
        self.assertEqual(
            match_quality["calendar_distance_sessions"]["median"],
            float(np.median(distances)),
        )
        self.assertEqual(
            match_quality["calendar_distance_sessions"]["max"], float(max(distances))
        )
        self.assertEqual(
            match_quality["calendar_distance_over_252_sessions_count"],
            sum(value > 252 for value in distances),
        )
        self.assertEqual(
            match_quality["absolute_paired_compression_over_5pct_count"],
            sum(abs(value) > 0.05 for value in compressions),
        )
        self.assertTrue(match_quality["diagnostic_only"])
        self.assertNotIn("match_quality", payload["train"]["gates"])
        json.dumps(payload, allow_nan=False)

    def test_synthetic_compression_signal_can_advance_discovery_gate(self):
        index = pd.bdate_range("2012-01-03", periods=2_400)
        close = 100.0 * np.exp(np.linspace(0.0, 0.12, len(index)))
        frame = pd.DataFrame(
            {
                "open": close,
                "high": close * 1.02,
                "low": close * 0.98,
                "close": close,
                "volume": 1_000_000,
            },
            index=index,
        )
        event_positions = list(range(300, 2_200, 120))
        for position in event_positions:
            frame.loc[index[position + 1 : position + 6], "high"] = (
                frame.loc[index[position + 1 : position + 6], "close"] * 1.001
            )
            frame.loc[index[position + 1 : position + 6], "low"] = (
                frame.loc[index[position + 1 : position + 6], "close"] * 0.999
            )
        events = pd.DataFrame(
            {
                "decision_date": [index[position] for position in event_positions],
                "release_at_new_york": [
                    pd.Timestamp(index[position]).tz_localize("America/New_York")
                    + pd.Timedelta(hours=14)
                    for position in event_positions
                ],
                "source_url": [
                    f"https://www.federalreserve.gov/BeigeBook_{index[position]:%Y%m%d}.pdf"
                    for position in event_positions
                ],
            }
        )

        payload = run_lab_from_frame(
            frame,
            events,
            control_exclusion_events=events,
            provenance={"fixture": True},
            min_train_pairs=1,
            min_event_years=1,
            min_control_support=0.0,
            min_positive_frequency=0.50,
            max_event_range_p90=1.0,
            bootstrap_samples=400,
        )

        self.assertEqual(payload["strategy_outcome"], "STRATEGY_ADVANCED")
        self.assertTrue(payload["train"]["gate_pass"])
        self.assertGreater(
            payload["train"]["metrics"]["mean_paired_compression_after_hurdle"],
            0.0,
        )
        self.assertTrue(all(payload["train"]["integrity"].values()))

    def test_official_source_cache_replays_exact_hashed_bytes(self):
        page = b'<a href="/monetarypolicy/files/BeigeBook_20240117.pdf">PDF</a>'
        calendar = json.dumps({"events": [], "announcement": []}).encode()
        calls = []

        def fetch(url):
            calls.append(url)
            return calendar if url.endswith("calendar.json") else page

        with tempfile.TemporaryDirectory() as directory:
            first_pages, first_calendar, first_meta = load_official_beige_sources(
                Path(directory), start_year=2024, end_year=2024, fetch_bytes=fetch
            )
            second_pages, second_calendar, second_meta = load_official_beige_sources(
                Path(directory),
                start_year=2024,
                end_year=2024,
                fetch_bytes=lambda url: self.fail("cache miss"),
            )

        self.assertEqual(len(calls), 2)
        self.assertEqual(first_pages, second_pages)
        self.assertEqual(first_calendar, second_calendar)
        self.assertEqual(first_meta["annual_pages"]["2024"]["sha256"], second_meta["annual_pages"]["2024"]["sha256"])
        self.assertEqual(first_meta["calendar"]["sha256"], second_meta["calendar"]["sha256"])

    def test_script_entrypoint_imports_from_repo_root(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/beige_book_range_compression_train_lab.py",
                "--help",
            ],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("range-compression discovery lab", result.stdout)


if __name__ == "__main__":
    unittest.main()

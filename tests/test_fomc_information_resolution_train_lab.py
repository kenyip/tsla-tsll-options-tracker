import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from scripts.fomc_information_resolution_train_lab import (
    EVENT_TITLE,
    _event_manifest,
    build_fomc_matched_blueprints,
    load_adjusted_ohlcv,
    load_official_press_records,
    parse_official_fomc_events,
    run_lab_from_frame,
)


class FomcInformationResolutionTrainLabTest(unittest.TestCase):
    def test_official_event_parser_accepts_only_exact_2pm_statement_rows(self):
        records = [
            {
                "d": "3/20/2024 2:00:00 PM",
                "t": "Federal Reserve issues FOMC statement",
                "pt": "Monetary Policy",
                "l": "/newsevents/pressreleases/monetary20240320a.htm",
            },
            {
                "d": "3/3/2020 10:00:00 AM",
                "t": "Federal Reserve issues FOMC statement",
                "pt": "Monetary Policy",
                "l": "/newsevents/pressreleases/monetary20200303a.htm",
            },
            {
                "d": "9/17/2014 2:00:00 PM",
                "t": "Federal Reserve issues FOMC statement on policy normalization principles and plans",
                "pt": "Monetary Policy",
                "l": "/newsevents/pressreleases/monetary20140917c.htm",
            },
            {
                "d": "3/20/2024 2:00:00 PM",
                "t": "Federal Reserve issues FOMC statement",
                "pt": "Other",
                "l": "/newsevents/pressreleases/monetary20240320a.htm",
            },
            {
                "d": "3/20/2024 2:00:00 PM",
                "t": "Federal Reserve issues FOMC statement",
                "pt": "Monetary Policy",
                "l": "/newsevents/pressreleases/orders20240320a.htm",
            },
        ]

        events = parse_official_fomc_events(records, start="2013-01-01", end="2025-12-31")

        self.assertEqual(len(events), 1)
        row = events.iloc[0]
        self.assertEqual(row["decision_date"], pd.Timestamp("2024-03-20"))
        self.assertEqual(str(row["release_at_new_york"]), "2024-03-20 14:00:00-04:00")
        self.assertEqual(
            row["statement_url"],
            "https://www.federalreserve.gov/newsevents/pressreleases/monetary20240320a.htm",
        )
        self.assertEqual(events.attrs["excluded_non_2pm"], 1)
        self.assertEqual(events.attrs["excluded_wrong_title"], 1)
        self.assertEqual(events.attrs["excluded_wrong_press_type"], 1)
        self.assertEqual(events.attrs["excluded_bad_url"], 1)

    def test_event_manifest_records_distinct_candidate_and_control_exclusion_scopes(self):
        records = [
            {
                "d": "3/13/2012 2:00:00 PM",
                "t": EVENT_TITLE,
                "pt": "Monetary Policy",
                "l": "/newsevents/pressreleases/monetary20120313a.htm",
            },
            {
                "d": "3/20/2024 2:00:00 PM",
                "t": EVENT_TITLE,
                "pt": "Monetary Policy",
                "l": "/newsevents/pressreleases/monetary20240320a.htm",
            },
        ]
        candidates = parse_official_fomc_events(
            records, start="2013-01-01", end="2025-12-31"
        )
        exclusions = parse_official_fomc_events(
            records, start="2012-01-01", end="2025-12-31"
        )

        manifest = _event_manifest(
            candidates,
            {"fixture": True},
            control_exclusion_events=exclusions,
        )

        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual(len(manifest["events"]), 1)
        self.assertEqual(len(manifest["control_exclusion_events"]), 2)
        self.assertEqual(
            manifest["control_exclusion_events"][0]["decision_date"], "2012-03-13"
        )

    def test_blueprint_uses_prior_features_next_session_open_and_no_outcome_matching(self):
        index = pd.bdate_range("2018-01-02", periods=700)
        close = 100.0 * np.exp(np.linspace(0.0, 0.8, len(index)))
        frame = pd.DataFrame(
            {
                "open": close * 1.0005,
                "high": close * 1.01,
                "low": close * 0.99,
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
                "statement_url": [
                    f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{decision_date:%Y%m%d}a.htm"
                ],
            }
        )

        baseline = build_fomc_matched_blueprints(
            frame,
            events,
            max_distance_sessions=300,
            max_hv20_gap=0.20,
            max_ret60_gap=0.20,
        )
        shocked = frame.copy()
        shocked.loc[index[521:526], ["open", "high", "low", "close"]] *= 1.25
        changed = build_fomc_matched_blueprints(
            shocked,
            events,
            max_distance_sessions=300,
            max_hv20_gap=0.20,
            max_ret60_gap=0.20,
        )

        self.assertEqual(len(baseline), 1)
        self.assertEqual(
            {k: v for k, v in baseline[0].items() if not k.endswith("return")},
            {k: v for k, v in changed[0].items() if not k.endswith("return")},
        )
        row = baseline[0]
        self.assertEqual(row["event_entry_date"], index[521])
        self.assertEqual(row["event_exit_date"], index[525])
        self.assertLess(row["control_exit_date"], decision_date)
        self.assertLess(row["control_exit_date"], index[515])
        self.assertLess(row["control_entry_date"], row["control_exit_date"])
        self.assertEqual(row["feature_date"], index[519])

    def test_control_window_cannot_touch_fomc_exclusion_band(self):
        index = pd.bdate_range("2020-01-02", periods=400)
        close = 100.0 * np.exp(np.arange(len(index)) * 0.001)
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
        decision_date = index[300]
        events = pd.DataFrame(
            {
                "decision_date": [decision_date],
                "release_at_new_york": [
                    pd.Timestamp(decision_date).tz_localize("America/New_York")
                    + pd.Timedelta(hours=14)
                ],
                "statement_url": ["https://www.federalreserve.gov/statement.htm"],
            }
        )

        blueprints = build_fomc_matched_blueprints(
            frame,
            events,
            max_distance_sessions=7,
            max_hv20_gap=1.0,
            max_ret60_gap=1.0,
            event_exclusion_sessions=5,
        )

        self.assertEqual(blueprints, [])

    def test_control_window_excludes_prior_official_events_outside_candidate_window(self):
        index = pd.bdate_range("2020-01-02", periods=400)
        close = 100.0 * np.exp(np.arange(len(index)) * 0.001)
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
        prior_decision = index[290]
        candidate_decision = index[300]

        def event_frame(dates):
            return pd.DataFrame(
                {
                    "decision_date": dates,
                    "release_at_new_york": [
                        pd.Timestamp(date).tz_localize("America/New_York")
                        + pd.Timedelta(hours=14)
                        for date in dates
                    ],
                    "statement_url": [
                        f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{date:%Y%m%d}a.htm"
                        for date in dates
                    ],
                }
            )

        candidate_events = event_frame([candidate_decision])
        all_official_events = event_frame([prior_decision, candidate_decision])
        contaminated = build_fomc_matched_blueprints(
            frame,
            candidate_events,
            max_distance_sessions=12,
            max_hv20_gap=1.0,
            max_ret60_gap=1.0,
            event_exclusion_sessions=5,
        )
        excluded = build_fomc_matched_blueprints(
            frame,
            candidate_events,
            control_exclusion_events=all_official_events,
            max_distance_sessions=12,
            max_hv20_gap=1.0,
            max_ret60_gap=1.0,
            event_exclusion_sessions=5,
        )

        self.assertEqual(len(contaminated), 1)
        self.assertEqual(contaminated[0]["control_entry_date"], prior_decision)
        self.assertEqual(excluded, [])

    def test_control_window_cannot_predate_official_event_source_coverage(self):
        index = pd.bdate_range("2020-01-02", periods=400)
        close = 100.0 * np.exp(np.arange(len(index)) * 0.001)
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
        decision_date = index[300]
        events = pd.DataFrame(
            {
                "decision_date": [decision_date],
                "release_at_new_york": [
                    pd.Timestamp(decision_date).tz_localize("America/New_York")
                    + pd.Timedelta(hours=14)
                ],
                "statement_url": [
                    f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{decision_date:%Y%m%d}a.htm"
                ],
            }
        )

        blueprints = build_fomc_matched_blueprints(
            frame,
            events,
            control_exclusion_events=events,
            max_distance_sessions=300,
            max_hv20_gap=1.0,
            max_ret60_gap=1.0,
            event_exclusion_sessions=5,
        )

        self.assertEqual(blueprints, [])

    def test_run_is_train_only_strict_json_and_fail_closed_on_no_incremental_edge(self):
        index = pd.bdate_range("2012-01-03", periods=2_200)
        close = 100.0 * np.exp(np.linspace(0.0, 1.0, len(index)))
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
        event_positions = list(range(300, 2_000, 120))
        events = pd.DataFrame(
            {
                "decision_date": [index[position] for position in event_positions],
                "release_at_new_york": [
                    pd.Timestamp(index[position]).tz_localize("America/New_York")
                    + pd.Timedelta(hours=14)
                    for position in event_positions
                ],
                "statement_url": [
                    f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{index[position]:%Y%m%d}a.htm"
                    for position in event_positions
                ],
            }
        )

        payload = run_lab_from_frame(
            frame,
            events,
            control_exclusion_events=events,
            provenance={"fixture": True},
            train_fraction=0.60,
            min_train_pairs=1,
            min_event_years=1,
            min_control_support=0.0,
            min_positive_frequency=0.0,
            worst_decile_floor=-1.0,
            bootstrap_samples=400,
        )

        self.assertEqual(payload["strategy_outcome"], "FAMILY_CLOSED")
        self.assertFalse(payload["train"]["gate_pass"])
        self.assertTrue(
            payload["train"]["integrity"][
                "control_windows_outside_event_exclusion_bands"
            ]
        )
        self.assertTrue(
            payload["train"]["integrity"]["control_windows_within_source_coverage"]
        )
        self.assertEqual(
            len(payload["train"]["pairs"]), payload["population"]["train_matched_pairs"]
        )
        self.assertTrue(
            all(
                pair["control_exit_date"] < pair["decision_date"]
                for pair in payload["train"]["pairs"]
            )
        )
        self.assertFalse(payload["untouched_holdout"]["outcome_metrics_read"])
        self.assertFalse(payload["untouched_holdout"]["simulation_run"])
        self.assertNotIn("mean_return", payload["untouched_holdout"])
        self.assertEqual(payload["option_stage"]["pricing_calls"], 0)
        self.assertEqual(
            payload["population"]["control_exclusion_official_events"], len(events)
        )
        self.assertEqual(
            payload["population"]["control_source_coverage_start"],
            str(events["decision_date"].min().date()),
        )
        self.assertFalse(payload["l1_claim"])
        json.dumps(payload, allow_nan=False)

    def test_adjusted_ohlcv_cache_round_trip_consumes_persisted_bytes(self):
        index = pd.bdate_range("2024-01-02", periods=120)
        downloaded = pd.DataFrame(
            {
                "Open": np.linspace(100.0, 110.0, len(index)),
                "High": np.linspace(101.0, 111.0, len(index)),
                "Low": np.linspace(99.0, 109.0, len(index)),
                "Close": np.linspace(100.5, 110.5, len(index)),
                "Volume": np.full(len(index), 1_000_000),
            },
            index=index,
        )
        calls = []

        def downloader(*args, **kwargs):
            calls.append((args, kwargs))
            return downloaded.copy()

        with tempfile.TemporaryDirectory() as directory:
            first, first_meta = load_adjusted_ohlcv(
                "SPY",
                cache_dir=Path(directory),
                start="2024-01-01",
                end="2024-07-01",
                downloader=downloader,
            )
            second, second_meta = load_adjusted_ohlcv(
                "SPY",
                cache_dir=Path(directory),
                start="2024-01-01",
                end="2024-07-01",
                downloader=lambda *args, **kwargs: self.fail("cache miss"),
            )

        self.assertEqual(len(calls), 1)
        pd.testing.assert_frame_equal(first, second)
        self.assertEqual(first_meta["sha256"], second_meta["sha256"])
        self.assertEqual(first_meta["adjustment_semantics"], "yfinance auto_adjust=True")

    def test_official_press_cache_hashes_and_replays_exact_source_bytes(self):
        source = (
            '\ufeff[{"d":"3/20/2024 2:00:00 PM","t":"Federal Reserve issues FOMC statement",'
            '"pt":"Monetary Policy","l":"/newsevents/pressreleases/monetary20240320a.htm"}]'
        ).encode("utf-8")
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fed.json"
            first, first_meta = load_official_press_records(
                path, fetch_bytes=lambda url: calls.append(url) or source
            )
            second, second_meta = load_official_press_records(
                path, fetch_bytes=lambda url: self.fail("cache miss")
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(first, second)
        self.assertEqual(first_meta["sha256"], second_meta["sha256"])
        self.assertEqual(first_meta["bytes"], len(source))


if __name__ == "__main__":
    unittest.main()

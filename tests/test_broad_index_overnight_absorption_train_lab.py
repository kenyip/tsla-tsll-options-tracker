import unittest

import numpy as np
import pandas as pd

from scripts.broad_index_overnight_absorption_train_lab import (
    _dependence_diagnostics,
    _identity_payload,
    build_features,
    evaluate_train,
    freeze_signals,
    match_prior_controls,
    planning_risk_boundaries,
    trigger_mask,
)


class BroadIndexOvernightAbsorptionTrainLabTest(unittest.TestCase):
    @staticmethod
    def _raw_frame(periods: int = 1500, trigger_pos: int = 300) -> pd.DataFrame:
        index = pd.bdate_range("2015-01-02", periods=periods)
        close = np.linspace(100.0, 180.0, periods)
        overnight = np.zeros(periods)
        intraday = np.zeros(periods)
        for position in range(trigger_pos - 4, trigger_pos + 1):
            overnight[position] = -0.003
            intraday[position] = 0.004
        open_price = np.empty(periods)
        open_price[0] = close[0]
        for position in range(1, periods):
            open_price[position] = close[position - 1] * (1.0 + overnight[position])
            close[position] = open_price[position] * (1.0 + intraday[position])
        high = np.maximum(open_price, close) * 1.001
        low = np.minimum(open_price, close) * 0.999
        return pd.DataFrame(
            {
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": np.full(periods, 1_000_000.0),
            },
            index=index,
        )

    @staticmethod
    def _feature_frame(periods: int = 900) -> pd.DataFrame:
        index = pd.bdate_range("2010-01-04", periods=periods)
        close = np.full(periods, 100.0)
        return pd.DataFrame(
            {
                "open": close,
                "close": close.copy(),
                "sma100": np.full(periods, 95.0),
                "ret60": np.full(periods, 0.05),
                "hv20": np.full(periods, 0.18),
                "overnight5": np.zeros(periods),
                "intraday5": np.zeros(periods),
                "sma_distance": np.full(periods, 100.0 / 95.0 - 1.0),
            },
            index=index,
        )

    @staticmethod
    def _matched_panel(event_returns: list[float]) -> tuple[dict[str, pd.DataFrame], list[dict]]:
        symbols = ("SPY", "QQQ", "IWM")
        features = {symbol: BroadIndexOvernightAbsorptionTrainLabTest._feature_frame() for symbol in symbols}
        matched: list[dict] = []
        for episode, event_return in enumerate(event_returns):
            signal_pos = 400 + episode * 12
            control_pos = 120 + episode * 12
            for symbol in symbols:
                frame = features[symbol]
                frame.iloc[signal_pos, frame.columns.get_loc("overnight5")] = -0.02
                frame.iloc[signal_pos, frame.columns.get_loc("intraday5")] = 0.02
                entry_pos = signal_pos + 1
                exit_pos = entry_pos + 5
                frame.iloc[entry_pos, frame.columns.get_loc("close")] = 100.0
                frame.iloc[exit_pos, frame.columns.get_loc("close")] = 100.0 * (1.0 + event_return)
                control_entry = control_pos + 1
                control_exit = control_entry + 5
                frame.iloc[control_entry, frame.columns.get_loc("close")] = 100.0
                frame.iloc[control_exit, frame.columns.get_loc("close")] = 100.0
                matched.append(
                    {
                        "symbol": symbol,
                        "signal_pos": signal_pos,
                        "signal_date": frame.index[signal_pos],
                        "feature_max_date": frame.index[signal_pos],
                        "entry_pos": entry_pos,
                        "entry_date": frame.index[entry_pos],
                        "exit_pos": exit_pos,
                        "exit_date": frame.index[exit_pos],
                        "ret60": 0.05,
                        "hv20": 0.18,
                        "sma_distance": 100.0 / 95.0 - 1.0,
                        "control_feature_pos": control_pos,
                        "control_feature_date": frame.index[control_pos],
                        "control_entry_pos": control_entry,
                        "control_entry_date": frame.index[control_entry],
                        "control_exit_pos": control_exit,
                        "control_exit_date": frame.index[control_exit],
                        "match_score": 0.0,
                        "control_distance_sessions": signal_pos - control_pos,
                    }
                )
        return features, matched

    def test_first_signal_identity_is_lagged_and_future_invariant(self):
        raw = self._raw_frame()
        features = build_features(raw, "SPY")
        signals = freeze_signals(features, "SPY")
        self.assertGreaterEqual(len(signals), 1)
        first = signals[0]
        self.assertEqual(first["feature_max_date"], first["signal_date"])
        self.assertEqual(first["entry_pos"], first["signal_pos"] + 1)
        self.assertEqual(first["exit_pos"], first["entry_pos"] + 5)

        mutated = raw.copy()
        mutated.loc[mutated.index > first["signal_date"], ["open", "high", "low", "close"]] *= 3.0
        replay = freeze_signals(build_features(mutated, "SPY"), "SPY")
        fields = ["symbol", "signal_pos", "signal_date", "feature_max_date", "entry_pos", "entry_date"]
        self.assertEqual(
            {field: first[field] for field in fields},
            {field: replay[0][field] for field in fields},
        )

    def test_controls_are_prior_nontrigger_and_not_reused(self):
        features = self._feature_frame(periods=1500)
        for position in range(300, 1400, 18):
            features.iloc[position, features.columns.get_loc("overnight5")] = -0.02
            features.iloc[position, features.columns.get_loc("intraday5")] = 0.02
        signals = freeze_signals(features, "SPY")
        matched = match_prior_controls(features, signals)
        self.assertGreater(len(matched), 20)
        windows = []
        for row in matched:
            self.assertLess(row["control_exit_pos"], row["signal_pos"])
            self.assertFalse(bool(trigger_mask(features).iloc[row["control_feature_pos"]]))
            window = (row["control_entry_pos"], row["control_exit_pos"])
            self.assertTrue(all(window[1] < prior[0] or window[0] > prior[1] for prior in windows))
            windows.append(window)

    def test_same_date_rows_are_clustered_before_inference(self):
        features, matched = self._matched_panel([0.02] * 6)
        result = evaluate_train(
            features,
            matched,
            n_train_eligible_rows=len(matched),
            min_episodes=6,
            min_years=1,
            bootstrap_samples=500,
        )
        self.assertEqual(result["n_matched_signal_rows"], 18)
        self.assertEqual(result["n_clustered_episodes"], 6)
        self.assertTrue(all(row["n_symbols"] == 3 for row in result["episodes"]))
        self.assertEqual(
            result["dependence_diagnostics"]["episode_n_symbols_distribution"], {"3": 6}
        )

    def test_dependence_diagnostics_keep_near_date_and_breadth_limits(self):
        episodes = [
            {"signal_date": "2020-01-02", "n_symbols": 1},
            {"signal_date": "2020-01-07", "n_symbols": 2},
            {"signal_date": "2020-01-20", "n_symbols": 1},
        ]
        diagnostic = _dependence_diagnostics(episodes)
        self.assertEqual(diagnostic["n_consecutive_episode_gaps"], 2)
        self.assertEqual(diagnostic["consecutive_episode_gaps_le_7_calendar_days"], 1)
        self.assertEqual(diagnostic["episode_n_symbols_distribution"], {"1": 2, "2": 1})
        self.assertTrue(diagnostic["same_date_rows_clustered"])

    def test_planning_option_is_not_mislabeled_as_measured_f0_path(self):
        boundary = planning_risk_boundaries()
        self.assertEqual(boundary["f0_underlying_horizon_sessions"], 5)
        self.assertEqual(
            (boundary["planned_option_dte_min"], boundary["planned_option_dte_max"]),
            (18, 24),
        )
        self.assertEqual(boundary["max_loss_usd"], 200.0)
        self.assertIn("frictionless planning", boundary["max_loss_semantics"])
        self.assertFalse(boundary["option_path_measured"])
        self.assertEqual(boundary["option_pricing_calls"], 0)

    def test_aligned_positive_panel_passes_complete_discovery_gate(self):
        features, matched = self._matched_panel([0.02] * 8)
        result = evaluate_train(
            features,
            matched,
            n_train_eligible_rows=len(matched),
            min_episodes=8,
            min_years=1,
            bootstrap_samples=500,
        )
        self.assertTrue(result["gate_pass"], result["gate_checks"])
        self.assertGreater(result["event_mean_return_after_cost"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0)
        self.assertGreater(result["paired_excess_block_bootstrap_lb90"], 0.0)

    def test_favorable_center_with_unstable_episode_fails_uncertainty(self):
        features, matched = self._matched_panel([0.02, 0.02, 0.02, 0.02, 0.02, -0.05])
        result = evaluate_train(
            features,
            matched,
            n_train_eligible_rows=len(matched),
            min_episodes=6,
            min_years=1,
            bootstrap_samples=2_000,
        )
        self.assertGreater(result["event_mean_return_after_cost"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0)
        self.assertFalse(result["gate_checks"]["paired_excess_five_episode_block_lb90_positive"])
        self.assertFalse(result["gate_pass"])

    def test_event_tail_gate_does_not_use_paired_excess_tail(self):
        features, matched = self._matched_panel([0.02, 0.02, 0.02, 0.02, 0.02, -0.06])
        for row in matched:
            frame = features[row["symbol"]]
            frame.iloc[row["control_entry_pos"], frame.columns.get_loc("close")] = 100.0
            frame.iloc[row["control_exit_pos"], frame.columns.get_loc("close")] = 80.0
        result = evaluate_train(
            features,
            matched,
            n_train_eligible_rows=len(matched),
            min_episodes=6,
            min_years=1,
            bootstrap_samples=2_000,
        )
        self.assertLess(result["event_return_worst_decile_mean_after_10bps"], -0.05)
        self.assertGreater(result["paired_excess_worst_decile_mean"], 0.0)
        self.assertFalse(
            result["gate_checks"]["event_return_worst_decile_at_least_negative_5pct"]
        )
        self.assertFalse(result["gate_pass"])

    def test_holdout_payload_contains_identity_only(self):
        frame = self._feature_frame()
        row = {
            "symbol": "SPY",
            "signal_date": frame.index[400],
            "entry_date": frame.index[401],
            "exit_date": frame.index[406],
            "control_feature_date": frame.index[200],
            "control_entry_date": frame.index[201],
            "control_exit_date": frame.index[206],
        }
        payload = _identity_payload([row], eligible_count=2)
        self.assertEqual(payload["n_eligible_signal_rows"], 2)
        self.assertEqual(payload["n_matched_signal_rows"], 1)
        self.assertFalse(payload["outcome_metrics_read"])
        self.assertFalse(payload["simulation_run"])
        self.assertEqual(payload["option_pricing_calls"], 0)
        self.assertNotIn("return", " ".join(payload.keys()).lower())


if __name__ == "__main__":
    unittest.main()

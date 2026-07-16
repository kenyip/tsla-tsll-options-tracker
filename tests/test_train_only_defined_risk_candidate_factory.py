import unittest

import numpy as np
import pandas as pd

from scripts.fomc_information_resolution_train_lab import _validate_price_frame
from scripts.train_only_defined_risk_candidate_factory import (
    CREDIT_SPEC,
    _dominant_failure_mechanism,
    evaluate_train,
    freeze_signal_geometry,
    match_prior_controls,
    run_mechanism,
)


class TrainOnlyDefinedRiskCandidateFactoryTest(unittest.TestCase):
    @staticmethod
    def _features(periods: int = 1400, trigger_every: int = 16) -> pd.DataFrame:
        index = pd.bdate_range("2015-01-02", periods=periods)
        close = np.linspace(100.0, 180.0, periods)
        features = pd.DataFrame(
            {
                "spy_open": close,
                "spy_close": close,
                "sma100": close * 0.95,
                "ret60": np.full(periods, 0.06),
                "ret5": np.full(periods, -0.002),
                "hv20": np.full(periods, 0.18),
                "hyg_ief_ret10": np.zeros(periods),
                "overnight5": np.zeros(periods),
                "intraday5": np.zeros(periods),
                "sma_distance": np.full(periods, 1.0 / 0.95 - 1.0),
            },
            index=index,
        )
        for position in range(160, periods - 8, trigger_every):
            features.iloc[position, features.columns.get_loc("hyg_ief_ret10")] = -0.02
        return features

    def test_signal_identity_is_lagged_and_unchanged_by_future_price_perturbation(self):
        features = self._features()
        baseline = freeze_signal_geometry(features, CREDIT_SPEC)
        self.assertGreater(len(baseline), 20)
        first = baseline[0]
        self.assertEqual(first["feature_max_date"], first["signal_date"])
        self.assertEqual(first["entry_pos"], first["signal_pos"] + 1)
        self.assertEqual(first["exit_pos"], first["entry_pos"] + 5)

        mutated = features.copy()
        mutated.loc[mutated.index > first["signal_date"], "spy_close"] *= 5.0
        replay = freeze_signal_geometry(mutated, CREDIT_SPEC)
        identity = ["signal_pos", "signal_date", "feature_max_date", "entry_pos", "entry_date"]
        self.assertEqual(
            {field: baseline[0][field] for field in identity},
            {field: replay[0][field] for field in identity},
        )

    def test_controls_are_prior_only_nontrigger_and_never_reused(self):
        features = self._features()
        signals = freeze_signal_geometry(features, CREDIT_SPEC)
        matched = match_prior_controls(features, signals, CREDIT_SPEC)
        self.assertGreater(len(matched), 20)
        windows = []
        for row in matched:
            self.assertLess(row["control_exit_pos"], row["signal_pos"])
            self.assertGreater(row["control_entry_pos"], row["control_feature_pos"])
            self.assertGreater(row["control_exit_pos"], row["control_entry_pos"])
            self.assertGreater(features.iloc[row["control_feature_pos"]]["hyg_ief_ret10"], -0.015)
            window = (row["control_entry_pos"], row["control_exit_pos"])
            self.assertTrue(
                all(window[1] < prior[0] or window[0] > prior[1] for prior in windows)
            )
            windows.append(window)

    def test_aligned_signed_event_path_passes_complete_discovery_gate(self):
        features = self._features(periods=800, trigger_every=18)
        signals = freeze_signal_geometry(features, CREDIT_SPEC)
        matched = match_prior_controls(features, signals, CREDIT_SPEC)[:12]
        self.assertGreaterEqual(len(matched), 8)
        altered = features.copy()
        for row in matched:
            event_entry = float(altered.iloc[row["entry_pos"]]["spy_close"])
            control_entry = float(altered.iloc[row["control_entry_pos"]]["spy_close"])
            altered.iloc[row["exit_pos"], altered.columns.get_loc("spy_close")] = event_entry * 0.98
            altered.iloc[
                row["control_exit_pos"], altered.columns.get_loc("spy_close")
            ] = control_entry
        result = evaluate_train(
            altered,
            matched,
            CREDIT_SPEC,
            n_train_eligible=len(matched),
            min_pairs=8,
            min_years=1,
            bootstrap_samples=500,
        )
        self.assertTrue(result["gate_pass"], result["gate_checks"])
        self.assertGreater(result["signed_event_mean_return_after_cost"], 0.0)
        self.assertGreater(result["signed_paired_excess_mean"], 0.0)
        self.assertGreater(result["paired_excess_block_bootstrap_lb90"], 0.0)

    def test_wrong_signed_event_path_fails_expectancy_and_uncertainty(self):
        features = self._features(periods=800, trigger_every=18)
        signals = freeze_signal_geometry(features, CREDIT_SPEC)
        matched = match_prior_controls(features, signals, CREDIT_SPEC)[:12]
        self.assertGreaterEqual(len(matched), 8)
        altered = features.copy()
        for row in matched:
            event_entry = float(altered.iloc[row["entry_pos"]]["spy_close"])
            control_entry = float(altered.iloc[row["control_entry_pos"]]["spy_close"])
            altered.iloc[row["exit_pos"], altered.columns.get_loc("spy_close")] = event_entry * 1.02
            altered.iloc[
                row["control_exit_pos"], altered.columns.get_loc("spy_close")
            ] = control_entry
        result = evaluate_train(
            altered,
            matched,
            CREDIT_SPEC,
            n_train_eligible=len(matched),
            min_pairs=8,
            min_years=1,
            bootstrap_samples=500,
        )
        self.assertFalse(result["gate_pass"])
        self.assertLess(result["signed_event_mean_return_after_cost"], 0.0)
        self.assertFalse(result["gate_checks"]["signed_event_mean_after_10bps_positive"])
        self.assertFalse(result["gate_checks"]["paired_excess_block_bootstrap_lb90_positive"])

    def test_run_mechanism_keeps_holdout_identity_only(self):
        features = self._features()
        result = run_mechanism(
            features,
            CREDIT_SPEC,
            min_pairs=20,
            min_years=1,
            bootstrap_samples=500,
        )
        self.assertGreater(result["holdout"]["n_eligible_signals"], 0)
        self.assertFalse(result["holdout"]["outcome_metrics_read"])
        self.assertFalse(result["holdout"]["simulation_run"])
        self.assertEqual(result["holdout"]["option_pricing_calls"], 0)
        self.assertNotIn("pairs", result["holdout"])
        self.assertFalse(result["f2_claim"])
        self.assertFalse(result["l1_claim"])
        self.assertEqual(result["max_loss_usd"], 200.0)
        self.assertEqual(result["max_lots"], 1)

    def test_dominant_failure_names_only_actual_failed_gates(self):
        candidate = {
            "failed_gates": [
                "signed_event_mean_after_10bps_positive",
                "signed_paired_excess_mean_positive",
                "paired_excess_block_bootstrap_lb90_positive",
                "signed_positive_frequency_at_least_55pct",
            ],
            "train": {
                "signed_event_mean_return_after_cost": -0.009,
                "signed_paired_excess_mean": -0.007,
            },
        }
        text = _dominant_failure_mechanism(candidate)
        for gate in candidate["failed_gates"]:
            self.assertIn(gate, text)
        for passed_dimension in ("density", "support", "tail", "integrity"):
            self.assertNotIn(passed_dimension, text.lower())
        self.assertIn("wrong signed five-session direction", text)
        self.assertIn("negative specificity", text)

    def test_ohlcv_validator_accepts_only_ulp_geometry_noise(self):
        index = pd.bdate_range("2024-01-02", periods=4)
        frame = pd.DataFrame(
            {
                "open": [100.0, 101.0, 102.0, 103.0],
                "high": [101.0, np.nextafter(101.0, 0.0), 103.0, 104.0],
                "low": [99.0, 100.0, 101.0, 102.0],
                "close": [100.5, 101.0, 102.5, 103.5],
                "volume": [1_000_000.0] * 4,
            },
            index=index,
        )
        validated = _validate_price_frame(frame)
        self.assertEqual(len(validated), 4)
        broken = frame.copy()
        broken.iloc[1, broken.columns.get_loc("high")] = 100.0
        with self.assertRaisesRegex(ValueError, "OHLC geometry"):
            _validate_price_frame(broken)


if __name__ == "__main__":
    unittest.main()

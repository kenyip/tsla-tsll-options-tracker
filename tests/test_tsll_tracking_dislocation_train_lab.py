import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

from scripts.tsll_tracking_dislocation_train_lab import (
    build_matched_blueprints,
    evaluate_train_partition,
    run_lab_from_panel,
)


class TsllTrackingDislocationTrainLabTest(unittest.TestCase):
    @staticmethod
    def _panel(periods: int = 320) -> pd.DataFrame:
        index = pd.bdate_range("2023-01-03", periods=periods)
        tsla = 100.0 * np.exp(np.arange(periods) * 0.001)
        tsll = 50.0 * (tsla / tsla[0]) ** 2
        for position in (130, 190, 250, 290):
            tsll[position] *= 0.94
        return pd.DataFrame({"TSLA": tsla, "TSLL": tsll}, index=index)

    def test_blueprints_use_prior_completed_pair_residual_and_prior_disjoint_controls(self):
        panel = self._panel()

        blueprints = build_matched_blueprints(
            panel,
            trend_lookback_sessions=20,
            max_match_distance_sessions=63,
            forward_sessions=5,
        )

        self.assertGreaterEqual(len(blueprints), 3)
        occupied = []
        for row in blueprints:
            self.assertLess(row["treated_signal_date"], row["treated_entry_date"])
            self.assertLess(row["treated_entry_date"], row["treated_exit_date"])
            self.assertLess(row["control_signal_date"], row["treated_signal_date"])
            self.assertLess(row["control_signal_date"], row["control_entry_date"])
            self.assertLessEqual(row["treated_residual_5d"], -0.04)
            self.assertGreaterEqual(row["control_residual_5d"], -0.01)
            self.assertLessEqual(row["control_residual_5d"], 0.01)
            self.assertLessEqual(row["calendar_distance_sessions"], 63)
            windows = [
                (row["treated_entry_date"], row["treated_exit_date"]),
                (row["control_entry_date"], row["control_exit_date"]),
            ]
            for start, end in windows:
                self.assertTrue(all(end < prior_start or start > prior_end for prior_start, prior_end in occupied))
                occupied.append((start, end))

        first = blueprints[0]
        shocked = panel.copy()
        shocked.loc[first["treated_entry_date"], "TSLL"] *= 1.50
        rebuilt = build_matched_blueprints(
            shocked,
            trend_lookback_sessions=20,
            max_match_distance_sessions=63,
            forward_sessions=5,
        )
        self.assertEqual(first["treated_signal_date"], rebuilt[0]["treated_signal_date"])
        self.assertEqual(first["control_signal_date"], rebuilt[0]["control_signal_date"])

    def test_train_gate_requires_positive_after_cost_rebound_and_uncertainty_bounded_excess(self):
        index = pd.bdate_range("2023-01-03", periods=320)
        panel = pd.DataFrame({"TSLA": 100.0, "TSLL": 100.0}, index=index)
        blueprints = []
        for pair_index in range(12):
            base = 5 + pair_index * 24
            control_entry, control_exit = index[base + 1], index[base + 6]
            treated_entry, treated_exit = index[base + 13], index[base + 18]
            panel.loc[control_exit, "TSLL"] = 101.0
            panel.loc[treated_exit, "TSLL"] = 105.0
            blueprints.append(
                {
                    "control_signal_date": index[base],
                    "control_entry_date": control_entry,
                    "control_exit_date": control_exit,
                    "control_residual_5d": 0.0,
                    "control_tsla_return_5d": 0.01,
                    "control_trend_distance": 0.05,
                    "treated_signal_date": index[base + 12],
                    "treated_entry_date": treated_entry,
                    "treated_exit_date": treated_exit,
                    "treated_residual_5d": -0.05,
                    "treated_tsla_return_5d": 0.01,
                    "treated_trend_distance": 0.05,
                    "calendar_distance_sessions": 12,
                    "tsla_return_match_distance": 0.0,
                    "trend_match_distance": 0.0,
                }
            )

        result = evaluate_train_partition(
            panel,
            blueprints,
            min_pairs=10,
            bootstrap_samples=500,
        )

        self.assertTrue(result["gate_pass"])
        self.assertGreater(result["treated_mean_return_after_cost"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0)
        self.assertGreater(result["paired_excess_bootstrap_lb90"], 0.0)
        self.assertEqual(result["integrity_violations"], [])

    def test_positive_point_excess_with_nonpositive_bootstrap_bound_closes(self):
        index = pd.bdate_range("2023-01-03", periods=320)
        panel = pd.DataFrame({"TSLA": 100.0, "TSLL": 100.0}, index=index)
        blueprints = []
        for pair_index, excess in enumerate([0.10, -0.09] * 6):
            base = 5 + pair_index * 24
            control_entry, control_exit = index[base + 1], index[base + 6]
            treated_entry, treated_exit = index[base + 13], index[base + 18]
            panel.loc[control_exit, "TSLL"] = 101.0
            panel.loc[treated_exit, "TSLL"] = 100.0 * (1.01 + excess)
            blueprints.append(
                {
                    "control_signal_date": index[base],
                    "control_entry_date": control_entry,
                    "control_exit_date": control_exit,
                    "control_residual_5d": 0.0,
                    "control_tsla_return_5d": 0.01,
                    "control_trend_distance": 0.05,
                    "treated_signal_date": index[base + 12],
                    "treated_entry_date": treated_entry,
                    "treated_exit_date": treated_exit,
                    "treated_residual_5d": -0.05,
                    "treated_tsla_return_5d": 0.01,
                    "treated_trend_distance": 0.05,
                    "calendar_distance_sessions": 12,
                    "tsla_return_match_distance": 0.0,
                    "trend_match_distance": 0.0,
                }
            )

        result = evaluate_train_partition(
            panel,
            blueprints,
            min_pairs=10,
            bootstrap_samples=2_000,
        )

        self.assertGreater(result["treated_mean_return_after_cost"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0)
        self.assertLessEqual(result["paired_excess_bootstrap_lb90"], 0.0)
        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["gate_checks"]["paired_excess_bootstrap_lb90_positive"])

    def test_payload_reserves_unread_holdout_and_never_prices_options(self):
        panel = self._panel()

        payload = run_lab_from_panel(
            panel,
            provenance={"fixture": True},
            train_fraction=0.60,
            trend_lookback_sessions=20,
            min_train_pairs=2,
            bootstrap_samples=500,
        )

        self.assertIn(payload["strategy_outcome"], {"STRATEGY_ADVANCED", "FAMILY_CLOSED"})
        self.assertFalse(payload["f2_or_l1_claim"])
        self.assertFalse(payload["untouched_holdout"]["outcome_metrics_read"])
        self.assertNotIn("pairs", payload["untouched_holdout"])
        self.assertEqual(payload["option_stage"]["pricing_calls"], 0)
        self.assertEqual(
            payload["structure"], "conditional_bull_call_debit_spread_not_yet_priced"
        )
        self.assertEqual(payload["capital_fit_usd"], 100.0)
        self.assertEqual(payload["max_loss_usd"], 100.0)
        self.assertEqual(payload["max_lots"], 1)
        encoded = __import__("json").dumps(payload, allow_nan=False)
        self.assertNotIn("holdout_return", encoded)

    def test_direct_script_cli_imports_from_repo_root(self):
        completed = subprocess.run(
            [sys.executable, "scripts/tsll_tracking_dislocation_train_lab.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Train-only TSLL-versus-TSLA", completed.stdout)

    def test_treated_and_neutral_populations_without_frozen_match_support_close(self):
        payload = run_lab_from_panel(
            self._panel(),
            provenance={"fixture": True},
            trend_lookback_sessions=20,
            max_match_distance_sessions=1,
            min_train_pairs=2,
            bootstrap_samples=500,
        )

        diagnostics = payload["selection_diagnostics"]
        self.assertGreater(diagnostics["treated_signal_candidates"], 0)
        self.assertGreater(diagnostics["neutral_control_candidates"], 0)
        self.assertEqual(diagnostics["matched_blueprints"], 0)
        self.assertEqual(payload["strategy_outcome"], "FAMILY_CLOSED")
        self.assertEqual(payload["train"]["n_pairs"], 0)
        self.assertIsNone(payload["train"]["treated_mean_return_after_cost"])
        self.assertIsNone(payload["train"]["paired_excess_mean"])
        self.assertFalse(payload["untouched_holdout"]["outcome_metrics_read"])
        self.assertEqual(payload["option_stage"]["pricing_calls"], 0)
        self.assertIn(
            "none admitted an earlier neutral-residual control",
            payload["dominant_failure_mechanism"],
        )

    def test_vacuous_population_closes_instead_of_crashing(self):
        index = pd.bdate_range("2023-01-03", periods=320)
        tsla = 100.0 * np.exp(np.arange(len(index)) * 0.001)
        panel = pd.DataFrame(
            {"TSLA": tsla, "TSLL": 50.0 * (tsla / tsla[0]) ** 2}, index=index
        )

        payload = run_lab_from_panel(
            panel,
            provenance={"fixture": True},
            trend_lookback_sessions=20,
            min_train_pairs=2,
            bootstrap_samples=500,
        )

        self.assertEqual(payload["strategy_outcome"], "FAMILY_CLOSED")
        self.assertEqual(payload["train"]["n_pairs"], 0)
        self.assertFalse(payload["train"]["gate_checks"]["minimum_train_pairs"])
        self.assertFalse(payload["untouched_holdout"]["outcome_metrics_read"])
        self.assertEqual(payload["selection_diagnostics"]["treated_signal_candidates"], 0)
        self.assertEqual(payload["selection_diagnostics"]["matched_blueprints"], 0)
        self.assertIn("no eligible treated signals", payload["dominant_failure_mechanism"])


if __name__ == "__main__":
    unittest.main()

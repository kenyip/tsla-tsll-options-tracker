import json
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

from scripts.cross_section_residual_reversal_train_lab import (
    build_residual_reversal_blueprints,
    evaluate_train_partition,
    run_lab_from_panel,
)


class CrossSectionResidualReversalTrainLabTest(unittest.TestCase):
    @staticmethod
    def _fixture(periods: int = 3000):
        index = pd.bdate_range("2012-01-03", periods=periods)
        symbols = ["A", "B", "C", "D", "E", "F", "G", "H"]
        panel = pd.DataFrame(
            {
                symbol: 100.0 * np.exp(np.arange(periods) * (0.00012 + rank * 0.000002))
                for rank, symbol in enumerate(symbols)
            },
            index=index,
        )
        target_positions = list(range(25, periods - 10, 20))
        for position in target_positions:
            panel.iloc[position, :3] *= np.array([0.88, 0.89, 0.90])
        all_blueprints = build_residual_reversal_blueprints(
            panel,
            feature_sessions=5,
            forward_sessions=5,
            rebalance_sessions=5,
            group_size=3,
            treated_mean_residual_max=-0.04,
        )
        target_dates = {index[position] for position in target_positions}
        blueprints = [row for row in all_blueprints if row["signal_date"] in target_dates]
        return panel, blueprints

    @staticmethod
    def _set_outcomes(panel, blueprints, *, treated_return: float, control_return: float):
        prepared = panel.copy()
        for row in blueprints:
            entry = row["entry_date"]
            exit_date = row["exit_date"]
            treated = row["treated_symbols"]
            controls = row["control_symbols"]
            prepared.loc[exit_date, treated] = prepared.loc[entry, treated].to_numpy() * (
                1.0 + treated_return
            )
            prepared.loc[exit_date, controls] = prepared.loc[entry, controls].to_numpy() * (
                1.0 + control_return
            )
        return prepared

    def test_blueprints_use_completed_features_and_ignore_entry_bar(self):
        panel, blueprints = self._fixture(periods=500)
        self.assertGreaterEqual(len(blueprints), 20)
        first = blueprints[0]
        self.assertLess(first["feature_start_date"], first["signal_date"])
        self.assertEqual(first["feature_max_date"], first["signal_date"])
        self.assertLess(first["signal_date"], first["entry_date"])
        self.assertLess(first["entry_date"], first["exit_date"])
        self.assertEqual(first["treated_symbols"], ["A", "B", "C"])
        self.assertTrue(set(first["treated_symbols"]).isdisjoint(first["control_symbols"]))
        self.assertLessEqual(first["treated_mean_residual"], -0.04)

        shocked = panel.copy()
        shocked.loc[first["entry_date"], "H"] *= 4.0
        rebuilt = build_residual_reversal_blueprints(
            shocked,
            feature_sessions=5,
            forward_sessions=5,
            rebalance_sessions=5,
            group_size=3,
            treated_mean_residual_max=-0.04,
        )
        rebuilt_first = next(row for row in rebuilt if row["signal_date"] == first["signal_date"])
        self.assertEqual(rebuilt_first["treated_symbols"], first["treated_symbols"])
        self.assertEqual(rebuilt_first["control_symbols"], first["control_symbols"])

    def test_train_gate_passes_only_with_absolute_and_control_relative_recovery(self):
        panel, blueprints = self._fixture()
        prepared = self._set_outcomes(
            panel,
            blueprints,
            treated_return=0.04,
            control_return=0.005,
        )
        result = evaluate_train_partition(
            prepared,
            blueprints[:90],
            min_episodes=40,
            min_signal_years=6,
            bootstrap_samples=500,
        )
        self.assertTrue(result["gate_pass"])
        self.assertGreater(result["treated_mean_return_after_cost"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0025)
        self.assertGreater(result["paired_excess_bootstrap_lb90"], 0.0)
        self.assertEqual(result["integrity_violations"], [])
        json.dumps(result, allow_nan=False)

    def test_positive_treated_return_without_control_edge_closes(self):
        panel, blueprints = self._fixture()
        prepared = self._set_outcomes(
            panel,
            blueprints,
            treated_return=0.01,
            control_return=0.03,
        )
        payload = run_lab_from_panel(
            prepared,
            symbols=list(prepared.columns),
            provenance={symbol: {"fixture": True} for symbol in prepared.columns},
            frozen_blueprints=blueprints[:120],
            train_fraction=0.60,
            min_episodes=40,
            min_signal_years=6,
            bootstrap_samples=500,
        )
        self.assertGreater(payload["train"]["treated_mean_return_after_cost"], 0.0)
        self.assertLess(payload["train"]["paired_excess_mean"], 0.0)
        self.assertEqual(payload["strategy_outcome"], "FAMILY_CLOSED")
        self.assertEqual(payload["closed_family"], "CROSS_SECTION_FIVE_SESSION_RESIDUAL_REVERSAL")
        self.assertIn("control failure", payload["dominant_failure_mechanism"])
        self.assertFalse(payload["f2_or_l1_claim"])
        self.assertFalse(payload["funnel_claim_f2"])
        self.assertFalse(payload["l1_claim"])
        self.assertFalse(payload["option_stage"]["pricing_run"])
        self.assertFalse(payload["holdout"]["outcome_metrics_read"])
        self.assertEqual(payload["max_loss_usd"], 200.0)
        self.assertIsNone(payload["observed_or_simulated_option_path_max_loss_usd"])
        self.assertIn("frictionless", payload["capital_basis"])
        self.assertIn("closing friction", payload["capital_basis"])
        self.assertEqual(payload["max_lots"], 1)
        encoded = json.dumps(payload, allow_nan=False)
        self.assertNotIn("holdout_return", encoded)

    def test_closed_family_quarantine_blocks_inspected_train_salvage(self):
        panel, blueprints = self._fixture()
        prepared = self._set_outcomes(
            panel,
            blueprints,
            treated_return=0.01,
            control_return=0.03,
        )
        payload = run_lab_from_panel(
            prepared,
            symbols=list(prepared.columns),
            provenance={symbol: {"fixture": True} for symbol in prepared.columns},
            frozen_blueprints=blueprints[:120],
            train_fraction=0.60,
            min_episodes=40,
            min_signal_years=6,
            bootstrap_samples=500,
        )

        quarantine = payload["quarantine"]
        self.assertTrue(quarantine["enabled"])
        self.assertIn("CROSS_SECTION_FIVE_SESSION_RESIDUAL_REVERSAL", quarantine["scope"])
        self.assertIn("CROSS_SECTION_RESIDUAL_REVERSAL_BULL_CALL_21D_V1", quarantine["scope"])
        self.assertTrue(any("-4%" in value for value in quarantine["scope"]))
        self.assertTrue(any("five-session" in value for value in quarantine["scope"]))
        self.assertTrue(any("AMD" in value for value in quarantine["banned_train_salvage"]))
        self.assertTrue(any("sealed holdout" in value for value in quarantine["banned_train_salvage"]))
        self.assertIn("prior-known event evidence", quarantine["reopen_condition"])
        self.assertIn("frozen before outcomes", quarantine["reopen_condition"])

    def test_boundary_tampering_fails_integrity_gate(self):
        panel, blueprints = self._fixture(periods=1200)
        prepared = self._set_outcomes(
            panel,
            blueprints,
            treated_return=0.04,
            control_return=0.005,
        )
        tampered = [dict(row) for row in blueprints[:50]]
        tampered[1] = dict(tampered[1])
        tampered[1]["entry_date"] = tampered[0]["entry_date"]
        tampered[1]["exit_date"] = tampered[0]["exit_date"]

        result = evaluate_train_partition(
            prepared,
            tampered,
            min_episodes=40,
            min_signal_years=2,
            bootstrap_samples=500,
        )
        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["gate_checks"]["zero_integrity_violations"])
        self.assertTrue(any(value.startswith("chronology:") for value in result["integrity_violations"]))
        self.assertTrue(any(value.startswith("overlap:") for value in result["integrity_violations"]))

    def test_cli_help_imports_from_repo_root(self):
        completed = subprocess.run(
            [sys.executable, "scripts/cross_section_residual_reversal_train_lab.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("residual-reversal discovery lab", completed.stdout)


if __name__ == "__main__":
    unittest.main()

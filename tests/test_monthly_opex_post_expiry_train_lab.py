import json
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

from scripts.monthly_opex_post_expiry_train_lab import (
    build_monthly_opex_blueprints,
    evaluate_train_partition,
    run_lab_from_panel,
)


class MonthlyOpexPostExpiryTrainLabTest(unittest.TestCase):
    @staticmethod
    def _panel(start: str = "2021-01-04", periods: int = 1_000) -> pd.DataFrame:
        index = pd.bdate_range(start, periods=periods)
        close = 100.0 * np.exp(np.arange(periods) * 0.0002)
        return pd.DataFrame(
            {symbol: close * scale for symbol, scale in zip(("SPY", "QQQ", "IWM", "DIA"), (1.0, 1.1, 0.8, 0.9), strict=True)},
            index=index,
        )

    def test_blueprints_use_adjusted_opex_and_outcome_free_nonoverlapping_control(self):
        panel = self._panel(start="2024-01-02", periods=90)
        panel = panel.drop(pd.Timestamp("2024-03-15"))

        blueprints = build_monthly_opex_blueprints(panel, forward_sessions=5)
        march = next(row for row in blueprints if row["month"] == "2024-03")

        self.assertEqual(march["calendar_opex_date"], pd.Timestamp("2024-03-15"))
        self.assertEqual(march["opex_session_date"], pd.Timestamp("2024-03-14"))
        self.assertEqual(march["event_entry_date"], pd.Timestamp("2024-03-18"))
        self.assertEqual(march["calendar_control_friday"], pd.Timestamp("2024-03-01"))
        self.assertEqual(march["control_session_date"], pd.Timestamp("2024-03-01"))
        self.assertLess(march["control_session_date"], march["control_entry_date"])
        self.assertLess(march["control_entry_date"], march["control_exit_date"])
        self.assertLessEqual(march["control_exit_date"], march["event_entry_date"])
        self.assertLess(march["opex_session_date"], march["event_entry_date"])
        self.assertLess(march["event_entry_date"], march["event_exit_date"])

        shocked = panel.copy()
        shocked.loc[march["event_exit_date"], "SPY"] *= 1.50
        rebuilt = build_monthly_opex_blueprints(shocked, forward_sessions=5)
        rebuilt_march = next(row for row in rebuilt if row["month"] == "2024-03")
        for key in (
            "opex_session_date",
            "event_entry_date",
            "event_exit_date",
            "control_session_date",
            "control_entry_date",
            "control_exit_date",
        ):
            self.assertEqual(march[key], rebuilt_march[key])

    def test_train_gate_requires_positive_after_cost_drift_and_uncertainty_bounded_paired_edge(self):
        index = pd.bdate_range("2018-01-02", periods=1_200)
        panel = pd.DataFrame(100.0, index=index, columns=["SPY", "QQQ", "IWM", "DIA"])
        blueprints = []
        for episode, start in enumerate(range(5, 905, 15)):
            control_entry = index[start]
            control_exit = index[start + 5]
            event_entry = index[start + 7]
            event_exit = index[start + 12]
            panel.loc[control_exit] = panel.loc[control_entry] * 1.002
            panel.loc[event_exit] = panel.loc[event_entry] * 1.012
            blueprints.append(
                {
                    "month": f"fixture-{episode:03d}",
                    "calendar_control_friday": index[start - 1],
                    "control_session_date": index[start - 1],
                    "control_entry_date": control_entry,
                    "control_exit_date": control_exit,
                    "calendar_opex_date": index[start + 6],
                    "opex_session_date": index[start + 6],
                    "event_entry_date": event_entry,
                    "event_exit_date": event_exit,
                }
            )

        result = evaluate_train_partition(
            panel,
            blueprints,
            min_episodes=48,
            round_trip_cost_bps=10.0,
            bootstrap_samples=500,
        )

        self.assertTrue(result["gate_pass"])
        self.assertGreater(result["event_basket_mean_return_after_cost"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0)
        self.assertGreater(result["paired_excess_bootstrap_lb90"], 0.0)
        self.assertEqual(result["integrity_violations"], [])
        json.dumps(result, allow_nan=False)

    def test_positive_point_edge_with_nonpositive_bootstrap_bound_closes_gate(self):
        index = pd.bdate_range("2018-01-02", periods=600)
        panel = pd.DataFrame(100.0, index=index, columns=["SPY", "QQQ", "IWM", "DIA"])
        blueprints = []
        excesses = [0.10, -0.09] * 12
        for episode, (start, excess) in enumerate(zip(range(5, 365, 15), excesses, strict=True)):
            control_entry = index[start]
            control_exit = index[start + 5]
            event_entry = index[start + 7]
            event_exit = index[start + 12]
            panel.loc[control_exit] = panel.loc[control_entry] * 1.01
            panel.loc[event_exit] = panel.loc[event_entry] * (1.01 + excess)
            blueprints.append(
                {
                    "month": f"fixture-{episode:03d}",
                    "calendar_control_friday": index[start - 1],
                    "control_session_date": index[start - 1],
                    "control_entry_date": control_entry,
                    "control_exit_date": control_exit,
                    "calendar_opex_date": index[start + 6],
                    "opex_session_date": index[start + 6],
                    "event_entry_date": event_entry,
                    "event_exit_date": event_exit,
                }
            )

        result = evaluate_train_partition(
            panel,
            blueprints,
            min_episodes=20,
            round_trip_cost_bps=10.0,
            bootstrap_samples=2_000,
        )

        self.assertGreater(result["event_basket_mean_return_after_cost"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0)
        self.assertLessEqual(result["paired_excess_bootstrap_lb90"], 0.0)
        self.assertFalse(result["gate_checks"]["paired_excess_bootstrap_lb90_positive"])
        self.assertFalse(result["gate_pass"])

    def test_positive_paired_edge_cannot_rescue_negative_absolute_after_cost_drift(self):
        index = pd.bdate_range("2018-01-02", periods=1_000)
        panel = pd.DataFrame(100.0, index=index, columns=["SPY", "QQQ", "IWM", "DIA"])
        blueprints = []
        for episode, start in enumerate(range(5, 725, 15)):
            control_entry = index[start]
            control_exit = index[start + 5]
            event_entry = index[start + 7]
            event_exit = index[start + 12]
            panel.loc[control_exit] = panel.loc[control_entry] * 1.0001
            panel.loc[event_exit] = panel.loc[event_entry] * 1.0005
            blueprints.append(
                {
                    "month": f"fixture-{episode:03d}",
                    "calendar_control_friday": index[start - 1],
                    "control_session_date": index[start - 1],
                    "control_entry_date": control_entry,
                    "control_exit_date": control_exit,
                    "calendar_opex_date": index[start + 6],
                    "opex_session_date": index[start + 6],
                    "event_entry_date": event_entry,
                    "event_exit_date": event_exit,
                }
            )

        result = evaluate_train_partition(
            panel,
            blueprints,
            min_episodes=48,
            round_trip_cost_bps=10.0,
            bootstrap_samples=500,
        )

        self.assertLess(result["event_basket_mean_return_after_cost"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0)
        self.assertGreater(result["paired_excess_bootstrap_lb90"], 0.0)
        self.assertFalse(result["gate_checks"]["positive_event_basket_mean_return_after_cost"])
        self.assertFalse(result["gate_pass"])

    def test_payload_keeps_holdout_unread_and_option_stage_unpriced(self):
        panel = self._panel(periods=1_600)

        payload = run_lab_from_panel(
            panel,
            symbols=list(panel.columns),
            provenance={symbol: {"fixture": True} for symbol in panel.columns},
            train_fraction=0.60,
            forward_sessions=5,
            min_train_episodes=24,
            round_trip_cost_bps=10.0,
            bootstrap_samples=500,
        )

        self.assertIn(payload["strategy_outcome"], {"STRATEGY_ADVANCED", "FAMILY_CLOSED"})
        self.assertFalse(payload["f2_or_l1_claim"])
        self.assertFalse(payload["untouched_holdout"]["outcome_metrics_read"])
        self.assertFalse(payload["untouched_holdout"]["simulation_run"])
        self.assertNotIn("episodes", payload["untouched_holdout"])
        self.assertEqual(payload["option_stage"]["pricing_calls"], 0)
        self.assertEqual(payload["structure"], "conditional_bull_call_debit_spread_not_yet_priced")
        self.assertEqual(payload["capital_fit_usd"], 200.0)
        self.assertEqual(payload["max_loss_usd"], 200.0)
        self.assertEqual(payload["max_lots"], 1)
        self.assertTrue(payload["population_validity"]["population_pure"])
        self.assertFalse(payload["population_validity"]["bias_free"])
        self.assertTrue(payload["population_validity"]["survivorship_bias"])
        self.assertFalse(payload["population_validity"]["generalization_allowed"])
        self.assertIn("evaluated completely", payload["population_validity"]["population_pure_semantics"])
        encoded = json.dumps(payload, allow_nan=False)
        self.assertNotIn("holdout_return", encoded)

    def test_invalid_chronology_fails_closed(self):
        panel = self._panel(periods=100)
        blueprint = {
            "month": "fixture",
            "calendar_control_friday": panel.index[4],
            "control_session_date": panel.index[4],
            "control_entry_date": panel.index[5],
            "control_exit_date": panel.index[12],
            "calendar_opex_date": panel.index[10],
            "opex_session_date": panel.index[10],
            "event_entry_date": panel.index[11],
            "event_exit_date": panel.index[16],
        }

        result = evaluate_train_partition(
            panel,
            [blueprint],
            min_episodes=1,
            bootstrap_samples=200,
        )

        self.assertFalse(result["gate_checks"]["zero_integrity_violations"])
        self.assertIn("control_overlaps_event:0", result["integrity_violations"])
        self.assertFalse(result["gate_pass"])

    def test_direct_script_cli_imports_from_repo_root(self):
        completed = subprocess.run(
            [sys.executable, "scripts/monthly_opex_post_expiry_train_lab.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("monthly-OPEX", completed.stdout)


if __name__ == "__main__":
    unittest.main()

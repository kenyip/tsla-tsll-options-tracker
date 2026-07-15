import json
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

from scripts.cross_section_momentum_train_lab import (
    build_monthly_momentum_blueprints,
    evaluate_train_partition,
    run_lab_from_panel,
)


class CrossSectionMomentumTrainLabTest(unittest.TestCase):
    @staticmethod
    def _momentum_panel(periods: int = 720) -> pd.DataFrame:
        index = pd.bdate_range("2021-01-04", periods=periods)
        cycle = np.resize(np.array([0.0002, -0.0001, 0.0003, 0.0]), periods)
        drifts = {
            "A": 0.0014,
            "B": 0.0011,
            "C": 0.0007,
            "D": -0.0002,
            "E": -0.0006,
            "F": -0.0009,
        }
        return pd.DataFrame(
            {
                symbol: 100.0 * np.exp(np.cumsum(drift + cycle))
                for symbol, drift in drifts.items()
            },
            index=index,
        )

    def test_blueprints_rank_prior_12_minus_1_momentum_without_entry_bar_leakage(self):
        panel = self._momentum_panel()

        blueprints = build_monthly_momentum_blueprints(
            panel,
            lookback_sessions=126,
            skip_sessions=21,
            forward_sessions=10,
            quantile_count=2,
        )

        self.assertGreaterEqual(len(blueprints), 8)
        first = blueprints[0]
        self.assertLess(first["feature_start_date"], first["feature_end_date"])
        self.assertEqual(first["feature_end_date"], first["rank_date"] - pd.offsets.BDay(21))
        self.assertLess(first["rank_date"], first["entry_date"])
        self.assertLess(first["entry_date"], first["exit_date"])
        self.assertEqual(first["top_momentum_symbols"], ["A", "B"])
        self.assertEqual(first["bottom_momentum_symbols"], ["E", "F"])
        self.assertTrue(
            set(first["top_momentum_symbols"]).isdisjoint(first["bottom_momentum_symbols"])
        )

        shocked = panel.copy()
        shocked.loc[first["entry_date"], "F"] *= 3.0
        rebuilt = build_monthly_momentum_blueprints(
            shocked,
            lookback_sessions=126,
            skip_sessions=21,
            forward_sessions=10,
            quantile_count=2,
        )
        self.assertEqual(first["top_momentum_symbols"], rebuilt[0]["top_momentum_symbols"])
        self.assertEqual(first["bottom_momentum_symbols"], rebuilt[0]["bottom_momentum_symbols"])

    def test_train_gate_advances_only_for_positive_absolute_and_paired_momentum_edge(self):
        panel = self._momentum_panel()
        blueprints = build_monthly_momentum_blueprints(
            panel,
            lookback_sessions=126,
            skip_sessions=21,
            forward_sessions=10,
            quantile_count=2,
        )
        train = blueprints[:12]

        result = evaluate_train_partition(
            panel,
            train,
            min_episodes=10,
            bootstrap_samples=500,
        )

        self.assertTrue(result["gate_pass"])
        self.assertGreater(result["top_momentum_mean_return"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0)
        self.assertGreater(result["paired_excess_bootstrap_lb90"], 0.0)
        self.assertEqual(result["integrity_violations"], [])
        json.dumps(result, allow_nan=False)

    def test_payload_reserves_unread_holdout_and_never_prices_options_at_f1(self):
        panel = self._momentum_panel()

        payload = run_lab_from_panel(
            panel,
            symbols=list(panel.columns),
            provenance={symbol: {"fixture": True} for symbol in panel.columns},
            train_fraction=0.60,
            lookback_sessions=126,
            skip_sessions=21,
            forward_sessions=10,
            quantile_count=2,
            min_train_episodes=10,
            bootstrap_samples=500,
        )

        self.assertEqual(payload["strategy_outcome"], "STRATEGY_ADVANCED")
        self.assertEqual(payload["funnel_stage_after"], "F1_TRAIN")
        self.assertFalse(payload["f2_or_l1_claim"])
        self.assertFalse(payload["untouched_holdout"]["outcome_metrics_read"])
        self.assertNotIn("episodes", payload["untouched_holdout"])
        self.assertEqual(payload["option_stage"]["pricing_calls"], 0)
        self.assertEqual(payload["structure"], "conditional_put_credit_spread_not_yet_priced")
        self.assertEqual(payload["capital_fit_usd"], 100.0)
        self.assertEqual(payload["max_loss_usd"], 100.0)
        self.assertEqual(payload["max_lots"], 1)
        encoded = json.dumps(payload, allow_nan=False)
        self.assertNotIn("holdout_return", encoded)

    def test_positive_top_drift_with_nonpositive_control_excess_closes_family(self):
        panel = self._momentum_panel().copy()
        # Reverse the forward ordering after features have formed: this fixture exercises
        # the reject path without weakening chronology or density.
        blueprints = build_monthly_momentum_blueprints(
            panel,
            lookback_sessions=126,
            skip_sessions=21,
            forward_sessions=10,
            quantile_count=2,
        )
        for blueprint in blueprints[:12]:
            entry = blueprint["entry_date"]
            exit_date = blueprint["exit_date"]
            panel.loc[exit_date, blueprint["top_momentum_symbols"]] = (
                panel.loc[entry, blueprint["top_momentum_symbols"]].to_numpy() * 1.01
            )
            panel.loc[exit_date, blueprint["bottom_momentum_symbols"]] = (
                panel.loc[entry, blueprint["bottom_momentum_symbols"]].to_numpy() * 1.03
            )

        result = evaluate_train_partition(
            panel,
            blueprints[:12],
            min_episodes=10,
            bootstrap_samples=500,
        )

        self.assertGreater(result["top_momentum_mean_return"], 0.0)
        self.assertLess(result["paired_excess_mean"], 0.0)
        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["gate_checks"]["positive_paired_excess_mean"])

    def test_positive_point_edge_with_nonpositive_bootstrap_bound_closes_family(self):
        panel = self._momentum_panel().copy()
        blueprints = build_monthly_momentum_blueprints(
            panel,
            lookback_sessions=126,
            skip_sessions=21,
            forward_sessions=10,
            quantile_count=2,
        )
        train = blueprints[:12]
        paired_excess = [0.10, -0.09] * 6
        for blueprint, excess in zip(train, paired_excess, strict=True):
            entry = blueprint["entry_date"]
            exit_date = blueprint["exit_date"]
            panel.loc[exit_date, blueprint["bottom_momentum_symbols"]] = (
                panel.loc[entry, blueprint["bottom_momentum_symbols"]].to_numpy() * 1.01
            )
            panel.loc[exit_date, blueprint["top_momentum_symbols"]] = (
                panel.loc[entry, blueprint["top_momentum_symbols"]].to_numpy()
                * (1.01 + excess)
            )

        result = evaluate_train_partition(
            panel,
            train,
            min_episodes=10,
            bootstrap_samples=2_000,
        )

        self.assertGreater(result["top_momentum_mean_return"], 0.0)
        self.assertGreater(result["paired_excess_mean"], 0.0)
        self.assertLessEqual(result["paired_excess_bootstrap_lb90"], 0.0)
        self.assertTrue(result["gate_checks"]["positive_paired_excess_mean"])
        self.assertFalse(result["gate_checks"]["paired_excess_bootstrap_lb90_positive"])
        self.assertFalse(result["gate_pass"])

    def test_direct_script_cli_imports_from_repo_root(self):
        completed = subprocess.run(
            [sys.executable, "scripts/cross_section_momentum_train_lab.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Train-only monthly cross-sectional", completed.stdout)


if __name__ == "__main__":
    unittest.main()

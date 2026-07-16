import json
import unittest

import numpy as np
import pandas as pd

from scripts.downside_shock_stand_aside_train_lab import (
    build_episode_blueprints,
    evaluate_train_partition,
    run_lab_from_panel,
)


class DownsideShockStandAsideTrainLabTest(unittest.TestCase):
    @staticmethod
    def _selection_panel(periods: int = 520) -> pd.DataFrame:
        index = pd.bdate_range("2018-01-02", periods=periods)
        spy = 100.0 * np.exp(np.arange(periods) * 0.0004)
        panel = {"SPY": spy}
        for symbol_index, symbol in enumerate(("AAPL", "AMD")):
            values = 100.0 * np.exp(np.arange(periods) * (0.0005 + symbol_index * 0.00005))
            for position in (170 + symbol_index * 3, 300 + symbol_index * 3, 430 + symbol_index * 3):
                values[position] = values[position - 1] * 0.95
                values[position + 1 :] *= values[position] / values[position + 1]
            panel[symbol] = values
        return pd.DataFrame(panel, index=index)

    def test_blueprints_are_next_session_nonoverlapping_and_outcome_independent(self):
        panel = self._selection_panel()
        blueprints = build_episode_blueprints(
            panel,
            symbols=["AAPL", "AMD"],
            trend_lookback_sessions=60,
            momentum_lookback_sessions=20,
            forward_sessions=10,
            shock_threshold=-0.03,
        )
        self.assertGreaterEqual(len(blueprints), 10)
        by_symbol: dict[str, list[dict]] = {}
        for row in blueprints:
            self.assertLess(row["signal_date"], row["entry_date"])
            self.assertLess(row["entry_date"], row["exit_date"])
            by_symbol.setdefault(row["symbol"], []).append(row)
        for rows in by_symbol.values():
            for previous, following in zip(rows, rows[1:]):
                self.assertLess(previous["exit_date"], following["entry_date"])

        first = blueprints[0]
        shocked = panel.copy()
        shocked.loc[first["exit_date"], first["symbol"]] *= 1.50
        rebuilt = build_episode_blueprints(
            shocked,
            symbols=["AAPL", "AMD"],
            trend_lookback_sessions=60,
            momentum_lookback_sessions=20,
            forward_sessions=10,
            shock_threshold=-0.03,
        )
        for key in ("symbol", "signal_date", "entry_date", "exit_date", "recent_shock", "stale_shock"):
            self.assertEqual(first[key], rebuilt[0][key])

    @staticmethod
    def _manual_partition(*, current_edge: bool = True):
        index = pd.bdate_range("2020-01-02", periods=480)
        symbols = ("AAPL", "AMD")
        panel = pd.DataFrame({"SPY": 100.0, **{symbol: 100.0 for symbol in symbols}}, index=index)
        blueprints = []
        for episode_index in range(32):
            base = 2 + episode_index * 14
            symbol = symbols[episode_index % len(symbols)]
            signal, entry, exit_ = index[base], index[base + 1], index[base + 11]
            recent_shock = episode_index % 4 in (1, 2)
            stale_shock = episode_index % 4 in (2, 3)
            if recent_shock:
                minimum = 0.90
                terminal = 0.97
            else:
                minimum = 0.98 if current_edge else 0.94
                terminal = 1.02
            panel.loc[entry:exit_, symbol] = 100.0
            panel.loc[index[base + 5], symbol] = 100.0 * minimum
            panel.loc[exit_, symbol] = 100.0 * terminal
            blueprints.append(
                {
                    "symbol": symbol,
                    "signal_date": signal,
                    "entry_date": entry,
                    "exit_date": exit_,
                    "spy_trend_distance": 0.10,
                    "symbol_trend_distance": 0.10,
                    "momentum_return": 0.08,
                    "recent_min_return": -0.04 if recent_shock else -0.01,
                    "stale_min_return": -0.04 if stale_shock else -0.01,
                    "recent_shock": recent_shock,
                    "stale_shock": stale_shock,
                }
            )
        return panel, blueprints

    def test_train_gate_passes_for_dense_specific_noncollapse_edge(self):
        panel, blueprints = self._manual_partition()
        result = evaluate_train_partition(
            panel,
            blueprints,
            min_eligible_episodes=12,
            min_shock_episodes=12,
            min_symbols=2,
            bootstrap_samples=500,
        )
        self.assertTrue(result["gate_pass"], result["gate_checks"])
        self.assertEqual(result["eligible_breach_rate"], 0.0)
        self.assertEqual(result["recent_shock_breach_rate"], 1.0)
        self.assertGreater(result["recent_shock_breach_rate_edge"], 0.05)
        self.assertGreater(result["recent_shock_edge_bootstrap_lb90"], 0.0)
        self.assertGreater(result["eligible_worst_decile_mean_min_return"], result["recent_shock_worst_decile_mean_min_return"])
        self.assertGreater(result["recent_shock_breach_rate_edge"], result["stale_shock_breach_rate_edge"])
        self.assertEqual(result["integrity_violations"], [])

    def test_stale_placebo_edge_above_current_fails_specificity_in_isolation(self):
        panel, blueprints = self._manual_partition()
        recent_rows = [row for row in blueprints if row["recent_shock"]]
        for row in recent_rows[:4]:
            path_index = panel.loc[row["entry_date"] : row["exit_date"]].index
            panel.loc[path_index, row["symbol"]] = 100.0
            panel.loc[path_index[4], row["symbol"]] = 98.0
            panel.loc[row["exit_date"], row["symbol"]] = 97.0
        softened = {
            (row["symbol"], row["signal_date"])
            for row in recent_rows[:4]
        }
        for row in blueprints:
            row["stale_shock"] = bool(
                row["recent_shock"]
                and (row["symbol"], row["signal_date"]) not in softened
            )

        result = evaluate_train_partition(
            panel,
            blueprints,
            min_eligible_episodes=12,
            min_shock_episodes=12,
            min_symbols=2,
            bootstrap_samples=500,
        )

        failed = [name for name, passed in result["gate_checks"].items() if not passed]
        self.assertEqual(failed, ["current_filter_edge_exceeds_stale_placebo"])
        self.assertGreater(
            result["stale_shock_breach_rate_edge"],
            result["recent_shock_breach_rate_edge"],
        )
        self.assertFalse(result["gate_pass"])

    def test_payload_reserves_holdout_and_carries_complete_noncollapse_stack(self):
        panel = self._selection_panel(periods=620)
        payload = run_lab_from_panel(
            panel,
            symbols=["AAPL", "AMD"],
            provenance={"fixture": True},
            train_fraction=0.60,
            trend_lookback_sessions=60,
            momentum_lookback_sessions=20,
            min_eligible_episodes=1,
            min_shock_episodes=1,
            min_symbols=1,
            bootstrap_samples=500,
        )
        self.assertIn(payload["strategy_outcome"], {"STRATEGY_ADVANCED", "FAMILY_CLOSED"})
        self.assertFalse(payload["funnel_claim_f2"])
        self.assertFalse(payload["l1_claim"])
        self.assertFalse(payload["untouched_holdout"]["outcome_metrics_read"])
        self.assertNotIn("episodes", payload["untouched_holdout"])
        self.assertLess(
            payload["data_window"]["train_last_signal_date"],
            payload["untouched_holdout"]["first_signal_date"],
        )
        self.assertEqual(payload["option_stage"]["pricing_calls"], 0)
        self.assertEqual(payload["structure"], "conditional_put_credit_spread_not_yet_priced")
        self.assertEqual(payload["option_entry_filter"]["dte_range"], [18, 24])
        self.assertEqual(payload["option_entry_filter"]["short_put_delta_range"], [0.18, 0.25])
        self.assertEqual(payload["option_entry_filter"]["wing_width_usd"], 2.0)
        self.assertEqual(payload["option_entry_filter"]["minimum_credit_usd"], 0.30)
        self.assertEqual(payload["capital_fit_usd"], 200.0)
        self.assertEqual(payload["one_lot_max_loss_usd"], 200.0)
        self.assertEqual(payload["max_lots"], 1)
        self.assertEqual(payload["forecast_type"], "non_collapse")
        self.assertIn("positive theta", payload["greek_exposures"]["intended"])
        self.assertTrue(payload["stand_aside_rule"])
        self.assertIn("underlying close-path", payload["claim_scope"])
        self.assertFalse(payload["methodology_boundaries"]["panel_bias_free"])
        self.assertIn("survivorship", payload["methodology_boundaries"]["panel_selection_bias"])
        self.assertIn("daily closes only", payload["methodology_boundaries"]["barrier_fidelity"])
        self.assertIn("can both be true", payload["methodology_boundaries"]["specificity_control"])
        self.assertIn(
            "not a multi-symbol date-blocked",
            payload["methodology_boundaries"]["bootstrap_dependence"],
        )
        if payload["strategy_outcome"] == "FAMILY_CLOSED":
            self.assertIn("failed gates:", payload["dominant_failure_mechanism"])
        json.dumps(payload, allow_nan=False)

    def test_positive_terminal_mean_cannot_hide_missing_barrier_edge(self):
        panel, blueprints = self._manual_partition(current_edge=False)
        result = evaluate_train_partition(
            panel,
            blueprints,
            min_eligible_episodes=12,
            min_shock_episodes=12,
            min_symbols=2,
            bootstrap_samples=500,
        )
        self.assertGreater(result["eligible_mean_terminal_return_after_cost"], 0.0)
        self.assertFalse(result["gate_checks"]["eligible_breach_rate_at_most_limit"])
        self.assertFalse(result["gate_checks"]["recent_shock_breach_rate_edge_at_least_minimum"])
        self.assertFalse(result["gate_pass"])

    def test_symbol_breadth_is_a_nonvacuous_gate(self):
        panel, blueprints = self._manual_partition()
        one_symbol = [row for row in blueprints if row["symbol"] == "AAPL"]
        result = evaluate_train_partition(
            panel,
            one_symbol,
            min_eligible_episodes=4,
            min_shock_episodes=4,
            min_symbols=2,
            bootstrap_samples=500,
        )
        self.assertFalse(result["gate_checks"]["minimum_eligible_symbol_breadth"])
        self.assertFalse(result["gate_checks"]["minimum_recent_shock_symbol_breadth"])
        self.assertFalse(result["gate_pass"])

    def test_overlap_and_nonfinite_inputs_fail_closed(self):
        panel, blueprints = self._manual_partition()
        duplicated = [blueprints[0], dict(blueprints[0]), *blueprints[1:]]
        result = evaluate_train_partition(
            panel,
            duplicated,
            min_eligible_episodes=1,
            min_shock_episodes=1,
            min_symbols=1,
            bootstrap_samples=500,
        )
        self.assertIn("episode_1:overlap", result["integrity_violations"])
        self.assertFalse(result["gate_pass"])

        broken = panel.copy()
        broken.iloc[0, 0] = np.nan
        with self.assertRaisesRegex(ValueError, "finite"):
            build_episode_blueprints(broken, symbols=["AAPL", "AMD"])


if __name__ == "__main__":
    unittest.main()

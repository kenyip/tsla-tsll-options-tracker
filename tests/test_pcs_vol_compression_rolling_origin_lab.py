import unittest

import numpy as np
import pandas as pd

from scripts.pcs_vol_compression_rolling_origin_lab import (
    COST_AXES,
    _fold_pass,
    compression_config,
    expansion_control,
    unconditional_control,
)
from trader_platform.research.pcs_sim import entry_filters_pass


class PcsVolCompressionRollingOriginLabTest(unittest.TestCase):
    def test_compression_and_expansion_controls_are_lagged_and_disjoint(self):
        compression = compression_config()
        expansion = expansion_control(compression)

        self.assertEqual(compression["entry_signal_lag_bars"], 1)
        self.assertEqual(expansion["entry_signal_lag_bars"], 1)
        self.assertTrue(entry_filters_pass(pd.Series({"hv_20": 0.16, "hv_60": 0.20}), compression))
        self.assertFalse(entry_filters_pass(pd.Series({"hv_20": 0.24, "hv_60": 0.20}), compression))
        self.assertTrue(entry_filters_pass(pd.Series({"hv_20": 0.24, "hv_60": 0.20}), expansion))
        self.assertFalse(entry_filters_pass(pd.Series({"hv_20": 0.16, "hv_60": 0.20}), expansion))
        self.assertNotIn("entry_hv_ratio_min", compression)
        self.assertNotIn("entry_hv_ratio_max", expansion)

    def test_hv_ratio_filter_fails_closed_on_missing_nonfinite_or_zero_denominator(self):
        config = compression_config()

        self.assertFalse(entry_filters_pass(pd.Series({"hv_20": 0.16}), config))
        self.assertFalse(entry_filters_pass(pd.Series({"hv_20": np.nan, "hv_60": 0.20}), config))
        self.assertFalse(entry_filters_pass(pd.Series({"hv_20": 0.16, "hv_60": 0.0}), config))
        self.assertFalse(entry_filters_pass(pd.Series({"hv_20": 0.16, "hv_60": -0.20}), config))
        self.assertFalse(entry_filters_pass(pd.Series({"hv_20": "invalid", "hv_60": 0.20}), config))
        self.assertFalse(entry_filters_pass(pd.Series({"hv_20": 0.16, "hv_60": "invalid"}), config))

    def test_fold_gate_rejects_passing_holdout_when_train_axis_failed(self):
        passing = self._run_row()
        failing = {**passing, "gate_pnl": -0.01, "pnl": -0.01, "verdict": "NULL"}
        train = {axis: passing for axis in COST_AXES}
        train["slip_5pct"] = failing
        holdout = {axis: passing for axis in COST_AXES}
        windows = {
            axis: {"dense_negative_n": 0, "window_max_dd": 10.0, "integrity": True}
            for axis in COST_AXES
        }

        self.assertFalse(_fold_pass(train, holdout, windows))

    def test_unconditional_control_removes_only_entry_filters_and_retains_lag(self):
        config = compression_config()
        control = unconditional_control(config)

        self.assertEqual(control["entry_signal_lag_bars"], 1)
        self.assertNotIn("entry_hv_ratio_max", control)
        self.assertEqual(control["long_dte"], config["long_dte"])
        self.assertTrue(entry_filters_pass(pd.Series(dtype=float), control))

    @staticmethod
    def _run_row():
        return {
            "ok": True,
            "n_trades": 10,
            "gate_pnl": 1.0,
            "pnl": 1.0,
            "verdict": "SHIP",
            "gate_max_loss_usd": 50.0,
            "max_loss_usd": 50.0,
            "gate_dd": 10.0,
            "dd": 10.0,
            "integrity": True,
        }


if __name__ == "__main__":
    unittest.main()

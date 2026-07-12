import unittest

import pandas as pd

from scripts.pcs_pullback_rolling_origin_lab import (
    _fold_boundaries,
    _fold_pass,
    _pullback_config,
    _run_pass,
    _bullish_mirror,
)
from trader_platform.research.pcs_sim import entry_filters_pass


class PcsPullbackRollingOriginLabTest(unittest.TestCase):
    def test_pullback_and_bullish_mirror_are_lagged_and_disjoint(self):
        pullback = _pullback_config()
        bullish = _bullish_mirror(pullback)

        self.assertEqual(pullback["entry_signal_lag_bars"], 1)
        self.assertTrue(entry_filters_pass(pd.Series({"ret_1d": -0.005, "rsi_14": 50.0}), pullback))
        self.assertFalse(entry_filters_pass(pd.Series({"ret_1d": 0.005, "rsi_14": 50.0}), pullback))
        self.assertTrue(entry_filters_pass(pd.Series({"ret_1d": 0.005, "rsi_14": 50.0}), bullish))
        self.assertFalse(entry_filters_pass(pd.Series({"ret_1d": -0.005, "rsi_14": 50.0}), bullish))
        self.assertNotIn("entry_ret_1d_max", bullish)

    def test_fold_boundaries_are_expanding_and_holdouts_do_not_overlap(self):
        folds = _fold_boundaries(100, train_fractions=(0.4, 0.6, 0.8))

        self.assertEqual(folds, [(0, 40, 60), (0, 60, 80), (0, 80, 100)])
        self.assertEqual([end - split for _, split, end in folds], [20, 20, 20])

    def test_fold_gate_fails_when_train_failed_despite_passing_holdout(self):
        passing = self._run_row()
        failing = {**passing, "gate_pnl": -0.01, "pnl": -0.01}
        windows = {
            "slip_5pct": {"dense_negative_n": 0, "window_max_dd": 10.0, "integrity": True},
            "fixed_0p01": {"dense_negative_n": 0, "window_max_dd": 10.0, "integrity": True},
        }

        self.assertFalse(
            _fold_pass(
                {"slip_5pct": failing, "fixed_0p01": failing},
                {"slip_5pct": passing, "fixed_0p01": passing},
                windows,
            )
        )

    def test_run_gate_uses_unrounded_drawdown_boundary(self):
        row = self._run_row()
        row["gate_dd"] = 75.0001

        self.assertFalse(_run_pass(row))

    def test_fold_gate_fails_closed_on_window_density_or_integrity(self):
        passing = self._run_row()
        axes = {"slip_5pct": passing, "fixed_0p01": passing}
        windows = {
            "slip_5pct": {"dense_negative_n": 6, "window_max_dd": 10.0, "integrity": True},
            "fixed_0p01": {"dense_negative_n": 0, "window_max_dd": 10.0, "integrity": True},
        }

        self.assertFalse(_fold_pass(axes, axes, windows))
        windows["slip_5pct"]["dense_negative_n"] = 0
        windows["fixed_0p01"]["integrity"] = False
        self.assertFalse(_fold_pass(axes, axes, windows))

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

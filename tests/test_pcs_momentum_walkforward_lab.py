import unittest

import pandas as pd

from scripts.pcs_momentum_walkforward_lab import (
    _mirror_control,
    axis_pass,
    momentum_config,
    rank_key,
    walkforward_pass,
)
from trader_platform.research.pcs_sim import entry_filters_pass


class PcsMomentumWalkforwardLabTest(unittest.TestCase):
    def test_momentum_and_mirror_filters_are_lag_ready_and_disjoint(self):
        config = momentum_config(dte=7, ret_min=0.005, rsi_min=55.0, rsi_max=75.0)
        mirror = _mirror_control(config)

        self.assertTrue(entry_filters_pass(pd.Series({"ret_1d": 0.005, "rsi_14": 55.0}), config))
        self.assertFalse(entry_filters_pass(pd.Series({"ret_1d": -0.005, "rsi_14": 45.0}), config))
        self.assertTrue(entry_filters_pass(pd.Series({"ret_1d": -0.005, "rsi_14": 45.0}), mirror))
        self.assertFalse(entry_filters_pass(pd.Series({"ret_1d": 0.005, "rsi_14": 55.0}), mirror))
        self.assertNotIn("entry_ret_1d_min", mirror)
        self.assertEqual(mirror["entry_signal_lag_bars"], 1)

    def test_zero_return_and_rsi_50_boundary_is_not_shared_with_mirror(self):
        config = momentum_config(dte=7, ret_min=0.0, rsi_min=50.0, rsi_max=65.0)
        mirror = _mirror_control(config)
        boundary = pd.Series({"ret_1d": 0.0, "rsi_14": 50.0})

        self.assertTrue(entry_filters_pass(boundary, config))
        self.assertFalse(entry_filters_pass(boundary, mirror))
        self.assertLess(mirror["entry_ret_1d_max"], 0.0)

    def test_axis_gate_rejects_dense_negative_pnl(self):
        row = {
            "ok": True,
            "n_trades": 50,
            "pnl": -0.01,
            "verdict": "SHIP",
            "max_loss_usd": 50.0,
            "dd": 10.0,
            "integrity": True,
        }

        self.assertFalse(axis_pass(row))

    def test_axis_gate_fails_closed_on_bad_result_and_unrounded_boundary(self):
        row = {
            "ok": False,
            "n_trades": 10,
            "pnl": 1.0,
            "verdict": "SHIP",
            "max_loss_usd": 50.0,
            "dd": 75.0,
            "integrity": True,
        }

        self.assertFalse(axis_pass(row))
        row.update({"ok": True, "gate_dd": 75.0001})
        self.assertFalse(axis_pass(row))

    def test_train_rank_never_reads_holdout_metrics(self):
        passing_axis = {
            "ok": True,
            "n_trades": 10,
            "pnl": 1.0,
            "verdict": "SHIP",
            "max_loss_usd": 50.0,
            "dd": 10.0,
            "integrity": True,
        }
        losing_axis = {**passing_axis, "pnl": -1.0, "verdict": "REJECT"}
        winner = {
            "train": {"slip_5pct": passing_axis, "fixed_0p01": passing_axis},
            "holdout": {"slip_5pct": losing_axis, "fixed_0p01": losing_axis},
        }
        loser = {
            "train": {"slip_5pct": losing_axis, "fixed_0p01": losing_axis},
            "holdout": {"slip_5pct": passing_axis, "fixed_0p01": passing_axis},
        }

        self.assertGreater(rank_key(winner), rank_key(loser))

    def test_walkforward_gate_rejects_holdout_pass_when_train_failed(self):
        passing_axis = {
            "ok": True,
            "n_trades": 10,
            "pnl": 1.0,
            "verdict": "SHIP",
            "max_loss_usd": 50.0,
            "dd": 10.0,
            "integrity": True,
        }
        losing_axis = {**passing_axis, "pnl": -1.0, "verdict": "REJECT"}
        windows = {"dense_negative_n": 0, "window_max_dd": 10.0, "integrity": True}

        self.assertFalse(
            walkforward_pass(
                {"slip_5pct": losing_axis, "fixed_0p01": losing_axis},
                {"slip_5pct": passing_axis, "fixed_0p01": passing_axis},
                windows,
            )
        )


if __name__ == "__main__":
    unittest.main()

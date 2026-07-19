import unittest

from scripts.pcs_income_post_shock_lab import (
    COST_AXES,
    discovery_pass,
    income_candidate_config,
    unconditional_control_config,
)


class PcsIncomePostShockLabTest(unittest.TestCase):
    def test_frozen_post_shock_bounds_and_pt(self):
        cfg = income_candidate_config()
        self.assertEqual(cfg["profit_target"], 0.50)
        self.assertLess(cfg["entry_ret_5d_max"], 0.0)
        self.assertEqual(cfg["entry_signal_lag_bars"], 1)

    def test_control_strips_entry(self):
        ctrl = unconditional_control_config()
        self.assertNotIn("entry_ret_5d_min", ctrl)
        self.assertEqual(ctrl["profit_target"], 0.50)

    def test_discovery(self):
        axis = {
            "ok": True,
            "n_trades": 10,
            "gate_pnl": 20.0,
            "pnl": 20.0,
            "gate_max_loss_usd": 90.0,
            "max_loss_usd": 90.0,
            "gate_dd": 40.0,
            "dd": 40.0,
            "integrity": True,
        }
        cand = {a: dict(axis) for a in COST_AXES}
        ctrl = {a: {**axis, "gate_pnl": 1.0, "pnl": 1.0} for a in COST_AXES}
        self.assertTrue(discovery_pass(cand, ctrl))


if __name__ == "__main__":
    unittest.main()

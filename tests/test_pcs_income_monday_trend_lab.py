import unittest

from scripts.pcs_income_monday_trend_lab import (
    COST_AXES,
    discovery_pass,
    income_candidate_config,
    unconditional_control_config,
)


class PcsIncomeMondayTrendLabTest(unittest.TestCase):
    @staticmethod
    def _axis(*, pnl=10.0, n=10, ml=90.0, dd=40.0, integrity=True, ok=True):
        return {
            "ok": ok,
            "n_trades": n,
            "gate_pnl": pnl,
            "pnl": pnl,
            "gate_max_loss_usd": ml,
            "max_loss_usd": ml,
            "gate_dd": dd,
            "dd": dd,
            "integrity": integrity,
        }

    def test_monday_and_profit_target_frozen(self):
        cfg = income_candidate_config()
        self.assertEqual(cfg["entry_weekdays"], [0])
        self.assertEqual(cfg["profit_target"], 0.50)
        self.assertEqual(cfg["bear_dte"], 0)

    def test_control_removes_entry_only(self):
        c = income_candidate_config()
        ctrl = unconditional_control_config(c)
        self.assertEqual(ctrl["profit_target"], 0.50)
        self.assertNotIn("entry_weekdays", ctrl)
        self.assertNotIn("entry_ret_5d_max", ctrl)

    def test_discovery_requires_beat_control(self):
        cand = {a: self._axis(pnl=15.0) for a in COST_AXES}
        ctrl = {a: self._axis(pnl=5.0) for a in COST_AXES}
        self.assertTrue(discovery_pass(cand, ctrl))
        self.assertFalse(discovery_pass(cand, {a: self._axis(pnl=15.0) for a in COST_AXES}))


if __name__ == "__main__":
    unittest.main()

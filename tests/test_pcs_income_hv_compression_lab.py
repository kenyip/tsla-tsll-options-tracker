import unittest

from scripts.pcs_income_hv_compression_lab import (
    COST_AXES,
    discovery_pass,
    income_candidate_config,
    unconditional_control_config,
)


class PcsIncomeHvCompressionLabTest(unittest.TestCase):
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

    def test_hv_compression_and_profit_target_frozen(self):
        cfg = income_candidate_config()
        self.assertEqual(cfg["profit_target"], 0.50)
        self.assertEqual(cfg["long_dte"], 21)
        self.assertEqual(cfg["entry_hv_ratio_max"], 0.85)
        self.assertEqual(cfg["bear_dte"], 0)
        self.assertEqual(cfg["entry_signal_lag_bars"], 1)

    def test_control_strips_entry_only(self):
        c = income_candidate_config()
        ctrl = unconditional_control_config(c)
        self.assertEqual(ctrl["profit_target"], 0.50)
        self.assertNotIn("entry_hv_ratio_max", ctrl)
        self.assertNotIn("entry_ema_stack_min", ctrl)

    def test_discovery_gate(self):
        cand = {a: self._axis(pnl=12.0) for a in COST_AXES}
        ctrl = {a: self._axis(pnl=1.0) for a in COST_AXES}
        self.assertTrue(discovery_pass(cand, ctrl))
        self.assertFalse(discovery_pass(cand, {a: self._axis(pnl=12.0) for a in COST_AXES}))


if __name__ == "__main__":
    unittest.main()

import unittest

from scripts.pcs_income_pilot_lab import (
    COST_AXES,
    discovery_pass,
    income_candidate_config,
    management_diagnostics,
    train_rank_key,
    unconditional_control_config,
)


class PcsIncomePilotLabTest(unittest.TestCase):
    @staticmethod
    def _axis(
        *,
        pnl: float = 10.0,
        n_trades: int = 10,
        max_loss: float = 90.0,
        dd: float = 40.0,
        integrity: bool = True,
        ok: bool = True,
    ):
        return {
            "ok": ok,
            "n_trades": n_trades,
            "gate_pnl": pnl,
            "pnl": pnl,
            "gate_max_loss_usd": max_loss,
            "max_loss_usd": max_loss,
            "gate_dd": dd,
            "dd": dd,
            "integrity": integrity,
        }

    def test_candidate_keeps_profit_target_and_stand_aside_bear(self):
        cfg = income_candidate_config()
        self.assertEqual(cfg["structure"], "put_credit_spread")
        self.assertEqual(cfg["profit_target"], 0.50)
        self.assertEqual(cfg["bear_dte"], 0)
        self.assertEqual(cfg["long_dte"], 21)
        self.assertLess(cfg["entry_ret_14d_max"], 0.0)
        self.assertTrue(cfg["regime_flip_exit_enabled"])

    def test_control_strips_only_entry_filters(self):
        candidate = income_candidate_config()
        control = unconditional_control_config(candidate)
        self.assertEqual(control["profit_target"], candidate["profit_target"])
        self.assertEqual(control["dte_stop"], candidate["dte_stop"])
        self.assertNotIn("entry_ret_14d_min", control)
        self.assertNotIn("entry_ema_stack_min", control)

    def test_discovery_gate_requires_dual_cost_edge_capital_and_control_beat(self):
        candidate = {axis: self._axis(pnl=20.0) for axis in COST_AXES}
        control = {axis: self._axis(pnl=5.0) for axis in COST_AXES}
        self.assertTrue(discovery_pass(candidate, control))

        for mutation in (
            {"slip_5pct": {**candidate["slip_5pct"], "n_trades": 7}},
            {"fixed_0p01": {**candidate["fixed_0p01"], "gate_pnl": 0.0}},
            {"slip_5pct": {**candidate["slip_5pct"], "integrity": False}},
            {"fixed_0p01": {**candidate["fixed_0p01"], "gate_max_loss_usd": 300.0001}},
            {"slip_5pct": {**candidate["slip_5pct"], "gate_dd": 150.0001}},
        ):
            changed = {axis: dict(candidate[axis]) for axis in COST_AXES}
            changed.update(mutation)
            self.assertFalse(discovery_pass(changed, control))

        tied = {axis: self._axis(pnl=20.0) for axis in COST_AXES}
        self.assertFalse(discovery_pass(candidate, tied))

    def test_train_rank_prefers_stronger_worst_axis(self):
        stronger = {
            "symbol": "AAA",
            "train": {
                "slip_5pct": self._axis(pnl=25.0, max_loss=100.0),
                "fixed_0p01": self._axis(pnl=20.0, max_loss=100.0),
            },
        }
        weaker = {
            "symbol": "BBB",
            "train": {
                "slip_5pct": self._axis(pnl=30.0, max_loss=80.0),
                "fixed_0p01": self._axis(pnl=19.0, max_loss=80.0),
            },
        }
        self.assertGreater(train_rank_key(stronger), train_rank_key(weaker))

    def test_management_diagnostics_track_profit_targets(self):
        result = type(
            "R",
            (),
            {
                "metrics": {
                    "avg_days_held": 6.0,
                    "exit_reasons": {"profit_target": 5, "dte_stop": 2, "regime_flip": 1},
                }
            },
        )()
        diag = management_diagnostics(result)
        self.assertEqual(diag["profit_target_exits"], 5)
        self.assertTrue(diag["profit_target_exercised"])
        self.assertEqual(diag["dte_stop_exits"], 2)


if __name__ == "__main__":
    unittest.main()

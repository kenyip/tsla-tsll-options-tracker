import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd

from trader_platform.research.evaluate_proxy import (
    discovery_pass_axes,
    evaluate_proxy,
    stand_aside_purity,
    summarize_sim_result,
)
from trader_platform.research.strategy_spec import strategy_spec_from_mapping


def _trade(credit: float, debit: float, max_loss_share: float = 0.9):
    return SimpleNamespace(
        net_credit=credit,
        exit_debit=debit,
        max_loss_per_share=max_loss_share,
        entry_date=pd.Timestamp("2020-01-02"),
        exit_date=pd.Timestamp("2020-01-10"),
    )


class EvaluateProxyTest(unittest.TestCase):
    def test_stand_aside_purity_fraction(self):
        purity = stand_aside_purity(
            {
                "stand_aside": 70,
                "put_credit_spread": 20,
                "call_credit_spread": 10,
            }
        )
        self.assertEqual(purity["stand_aside_count"], 70)
        self.assertEqual(purity["route_event_count"], 100)
        self.assertAlmostEqual(float(purity["stand_aside_frac"]), 0.7)

    def test_summarize_integrity_pass(self):
        trades = [_trade(1.0, 0.4), _trade(1.0, 0.5)]
        # pnl per contract: (0.6 + 0.5)*100 = 110
        metrics = {
            "total_pnl_per_contract": 110.0,
            "max_dd_per_contract": 0.0,
            "n_trades": 2,
            "exit_reasons": {"profit_target": 2},
        }
        # recompute dd from ledger: [60, 50] cum [60, 110] dd 0
        result = SimpleNamespace(
            ok=True,
            skipped=False,
            n_trades=2,
            metrics=metrics,
            trades=trades,
            capital={},
            route_counts={"put_credit_spread": 2},
        )
        frame = pd.DataFrame({"close": [1.0, 2.0]})
        summary = summarize_sim_result(result, frame)
        self.assertTrue(summary.ok)
        self.assertTrue(summary.integrity)
        self.assertEqual(summary.n_trades, 2)
        self.assertAlmostEqual(summary.pnl, 110.0)

    def test_discovery_pass_axes_requires_dual_cost(self):
        good = {
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
        gates = strategy_spec_from_mapping(
            {
                "candidate_id": "C",
                "family_id": "F",
                "evaluation_mode": "single_structure",
                "structure": "put_credit_spread",
                "forecast_type": "x",
                "economic_mechanism": "y",
                "symbols": ["BAC"],
            }
        ).discovery_gates
        axes = {"slip_5pct": dict(good), "fixed_0p01": dict(good)}
        self.assertTrue(discovery_pass_axes(axes, gates))
        bad = {**good, "gate_pnl": -1.0, "pnl": -1.0}
        self.assertFalse(
            discovery_pass_axes(
                {"slip_5pct": bad, "fixed_0p01": dict(good)},
                gates,
            )
        )

    def test_evaluate_proxy_uses_mocked_runner_paths(self):
        idx = pd.date_range("2019-01-01", periods=100, freq="B")
        frame = pd.DataFrame(
            {
                "open": np.linspace(10, 20, len(idx)),
                "high": np.linspace(10, 20, len(idx)) + 0.5,
                "low": np.linspace(10, 20, len(idx)) - 0.5,
                "close": np.linspace(10, 20, len(idx)),
                "volume": 1_000_000,
                "iv_proxy": 0.4,
                "iv_rank": 20.0,
                "regime": ["bullish"] * len(idx),
            },
            index=idx,
        )

        def fake_build(symbol, period="5y", use_cache=True):
            return frame.copy()

        trade = _trade(1.0, 0.3, max_loss_share=0.7)
        metrics = {
            "total_pnl_per_contract": 70.0,
            "max_dd_per_contract": 0.0,
            "n_trades": 1,
            "exit_reasons": {"profit_target": 1},
            "profit_factor": 2.0,
        }
        pcs_result = SimpleNamespace(
            ok=True,
            skipped=False,
            n_trades=1,
            metrics=metrics,
            trades=[trade],
            capital={"capital_fit_usd": 70.0},
        )

        with patch("trader_platform.research.evaluate_proxy.build_market_frame", fake_build), patch(
            "trader_platform.research.evaluate_proxy.run_pcs_backtest",
            return_value=pcs_result,
        ):
            spec = strategy_spec_from_mapping(
                {
                    "candidate_id": "MOCK_PCS",
                    "family_id": "MOCK",
                    "evaluation_mode": "single_structure",
                    "structure": "put_credit_spread",
                    "forecast_type": "non_collapse",
                    "economic_mechanism": "mock",
                    "symbols": ["BAC", "KO"],
                    "management": {"profit_target": 0.5},
                    "discovery_gates": {
                        "min_trades": 1,
                        "max_loss_usd": 300,
                        "max_dd_discovery_usd": 150,
                    },
                }
            )
            report = evaluate_proxy(spec)
            self.assertTrue(report["ranking_complete"])
            self.assertEqual(report["n_completed"], 2)
            self.assertIn(report["decision"], {
                "STRATEGY_ADVANCED_F2",
                "STRATEGY_ADVANCED_F1_HOLDOUT_FAILED",
                "FAMILY_CLOSED",
            })
            # With min_trades=1 and positive pnl both axes, train should pass.
            self.assertTrue(report["strategy_advanced_train"])


if __name__ == "__main__":
    unittest.main()

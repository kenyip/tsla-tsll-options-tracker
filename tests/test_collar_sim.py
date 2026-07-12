import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from trader_platform.evolve_tick import build_population
from trader_platform.research.collar_sim import (
    capital_fit_collar,
    collar_symbol_eligible,
    defined_collar_max_loss_per_share,
    pick_collar_entry,
    run_collar_backtest,
    run_collar_cost_axes,
)
from trader_platform.strategy_dna import STRUCTURE_CATALOG, dna_from_structure


class CollarSimTest(unittest.TestCase):
    def _bars(self, spot0: float = 20.0, regime: str = "bullish", n: int = 100) -> pd.DataFrame:
        # Mild grind up so collars can cycle without constant defined-loss.
        closes = np.linspace(spot0, spot0 * 1.08, n)
        return pd.DataFrame(
            {
                "close": closes,
                "iv_proxy": np.full(n, 0.40),
                "iv_rank": np.full(n, 40.0),
                "regime": [regime] * n,
            },
            index=pd.bdate_range("2024-01-02", periods=n),
        )

    def test_catalog_engine_and_uses_flag(self):
        self.assertIn("collared_covered_call", STRUCTURE_CATALOG)
        dna = dna_from_structure("collared_covered_call", ["F"])
        self.assertTrue(dna.uses_collar_sim())
        self.assertEqual(STRUCTURE_CATALOG["collared_covered_call"]["sim_engine"], "collar_sim")

    def test_eligibility_rejects_levered_and_oversized(self):
        ok, why = collar_symbol_eligible("TSLL", 13.0)
        self.assertFalse(ok)
        self.assertIn("levered", why)
        ok2, why2 = collar_symbol_eligible("AAPL", 300.0)
        self.assertFalse(ok2)
        self.assertIn("share_lot", why2)
        ok3, why3 = collar_symbol_eligible("F", 14.0)
        self.assertTrue(ok3)
        self.assertEqual(why3, "ok")

    def test_capital_fit_uses_stock_notional(self):
        cap = capital_fit_collar(
            entry_spot=20.0,
            net_option_debit_per_share=0.15,
            max_loss_usd=180.0,
            sleeve_usd=3000.0,
        )
        self.assertAlmostEqual(cap["share_lot_usd"], 2000.0)
        self.assertAlmostEqual(cap["capital_fit_usd"], 2015.0)
        self.assertEqual(cap["capital_fit"], "fit_3k")
        self.assertIn("100*spot", cap["note"])

    def test_defined_max_loss_downside_floor(self):
        # spot 20, put 18, net debit 0.20 → max loss 2.20/share = $220
        ml = defined_collar_max_loss_per_share(20.0, 18.0, 0.20)
        self.assertAlmostEqual(ml, 2.20)

    def test_half_spread_counts_two_option_legs_entry(self):
        bars = self._bars()
        row = bars.iloc[0]
        today = bars.index[0]
        base = {
            "long_dte": 21,
            "collar_put_delta": 0.25,
            "collar_call_delta": 0.25,
            "max_loss_budget_usd": 500.0,
        }
        mid = pick_collar_entry(row, 20.0, today, base, symbol="F")
        costly = pick_collar_entry(
            row, 20.0, today, {**base, "half_spread_per_leg": 0.01}, symbol="F"
        )
        self.assertIsNotNone(mid)
        self.assertIsNotNone(costly)
        assert mid is not None and costly is not None
        # buy put + sell call: +half on put, -half on call credit → +0.02 net debit
        self.assertAlmostEqual(costly.net_option_debit - mid.net_option_debit, 0.02, places=6)

    def test_does_not_reenter_on_same_bar_after_exit(self):
        dna = dna_from_structure("collared_covered_call", ["F"])
        cfg = {**dna.sim_config(), "dte_stop": 100, "max_loss_budget_usd": 500.0}
        result = run_collar_backtest(
            "F", period="smoke", df=self._bars(), config=cfg, apply_absolute_gates=False
        )
        self.assertTrue(result.ok, result.reason)
        self.assertGreater(len(result.trades), 1)
        for previous, following in zip(result.trades, result.trades[1:]):
            self.assertNotEqual(previous.exit_date, following.entry_date)

    def test_tsll_fail_closed(self):
        result = run_collar_backtest(
            "TSLL", period="smoke", df=self._bars(spot0=13.0), config={"long_dte": 21}
        )
        self.assertTrue(result.skipped)
        self.assertIn("levered", result.reason)

    def test_bearish_regime_fails_closed(self):
        row = self._bars(regime="bearish").iloc[0]
        trade = pick_collar_entry(
            row,
            20.0,
            self._bars().index[0],
            dna_from_structure("collared_covered_call", ["F"]).sim_config(),
            symbol="F",
        )
        self.assertIsNone(trade)

    def test_structure_pure_population(self):
        population = build_population(
            [{"symbol": "F", "strategy_family": "wheel"}],
            structures=["collared_covered_call"],
            mutants_per_seed=12,
            seed=3,
        )
        self.assertGreater(len(population), 1)
        self.assertEqual({d.structure for d in population}, {"collared_covered_call"})
        self.assertTrue(all(d.uses_collar_sim() for d in population))

    def test_cost_axes_never_register_proxy_ship(self):
        dna = dna_from_structure("collared_covered_call", ["F"])
        lab = run_collar_cost_axes("F", df=self._bars(), config=dna.sim_config())
        self.assertFalse(lab["register_proxy_ship"])
        for axis in lab["axes"].values():
            self.assertFalse((axis.get("gate") or {}).get("register_proxy_ship", True))
        # Decision is reject-unless; synthetic mild path may pass or fail but must be explicit.
        self.assertIn(lab["decision"], {"PASS_COLLAR_COST_GATES", "REJECT_COLLAR_CLASS_THIS_CYCLE"})

    def test_vacuous_single_trade_fails_absolute_gates(self):
        from trader_platform.research.collar_sim import evaluate_collar_absolute_gates

        gate = evaluate_collar_absolute_gates(
            {"n_trades": 1, "max_dd_per_contract": 0.0, "worst_max_loss_usd": 100.0},
            {"max_loss_usd": 100.0},
            {"window_max_dd_usd": 0.0, "dense_neg_count": 0, "n_dense_windows": 0},
        )
        self.assertFalse(gate["passed"])
        self.assertTrue(any("vacuous" in r for r in gate["reasons"]))
        self.assertFalse(gate["register_proxy_ship"])

    def test_dense_negative_result_cannot_pass_absolute_gates(self):
        from trader_platform.research.collar_sim import evaluate_collar_absolute_gates

        gate = evaluate_collar_absolute_gates(
            {"n_trades": 20, "total_pnl_per_contract": -0.01, "worst_max_loss_usd": 50.0},
            {"max_loss_usd": 50.0},
            {"window_max_dd_usd": 10.0, "dense_neg_count": 1, "n_dense_windows": 4},
        )
        self.assertFalse(gate["passed"])
        self.assertIn("non_positive_after_cost_pnl_-0.01", gate["reasons"])


if __name__ == "__main__":
    unittest.main()

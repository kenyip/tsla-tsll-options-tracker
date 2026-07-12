import unittest

import numpy as np
import pandas as pd

from trader_platform.research.iron_butterfly_sim import run_iron_butterfly_backtest
from trader_platform.strategy_dna import dna_from_structure


class IronButterflySimTest(unittest.TestCase):
    def _bars(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "close": np.linspace(50.0, 51.0, 60),
                "iv_proxy": np.full(60, 0.45),
                "iv_rank": np.full(60, 55.0),
                "regime": ["neutral"] * 60,
            },
            index=pd.bdate_range("2026-01-02", periods=60),
        )

    def test_credit_iron_butterfly_has_defined_risk_and_ordered_wings(self):
        result = run_iron_butterfly_backtest(
            "TEST",
            period="smoke",
            df=self._bars(),
            config={
                "long_dte": 21,
                "spread_width": 2.0,
                "min_credit_pct": 0.25,
                "max_loss_budget_usd": 300.0,
            },
        )

        self.assertTrue(result.ok, result.reason)
        self.assertGreater(result.n_trades, 0)
        self.assertEqual(result.capital["structure"], "iron_butterfly")
        self.assertLessEqual(result.capital["max_loss_usd"], 300.0)
        trade = result.trades[0]
        self.assertLess(trade.lower_strike, trade.middle_strike)
        self.assertLess(trade.middle_strike, trade.upper_strike)
        self.assertGreater(trade.entry_credit, 0.0)
        self.assertAlmostEqual(
            trade.max_loss_per_share,
            trade.middle_strike - trade.lower_strike - trade.entry_credit,
        )

    def test_catalog_routes_iron_butterfly_to_its_simulator(self):
        dna = dna_from_structure("iron_butterfly", ["TEST"])

        self.assertTrue(dna.uses_iron_butterfly_sim())
        self.assertEqual(dna.config["max_loss_budget_usd"], 300.0)

    def test_broken_wing_has_wider_put_side_and_defined_worst_case(self):
        dna = dna_from_structure("broken_wing_iron_butterfly", ["TEST"])
        result = run_iron_butterfly_backtest(
            "TEST",
            period="smoke",
            df=self._bars(),
            config={**dna.sim_config(), "structure": dna.structure},
        )

        self.assertTrue(result.ok, result.reason)
        self.assertGreater(result.n_trades, 0)
        trade = result.trades[0]
        lower_width = trade.middle_strike - trade.lower_strike
        upper_width = trade.upper_strike - trade.middle_strike
        self.assertGreater(lower_width, upper_width)
        self.assertAlmostEqual(trade.max_loss_per_share, lower_width - trade.entry_credit)
        self.assertEqual(result.capital["structure"], "broken_wing_iron_butterfly")
        self.assertLessEqual(result.capital["max_loss_usd"], 300.0)


if __name__ == "__main__":
    unittest.main()

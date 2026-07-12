import unittest

import numpy as np
import pandas as pd

from trader_platform.research.debit_vertical_sim import run_debit_vertical_backtest
from trader_platform.strategy_dna import dna_from_structure


class DebitVerticalSimTest(unittest.TestCase):
    def _bars(self, regime: str, start: float, end: float) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "close": np.linspace(start, end, 60),
                "iv_proxy": np.full(60, 0.45),
                "iv_rank": np.full(60, 35.0),
                "regime": [regime] * 60,
            },
            index=pd.bdate_range("2026-01-02", periods=60),
        )

    def test_bull_call_vertical_is_defined_debit_and_ordered(self):
        result = run_debit_vertical_backtest(
            "TEST",
            structure="bull_call_debit_spread",
            period="smoke",
            df=self._bars("bullish", 50.0, 58.0),
            config={
                "long_dte": 21,
                "debit_long_delta": 0.55,
                "spread_width": 2.0,
                "max_loss_budget_usd": 300.0,
            },
        )

        self.assertTrue(result.ok, result.reason)
        self.assertGreater(result.n_trades, 0)
        self.assertEqual(result.capital["structure"], "bull_call_debit_spread")
        self.assertLessEqual(result.capital["max_loss_usd"], 300.0)
        trade = result.trades[0]
        self.assertEqual(trade.right, "call")
        self.assertLess(trade.long_strike, trade.short_strike)
        self.assertGreater(trade.entry_debit, 0.0)

    def test_bear_put_vertical_is_defined_debit_and_ordered(self):
        result = run_debit_vertical_backtest(
            "TEST",
            structure="bear_put_debit_spread",
            period="smoke",
            df=self._bars("bearish", 58.0, 50.0),
            config={
                "long_dte": 21,
                "debit_long_delta": 0.55,
                "spread_width": 2.0,
                "max_loss_budget_usd": 300.0,
            },
        )

        self.assertTrue(result.ok, result.reason)
        self.assertGreater(result.n_trades, 0)
        trade = result.trades[0]
        self.assertEqual(trade.right, "put")
        self.assertGreater(trade.long_strike, trade.short_strike)

    def test_catalog_routes_both_structures_to_debit_vertical_sim(self):
        for structure in ("bull_call_debit_spread", "bear_put_debit_spread"):
            dna = dna_from_structure(structure, ["TEST"])
            self.assertTrue(dna.uses_debit_vertical_sim())
            self.assertEqual(dna.config["max_loss_budget_usd"], 300.0)


if __name__ == "__main__":
    unittest.main()

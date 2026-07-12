import unittest
from typing import cast

import numpy as np
import pandas as pd

from trader_platform.evolve_tick import build_population
from trader_platform.research.put_ratio_backspread_sim import (
    pick_put_ratio_backspread_entry,
    run_put_ratio_backspread_backtest,
)
from trader_platform.strategy_dna import dna_from_structure


class PutRatioBackspreadSimTest(unittest.TestCase):
    def _bars(self, regime: str = "bearish") -> pd.DataFrame:
        return pd.DataFrame(
            {
                "close": np.linspace(50.0, 47.0, 80),
                "iv_proxy": np.full(80, 0.45),
                "iv_rank": np.full(80, 55.0),
                "regime": [regime] * 80,
            },
            index=pd.bdate_range("2026-01-02", periods=80),
        )

    def test_defined_valley_loss_matches_expiry_payoff(self):
        dna = dna_from_structure("put_ratio_backspread", ["TEST"])
        result = run_put_ratio_backspread_backtest(
            "TEST", period="smoke", df=self._bars(), config=dna.sim_config()
        )

        self.assertTrue(result.ok, result.reason)
        self.assertGreater(result.n_trades, 0)
        trade = result.trades[0]
        self.assertLess(trade.long_strike, trade.short_strike)
        expiry_value_at_long_strike = trade.mark_value(
            trade.long_strike, trade.iv_at_entry, trade.expiration
        )
        expiry_loss = trade.entry_debit - expiry_value_at_long_strike
        self.assertAlmostEqual(expiry_loss, trade.max_loss_per_share)
        self.assertLessEqual(result.capital["max_loss_usd"], 300.0)

    def test_adverse_cost_increases_entry_debit_and_defined_loss(self):
        row = self._bars().iloc[0]
        today = self._bars().index[0]
        base = {
            "long_dte": 21,
            "short_target_delta": 0.30,
            "spread_width": 1.0,
            "max_loss_budget_usd": 500.0,
        }
        mid = pick_put_ratio_backspread_entry(row, 50.0, today, base)
        costly = pick_put_ratio_backspread_entry(
            row, 50.0, today, {**base, "slippage_pct": 0.05, "half_spread_per_leg": 0.01}
        )

        self.assertIsNotNone(mid)
        self.assertIsNotNone(costly)
        assert mid is not None and costly is not None
        self.assertGreater(costly.entry_debit, mid.entry_debit)
        self.assertGreater(costly.max_loss_per_share, mid.max_loss_per_share)

    def test_half_spread_cost_counts_three_legs_each_way(self):
        bars = self._bars()
        row = bars.iloc[0]
        today = cast(pd.Timestamp, pd.Timestamp("2026-01-02"))
        base = {
            "long_dte": 21,
            "short_target_delta": 0.30,
            "spread_width": 1.0,
            "max_loss_budget_usd": 500.0,
        }
        mid = pick_put_ratio_backspread_entry(row, 50.0, today, base)
        costly = pick_put_ratio_backspread_entry(
            row, 50.0, today, {**base, "half_spread_per_leg": 0.01}
        )

        self.assertIsNotNone(mid)
        self.assertIsNotNone(costly)
        assert mid is not None and costly is not None
        self.assertAlmostEqual(costly.entry_debit - mid.entry_debit, 0.03, places=8)
        mark_day = today + pd.Timedelta(days=5)
        mid_exit = mid.mark_value(48.0, 0.45, mark_day)
        costly_exit = costly.mark_value(48.0, 0.45, mark_day, half_spread_per_leg=0.01)
        self.assertAlmostEqual(mid_exit - costly_exit, 0.03, places=8)
        mid_pnl = mid_exit - mid.entry_debit
        costly_pnl = costly_exit - costly.entry_debit
        self.assertAlmostEqual(mid_pnl - costly_pnl, 0.06, places=8)

    def test_does_not_reenter_on_same_bar_after_exit(self):
        dna = dna_from_structure("put_ratio_backspread", ["TEST"])
        cfg = {**dna.sim_config(), "dte_stop": 100}
        result = run_put_ratio_backspread_backtest(
            "TEST", period="smoke", df=self._bars(), config=cfg
        )

        self.assertTrue(result.ok, result.reason)
        self.assertGreater(len(result.trades), 2)
        for previous, following in zip(result.trades, result.trades[1:]):
            self.assertNotEqual(previous.exit_date, following.entry_date)

    def test_bullish_regime_fails_closed(self):
        row = self._bars("bullish").iloc[0]
        trade = pick_put_ratio_backspread_entry(
            row,
            50.0,
            self._bars("bullish").index[0],
            dna_from_structure("put_ratio_backspread", ["TEST"]).sim_config(),
        )
        self.assertIsNone(trade)

    def test_catalog_and_explicit_population_are_structure_pure(self):
        dna = dna_from_structure("put_ratio_backspread", ["TEST"])
        self.assertTrue(dna.uses_put_ratio_backspread_sim())
        population = build_population(
            [{"symbol": "TEST", "strategy_family": "wheel"}],
            structures=["put_ratio_backspread"],
            mutants_per_seed=20,
            seed=7,
        )
        self.assertGreater(len(population), 1)
        self.assertEqual({d.structure for d in population}, {"put_ratio_backspread"})


if __name__ == "__main__":
    unittest.main()

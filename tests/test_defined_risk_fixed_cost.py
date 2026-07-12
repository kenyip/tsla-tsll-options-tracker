import unittest

import numpy as np
import pandas as pd

from trader_platform.research.butterfly_sim import run_butterfly_backtest
from trader_platform.research.calendar_sim import run_calendar_backtest
from trader_platform.research.debit_vertical_sim import run_debit_vertical_backtest
from trader_platform.research.diagonal_sim import run_diagonal_backtest
from trader_platform.research.iron_butterfly_sim import run_iron_butterfly_backtest
from trader_platform.research.pcs_sim import run_pcs_backtest


class DefinedRiskFixedCostTest(unittest.TestCase):
    def _bars(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "close": np.linspace(50.0, 51.0, 80),
                "iv_proxy": np.full(80, 0.45),
                "iv_rank": np.full(80, 55.0),
                "regime": ["neutral"] * 80,
            },
            index=pd.bdate_range("2026-01-02", periods=80),
        )

    def test_fixed_half_spread_reduces_pcs_results(self):
        config = {
            "long_dte": 21,
            "long_target_delta": 0.20,
            "spread_width": 2.0,
            "min_credit_pct": 0.05,
            "max_loss_budget_usd": 300.0,
            "bear_dte": 1,
        }
        baseline = run_pcs_backtest("TEST", period="smoke", df=self._bars(), config=config)
        stressed = run_pcs_backtest(
            "TEST",
            period="smoke",
            df=self._bars(),
            config={**config, "half_spread_per_leg": 0.02},
        )

        self.assertGreater(baseline.n_trades, 0)
        self.assertGreater(stressed.n_trades, 0)
        self.assertLess(
            stressed.metrics["total_pnl_per_contract"],
            baseline.metrics["total_pnl_per_contract"],
        )

    def test_fixed_half_spread_reduces_iron_butterfly_results(self):
        config = {
            "long_dte": 21,
            "spread_width": 2.0,
            "min_credit_pct": 0.10,
            "max_loss_budget_usd": 300.0,
        }
        baseline = run_iron_butterfly_backtest("TEST", period="smoke", df=self._bars(), config=config)
        stressed = run_iron_butterfly_backtest(
            "TEST",
            period="smoke",
            df=self._bars(),
            config={**config, "half_spread_per_leg": 0.02},
        )

        self.assertGreater(baseline.n_trades, 0)
        self.assertGreater(stressed.n_trades, 0)
        self.assertLess(
            stressed.metrics["total_pnl_per_contract"],
            baseline.metrics["total_pnl_per_contract"],
        )

    def test_fixed_half_spread_reduces_proxy_defined_risk_results(self):
        cases = [
            (run_calendar_backtest, {}),
            (run_diagonal_backtest, {}),
            (run_butterfly_backtest, {}),
            (run_debit_vertical_backtest, {"structure": "bull_call_debit_spread"}),
        ]
        config = {
            "long_dte": 21,
            "short_dte": 7,
            "diagonal_short_dte": 7,
            "diagonal_long_dte": 35,
            "iv_rank_min": 0.0,
            "max_loss_budget_usd": 750.0,
        }
        for runner, kwargs in cases:
            with self.subTest(runner=runner.__name__):
                baseline = runner("TEST", period="smoke", df=self._bars(), config=config, **kwargs)
                stressed = runner(
                    "TEST",
                    period="smoke",
                    df=self._bars(),
                    config={**config, "half_spread_per_leg": 0.01},
                    **kwargs,
                )
                self.assertGreater(baseline.n_trades, 0)
                self.assertGreater(stressed.n_trades, 0)
                self.assertLess(
                    stressed.metrics["total_pnl_per_contract"],
                    baseline.metrics["total_pnl_per_contract"],
                )

    def test_pcs_ledger_recompute_exact_and_collar_style_bogus(self):
        from scripts.bac_fri7_management_grid import ledger_integrity

        config = {
            "long_dte": 21,
            "long_target_delta": 0.20,
            "spread_width": 2.0,
            "min_credit_pct": 0.05,
            "max_loss_budget_usd": 300.0,
            "bear_dte": 1,
            "half_spread_per_leg": 0.01,
        }
        sim = run_pcs_backtest("TEST", period="smoke", df=self._bars(), config=config)
        self.assertGreater(sim.n_trades, 0)
        reported = float(sim.metrics["total_pnl_per_contract"])
        integrity = ledger_integrity(list(sim.trades), reported)
        self.assertTrue(integrity["ledger_exact"])
        self.assertAlmostEqual(integrity["pnl_recompute_delta"], 0.0, places=9)
        self.assertEqual(integrity["same_bar_reentries"], 0)
        # Collar-field formula zeros PcsTrade → delta ≈ -reported (matches prior BAC false alarm).
        self.assertAlmostEqual(
            integrity["bogus_delta_vs_reported"],
            -reported,
            places=9,
        )


if __name__ == "__main__":
    unittest.main()

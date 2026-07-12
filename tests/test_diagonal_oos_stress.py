import unittest
from types import SimpleNamespace

import pandas as pd

from scripts.diagonal_oos_stress import _summary


class DiagonalOosStressTest(unittest.TestCase):
    def test_summary_reports_entry_density_by_year(self):
        result = SimpleNamespace(
            ok=True,
            skipped=False,
            reason="ok",
            n_trades=3,
            metrics={
                "total_pnl_per_contract": 25.0,
                "max_dd_per_contract": 10.0,
                "win_rate_pct": 66.7,
                "profit_factor": 2.0,
            },
            capital={"max_loss_usd": 125.0, "capital_fit": "fit_3k"},
            trades=[
                SimpleNamespace(entry_date=pd.Timestamp("2024-01-05")),
                SimpleNamespace(entry_date=pd.Timestamp("2024-07-05")),
                SimpleNamespace(entry_date=pd.Timestamp("2025-01-05")),
            ],
        )

        summary = _summary(result)

        self.assertEqual(summary["entry_years"], {"2024": 2, "2025": 1})
        self.assertEqual(summary["n_entry_years"], 2)


if __name__ == "__main__":
    unittest.main()

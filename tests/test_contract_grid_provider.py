import unittest
from datetime import date, datetime, timezone

from trader_platform.research.contract_grid_provider import ArchivedContractGridProvider
from trader_platform.research.option_quote_observations import OptionQuoteObservation


class ArchivedContractGridProviderTest(unittest.TestCase):
    def test_market_date_coverage_and_fail_closed_counter(self):
        rows = [
            OptionQuoteObservation(
                observed_at=datetime(2026, 7, 12, 0, 13, tzinfo=timezone.utc),
                symbol="TSLL",
                expiration=date(2026, 7, 17),
                option_type=option_type,
                strike=strike,
                bid=0.20,
                ask=0.24,
                source="test",
                is_observed=True,
            )
            for option_type, strike in (("put", 10.0), ("put", 11.0), ("call", 13.0))
        ]
        provider = ArchivedContractGridProvider(rows)

        covered = provider("tsll", date(2026, 7, 11))
        missing = provider("TSLL", date(2026, 7, 10))

        self.assertEqual(
            covered,
            {"2026-07-17": {"put": [10.0, 11.0], "call": [13.0]}},
        )
        self.assertIsNone(missing)
        self.assertEqual(
            provider.coverage_counters(),
            {
                "requests": 2,
                "covered_requests": 1,
                "missing_symbol_date": 1,
                "observations_selected": 3,
                "coverage_ratio": 0.5,
                "market_timezone": "America/New_York",
            },
        )

    def test_synthetic_rows_never_enter_grid(self):
        row = OptionQuoteObservation(
            observed_at=datetime(2026, 7, 11, 20, 0, tzinfo=timezone.utc),
            symbol="TSLL",
            expiration=date(2026, 7, 17),
            option_type="put",
            strike=10.0,
            bid=0.20,
            ask=0.24,
            source="fixture",
            is_observed=False,
        )

        provider = ArchivedContractGridProvider([row])

        self.assertIsNone(provider("TSLL", date(2026, 7, 11)))
        self.assertEqual(provider.coverage_counters()["missing_symbol_date"], 1)


    def test_provider_drives_required_mode_backtest(self):
        import pandas as pd

        entry_date = date(2026, 7, 11)
        rows = [
            OptionQuoteObservation(
                observed_at=datetime(2026, 7, 11, 20, 0, tzinfo=timezone.utc),
                symbol="TEST",
                expiration=date(2026, 7, 31),
                option_type="put",
                strike=strike,
                bid=0.20,
                ask=0.24,
                source="test",
                is_observed=True,
            )
            for strike in (40.0, 42.0, 44.0, 46.0, 48.0)
        ]
        history = pd.DataFrame(
            {
                "close": [50.0] * 20,
                "iv_proxy": [0.45] * 20,
                "iv_rank": [60.0] * 20,
                "regime": ["neutral"] * 20,
            },
            index=pd.date_range("2026-06-22", periods=20),
        )
        provider = ArchivedContractGridProvider(rows)

        from trader_platform.research.pcs_sim import run_pcs_backtest

        result = run_pcs_backtest(
            "TEST",
            df=history,
            config={
                "long_dte": 14,
                "long_target_delta": 0.20,
                "spread_width": 2.0,
                "min_credit_pct": 0.01,
                "max_loss_budget_usd": 300.0,
            },
            contract_grid_provider=provider,
            require_contract_grid=True,
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.n_trades, 1)
        self.assertEqual(result.trades[0].entry_date.date(), entry_date)
        self.assertEqual(result.trades[0].expiration.date(), date(2026, 7, 31))
        self.assertEqual(result.metrics["contract_grid_mode"], "required_observed")
        self.assertEqual(provider.coverage_counters()["covered_requests"], 1)


if __name__ == "__main__":
    unittest.main()

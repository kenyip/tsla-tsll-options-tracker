import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


class BreakoutBullCallOptionLabTest(unittest.TestCase):
    def test_exact_one_dollar_width_fails_closed_when_proxy_grid_increment_is_too_wide(self):
        try:
            from scripts.breakout_bull_call_option_lab import select_proxy_contract
        except ModuleNotFoundError as exc:
            self.fail(f"option payoff lab module is missing: {exc}")

        contract = select_proxy_contract(
            spot=150.0,
            sigma=0.30,
            entry_date="2021-01-04",
        )

        self.assertIsNone(contract)

    def test_signed_liquidation_keeps_fixed_closing_friction_below_zero(self):
        from scripts import breakout_bull_call_option_lab as lab

        price_vertical_package = getattr(lab, "price_vertical_package", None)
        self.assertIsNotNone(price_vertical_package, "signed package pricer is missing")
        liquidation = price_vertical_package(
            spot=1.0,
            sigma=0.20,
            today="2021-01-15",
            expiration="2021-01-15",
            long_strike=10.0,
            short_strike=11.0,
            side="exit",
            slippage_pct=0.0,
            half_spread_per_leg=0.01,
        )

        self.assertAlmostEqual(liquidation, -0.02)

    def test_invalidation_exits_on_first_later_close_below_prebreakout_high(self):
        from scripts import breakout_bull_call_option_lab as lab

        simulate_signal = getattr(lab, "simulate_signal", None)
        self.assertIsNotNone(simulate_signal, "signal simulator is missing")
        dates = pd.bdate_range("2021-01-04", periods=12)
        close = pd.Series([52.0, 49.0, *([49.0] * 10)], index=dates)

        trade = simulate_signal(
            symbol="TEST",
            close=close,
            entry_date=dates[0],
            sigma=0.30,
            prebreakout_high=50.0,
            cost={"slippage_pct": 0.0, "half_spread_per_leg": 0.01},
        )

        self.assertEqual(trade["exit_reason"], "breakout_invalidation")
        self.assertEqual(trade["sessions_held"], 1)
        self.assertEqual(trade["exit_date"], "2021-01-05")

    def test_portfolio_ledger_blocks_overlap_and_same_day_reentry(self):
        from scripts import breakout_bull_call_option_lab as lab

        build_portfolio_ledger = getattr(lab, "build_portfolio_ledger", None)
        self.assertIsNotNone(build_portfolio_ledger, "portfolio admission policy is missing")
        trades = [
            {"symbol": "AAPL", "entry_date": "2021-01-04", "exit_date": "2021-01-06", "pnl_usd": 2.0},
            {"symbol": "MSFT", "entry_date": "2021-01-05", "exit_date": "2021-01-07", "pnl_usd": 9.0},
            {"symbol": "NVDA", "entry_date": "2021-01-06", "exit_date": "2021-01-08", "pnl_usd": 9.0},
            {"symbol": "AMD", "entry_date": "2021-01-07", "exit_date": "2021-01-11", "pnl_usd": 3.0},
        ]

        ledger, skipped = build_portfolio_ledger(
            trades,
            symbol_order=["AAPL", "MSFT", "NVDA", "AMD"],
        )

        self.assertEqual([row["symbol"] for row in ledger], ["AAPL", "AMD"])
        self.assertEqual(len(skipped), 2)
        self.assertTrue(all(row["reason"] == "global_risk_unit_open_or_same_day_exit" for row in skipped))

    def test_negative_control_counts_first_loss_in_drawdown_and_fails_edge_gate(self):
        from scripts import breakout_bull_call_option_lab as lab

        summarize_axis = getattr(lab, "summarize_axis", None)
        self.assertIsNotNone(summarize_axis, "axis summarizer is missing")
        dates = pd.bdate_range("2021-01-04", periods=12)
        trades = []
        for index in range(6):
            trades.append(
                {
                    "symbol": "TEST",
                    "entry_date": str(dates[index * 2].date()),
                    "exit_date": str(dates[index * 2 + 1].date()),
                    "pnl_usd": -20.0,
                    "entry_debit_risk_usd": 50.0,
                    "one_lot_max_loss_usd": 50.0,
                }
            )

        summary = summarize_axis(
            trades,
            requested=6,
            symbol_order=["TEST"],
            min_event_trades=6,
            min_portfolio_trades=6,
            min_symbols=1,
        )

        self.assertEqual(summary["portfolio"]["max_drawdown_usd"], 120.0)
        self.assertEqual(summary["portfolio"]["dense_negative_windows"], 1)
        self.assertFalse(summary["gate_checks"]["positive_event_total_pnl"])
        self.assertFalse(summary["gate_checks"]["positive_portfolio_total_pnl"])
        self.assertFalse(summary["gate_checks"]["portfolio_max_drawdown_lte_75"])
        self.assertFalse(summary["gate_pass"])

    def test_partition_prices_only_frozen_treated_entry_with_ten_session_cap(self):
        from scripts import breakout_bull_call_option_lab as lab

        evaluate_partition = getattr(lab, "evaluate_partition", None)
        self.assertIsNotNone(evaluate_partition, "partition evaluator is missing")
        dates = pd.bdate_range("2021-01-04", periods=45)
        values = [50.0] * 20 + [51.0, 52.0] + [54.0] * 23
        panel = pd.DataFrame({"TEST": values}, index=dates)
        blueprint = {
            "symbol": "TEST",
            "control_entry_date": str(dates[5].date()),
            "treated_signal_date": str(dates[20].date()),
            "treated_entry_date": str(dates[21].date()),
            "treated_hv_20": 0.30,
        }

        summary = evaluate_partition(
            panel,
            [blueprint],
            cost={"slippage_pct": 0.0, "half_spread_per_leg": 0.0},
            symbol_order=["TEST"],
            min_event_trades=1,
            min_portfolio_trades=1,
            min_symbols=1,
        )

        self.assertEqual(summary["n_requested"], 1)
        self.assertEqual(summary["n_eligible"], 1)
        self.assertEqual(summary["trades"][0]["entry_date"], str(dates[21].date()))
        self.assertLessEqual(summary["trades"][0]["sessions_held"], 10)

    def test_strategy_advances_only_when_every_primary_and_secondary_axis_passes(self):
        from scripts import breakout_bull_call_option_lab as lab

        decide = getattr(lab, "decide_strategy_outcome", None)
        self.assertIsNotNone(decide, "strategy decision function is missing")
        passing = {
            "development": {"percentage_5pct": {"gate_pass": True}, "fixed_0p01": {"gate_pass": True}},
            "inspected_secondary_stress": {
                "percentage_5pct": {"gate_pass": True},
                "fixed_0p01": {"gate_pass": True},
            },
        }
        self.assertEqual(decide(passing)["strategy_outcome"], "STRATEGY_ADVANCED")

        passing["inspected_secondary_stress"]["fixed_0p01"]["gate_pass"] = False
        decision = decide(passing)
        self.assertEqual(decision["strategy_outcome"], "FAMILY_CLOSED")
        self.assertIn("inspected_secondary_stress.fixed_0p01", decision["failed_axes"])

    def test_cli_help_runs_from_direct_script_entrypoint(self):
        completed = subprocess.run(
            [sys.executable, "scripts/breakout_bull_call_option_lab.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--frozen-train", completed.stdout)
        self.assertIn("--f2-summary", completed.stdout)

    def test_contract_expiry_session_precedes_hard_stop_on_sparse_calendar(self):
        from scripts.breakout_bull_call_option_lab import simulate_signal

        dates = pd.to_datetime(
            [
                "2021-01-04",
                "2021-01-05",
                "2021-01-06",
                "2021-01-07",
                "2021-01-08",
                "2021-01-11",
                "2021-01-12",
                "2021-01-13",
                "2021-01-14",
                "2021-01-21",
                "2021-01-25",
                "2021-01-26",
            ]
        )
        trade = simulate_signal(
            symbol="TEST",
            close=pd.Series([52.0] * len(dates), index=dates),
            entry_date="2021-01-04",
            sigma=0.30,
            prebreakout_high=50.0,
            cost={"slippage_pct": 0.0, "half_spread_per_leg": 0.0},
        )

        self.assertIsNotNone(trade)
        assert trade is not None
        self.assertEqual(trade["exit_reason"], "contract_expiration_session")
        self.assertEqual(trade["exit_date"], "2021-01-21")
        self.assertLessEqual(pd.Timestamp(trade["exit_date"]), pd.Timestamp(trade["expiration"]))

    def test_normalized_evidence_hash_ignores_only_generated_at(self):
        from scripts.breakout_bull_call_option_lab import normalized_evidence_sha256

        first = {"generated_at": "2026-01-01T00:00:00Z", "outcome": "FAMILY_CLOSED", "n": 13}
        second = {"generated_at": "2026-01-02T00:00:00Z", "outcome": "FAMILY_CLOSED", "n": 13}
        changed = {"generated_at": "2026-01-02T00:00:00Z", "outcome": "FAMILY_CLOSED", "n": 14}

        self.assertEqual(normalized_evidence_sha256(first), normalized_evidence_sha256(second))
        self.assertNotEqual(normalized_evidence_sha256(first), normalized_evidence_sha256(changed))

    def test_cli_refuses_existing_output_before_reading_inputs_and_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "existing.json"
            original = b'{"preserve":true}\n'
            out.write_bytes(original)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/breakout_bull_call_option_lab.py",
                    "--frozen-train",
                    str(Path(tmp) / "missing-train.json"),
                    "--f2-summary",
                    str(Path(tmp) / "missing-summary.json"),
                    "--out",
                    str(out),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("refusing to overwrite option payoff evidence", completed.stderr)
            self.assertEqual(out.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()

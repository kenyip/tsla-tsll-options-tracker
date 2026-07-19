"""Path-stress staging contracts — engine gates, not strategy edge claims."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from trader_platform.research.path_stress import (
    load_path_stress_config,
    pack_regimes,
    regime_passes_gates,
    run_path_stress_pack,
    run_staged_path_stress,
    window_days_for_spec,
)
from trader_platform.research.strategy_spec import load_strategy_spec, strategy_spec_from_mapping


def _synth_frame(n: int = 80, trend: float = 0.0) -> pd.DataFrame:
    idx = pd.bdate_range("2023-01-02", periods=n)
    close = 100 * (1 + trend) ** np.arange(n)
    # inject a mid dump then recovery so discovery can find shapes
    close = close.copy()
    close[30:40] *= np.linspace(1.0, 0.75, 10)
    close[40:55] *= np.linspace(0.75, 1.05, 15)
    df = pd.DataFrame(
        {
            "open": close * 0.99,
            "high": close * 1.01,
            "low": close * 0.98,
            "close": close,
            "volume": 1_000_000,
            "regime": ["bullish"] * n,
            "iv_rank": np.linspace(20, 60, n),
            "iv_proxy": 0.3,
            "ema_stack": 0.2,
            "rsi_14": 50.0,
            "hv_20": 0.25,
            "hv_60": 0.3,
            "volume_surge": 1.0,
            "ret_1d": 0.0,
            "ret_5d": 0.0,
            "ret_14d": 0.0,
            "intraday_return": 0.0,
            "macd": 0.1,
            "ema_21": close,
            "ema_55": close * 0.99,
            "ema_200": close * 0.95,
        },
        index=idx,
    )
    # one gap shock day
    df.iloc[50, df.columns.get_loc("open")] = float(df["close"].iloc[49]) * 1.10
    return df


class PathStressGatesTest(unittest.TestCase):
    def test_config_loads_quick_and_full(self):
        cfg = load_path_stress_config()
        quick = pack_regimes("quick", cfg)
        full = pack_regimes("full", cfg)
        self.assertIn("huge_down", quick)
        self.assertIn("gap_shock", quick)
        self.assertLess(len(quick), len(full))
        self.assertIn("vol_expansion", full)

    def test_window_days_scales_with_dte(self):
        seed_45 = load_strategy_spec(
            Path("configs/strategy_specs/pcs_bull_neutral_income_45d_v1.json")
        )
        seed_21 = load_strategy_spec(
            Path("configs/strategy_specs/pcs_iv_rich_noncollapse_21d_v1.json")
        )
        d45 = window_days_for_spec(seed_45)
        d21 = window_days_for_spec(seed_21)
        # 45 DTE + pad 7 → 52; 21 + 7 → 28
        self.assertGreaterEqual(d45, 45)
        self.assertGreater(d45, d21)
        raw = seed_45.to_dict()
        raw["management"] = {**raw["management"], "long_dte": 7}
        short = strategy_spec_from_mapping(raw)
        self.assertEqual(window_days_for_spec(short), 21)  # min_days floor

    def test_zero_trades_pass_by_default(self):
        ok, issues = regime_passes_gates(
            {"n_trades": 0, "ok": True, "integrity": True, "max_loss_usd": 0, "dd": 0, "pnl": 0},
            {"allow_zero_trades": True, "require_integrity": True, "max_loss_usd": 300, "max_dd_usd": 400},
            available=True,
        )
        self.assertTrue(ok)
        self.assertIn("zero_trades_stand_aside", issues)

    def test_max_loss_breach_fails(self):
        ok, issues = regime_passes_gates(
            {
                "n_trades": 3,
                "ok": True,
                "integrity": True,
                "max_loss_usd": 500,
                "dd": 50,
                "pnl": -20,
            },
            {"allow_zero_trades": True, "require_integrity": True, "max_loss_usd": 300, "max_dd_usd": 400},
            available=True,
        )
        self.assertFalse(ok)
        self.assertTrue(any("max_loss" in i for i in issues))

    def test_unavailable_window_not_hard_fail(self):
        ok, _ = regime_passes_gates({}, {}, available=False)
        self.assertTrue(ok)

    def test_negative_pnl_ok_when_not_required(self):
        ok, issues = regime_passes_gates(
            {
                "n_trades": 2,
                "ok": True,
                "integrity": True,
                "max_loss_usd": 100,
                "dd": 80,
                "pnl": -40,
            },
            {
                "require_positive_pnl": False,
                "require_integrity": True,
                "max_loss_usd": 300,
                "max_dd_usd": 400,
            },
            available=True,
        )
        self.assertTrue(ok, issues)


class PathStressStagingTest(unittest.TestCase):
    def test_quick_fail_skips_full(self):
        seed = load_strategy_spec(
            Path("configs/strategy_specs/pcs_bull_neutral_income_45d_v1.json")
        )
        frame = _synth_frame()

        def _fake_pack(spec, *, pack, **kwargs):
            from trader_platform.research.path_stress import PathStressReport

            return PathStressReport(
                generated_at="t",
                pack=pack,
                candidate_id=spec.candidate_id,
                symbols=["TEST"],
                pack_pass=(pack != "quick"),  # quick fails
                n_regimes=4,
                n_available=1,
                n_pass=0 if pack == "quick" else 1,
                n_fail=1 if pack == "quick" else 0,
                n_unavailable=0,
            )

        with patch(
            "trader_platform.research.path_stress.run_path_stress_pack",
            side_effect=_fake_pack,
        ):
            report = run_staged_path_stress(
                seed, symbols=["TEST"], frames={"TEST": frame}
            )
        self.assertFalse(report["full_ran"])
        self.assertFalse(report["staged_pass"])
        self.assertEqual(report["stage_note"], "stopped_after_quick_fail")

    def test_quick_pass_promotes_to_full(self):
        seed = load_strategy_spec(
            Path("configs/strategy_specs/pcs_bull_neutral_income_45d_v1.json")
        )

        def _fake_pack(spec, *, pack, **kwargs):
            from trader_platform.research.path_stress import PathStressReport

            return PathStressReport(
                generated_at="t",
                pack=pack,
                candidate_id=spec.candidate_id,
                symbols=["TEST"],
                pack_pass=True,
                n_regimes=4 if pack == "quick" else 12,
                n_available=2,
                n_pass=2,
                n_fail=0,
                n_unavailable=0,
            )

        with patch(
            "trader_platform.research.path_stress.run_path_stress_pack",
            side_effect=_fake_pack,
        ):
            report = run_staged_path_stress(seed, symbols=["TEST"])
        self.assertTrue(report["full_ran"])
        self.assertTrue(report["staged_pass"])
        self.assertEqual(report["stage_note"], "quick_and_full")

    def test_quick_only_never_runs_full(self):
        seed = load_strategy_spec(
            Path("configs/strategy_specs/pcs_bull_neutral_income_45d_v1.json")
        )

        calls: list[str] = []

        def _fake_pack(spec, *, pack, **kwargs):
            from trader_platform.research.path_stress import PathStressReport

            calls.append(pack)
            return PathStressReport(
                generated_at="t",
                pack=pack,
                candidate_id=spec.candidate_id,
                symbols=["TEST"],
                pack_pass=True,
                n_regimes=4,
                n_available=1,
                n_pass=1,
                n_fail=0,
                n_unavailable=0,
            )

        with patch(
            "trader_platform.research.path_stress.run_path_stress_pack",
            side_effect=_fake_pack,
        ):
            report = run_staged_path_stress(seed, symbols=["TEST"], quick_only=True)
        self.assertEqual(calls, ["quick"])
        self.assertTrue(report["staged_pass"])
        self.assertFalse(report["full_ran"])


if __name__ == "__main__":
    unittest.main()

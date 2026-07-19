import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from trader_platform.research.living_registry import (
    LivingRegistry,
    LivingSeat,
    save_living_registry,
)
from trader_platform.research.opportunity_watcher import watch_once


class OpportunityWatcherTest(unittest.TestCase):
    def test_no_qualified_when_registry_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reg.json"
            save_living_registry(LivingRegistry(), path)
            result = watch_once(registry_path=path)
            self.assertEqual(result.status, "NO_QUALIFIED_STRATEGY")
            self.assertFalse(result.trading_authority)

    def test_f1_not_watchable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reg.json"
            reg = LivingRegistry()
            reg.upsert(
                LivingSeat(
                    seat_id="C:BAC",
                    candidate_id="C",
                    family_id="F",
                    status="f1_train",
                    symbols=["BAC"],
                )
            )
            save_living_registry(reg, path)
            result = watch_once(registry_path=path)
            self.assertEqual(result.status, "NO_QUALIFIED_STRATEGY")

    def test_watchable_stand_aside_is_no_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reg.json"
            reg = LivingRegistry()
            reg.upsert(
                LivingSeat(
                    seat_id="C:BAC",
                    candidate_id="C",
                    family_id="F",
                    status="f2_holdout",
                    symbols=["BAC"],
                    router_policy="pcs_non_bear",
                )
            )
            save_living_registry(reg, path)
            row = pd.Series(
                {
                    "close": 40.0,
                    "iv_proxy": 0.4,
                    "iv_rank": 20.0,
                    "regime": "bearish",
                }
            )

            with patch(
                "trader_platform.research.opportunity_watcher._latest_bar",
                return_value=(row, pd.Timestamp("2026-07-18")),
            ):
                result = watch_once(registry_path=path)
            self.assertEqual(result.status, "NO_SETUP")
            self.assertIn("stand aside", result.reason.lower())

    def test_watchable_bullish_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reg.json"
            reg = LivingRegistry()
            reg.upsert(
                LivingSeat(
                    seat_id="C:BAC",
                    candidate_id="C",
                    family_id="F",
                    status="f2_holdout",
                    symbols=["BAC"],
                    router_policy="pcs_non_bear",
                )
            )
            save_living_registry(reg, path)
            row = pd.Series(
                {
                    "close": 40.0,
                    "iv_proxy": 0.4,
                    "iv_rank": 20.0,
                    "regime": "bullish",
                }
            )
            with patch(
                "trader_platform.research.opportunity_watcher._latest_bar",
                return_value=(row, pd.Timestamp("2026-07-18")),
            ):
                result = watch_once(registry_path=path)
            self.assertEqual(result.status, "PAPER_PACKET_READY")
            self.assertEqual(result.selected_structure, "put_credit_spread")
            self.assertFalse(result.packet.get("live_authority"))


if __name__ == "__main__":
    unittest.main()

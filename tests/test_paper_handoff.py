import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from trader_platform.research.living_registry import (
    LivingRegistry,
    LivingSeat,
    save_living_registry,
)
from trader_platform.research.opportunity_watcher import WatchResult
from trader_platform.research.paper_handoff import intent_from_watch, run_paper_handoff
from trader_platform.risk_governor import OrderIntent


class PaperHandoffTest(unittest.TestCase):
    def test_non_ready_watch_stands_aside(self):
        watch = WatchResult(
            status="NO_QUALIFIED_STRATEGY",
            generated_at="2026-07-19T00:00:00+00:00",
            reason="none",
        )
        result = run_paper_handoff(watch=watch)
        self.assertEqual(result.status, "NO_QUALIFIED_STRATEGY")
        self.assertEqual(result.paper_action, "none")

    def test_intent_from_watch_builds_defined_risk(self):
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
                    spec_path="",
                )
            )
            save_living_registry(reg, path)
            watch = WatchResult(
                status="PAPER_PACKET_READY",
                generated_at="2026-07-19T00:00:00+00:00",
                seat_id="C:BAC",
                candidate_id="C",
                symbol="BAC",
                regime="bullish",
                selected_structure="put_credit_spread",
                packet={},
            )
            fake_trade = SimpleNamespace(
                net_credit=0.35,
                max_loss_per_share=0.65,
                short_strike=35.0,
                long_strike=34.0,
                width=1.0,
                right="put",
                expiration=pd.Timestamp("2026-08-21"),
                dte_at_entry=21,
                call_short_strike=0.0,
                call_long_strike=0.0,
            )
            idx = pd.date_range("2026-01-01", periods=30, freq="B")
            frame = pd.DataFrame(
                {
                    "close": 40.0,
                    "iv_proxy": 0.4,
                    "iv_rank": 40.0,
                    "regime": "bullish",
                    "open": 40.0,
                    "high": 41.0,
                    "low": 39.0,
                    "volume": 1e6,
                },
                index=idx,
            )
            with patch(
                "trader_platform.research.paper_handoff.build_market_frame",
                return_value=frame,
            ), patch(
                "trader_platform.research.paper_handoff.pick_structure_entry",
                return_value=fake_trade,
            ):
                intent, reason, meta = intent_from_watch(watch, registry_path=path)
            self.assertEqual(reason, "ok")
            self.assertIsInstance(intent, OrderIntent)
            self.assertTrue(intent.defined_risk)
            self.assertEqual(intent.structure, "put_credit_spread")
            self.assertEqual(intent.max_loss_usd, 65.0)
            self.assertEqual(len(intent.legs or []), 2)


if __name__ == "__main__":
    unittest.main()

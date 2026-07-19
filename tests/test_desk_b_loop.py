import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from trader_platform.research.desk_b_loop import run_desk_b_loop
from trader_platform.research.living_registry import LivingRegistry, save_living_registry
from trader_platform.research.opportunity_watcher import WatchResult
from trader_platform.research.paper_handoff import PaperHandoffResult


class DeskBLoopTest(unittest.TestCase):
    def test_loop_skip_evolve_watcher_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg_path = Path(tmp) / "reg.json"
            out_dir = Path(tmp) / "out"
            save_living_registry(LivingRegistry(), reg_path)
            watch = WatchResult(
                status="NO_QUALIFIED_STRATEGY",
                generated_at="2026-07-19T00:00:00+00:00",
                reason="empty",
            )
            handoff = PaperHandoffResult(
                status="NO_QUALIFIED_STRATEGY",
                watch_status="NO_QUALIFIED_STRATEGY",
                reason="empty",
                generated_at="2026-07-19T00:00:00+00:00",
            )
            with patch(
                "trader_platform.research.desk_b_loop.watch_once", return_value=watch
            ), patch(
                "trader_platform.research.desk_b_loop.run_paper_handoff",
                return_value=handoff,
            ):
                report = run_desk_b_loop(
                    skip_evolve=True,
                    registry_path=reg_path,
                    out_dir=out_dir,
                )
            self.assertEqual(report["bottom_line"], "searching")
            self.assertTrue(Path(report["latest_path"]).exists())


if __name__ == "__main__":
    unittest.main()

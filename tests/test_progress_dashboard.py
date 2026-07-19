import tempfile
import unittest
from pathlib import Path

from trader_platform.research.living_registry import (
    LivingRegistry,
    LivingSeat,
    save_living_registry,
)
from trader_platform.research.progress_dashboard import (
    collect_progress,
    format_progress_text,
    progress_bar,
)


class ProgressDashboardTest(unittest.TestCase):
    def test_progress_bar_bounds(self):
        self.assertIn("100.0%", progress_bar(10, 10))
        self.assertIn("0.0%", progress_bar(0, 10))
        self.assertIn("/", progress_bar(3, 10))

    def test_format_lists_f2(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg_path = Path(tmp) / "reg.json"
            reg = LivingRegistry()
            reg.upsert(
                LivingSeat(
                    seat_id="C_INTC",
                    candidate_id="CAND",
                    family_id="FAM",
                    status="f2_holdout",
                    symbols=["INTC"],
                    router_policy="pcs_bull_only",
                    funnel_stage="F2_UNTOUCHED_HOLDOUT",
                )
            )
            reg.upsert(
                LivingSeat(
                    seat_id="C_KO",
                    candidate_id="CAND2",
                    family_id="FAM2",
                    status="f1_train",
                    symbols=["KO"],
                )
            )
            save_living_registry(reg, reg_path)
            snap = collect_progress(registry_path=reg_path)
            text = format_progress_text(snap)
            self.assertIn("PASSED holdout", text)
            self.assertIn("INTC", text)
            self.assertIn("CAND", text)
            self.assertIn("Train-only", text)
            self.assertGreaterEqual(len(snap.f2_seats), 1)


if __name__ == "__main__":
    unittest.main()

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
    _describe_from_id,
)


class ProgressDashboardTest(unittest.TestCase):
    def test_progress_bar_bounds(self):
        self.assertIn("100.0%", progress_bar(10, 10))
        self.assertIn("0.0%", progress_bar(0, 10))

    def test_describe_grid_id(self):
        d = _describe_from_id(
            "SEED__g_d21_pt50_dl18_iv30_c12_pcs_bu"
        )
        self.assertIn("21DTE", d)
        self.assertIn("50%", d)

    def test_compact_format_stats_and_top(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg_path = Path(tmp) / "reg.json"
            reg = LivingRegistry()
            reg.upsert(
                LivingSeat(
                    seat_id="C_INTC",
                    candidate_id="CAND__bull_only_21",
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
            text = format_progress_text(snap, max_f2=5, show_f1=False)
            self.assertIn("STATS", text)
            self.assertIn("TOP", text)
            self.assertIn("INTC", text)
            self.assertIn("bullish", text.lower())
            # F1 hidden by default
            self.assertNotIn("Train-only", text)
            self.assertNotIn("F1 train-only", text)


if __name__ == "__main__":
    unittest.main()

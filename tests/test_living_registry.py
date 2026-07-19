import tempfile
import unittest
from pathlib import Path

from trader_platform.research.living_registry import (
    LivingRegistry,
    LivingSeat,
    ingest_evaluate_report,
    load_living_registry,
    save_living_registry,
    seat_id_for,
)


class LivingRegistryTest(unittest.TestCase):
    def test_ingest_f2_creates_watchable_seat(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reg.json"
            report = {
                "candidate_id": "C1",
                "family_id": "F1",
                "decision": "STRATEGY_ADVANCED_F2",
                "evaluation_mode": "regime_router",
                "router_policy": "router",
                "living_candidates": [
                    {
                        "candidate_id": "C1_BAC",
                        "symbol": "BAC",
                        "funnel_stage": "F2_UNTOUCHED_HOLDOUT",
                    }
                ],
            }
            reg = ingest_evaluate_report(report, registry_path=path, spec_path="/s.json")
            self.assertEqual(len(reg.watchable_seats()), 1)
            self.assertEqual(reg.watchable_seats()[0].status, "f2_holdout")
            reloaded = load_living_registry(path)
            self.assertEqual(reloaded.watchable_seats()[0].seat_id, "C1_BAC")

    def test_family_closed_quarantines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reg.json"
            reg = LivingRegistry()
            reg.upsert(
                LivingSeat(
                    seat_id=seat_id_for("C", "KO"),
                    candidate_id="C",
                    family_id="FAM",
                    status="f1_train",
                    symbols=["KO"],
                )
            )
            save_living_registry(reg, path)
            ingest_evaluate_report(
                {
                    "candidate_id": "C",
                    "family_id": "FAM",
                    "decision": "FAMILY_CLOSED",
                    "symbols": ["KO"],
                },
                registry_path=path,
            )
            reloaded = load_living_registry(path)
            self.assertTrue(all(s.status == "quarantined" for s in reloaded.seats))


if __name__ == "__main__":
    unittest.main()

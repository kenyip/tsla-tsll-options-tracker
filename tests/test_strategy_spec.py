import json
import tempfile
import unittest
from pathlib import Path

from trader_platform.research.strategy_spec import (
    load_strategy_spec,
    save_strategy_spec,
    strategy_spec_from_mapping,
)


class StrategySpecTest(unittest.TestCase):
    def test_regime_router_spec_validates_and_builds_configs(self):
        raw = {
            "candidate_id": "TEST_ROUTER",
            "family_id": "TEST_FAMILY",
            "evaluation_mode": "regime_router",
            "forecast_type": "regime_directed",
            "economic_mechanism": "test mechanism",
            "symbols": ["SPY", "QQQ"],
            "management": {"long_dte": 21, "profit_target": 0.5},
            "structure_overrides": {"iron_condor": {"iv_rank_min": 20.0}},
        }
        spec = strategy_spec_from_mapping(raw)
        self.assertIsNone(spec.structure)
        configs = spec.router_configs()
        self.assertIn("put_credit_spread", configs)
        self.assertEqual(configs["put_credit_spread"]["long_dte"], 21)
        self.assertEqual(configs["iron_condor"]["iv_rank_min"], 20.0)

    def test_single_structure_requires_structure(self):
        with self.assertRaises(ValueError):
            strategy_spec_from_mapping(
                {
                    "candidate_id": "X",
                    "family_id": "Y",
                    "evaluation_mode": "single_structure",
                    "forecast_type": "non_collapse",
                    "economic_mechanism": "m",
                    "symbols": ["BAC"],
                }
            )

    def test_round_trip_json(self):
        spec = strategy_spec_from_mapping(
            {
                "candidate_id": "PCS_TEST",
                "family_id": "FAM",
                "evaluation_mode": "single_structure",
                "structure": "put_credit_spread",
                "forecast_type": "non_collapse",
                "economic_mechanism": "theta on mild bull",
                "symbols": ["BAC", "KO"],
                "management": {"profit_target": 0.5, "long_dte": 21},
                "entry": {"entry_signal_lag_bars": 1},
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            save_strategy_spec(spec, path)
            loaded = load_strategy_spec(path)
            self.assertEqual(loaded.candidate_id, "PCS_TEST")
            self.assertEqual(loaded.structure, "put_credit_spread")
            self.assertEqual(loaded.single_config()["profit_target"], 0.5)
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw["evaluation_mode"], "single_structure")

    def test_repo_regime_router_spec_loads(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "configs/strategy_specs/regime_router_income_v1.json"
        )
        spec = load_strategy_spec(path)
        self.assertEqual(spec.evaluation_mode, "regime_router")
        self.assertEqual(spec.candidate_id, "REGIME_ROUTER_INCOME_21D_PT50_V1")
        self.assertTrue(spec.discovery_gates.require_control_beat)

    def test_repo_45d_and_pcs_non_bear_specs_load(self):
        root = Path(__file__).resolve().parents[1] / "configs/strategy_specs"
        longer = load_strategy_spec(root / "regime_router_income_45d_v1.json")
        pcs_only = load_strategy_spec(root / "pcs_bull_neutral_income_45d_v1.json")
        self.assertEqual(longer.management["long_dte"], 45)
        self.assertEqual(longer.router_policy, "router")
        self.assertEqual(pcs_only.router_policy, "pcs_non_bear")
        self.assertEqual(pcs_only.management["long_dte"], 45)


if __name__ == "__main__":
    unittest.main()

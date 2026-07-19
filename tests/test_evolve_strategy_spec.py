import unittest

from trader_platform.research.evolve_strategy_spec import DEFAULT_MUTANTS, apply_mutant
from trader_platform.research.strategy_spec import strategy_spec_from_mapping


class EvolveStrategySpecTest(unittest.TestCase):
    def test_apply_mutant_changes_id_and_management(self):
        seed = strategy_spec_from_mapping(
            {
                "candidate_id": "SEED",
                "family_id": "FAM",
                "evaluation_mode": "regime_router",
                "router_policy": "router",
                "forecast_type": "regime",
                "economic_mechanism": "m",
                "symbols": ["BAC", "KO"],
                "management": {"long_dte": 21, "profit_target": 0.5},
            }
        )
        plan = DEFAULT_MUTANTS[0]
        mutant = apply_mutant(seed, plan)
        self.assertTrue(mutant.candidate_id.startswith("SEED__"))
        self.assertEqual(mutant.management["long_dte"], plan.management_patch["long_dte"])
        self.assertNotEqual(mutant.family_id, seed.family_id)

    def test_pcs_non_bear_mutant_sets_policy(self):
        seed = strategy_spec_from_mapping(
            {
                "candidate_id": "SEED",
                "family_id": "FAM",
                "evaluation_mode": "regime_router",
                "forecast_type": "regime",
                "economic_mechanism": "m",
                "symbols": ["BAC"],
                "management": {"long_dte": 21},
            }
        )
        plan = [p for p in DEFAULT_MUTANTS if p.router_policy == "pcs_non_bear"][0]
        mutant = apply_mutant(seed, plan)
        self.assertEqual(mutant.router_policy, "pcs_non_bear")


if __name__ == "__main__":
    unittest.main()

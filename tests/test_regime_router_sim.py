import unittest
from typing import cast
from unittest.mock import patch

import pandas as pd

from trader_platform.research.pcs_sim import PcsTrade
from trader_platform.research.regime_router_sim import (
    default_structure_configs,
    diagnose_entry_rejection,
    run_regime_router_backtest,
    select_structure,
)


class RegimeRouterSimTest(unittest.TestCase):
    def _bars(self, regimes: list[str]) -> pd.DataFrame:
        dates = pd.date_range("2026-01-02", periods=len(regimes), freq="B")
        return pd.DataFrame(
            {
                "close": [20.0] * len(regimes),
                "iv_proxy": [0.5] * len(regimes),
                "iv_rank": [30.0] * len(regimes),
                "regime": regimes,
            },
            index=dates,
        )

    def _fake_entry(self, row, spot, today, cfg, *, structure, **kwargs):
        right = {
            "put_credit_spread": "put",
            "call_credit_spread": "call",
            "iron_condor": "iron_condor",
        }[structure]
        return PcsTrade(
            entry_date=today,
            expiration=today + pd.Timedelta(days=30),
            short_strike=18.0,
            long_strike=17.0,
            width=1.0,
            net_credit=0.25,
            dte_at_entry=30,
            iv_at_entry=0.5,
            regime_at_entry=str(row["regime"]),
            short_delta_entry=0.2,
            max_loss_per_share=0.75,
            right=right,
            call_short_strike=22.0 if right == "iron_condor" else 0.0,
            call_long_strike=23.0 if right == "iron_condor" else 0.0,
            call_width=1.0 if right == "iron_condor" else 0.0,
        )

    def test_routes_current_regime_and_stands_aside_on_unknown_or_low_iv_neutral(self):
        configs = default_structure_configs()
        self.assertEqual(select_structure(pd.Series({"regime": "bullish"}), configs), "put_credit_spread")
        self.assertEqual(select_structure(pd.Series({"regime": "bearish"}), configs), "call_credit_spread")
        self.assertEqual(
            select_structure(pd.Series({"regime": "neutral", "iv_rank": 30.0}), configs),
            "iron_condor",
        )
        self.assertIsNone(select_structure(pd.Series({"regime": "neutral", "iv_rank": 10.0}), configs))
        self.assertIsNone(select_structure(pd.Series({"regime": "unknown", "iv_rank": 99.0}), configs))

    def test_shared_loop_defers_reentry_and_keeps_routing_population_pure(self):
        bars = self._bars(["bullish", "bullish", "bearish", "bearish", "neutral", "neutral"])
        configs = {
            structure: {"dte_stop": 100, "regime_flip_exit_enabled": False}
            for structure in ("put_credit_spread", "call_credit_spread", "iron_condor")
        }
        with patch(
            "trader_platform.research.regime_router_sim.pick_structure_entry",
            side_effect=self._fake_entry,
        ):
            result = run_regime_router_backtest("TEST", df=bars, configs=configs, min_bars=1)

        self.assertEqual([trade.right for trade in result.trades], ["put", "call", "iron_condor"])
        self.assertEqual(result.metrics["same_bar_reentries"], 0)
        self.assertTrue(result.metrics["population_pure"])
        self.assertEqual(result.metrics["routing_violations"], 0)
        self.assertEqual(
            result.entry_funnel["selected"],
            {"put_credit_spread": 1, "call_credit_spread": 1, "iron_condor": 1},
        )
        self.assertEqual(result.entry_funnel["accepted"], result.entry_funnel["selected"])
        for previous, following in zip(result.trades, result.trades[1:]):
            self.assertNotEqual(previous.exit_date, following.entry_date)

    def test_future_regime_changes_do_not_change_prior_entries(self):
        base = self._bars(["bullish", "bullish", "bearish", "bearish", "neutral", "neutral", "bullish", "bullish"])
        changed = base.copy()
        changed.loc[changed.index[6]:, "regime"] = "bearish"
        configs = {
            structure: {"dte_stop": 100, "regime_flip_exit_enabled": False}
            for structure in ("put_credit_spread", "call_credit_spread", "iron_condor")
        }
        with patch(
            "trader_platform.research.regime_router_sim.pick_structure_entry",
            side_effect=self._fake_entry,
        ):
            first = run_regime_router_backtest("TEST", df=base, configs=configs, min_bars=1)
            second = run_regime_router_backtest("TEST", df=changed, configs=configs, min_bars=1)

        cutoff = base.index[6]
        first_prior = [(trade.entry_date, trade.right) for trade in first.trades if trade.entry_date < cutoff]
        second_prior = [(trade.entry_date, trade.right) for trade in second.trades if trade.entry_date < cutoff]
        self.assertEqual(first_prior, second_prior)

    def test_rejection_funnel_uses_counterfactual_filter_and_reconciles(self):
        bars = self._bars(["bearish"])
        bars.loc[:, "iv_rank"] = 0.0

        def reject_until_iv_relaxed(row, spot, today, cfg, *, structure):
            if float(cfg.get("iv_rank_min", 0.0)) == 0.0:
                return self._fake_entry(row, spot, today, cfg, structure=structure)
            return None

        with patch(
            "trader_platform.research.regime_router_sim.pick_structure_entry",
            side_effect=reject_until_iv_relaxed,
        ):
            result = run_regime_router_backtest(
                "TEST",
                df=bars,
                configs={"call_credit_spread": {"iv_rank_min": 15.0}},
                min_bars=1,
            )

        funnel = result.entry_funnel
        self.assertEqual(funnel["selected"]["call_credit_spread"], 1)
        self.assertEqual(funnel["accepted"]["call_credit_spread"], 0)
        self.assertEqual(
            funnel["reject_reasons"]["call_credit_spread"],
            {"iv_rank_below_min": 1},
        )
        selected = sum(funnel["selected"].values())
        accepted = sum(funnel["accepted"].values())
        rejected = sum(funnel["rejected"].values())
        self.assertEqual(selected, accepted + rejected)
        for structure, rejected_count in funnel["rejected"].items():
            self.assertEqual(
                rejected_count,
                sum(funnel["reject_reasons"][structure].values()),
            )

    def test_multiple_blockers_stay_conservatively_composite(self):
        row = pd.Series({"iv_proxy": 0.5, "iv_rank": 0.0, "regime": "bearish"})

        def require_two_relaxations(row, spot, today, cfg, *, structure):
            if float(cfg.get("iv_rank_min", 0.0)) == 0.0 and float(cfg.get("min_credit_pct", 0.0)) == 0.0:
                return self._fake_entry(row, spot, today, cfg, structure=structure)
            return None

        with patch(
            "trader_platform.research.regime_router_sim.pick_structure_entry",
            side_effect=require_two_relaxations,
        ):
            reason = diagnose_entry_rejection(
                row,
                20.0,
                cast(pd.Timestamp, pd.Timestamp("2026-01-02")),
                {
                    **default_structure_configs()["call_credit_spread"],
                    "iv_rank_min": 15.0,
                    "min_credit_pct": 0.2,
                },
                structure="call_credit_spread",
            )

        self.assertEqual(reason, "contract_strike_or_nonpositive_credit")

    def test_invalid_iv_is_not_misclassified_as_a_tunable_filter(self):
        row = pd.Series({"iv_proxy": 0.0, "iv_rank": 99.0, "regime": "bearish"})
        reason = diagnose_entry_rejection(
            row,
            20.0,
            cast(pd.Timestamp, pd.Timestamp("2026-01-02")),
            default_structure_configs()["call_credit_spread"],
            structure="call_credit_spread",
        )
        self.assertEqual(reason, "invalid_iv")


if __name__ == "__main__":
    unittest.main()

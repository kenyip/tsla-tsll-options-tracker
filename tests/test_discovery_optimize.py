"""Wave A discovery optimization: bag size, densify, tiers."""

from __future__ import annotations

from trader_platform.research.discovery_loop import (
    all_grid_mutants,
    densify_neighbors,
    load_grid_config,
    list_seed_specs,
)
from trader_platform.research.discovery_universe import prove_symbols, screen_symbols
from trader_platform.research.evolve_strategy_spec import MutantPlan


def test_wave_a_bag_is_bounded() -> None:
    cfg = load_grid_config()
    assert cfg.get("wave") == "A_screen"
    plans = all_grid_mutants()
    # curated waves + combinatorial; combinatorial alone should be ~1.3k
    assert 500 < len(plans) < 5000
    primary = cfg.get("primary_seeds") or []
    seeds = list_seed_specs()
    if primary:
        n_seeds = len([p for p in seeds if p.name in set(primary)]) or len(seeds)
    else:
        n_seeds = len(seeds)
    bag = len(plans) * n_seeds
    assert bag < 15_000, f"bag too large: {bag}"


def test_densify_neighbors_unique() -> None:
    base = MutantPlan(
        suffix="g_d21_pt50_dl18_iv25_c8_w1_pcs_bu",
        management_patch={
            "long_dte": 21,
            "dte_stop": 7,
            "profit_target": 0.5,
            "long_target_delta": 0.18,
            "iv_rank_min": 25.0,
            "min_credit_pct": 0.08,
            "spread_width": 1.0,
        },
        router_policy="pcs_bull_only",
        notes="test",
    )
    nbs = densify_neighbors(base)
    assert 4 <= len(nbs) <= 12
    suffixes = [n.suffix for n in nbs]
    assert len(suffixes) == len(set(suffixes))
    assert all(s.startswith("dn_") for s in suffixes)


def test_symbol_tiers() -> None:
    core = screen_symbols()
    prove = prove_symbols()
    assert core
    assert set(core).issubset(set(prove)) or set(core) == set(prove)
    # growth names should appear in prove, not necessarily screen
    assert "KO" in core or "INTC" in core

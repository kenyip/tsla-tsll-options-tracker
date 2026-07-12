#!/usr/bin/env python3
"""Paper-only put credit spread DNA grid for $3k sleeve. Never places orders."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.evolve_tick import assert_ship_bar, sim_dna  # noqa: E402
from trader_platform.strategy_dna import STRUCTURE_CATALOG, dna_from_structure, mutate_dna  # noqa: E402


def main() -> int:
    assert "put_credit_spread" in STRUCTURE_CATALOG
    assert_ship_bar()
    print("catalog+ship_bar OK")

    seeds = []
    for width in (1.0, 1.5, 2.0, 3.0):
        for delta in (0.15, 0.20, 0.25):
            for dte in (7, 14, 21):
                for min_c in (0.15, 0.22):
                    seeds.append(
                        dna_from_structure(
                            "put_credit_spread",
                            ["TSLL"],
                            config_overrides={
                                "spread_width": width,
                                "long_target_delta": delta,
                                "long_dte": dte,
                                "min_credit_pct": min_c,
                                "max_loss_budget_usd": 300.0,
                                "profit_target": 0.50,
                                "defined_loss_exit_frac": 0.85,
                            },
                        )
                    )
    rng = random.Random(42)
    base = dna_from_structure("put_credit_spread", ["TSLL"])
    for _ in range(6):
        seeds.append(mutate_dna(base, rng=rng, n_knobs=3))

    print(f"population={len(seeds)}")
    dump = _REPO / ".cache/platform/pcs_evolve"
    results = []
    for i, dna in enumerate(seeds):
        v = sim_dna(dna, period="2y", use_cache=True, dump_dir=dump)
        cap = (dna.last_sim or {}).get("capital") or {}
        results.append(
            {
                "i": i,
                "dna_id": dna.ensure_id(),
                "verdict": v.verdict,
                "score": round(float(v.score), 2),
                "n": v.n_trades,
                "pnl": round(float(dna.last_sim.get("pnl_per_contract") or 0), 2),
                "dd": round(float(dna.last_sim.get("max_dd_per_contract") or 0), 2),
                "wr": round(float(dna.last_sim.get("win_rate") or 0) * 100, 1),
                "pf": round(float(dna.last_sim.get("profit_factor") or 0), 3),
                "width": dna.config.get("spread_width"),
                "delta": dna.config.get("long_target_delta"),
                "dte": dna.config.get("long_dte"),
                "min_c": dna.config.get("min_credit_pct"),
                "max_loss_usd": cap.get("max_loss_usd"),
                "capital_fit": cap.get("capital_fit"),
                "fits_open_risk": cap.get("fits_open_risk_budget"),
                "reason": v.reason,
                "config": dict(dna.config),
            }
        )
        if (i + 1) % 15 == 0:
            print(f"  simmed {i + 1}/{len(seeds)}")

    results.sort(key=lambda r: (r["verdict"] == "SHIP", r["score"]), reverse=True)
    print("\nTOP 12:")
    for r in results[:12]:
        print(
            f"  {r['verdict']:16} score={r['score']:8.1f} n={r['n']:3} pnl={r['pnl']:8.1f} "
            f"dd={r['dd']:6.1f} wr={r['wr']:5.1f} w={r['width']} d={r['delta']} "
            f"dte={r['dte']} ml={r['max_loss_usd']} fit={r['capital_fit']}"
        )

    ship = [
        r
        for r in results
        if r["verdict"] == "SHIP"
        and r.get("fits_open_risk")
        and (r.get("max_loss_usd") or 999) <= 300
    ]
    print(f"\nSHIP+capital envelope: {len(ship)}")
    for r in ship[:10]:
        print(
            f"  {r['dna_id']} score={r['score']} n={r['n']} ml={r['max_loss_usd']} "
            f"w={r['width']} dte={r['dte']} delta={r['delta']}"
        )

    out = _REPO / ".cache/platform/pcs_grid_2y.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"results": results, "ship_fit": ship}, indent=2, default=str))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

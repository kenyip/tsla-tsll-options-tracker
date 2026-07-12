#!/usr/bin/env python3
"""5y stress for SHIP+capital-fit PCS DNA from pcs_grid_2y.json. Paper only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.evolve_tick import sim_dna  # noqa: E402
from trader_platform.strategy_dna import dna_from_structure  # noqa: E402


def main() -> int:
    grid_path = _REPO / ".cache/platform/pcs_grid_2y.json"
    grid = json.loads(grid_path.read_text())
    ship = grid.get("ship_fit") or []
    print(f"stressing {len(ship)} ship+fit on 5y")
    out = []
    for r in ship:
        cfg = r["config"]
        dna = dna_from_structure("put_credit_spread", ["TSLL"], config_overrides=cfg)
        v2 = sim_dna(dna, period="2y", use_cache=True)
        dna2 = dna  # last_sim overwritten by next call — capture first
        m2 = dict(dna2.last_sim or {})
        v5 = sim_dna(dna, period="5y", use_cache=True)
        m5 = dict(dna.last_sim or {})
        cap = m5.get("capital") or m2.get("capital") or {}
        row = {
            "dna_id": dna.ensure_id(),
            "config": cfg,
            "2y": {
                "verdict": v2.verdict,
                "score": round(float(v2.score), 2),
                "n": v2.n_trades,
                "pnl": round(float(m2.get("pnl_per_contract") or 0), 2),
                "dd": round(float(m2.get("max_dd_per_contract") or 0), 2),
                "wr": round(float(m2.get("win_rate") or 0) * 100, 1),
                "pf": round(float(m2.get("profit_factor") or 0), 3),
                "max_loss_usd": (m2.get("capital") or {}).get("max_loss_usd"),
            },
            "5y": {
                "verdict": v5.verdict,
                "score": round(float(v5.score), 2),
                "n": v5.n_trades,
                "pnl": round(float(m5.get("pnl_per_contract") or 0), 2),
                "dd": round(float(m5.get("max_dd_per_contract") or 0), 2),
                "wr": round(float(m5.get("win_rate") or 0) * 100, 1),
                "pf": round(float(m5.get("profit_factor") or 0), 3),
                "max_loss_usd": (m5.get("capital") or {}).get("max_loss_usd"),
            },
            "capital": cap,
        }
        out.append(row)
        c = cfg
        print(
            f"w={c.get('spread_width')} dte={c.get('long_dte')} d={c.get('long_target_delta')} | "
            f"2y {row['2y']['verdict']} n={row['2y']['n']} pnl={row['2y']['pnl']} dd={row['2y']['dd']} | "
            f"5y {row['5y']['verdict']} n={row['5y']['n']} pnl={row['5y']['pnl']} dd={row['5y']['dd']} "
            f"ml={cap.get('max_loss_usd')}"
        )

    path = _REPO / ".cache/platform/pcs_stress_5y.json"
    path.write_text(json.dumps(out, indent=2, default=str))
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

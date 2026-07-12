#!/usr/bin/env python3
"""Register top defined-risk PCS DNA as testing candidates (paper-side only)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.evolve_tick import hyp_id_for_dna, sim_dna  # noqa: E402
from trader_platform.hypothesis_registry import HypothesisRegistry  # noqa: E402
from trader_platform.strategy_dna import dna_from_structure  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    stress = json.loads((_REPO / ".cache/platform/pcs_stress_5y.json").read_text())
    # Prefer: lower max_loss, denser 5y, still SHIP both periods
    ranked = []
    for row in stress:
        if row["2y"]["verdict"] != "SHIP" or row["5y"]["verdict"] != "SHIP":
            continue
        cap = row.get("capital") or {}
        ml = float(cap.get("max_loss_usd") or row["5y"].get("max_loss_usd") or 999)
        if ml > 300 or not cap.get("fits_open_risk_budget", True):
            continue
        # rank: 5y score, then density, then lower max loss
        ranked.append((float(row["5y"]["score"]), float(row["5y"]["n"]), -ml, row))
    ranked.sort(reverse=True)

    # pick diversified top: best score, best density/small-ml, best dd proxy
    picks = []
    seen_keys = set()
    for _, __, ___, row in ranked:
        c = row["config"]
        key = (round(float(c.get("spread_width") or 0), 2), int(c.get("long_dte") or 0), round(float(c.get("long_target_delta") or 0), 3))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        picks.append(row)
        if len(picks) >= 3:
            break

    reg = HypothesisRegistry()
    store = reg.load()
    by_id = {h.get("id"): h for h in store.get("hypotheses") or []}
    registered = []

    for row in picks:
        cfg = row["config"]
        dna = dna_from_structure("put_credit_spread", ["TSLL"], config_overrides=cfg)
        # refresh last_sim with 2y then attach stress
        v2 = sim_dna(dna, period="2y", use_cache=True)
        m2 = dict(dna.last_sim or {})
        v5 = sim_dna(dna, period="5y", use_cache=True)
        m5 = dict(dna.last_sim or {})
        cap = m5.get("capital") or m2.get("capital") or {}
        dna.last_sim = m5
        dna.last_sim["stress"] = {
            "period_2y": {
                "verdict": v2.verdict,
                "score": round(float(v2.score), 2),
                "n": v2.n_trades,
                "pnl": round(float(m2.get("pnl_per_contract") or 0), 2),
                "dd": round(float(m2.get("max_dd_per_contract") or 0), 2),
                "wr": round(float(m2.get("win_rate") or 0) * 100, 1),
                "pf": round(float(m2.get("profit_factor") or 0), 3),
            },
            "period_5y": {
                "verdict": v5.verdict,
                "score": round(float(v5.score), 2),
                "n": v5.n_trades,
                "pnl": round(float(m5.get("pnl_per_contract") or 0), 2),
                "dd": round(float(m5.get("max_dd_per_contract") or 0), 2),
                "wr": round(float(m5.get("win_rate") or 0) * 100, 1),
                "pf": round(float(m5.get("profit_factor") or 0), 3),
            },
            "stressed_at": _now(),
            "judgment": (
                f"defined-risk PCS; 2y {v2.verdict} n={v2.n_trades}; "
                f"5y {v5.verdict} n={v5.n_trades}; max_loss_usd={cap.get('max_loss_usd')}"
            ),
        }
        # Keep 2y as primary ship evidence in last_sim headline when denser period differs
        dna.last_sim["period"] = "5y"
        dna.last_sim["verdict"] = v5.verdict
        dna.last_sim["score"] = float(v5.score)

        hid = hyp_id_for_dna(dna)
        thesis = dna.thesis_text()
        evidence = [
            f"evolve_sim:{dna.ensure_id()}:verdict={v2.verdict}:score={round(v2.score,2)}:trades={v2.n_trades}:period=2y",
            f"stress_5y:verdict={v5.verdict}:n={v5.n_trades}:score={round(v5.score,2)}:dd={round(float(m5.get('max_dd_per_contract') or 0),2)}",
            f"capital_fit:{cap.get('capital_fit')}:max_loss_usd={cap.get('max_loss_usd')}:max_lots={cap.get('max_lots')}",
            "sim_engine=pcs_sim defined_risk",
            str(_REPO / ".cache/platform/pcs_stress_5y.json"),
            str(_REPO / ".cache/platform/pcs_grid_2y.json"),
        ]
        notes = (
            f"source=build_wake_pcs; structure=put_credit_spread; never_auto_live=true; "
            f"capital_fit={cap.get('capital_fit')}; capital_fit_usd={cap.get('capital_fit_usd')}; "
            f"max_lots={cap.get('max_lots')}; max_loss_usd={cap.get('max_loss_usd')}; "
            f"fits_open_risk={cap.get('fits_open_risk_budget')}"
        )
        payload = {
            "id": hid,
            "name": f"DNA:put_credit_spread TSLL w={cfg.get('spread_width')} dte={cfg.get('long_dte')}",
            "thesis": thesis,
            "sleeve": "premium",
            "instruments": ["TSLL"],
            "entry_logic_ref": f"pcs_sim.pick_pcs_entry+dna:{dna.ensure_id()}",
            "exit_logic_ref": f"pcs_sim.check_pcs_exit+dna:{dna.ensure_id()}",
            "status": "testing",
            "evidence_links": evidence,
            "null_results": [],
            "created": _now(),
            "updated": _now(),
            "notes": notes,
            "dna": dna.to_dict(),
            "capital_fit_usd": cap.get("capital_fit_usd"),
            "max_lots": cap.get("max_lots"),
            "capital_fit": cap.get("capital_fit"),
            "max_loss_usd": cap.get("max_loss_usd"),
            "capital": {
                "structure": "put_credit_spread",
                "sleeve_usd": 3000,
                "open_risk_budget_usd": 750,
                "max_loss_budget_usd": cfg.get("max_loss_budget_usd", 300),
                "max_loss_usd": cap.get("max_loss_usd"),
                "capital_fit_usd": cap.get("capital_fit_usd"),
                "capital_fit": cap.get("capital_fit"),
                "max_lots": cap.get("max_lots"),
                "fits_open_risk_budget": cap.get("fits_open_risk_budget"),
                "note": "defined_risk_bp_proxy=max_loss_usd (not cash CSP)",
            },
        }

        if hid in by_id:
            # merge update
            old = by_id[hid]
            payload["created"] = old.get("created") or payload["created"]
            payload["status"] = old.get("status") if old.get("status") in ("testing", "candidate", "paper") else "testing"
            # never bump to shadow/live
            if payload["status"] in ("shadow", "live"):
                payload["status"] = "testing"
            by_id[hid] = payload
            print(f"updated {hid} status={payload['status']} ml={cap.get('max_loss_usd')}")
        else:
            by_id[hid] = payload
            print(f"added {hid} status=testing ml={cap.get('max_loss_usd')} 5y={v5.verdict} n={v5.n_trades}")
        registered.append(
            {
                "id": hid,
                "dna_id": dna.ensure_id(),
                "max_loss_usd": cap.get("max_loss_usd"),
                "2y": payload["dna"]["last_sim"]["stress"]["period_2y"],
                "5y": payload["dna"]["last_sim"]["stress"]["period_5y"],
                "config": {
                    "spread_width": cfg.get("spread_width"),
                    "long_dte": cfg.get("long_dte"),
                    "long_target_delta": cfg.get("long_target_delta"),
                    "min_credit_pct": cfg.get("min_credit_pct"),
                },
            }
        )

    # rewrite store preserving order, append new at end
    existing_ids = [h.get("id") for h in store.get("hypotheses") or []]
    new_hyps = []
    for hid in existing_ids:
        if hid in by_id:
            new_hyps.append(by_id.pop(hid))
    for hid, h in by_id.items():
        new_hyps.append(h)
    store["hypotheses"] = new_hyps
    reg.save(store)

    summary = _REPO / ".cache/platform/pcs_registered.json"
    summary.write_text(json.dumps({"registered": registered, "at": _now()}, indent=2))
    print(f"wrote {summary}; registry hyps={len(new_hyps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

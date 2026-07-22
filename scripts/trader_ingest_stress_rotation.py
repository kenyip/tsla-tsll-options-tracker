#!/usr/bin/env python3
"""Append B3/B4 outcomes into the stress-rotation ledger + refresh QUALITY_SHORTLIST.

Used by continuum coach and (optionally) quality residual after stress.
Never touches live/arm. Does not rewrite hypotheses.yaml (worker owns that).
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
_LEDGER = _REPO / "reports" / "bootstrap" / "STRESS_ROTATION.json"
_SHORTLIST = _REPO / "reports" / "bootstrap" / "QUALITY_SHORTLIST.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def ingest_pair(regime_path: Path, cost_path: Path, *, source: str = "coach") -> dict[str, Any]:
    reg = json.loads(regime_path.read_text(encoding="utf-8"))
    cost = json.loads(cost_path.read_text(encoding="utf-8"))
    cost_by = {r.get("hyp_id"): r for r in (cost.get("results") or [])}
    # also summaries list shape
    if not cost_by and cost.get("summaries"):
        for s in cost["summaries"]:
            hid = s.get("hyp") or s.get("hyp_id")
            if hid:
                cost_by[hid] = {"hyp_id": hid, "summary": s}

    ledger = _load_json(_LEDGER)
    by_id: dict[str, Any] = dict(ledger.get("by_hyp_id") or {})
    stamp = Path(regime_path).stem

    rows_out: list[dict[str, Any]] = []
    for r in reg.get("results") or []:
        hid = r.get("hyp_id")
        if not hid:
            continue
        s = r.get("summary") or {}
        fh = r.get("full_history") or {}
        c = cost_by.get(hid) or {}
        cs = c.get("summary") or {}
        if not cs and c:
            # flatten
            cs = {
                "baseline_verdict": c.get("baseline_verdict"),
                "baseline_pnl": c.get("baseline_pnl"),
                "slip_5_verdict": c.get("slip_5_verdict"),
                "slip_5_pnl": c.get("slip_5_pnl"),
                "cost_hold": c.get("cost_hold"),
                "note": c.get("note"),
            }
            # try by_slip
            if cs.get("cost_hold") is None:
                for slip_row in c.get("by_slip") or []:
                    if abs(float(slip_row.get("slippage_pct") or -1) - 0.05) < 1e-9:
                        cs["slip_5_verdict"] = slip_row.get("verdict")
                        cs["slip_5_pnl"] = slip_row.get("pnl")
                        cs["slip_5_dd"] = slip_row.get("dd")
                        cs["slip_5_n"] = slip_row.get("n_trades")
                # cost_hold from preferred summary in parent
        # recover cost_hold from sibling summaries if needed
        if cs.get("cost_hold") is None:
            for srow in cost.get("summaries") or []:
                if (srow.get("hyp") or srow.get("hyp_id")) == hid:
                    cs = {**cs, **srow}
                    break

        b3 = bool(s.get("regime_hold"))
        b4 = bool(cs.get("cost_hold")) if cs.get("cost_hold") is not None else None
        slip5_v = cs.get("slip_5_verdict")
        slip5_pnl = cs.get("slip_5_pnl")
        # Hard quality rejects
        reject_reason = None
        if not b3:
            reject_reason = f"B3 hold=false dense_neg={s.get('n_negative_n_ge_3')} dd={s.get('max_dd_across_windows')}"
        elif b4 is False:
            reject_reason = f"B4 cost_hold=false slip5={slip5_v} pnl={slip5_pnl}"
        elif slip5_v == "NULL" and (slip5_pnl is not None and float(slip5_pnl) < 0):
            # soft cost_hold can still be soft_loss — treat as fragile for capital path
            reject_reason = f"B4 slip5 NULL/neg pnl={slip5_pnl} (soft cost only)"
        elif int(s.get("n_negative_n_ge_3") or 0) >= 4 and float(s.get("max_dd_across_windows") or 0) > 200:
            reject_reason = (
                f"risk profile worse than leader bar: dense_neg={s.get('n_negative_n_ge_3')} "
                f"dd={s.get('max_dd_across_windows')}"
            )

        entry = {
            "hyp_id": hid,
            "symbol": r.get("symbol"),
            "structure": r.get("structure"),
            "stressed_at": _now(),
            "source": source,
            "regime_path": str(regime_path),
            "cost_path": str(cost_path),
            "b3_hold": b3,
            "dense_neg_ge3": s.get("n_negative_n_ge_3"),
            "max_dd": s.get("max_dd_across_windows"),
            "worst_window_pnl": s.get("worst_window_pnl"),
            "full_pnl": fh.get("pnl"),
            "full_n": fh.get("n_trades"),
            "full_verdict": fh.get("verdict"),
            "max_loss_usd": fh.get("max_loss_usd"),
            "b4_cost_hold": b4,
            "b4_slip5_verdict": slip5_v,
            "b4_slip5_pnl": slip5_pnl,
            "b4_note": cs.get("note"),
            "reject_reason": reject_reason,
            "capital_path_ok": reject_reason is None and b3 and b4 is not False,
        }
        by_id[hid] = entry
        rows_out.append(entry)

    ledger = {
        "generated_at": _now(),
        "schema_version": 1,
        "note": "Rotation ledger for quality-cycle B3/B4 — prevents re-stress thrash; not TOP_HYP.",
        "last_ingest": {
            "source": source,
            "stamp": stamp,
            "regime_path": str(regime_path),
            "cost_path": str(cost_path),
            "n": len(rows_out),
        },
        "by_hyp_id": by_id,
    }
    _LEDGER.parent.mkdir(parents=True, exist_ok=True)
    _LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"ledger_path": str(_LEDGER), "rows": rows_out, "n_ledger": len(by_id)}


def refresh_shortlist_from_ledger() -> dict[str, Any]:
    ledger = _load_json(_LEDGER)
    by_id = dict(ledger.get("by_hyp_id") or {})
    prev = _load_json(_SHORTLIST)

    # Rank capital-path-ok multi-leg by risk profile (BAC-style bar)
    def rank_key(e: dict[str, Any]) -> tuple:
        # lower dense_neg, lower max_dd, higher slip5 pnl, higher full pnl
        dense = int(e.get("dense_neg_ge3") or 99)
        dd = float(e.get("max_dd") or 1e9)
        slip = float(e.get("b4_slip5_pnl") or -1e9)
        pnl = float(e.get("full_pnl") or -1e9)
        return (-int(bool(e.get("capital_path_ok"))), dense, dd, -slip, -pnl)

    multi = [
        e
        for e in by_id.values()
        if e.get("structure") in ("put_credit_spread", "call_credit_spread", "iron_condor")
    ]
    multi_sorted = sorted(multi, key=rank_key)

    shortlist: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = list(prev.get("rejected_tonight") or [])
    seen_reject = {r.get("hyp_id") for r in rejected}

    # Keep MCP-native rows from previous shortlist (CSP/wheel) — not restressed here
    mcp_prev = [
        r
        for r in (prev.get("shortlist") or [])
        if r.get("lane") == "mcp_native_live_candidate_path"
        or r.get("structure")
        in ("cash_secured_put", "wheel_assignment", "short_put_credit")
    ]

    for i, e in enumerate(multi_sorted):
        hid = e["hyp_id"]
        if e.get("reject_reason") or not e.get("capital_path_ok"):
            if hid not in seen_reject:
                rejected.append({"hyp_id": hid, "reason": e.get("reject_reason") or "failed quality bar"})
                seen_reject.add(hid)
            continue
        # stress_priority: top 2 capital-path ok
        shortlist.append(
            {
                "hyp_id": hid,
                "structure": e.get("structure"),
                "symbol": e.get("symbol"),
                "status": "testing" if i < 2 else "candidate",
                "lane": "paper_research",
                "stress_priority": i < 2,
                "b3_hold": e.get("b3_hold"),
                "dense_neg_ge3": e.get("dense_neg_ge3"),
                "full_pnl": e.get("full_pnl"),
                "max_dd": e.get("max_dd"),
                "max_loss_usd_approx": e.get("max_loss_usd"),
                "b4_cost_hold": e.get("b4_cost_hold"),
                "b4_note": f"{e.get('b4_slip5_verdict')}@5pct pnl~{e.get('b4_slip5_pnl')} {e.get('b4_note') or ''}".strip(),
                "why": (
                    "Best risk profile among rotated B3/B4"
                    if i == 0
                    else "Rotated stress survivor; secondary to tighter-DD leader"
                ),
                "caveat": "Proxy BS + B3/B4 only. Multi-leg not MCP placeable. Not pack multi-symbol quality_pass.",
                "stress_source": e.get("source"),
                "stressed_at": e.get("stressed_at"),
            }
        )
        if len(shortlist) >= 6:
            break

    # Prefer known paper leaders BAC/PLTR if still on shortlist — ensure paper campaign symbols stay first if equal
    # Append MCP toys (capped)
    for r in mcp_prev[:3]:
        if not any(x.get("hyp_id") == r.get("hyp_id") for x in shortlist):
            shortlist.append(r)

    out = {
        "generated_at": _now(),
        "phase": "BUILD_PAPER_SEARCH",
        "authority": "research_paper_only",
        "honesty": (
            "Proxy BS sims + B3/B4 only. Not TOP_HYP. Multi-leg not MCP-live. "
            "Stress rotation ledger drives shortlist; quality_cycle mixes leaders+fresh."
        ),
        "agentic": prev.get("agentic")
        or {
            "cash_usd": 500,
            "option_level": 2,
            "type": "cash",
            "mcp_place": "single_leg_only",
        },
        "shortlist": shortlist,
        "rejected_tonight": rejected[-40:],
        "densify_pack": prev.get("densify_pack")
        or {"quality_pass": False, "note": "plumbing only"},
        "stress_rotation_ledger": str(_LEDGER),
        "capital_note_500": prev.get("capital_note_500")
        or "CSP ATM rarely fits $500 cash; $3k at LIVE_PACKET.",
        "next": [
            "Manage open paper campaign (BAC/PLTR) through multi-session B6",
            "Quality cycles now rotate unstressed multi-leg SHIPs into B3/B4",
            "Do not arm multi-leg; MCP lane remains CSP sized to cash",
            "No densify bag thrash",
        ],
    }
    _SHORTLIST.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return {"shortlist_path": str(_SHORTLIST), "n_shortlist": len(shortlist), "n_rejected": len(rejected)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--regime", required=True, type=Path)
    ap.add_argument("--cost", required=True, type=Path)
    ap.add_argument("--source", default="coach")
    ap.add_argument("--refresh-shortlist", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = ingest_pair(args.regime, args.cost, source=args.source)
    if args.refresh_shortlist:
        res["shortlist"] = refresh_shortlist_from_ledger()
    if args.json:
        print(json.dumps(res, indent=2, sort_keys=True))
    else:
        print(f"ledger n={res['n_ledger']} wrote {res['ledger_path']}")
        if "shortlist" in res:
            print(f"shortlist n={res['shortlist']['n_shortlist']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

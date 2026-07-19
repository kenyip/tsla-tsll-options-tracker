#!/usr/bin/env python3
"""Paper residual loop for Desk B starter seats (Trader ops).

Does NOT place live orders. Dry handoff by default; optional plumbing smoke.
Writes reports/bootstrap/paper_loop_LATEST.json for wake residue.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.living_registry import load_living_registry
from trader_platform.research.opportunity_watcher import watch_once, write_watch_result
from trader_platform.research.paper_handoff import run_paper_handoff, run_paper_plumbing_smoke

_OUT = _REPO / "reports" / "bootstrap" / "paper_loop_LATEST.json"
_WATCH = _REPO / ".cache" / "platform" / "spine" / "watcher_LATEST.json"
_HANDOFF = _REPO / ".cache" / "platform" / "spine" / "paper_handoff_LATEST.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Desk B paper residual loop")
    p.add_argument(
        "--execute-paper",
        action="store_true",
        help="Allow paper ledger mutate when seat is paper_eligible (still no live)",
    )
    p.add_argument(
        "--plumbing-smoke",
        action="store_true",
        help="Also run forced plumbing smoke (ledger path check)",
    )
    args = p.parse_args(argv)

    reg = load_living_registry()
    paper_seats = [
        {
            "seat_id": s.seat_id,
            "candidate_id": s.candidate_id,
            "symbols": list(s.symbols or []),
            "status": s.status,
            "funnel_stage": s.funnel_stage,
        }
        for s in reg.seats
        if s.status == "paper_eligible"
    ]

    watch = watch_once()
    write_watch_result(watch, _WATCH)

    handoff = run_paper_handoff(execute_paper=bool(args.execute_paper))
    hd = handoff.to_dict() if hasattr(handoff, "to_dict") else dict(handoff)
    _HANDOFF.parent.mkdir(parents=True, exist_ok=True)
    _HANDOFF.write_text(json.dumps(hd, indent=2, sort_keys=True, default=str) + "\n")

    smoke = None
    if args.plumbing_smoke:
        smoke_res = run_paper_plumbing_smoke()
        smoke = smoke_res.to_dict() if hasattr(smoke_res, "to_dict") else smoke_res

    report = {
        "generated_at": _now(),
        "mode": "paper_loop",
        "phase": "PAPER",
        "n_paper_eligible": len(paper_seats),
        "paper_eligible_seats": paper_seats[:20],
        "watch": watch.to_dict() if hasattr(watch, "to_dict") else {},
        "handoff": {
            "status": hd.get("status"),
            "reason": hd.get("reason"),
            "watch_status": hd.get("watch_status"),
            "paper_action": hd.get("paper_action"),
            "paper_order_id": hd.get("paper_order_id"),
            "risk": hd.get("risk"),
            "intent_symbol": (hd.get("intent") or {}).get("symbol"),
            "intent_structure": (hd.get("intent") or {}).get("structure"),
            "intent_max_loss_usd": (hd.get("intent") or {}).get("max_loss_usd"),
        },
        "plumbing_smoke": smoke,
        "execute_paper": bool(args.execute_paper),
        "trading_authority": False,
        "live_authority": False,
        "next_ops": [
            "Stand-aside is success when watch is NO_SETUP",
            "Dry handoff PAPER_INTENT_READY = plumbing green without mutate",
            "Use --execute-paper only when deliberately exercising paper ledger",
            "Never agentic_live without Ken arm",
        ],
        "doctrine": "docs/TRADER_BUILD.md",
        "handoff_doc": "reports/bootstrap/ENGINE_PROVE_HANDOFF.md",
    }
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")

    print(json.dumps(report, indent=2, default=str))
    print(f"\n# wrote {_OUT}", file=sys.stderr)
    # Exit 0 even on stand-aside — ops success
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

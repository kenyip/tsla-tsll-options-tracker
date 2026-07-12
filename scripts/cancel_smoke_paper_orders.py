#!/usr/bin/env python3
"""One-shot: cancel m0_stub/smoke_test working paper orders. Paper ledger only."""
from __future__ import annotations

import json
from pathlib import Path

from trader_platform.execution.broker_adapter import PaperBroker
from trader_platform.paper_filters import is_smoke_stub_order, is_smoke_stub_tag


def main() -> int:
    pb = PaperBroker()
    p = Path(".cache/platform/paper_ledger.json")
    data = json.loads(p.read_text())
    orders = data.get("orders") or {}
    canceled = []
    for oid, raw in list(orders.items()):
        if raw.get("status") != "working":
            continue
        if is_smoke_stub_order(raw) or is_smoke_stub_tag(str(raw.get("tag") or "")):
            r = pb.cancel(oid)
            canceled.append({"order_id": oid, "ok": r.ok, "message": r.message})
    snap = pb.portfolio_snapshot() if hasattr(pb, "portfolio_snapshot") else None
    data2 = json.loads(p.read_text())
    working = [o for o in (data2.get("orders") or {}).values() if o.get("status") == "working"]
    print(json.dumps({"canceled_smoke": canceled, "portfolio": snap, "working_left": len(working)}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

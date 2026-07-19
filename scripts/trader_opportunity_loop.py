#!/usr/bin/env python3
"""Patient opportunity loop — watch market + paper handoff only (no discovery).

Use when living strategies exist or you want RTH/setup monitoring without
burning CPU on simulations.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.living_registry import DEFAULT_REGISTRY_PATH  # noqa: E402
from trader_platform.research.opportunity_watcher import watch_once, write_watch_result  # noqa: E402
from trader_platform.research.paper_handoff import run_paper_handoff, write_handoff_result  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY_PATH))
    p.add_argument("--execute-paper", action="store_true")
    p.add_argument(
        "--out-dir",
        default=str(_REPO / ".cache/platform/spine/opportunity"),
    )
    args = p.parse_args(argv)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    watch = watch_once(registry_path=args.registry)
    write_watch_result(watch, out / "watcher_LATEST.json")
    write_watch_result(
        watch, _REPO / ".cache/platform/spine/watcher_LATEST.json"
    )
    handoff = run_paper_handoff(
        watch=watch,
        registry_path=args.registry,
        execute_paper=bool(args.execute_paper),
        dry_run=not bool(args.execute_paper),
    )
    write_handoff_result(handoff, out / "paper_handoff_LATEST.json")
    write_handoff_result(
        handoff, _REPO / ".cache/platform/spine/paper_handoff_LATEST.json"
    )

    if watch.status == "NO_QUALIFIED_STRATEGY":
        bottom = "no_strategy"
    elif watch.status == "NO_SETUP":
        bottom = "waiting_for_setup"
    elif handoff.status in {"PAPER_INTENT_READY", "PAPER_PLACED"}:
        bottom = "opportunity"
    else:
        bottom = handoff.status.lower()

    print(
        json.dumps(
            {
                "bottom_line": bottom,
                "watch": watch.status,
                "handoff": handoff.status,
                "reason": handoff.reason or watch.reason,
                "seat_id": watch.seat_id,
                "symbol": watch.symbol,
                "trading_authority": False,
            },
            indent=2,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

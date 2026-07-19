#!/usr/bin/env python3
"""Desk B opportunity watcher CLI — patient; never places orders."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.living_registry import (  # noqa: E402
    DEFAULT_REGISTRY_PATH,
    load_living_registry,
    summary_lines,
)
from trader_platform.research.opportunity_watcher import (  # noqa: E402
    watch_once,
    write_watch_result,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY_PATH),
        help="Living registry JSON path",
    )
    parser.add_argument("--symbol", default="", help="Optional single-symbol override")
    parser.add_argument(
        "--out",
        default=str(_REPO / ".cache/platform/spine/watcher_LATEST.json"),
    )
    parser.add_argument(
        "--allow-live-packet",
        action="store_true",
        help="Emit GATED_LIVE_PACKET draft when setup exists (still no authority)",
    )
    args = parser.parse_args(argv)

    reg = load_living_registry(args.registry)
    result = watch_once(
        registry=reg,
        symbol_override=args.symbol or None,
        allow_live_packet=bool(args.allow_live_packet),
    )
    out = write_watch_result(result, args.out)
    print(
        json.dumps(
            {
                "status": result.status,
                "reason": result.reason,
                "living_watchable_count": result.living_watchable_count,
                "seat_id": result.seat_id,
                "symbol": result.symbol,
                "regime": result.regime,
                "selected_structure": result.selected_structure,
                "trading_authority": result.trading_authority,
                "out": str(out),
                "registry": summary_lines(reg),
            },
            indent=2,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

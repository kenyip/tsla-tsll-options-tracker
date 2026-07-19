#!/usr/bin/env python3
"""Easy discovery progress: stats + top strategies that passed."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.living_registry import DEFAULT_REGISTRY_PATH  # noqa: E402
from trader_platform.research.progress_dashboard import (  # noqa: E402
    collect_progress,
    format_progress_text,
)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY_PATH))
    p.add_argument("--json", action="store_true", help="Machine-readable snapshot")
    p.add_argument(
        "--watch",
        type=float,
        nargs="?",
        const=5.0,
        default=None,
        help="Refresh every N seconds (default 5 if flag present)",
    )
    p.add_argument(
        "--full",
        action="store_true",
        help="Longer lists (all F2 + F1 samples)",
    )
    p.add_argument(
        "--top",
        type=int,
        default=5,
        help="How many holdout-pass strategies to show (default 5)",
    )
    p.add_argument(
        "--show-f1",
        action="store_true",
        help="Also list a few train-only F1 candidates",
    )
    args = p.parse_args(argv)

    def once() -> None:
        snap = collect_progress(registry_path=args.registry)
        if args.json:
            print(json.dumps(snap.to_dict(), indent=2, sort_keys=True, allow_nan=False))
            return
        text = format_progress_text(
            snap,
            show_f1=bool(args.show_f1 or args.full),
            max_f2=50 if args.full else max(1, int(args.top)),
            max_f1=20 if args.full else (8 if args.show_f1 else 0),
            full=bool(args.full),
        )
        if args.watch is not None:
            sys.stdout.write("\033[2J\033[H")
        sys.stdout.write(text)
        sys.stdout.flush()

    if args.watch is None:
        once()
        return 0

    interval = max(1.0, float(args.watch))
    try:
        while True:
            once()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n(stopped)", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

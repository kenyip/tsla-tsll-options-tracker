#!/usr/bin/env python3
"""Capture or validate an announcement-time-aware dividend event archive."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.dividend_event_archive import (  # noqa: E402
    load_dividend_event_archive,
    snapshot_nasdaq_dividend_history,
    summarize_dividend_event_archive,
    write_dividend_event_archive,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--snapshot", help="Nasdaq-listed symbol to capture")
    group.add_argument("--input", help="Existing normalized JSON archive to validate")
    parser.add_argument("--out", help="JSON output path required by --snapshot")
    parser.add_argument("--summary-out", help="Optional JSON summary path")
    args = parser.parse_args(argv)

    if args.snapshot:
        if not args.out:
            parser.error("--snapshot requires --out")
        archive = snapshot_nasdaq_dividend_history(args.snapshot)
        write_dividend_event_archive(args.out, archive)
        archive = load_dividend_event_archive(args.out)
    else:
        archive = load_dividend_event_archive(args.input)

    summary = summarize_dividend_event_archive(archive)
    if args.summary_out:
        target = Path(args.summary_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

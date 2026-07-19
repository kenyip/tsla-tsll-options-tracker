#!/usr/bin/env python3
"""Manage Desk B discovery universe (add / remove / list / promote).

Examples:
  just trader-universe
  just trader-universe list --status active
  just trader-universe add TSLA --tags ai_growth,high_vol,liquid
  just trader-universe demote SOFI --notes "no F1 after 2k evals"
  just trader-universe activate RKLB
  just trader-universe remove F --hard
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.discovery_universe import (  # noqa: E402
    VALID_STATUS,
    active_symbols,
    add_symbol,
    list_symbols,
    remove_symbol,
    set_status,
    summary,
)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--path", default="", help="Override universe JSON path")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("summary", help="Counts by status (default)")

    pl = sub.add_parser("list", help="List symbols")
    pl.add_argument("--status", default="", choices=["", *sorted(VALID_STATUS)])
    pl.add_argument("--json", action="store_true")

    pa = sub.add_parser("add", help="Add or update a symbol")
    pa.add_argument("symbol")
    pa.add_argument("--status", default="active", choices=sorted(VALID_STATUS))
    pa.add_argument("--tags", default="", help="Comma tags e.g. ai_growth,high_vol")
    pa.add_argument("--notes", default="")

    pd = sub.add_parser("demote", help="Soft-remove (status=demoted)")
    pd.add_argument("symbol")
    pd.add_argument("--notes", default="")

    pb = sub.add_parser("ban", help="Never use")
    pb.add_argument("symbol")
    pb.add_argument("--notes", default="")

    pw = sub.add_parser("watch", help="Park on watchlist (not evaluated)")
    pw.add_argument("symbol")
    pw.add_argument("--notes", default="")

    pp = sub.add_parser("activate", help="Set status=active")
    pp.add_argument("symbol")
    pp.add_argument("--notes", default="")

    pr = sub.add_parser("remove", help="Demote (default) or hard-delete")
    pr.add_argument("symbol")
    pr.add_argument("--hard", action="store_true", help="Delete entry entirely")

    pa2 = sub.add_parser("active", help="Print active list only")
    pa2.add_argument("--tags", default="", help="Comma tags filter (OR)")

    args = p.parse_args(argv)
    path = args.path or None
    cmd = args.cmd or "summary"

    if cmd == "summary":
        print(json.dumps(summary(path), indent=2))
        return 0

    if cmd == "list":
        rows = list_symbols(path, status=args.status or None)
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            for r in rows:
                tags = ",".join(r["tags"]) if r["tags"] else "-"
                notes = (r["notes"] or "")[:60]
                print(f"{r['symbol']:8} {r['status']:8} [{tags}]  {notes}")
        return 0

    if cmd == "active":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] or None
        print(json.dumps(active_symbols(path, tags=tags), indent=2))
        return 0

    if cmd == "add":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        print(
            json.dumps(
                add_symbol(
                    args.symbol,
                    status=args.status,
                    tags=tags,
                    notes=args.notes,
                    path=path,
                ),
                indent=2,
            )
        )
        return 0

    if cmd == "demote":
        print(
            json.dumps(
                set_status(args.symbol, "demoted", notes=args.notes or None, path=path),
                indent=2,
            )
        )
        return 0

    if cmd == "ban":
        print(
            json.dumps(
                set_status(args.symbol, "banned", notes=args.notes or None, path=path),
                indent=2,
            )
        )
        return 0

    if cmd == "watch":
        print(
            json.dumps(
                set_status(args.symbol, "watch", notes=args.notes or None, path=path),
                indent=2,
            )
        )
        return 0

    if cmd == "activate":
        print(
            json.dumps(
                set_status(args.symbol, "active", notes=args.notes or None, path=path),
                indent=2,
            )
        )
        return 0

    if cmd == "remove":
        print(json.dumps(remove_symbol(args.symbol, hard=args.hard, path=path), indent=2))
        return 0

    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

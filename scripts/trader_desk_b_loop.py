#!/usr/bin/env python3
"""Desk B scheduled loop CLI: evolve → living → watch → paper handoff."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.desk_b_loop import run_desk_b_loop  # noqa: E402
from trader_platform.research.living_registry import DEFAULT_REGISTRY_PATH  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seed",
        default=str(
            _REPO / "configs/strategy_specs/pcs_iv_rich_noncollapse_21d_v1.json"
        ),
    )
    parser.add_argument("--max-mutants", type=int, default=2)
    parser.add_argument("--symbols", default="", help="Optional comma symbol override")
    parser.add_argument("--skip-evolve", action="store_true")
    parser.add_argument(
        "--train-only",
        action="store_true",
        help="Faster evolve screen without holdout (no F2 this tick)",
    )
    parser.add_argument(
        "--execute-paper",
        action="store_true",
        help="Allow paper ledger mutate only for paper_eligible seats",
    )
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY_PATH))
    parser.add_argument(
        "--out-dir",
        default=str(_REPO / ".cache/platform/spine/desk_b_loop"),
    )
    parser.add_argument(
        "--quiet-if-searching",
        action="store_true",
        help="Print compact one-liner when bottom_line is searching/waiting",
    )
    args = parser.parse_args(argv)

    symbols = (
        [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
        if args.symbols.strip()
        else None
    )
    report = run_desk_b_loop(
        seed_spec=args.seed,
        max_mutants=args.max_mutants,
        symbols=symbols,
        skip_evolve=args.skip_evolve,
        execute_paper=args.execute_paper,
        train_only=args.train_only,
        registry_path=args.registry,
        out_dir=args.out_dir,
    )
    bottom = report.get("bottom_line")
    if args.quiet_if_searching and bottom in {"searching", "waiting"}:
        print(
            json.dumps(
                {
                    "bottom_line": bottom,
                    "watch": (report.get("watch") or {}).get("status"),
                    "living_watchable": (report.get("living") or {}).get("watchable"),
                    "latest_path": report.get("latest_path"),
                },
                allow_nan=False,
            )
        )
    else:
        print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

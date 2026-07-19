#!/usr/bin/env python3
"""Multi-symbol re-prove densify DNA (kill single-name luck)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.bootstrap import (
    DEFAULT_MULTI_SYMBOL_BOOK,
    run_multi_symbol_pack,
)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Multi-symbol dual-cost re-prove")
    p.add_argument(
        "--symbols",
        default=",".join(DEFAULT_MULTI_SYMBOL_BOOK),
        help="Comma-separated symbols to test each DNA on",
    )
    p.add_argument("--report", default=None)
    args = p.parse_args(argv)
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    report = run_multi_symbol_pack(symbols=symbols, report_path=args.report)
    print(
        json.dumps(
            {
                "n_dna": report.get("n_dna"),
                "n_quality_pass": report.get("n_quality_pass"),
                "n_multi_f2": report.get("n_multi_f2"),
                "report_path": report.get("report_path"),
                "results": [
                    {
                        "candidate_id": r.get("candidate_id"),
                        "f2_symbols": r.get("f2_symbols"),
                        "thick_f2_symbols": r.get("thick_f2_symbols"),
                        "multi_symbol_f2": r.get("multi_symbol_f2"),
                        "quality_pass": r.get("quality_pass"),
                        "per_symbol": [
                            {
                                "symbol": x.get("symbol"),
                                "decision": x.get("decision"),
                                "f2": x.get("f2"),
                                "n_trades": x.get("n_trades_holdout_worst_axis"),
                                "thick": x.get("thick_enough"),
                            }
                            for x in (r.get("per_symbol") or [])
                        ],
                    }
                    for r in (report.get("results") or [])
                ],
                "honesty": report.get("honesty"),
            },
            indent=2,
        )
    )
    # quality_pass count is research outcome — do not fail CI solely on 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

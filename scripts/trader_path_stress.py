#!/usr/bin/env python3
"""Staged market-path stress for Desk B StrategySpec.

Examples:
  just trader-path-stress --spec configs/strategy_specs/pcs_bull_neutral_income_45d_v1.json --symbols BAC --quick-only
  just trader-path-stress --spec path/to/mutant.json --symbols AMZN
  just trader-path-stress --spec path/to/mutant.json --symbols IWM --force-full
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.path_stress import path_stress_from_spec_path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Desk B staged path stress (quick → full)")
    p.add_argument("--spec", required=True, help="StrategySpec JSON path")
    p.add_argument(
        "--symbols",
        default="",
        help="Comma-separated symbols (default: first symbol on the spec)",
    )
    p.add_argument(
        "--quick-only",
        action="store_true",
        help="Run quick pack only (do not promote to full suite)",
    )
    p.add_argument(
        "--force-full",
        action="store_true",
        help="Always run full suite after quick (even if quick fails)",
    )
    p.add_argument("--report", default=None, help="Output report path")
    args = p.parse_args(argv)

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()] or None
    report = path_stress_from_spec_path(
        args.spec,
        symbols=symbols,
        quick_only=args.quick_only,
        force_full=args.force_full,
        report_path=args.report,
    )

    # Compact human summary
    quick = report.get("quick") or {}
    full = report.get("full")
    print(
        json.dumps(
            {
                "candidate_id": report.get("candidate_id"),
                "symbols": report.get("symbols"),
                "staged_pass": report.get("staged_pass"),
                "stage_note": report.get("stage_note"),
                "full_ran": report.get("full_ran"),
                "quick_pass": quick.get("pack_pass"),
                "quick_n_fail": quick.get("n_fail"),
                "quick_n_available": quick.get("n_available"),
                "full_pass": None if full is None else full.get("pack_pass"),
                "full_n_fail": None if full is None else full.get("n_fail"),
                "report_path": report.get("report_path"),
                "honesty": report.get("honesty"),
            },
            indent=2,
        )
    )

    # Per-regime lines for management prep
    def _print_pack(name: str, pack: dict | None) -> None:
        if not pack:
            return
        print(f"\n# {name} pack_pass={pack.get('pack_pass')}")
        for row in pack.get("rows") or []:
            sim = row.get("sim") or {}
            flag = "PASS" if row.get("pass") else "FAIL"
            if not row.get("available"):
                flag = "SKIP"
            used = row.get("used_regime") or row.get("regime")
            label = str(row.get("regime") or "")
            if used and used != row.get("regime"):
                label = f"{row.get('regime')}→{used}"
            print(
                f"  [{flag}] {row.get('symbol')} {label:22} "
                f"n={sim.get('n_trades', '-')} pnl={sim.get('pnl', '-')} "
                f"dd={sim.get('dd', '-')} exit={sim.get('dominant_exit', '-') or '-'} "
                f"{','.join(row.get('issues') or [])}"
            )

    _print_pack("quick", quick)
    _print_pack("full", full)
    return 0 if report.get("staged_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())

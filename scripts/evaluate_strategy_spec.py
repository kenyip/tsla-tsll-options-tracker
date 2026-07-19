#!/usr/bin/env python3
"""Evaluate a frozen StrategySpec through the shared proxy spine.

Research only. Dual-cost train → sealed holdout for train survivors.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.evaluate_proxy import (  # noqa: E402
    evaluate_proxy,
    write_living_scoreboard,
)
from trader_platform.research.living_registry import (  # noqa: E402
    DEFAULT_REGISTRY_PATH,
    ingest_evaluate_report,
)
from trader_platform.research.strategy_spec import load_strategy_spec  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Path to StrategySpec JSON")
    parser.add_argument("--out", required=True, help="Write full evaluation report JSON")
    parser.add_argument(
        "--living-out",
        default="",
        help="Optional living scoreboard path (F2+ only)",
    )
    parser.add_argument(
        "--symbols",
        default="",
        help="Optional comma override of spec symbols",
    )
    parser.add_argument("--period", default="", help="Optional period override")
    parser.add_argument("--train-fraction", type=float, default=None)
    parser.add_argument(
        "--no-holdout",
        action="store_true",
        help="Train-only screen (do not run sealed holdout)",
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY_PATH),
        help="Desk B living registry path (updated from evaluation decision)",
    )
    parser.add_argument(
        "--no-registry",
        action="store_true",
        help="Do not ingest result into living registry",
    )
    args = parser.parse_args(argv)

    spec = load_strategy_spec(args.spec)
    symbols = (
        [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
        if args.symbols.strip()
        else None
    )
    report = evaluate_proxy(
        spec,
        symbols=symbols,
        period=args.period or None,
        train_fraction=args.train_fraction,
        run_holdout_on_train_pass=not args.no_holdout,
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")

    living_path = args.living_out.strip()
    if not living_path:
        living_path = str(out.parent / "living_LATEST.json")
    write_living_scoreboard(report, living_path)

    if not args.no_registry:
        ingest_evaluate_report(
            report,
            registry_path=args.registry,
            spec_path=str(Path(args.spec).resolve()),
            report_path=str(out.resolve()),
        )

    summary = {
        "decision": report["decision"],
        "funnel_stage_after": report["funnel_stage_after"],
        "candidate_id": report["candidate_id"],
        "evaluation_mode": report["evaluation_mode"],
        "n_completed": report["n_completed"],
        "n_train_pass": report["n_train_pass"],
        "n_holdout_pass": report["n_holdout_pass"],
        "living_count": len(report.get("living_candidates") or []),
        "living_candidates": report.get("living_candidates") or [],
        "errors": report.get("errors") or [],
        "out": str(out),
        "living_out": living_path,
    }
    # Per-symbol train brief
    summary["train_brief"] = [
        {
            "symbol": row["symbol"],
            "pass": row["train_discovery_pass"],
            "worst_pnl": min(
                float(row["train"][a]["pnl"]) for a in ("slip_5pct", "fixed_0p01")
            ),
            "n": min(int(row["train"][a]["n_trades"]) for a in ("slip_5pct", "fixed_0p01")),
            "stand_aside_frac": min(
                float(row["train"][a].get("stand_aside_frac") or 0.0)
                for a in ("slip_5pct", "fixed_0p01")
            ),
        }
        for row in report.get("train_rows") or []
    ]
    if report.get("holdout_rows"):
        summary["holdout_brief"] = [
            {
                "symbol": row["symbol"],
                "pass": row["holdout_dual_cost_pass"],
                "slip_pnl": row["holdout"]["slip_5pct"]["pnl"],
                "fix_pnl": row["holdout"]["fixed_0p01"]["pnl"],
                "slip_n": row["holdout"]["slip_5pct"]["n_trades"],
                "fix_n": row["holdout"]["fixed_0p01"]["n_trades"],
            }
            for row in report["holdout_rows"]
        ]
    print(json.dumps(summary, indent=2, allow_nan=False))
    return 0 if report.get("ranking_complete") else 1


if __name__ == "__main__":
    raise SystemExit(main())

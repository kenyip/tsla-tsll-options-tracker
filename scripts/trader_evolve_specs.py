#!/usr/bin/env python3
"""Desk B: mutate StrategySpec seeds → evaluate_proxy → living registry."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.evolve_strategy_spec import evolve_from_seed  # noqa: E402
from trader_platform.research.living_registry import DEFAULT_REGISTRY_PATH  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seed",
        default=str(_REPO / "configs/strategy_specs/regime_router_income_v1.json"),
        help="Seed StrategySpec JSON",
    )
    parser.add_argument("--max-mutants", type=int, default=3)
    parser.add_argument(
        "--symbols",
        default="",
        help="Optional comma symbol override (smaller screens)",
    )
    parser.add_argument(
        "--out-dir",
        default=str(_REPO / ".cache/platform/spine/evolve"),
    )
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY_PATH))
    parser.add_argument(
        "--train-only",
        action="store_true",
        help="Skip holdout (faster screen; F2 impossible this run)",
    )
    args = parser.parse_args(argv)

    symbols = (
        [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
        if args.symbols.strip()
        else None
    )
    summary = evolve_from_seed(
        args.seed,
        max_mutants=args.max_mutants,
        symbols=symbols,
        out_dir=args.out_dir,
        registry_path=args.registry,
        run_holdout_on_train_pass=not args.train_only,
    )
    print(json.dumps(summary, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

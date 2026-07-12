#!/usr/bin/env python3
"""Capture or validate option bid/ask observations for cost-model research."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.option_quote_observations import (  # noqa: E402
    load_observations_csv,
    snapshot_yfinance_option_quotes,
    summarize_archive_density,
    summarize_half_spreads,
    write_observations_csv,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="Archived normalized CSV to validate")
    group.add_argument("--snapshot", help="Symbol for one current yfinance chain snapshot")
    parser.add_argument("--expiration", help="YYYY-MM-DD; omit to capture all current expirations")
    parser.add_argument("--out", help="CSV output for --snapshot")
    parser.add_argument("--summary-out", help="Optional JSON path for the emitted summary")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace --out instead of the default idempotent archive append",
    )
    parser.add_argument(
        "--allow-synthetic-fixture",
        action="store_true",
        help="Allow fixture rows for plumbing smoke only; never calibration",
    )
    args = parser.parse_args(argv)

    if args.input:
        rows = load_observations_csv(
            args.input, require_observed=not args.allow_synthetic_fixture
        )
    else:
        if not args.out:
            parser.error("--snapshot requires --out")
        rows = snapshot_yfinance_option_quotes(args.snapshot, args.expiration)
        write_observations_csv(args.out, rows, append=not args.overwrite)
        rows = load_observations_csv(args.out, require_observed=True)
    payload = summarize_half_spreads(rows)
    payload["quote_provenance_eligible"] = payload.pop("calibration_eligible")
    payload["archive_density"] = summarize_archive_density(rows)
    payload["provider_backtest_eligible"] = (
        payload["quote_provenance_eligible"]
        and payload["archive_density"]["provider_backtest_eligible"]
    )
    if args.summary_out:
        summary_target = Path(args.summary_out)
        summary_target.parent.mkdir(parents=True, exist_ok=True)
        summary_target.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Assess an independent explicit AAPL ex-date source against the bounded archive."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
from typing import cast

import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.dividend_event_archive import (  # noqa: E402
    load_dividend_event_archive,
)
from trader_platform.research.dividend_event_crosscheck import (  # noqa: E402
    crosscheck_stockanalysis_ex_dates,
    snapshot_stockanalysis_aapl_dividend_history,
)


def _atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nasdaq-archive", required=True)
    parser.add_argument("--issuer-crosscheck", required=True)
    parser.add_argument("--expected-target-events", type=int, default=40)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    archive = load_dividend_event_archive(args.nasdaq_archive)
    issuer = json.loads(Path(args.issuer_crosscheck).read_text())
    if issuer.get("provider_status") != "partial_issuer_corroboration":
        raise ValueError("issuer cross-check must have bounded partial corroboration")
    if "known_at" not in issuer.get("qualified_fields", []):
        raise ValueError("issuer cross-check does not qualify the target known_at window")
    if "ex_date" not in issuer.get("unqualified_fields", []):
        raise ValueError("issuer cross-check must leave ex_date explicitly unqualified")
    rows = snapshot_stockanalysis_aapl_dividend_history()
    result = crosscheck_stockanalysis_ex_dates(
        archive,
        rows,
        coverage_start=cast(pd.Timestamp, pd.Timestamp(issuer["coverage_start"])),
        coverage_end=cast(pd.Timestamp, pd.Timestamp(issuer["coverage_end"])),
    )
    if result.target_events != args.expected_target_events:
        raise ValueError(
            f"bounded target changed: expected {args.expected_target_events}, "
            f"found {result.target_events}"
        )
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "decision": (
            "QUALIFY_BOUNDED_EX_DATE"
            if result.provider_status == "bounded_ex_date_corroboration"
            else "CLOSE_EX_DATE_ROUTE_INSUFFICIENT_COVERAGE"
        ),
        **result.to_dict(),
    }
    _atomic_write_json(Path(args.out), payload)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

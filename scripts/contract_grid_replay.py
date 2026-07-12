#!/usr/bin/env python3
"""Replay observed archives through the date-aware contract-grid provider."""
from __future__ import annotations

import argparse
import glob
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.contract_grid_provider import (  # noqa: E402
    ArchivedContractGridProvider,
)
from trader_platform.research.option_quote_observations import (  # noqa: E402
    load_observations_csv,
)


def _grid_summary(grid) -> dict:
    if grid is None:
        return {"covered": False, "expirations": 0, "rights": [], "strikes": 0}
    rights = sorted({right for expiration in grid.values() for right in expiration})
    return {
        "covered": True,
        "expirations": len(grid),
        "rights": rights,
        "strikes": sum(len(strikes) for expiration in grid.values() for strikes in expiration.values()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quotes", required=True, help="Glob for normalized observed quote CSVs")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--market-date", required=True, help="Archive market date, YYYY-MM-DD")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    paths = sorted(glob.glob(args.quotes))
    if not paths:
        raise SystemExit(f"no quote archives matched {args.quotes}")
    observations = []
    for path in paths:
        observations.extend(load_observations_csv(path, require_observed=True))

    market_date = date.fromisoformat(args.market_date)
    provider = ArchivedContractGridProvider(observations)
    current = provider(args.symbol, market_date)
    prior = provider(args.symbol, market_date - timedelta(days=1))
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "symbol": args.symbol.upper(),
        "market_date": market_date.isoformat(),
        "quote_paths": paths,
        "n_quote_observations": len(observations),
        "market_date_grid": _grid_summary(current),
        "prior_date_grid": _grid_summary(prior),
        "provider_counters": provider.coverage_counters(),
        "replay_decision": (
            "PASS_COVERED_DATE_FAILS_CLOSED_MISSING_DATE"
            if current is not None and prior is None
            else "FAIL_REPLAY_EXPECTATION"
        ),
    }
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return 0 if payload["replay_decision"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Print Desk B living registry status."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.living_registry import (  # noqa: E402
    DEFAULT_REGISTRY_PATH,
    load_living_registry,
    summary_lines,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    reg = load_living_registry(args.registry)
    if args.json:
        print(json.dumps(reg.to_dict(), indent=2, sort_keys=True, allow_nan=False))
    else:
        print("\n".join(summary_lines(reg)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

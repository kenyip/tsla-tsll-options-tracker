#!/usr/bin/env python3
"""Stress one unregistered PCS/CCS/IC time-grid variant without changing the registry."""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from scripts.pcs_cost_stress import stress_hyp  # noqa: E402
from scripts.pcs_regime_stress import stress_one  # noqa: E402

HYPS_PATH = _REPO / "trader_platform/data/hypotheses.yaml"
_WEEKDAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4}


def _load_variant(args: argparse.Namespace) -> dict:
    store = yaml.safe_load(HYPS_PATH.read_text()) or {}
    by_id = {hyp.get("id"): hyp for hyp in store.get("hypotheses") or []}
    if args.hyp not in by_id:
        raise SystemExit(f"missing hyp {args.hyp}")
    hyp = deepcopy(by_id[args.hyp])
    dna = hyp.get("dna") or {}
    structure = str(dna.get("structure") or "")
    if structure not in {"put_credit_spread", "call_credit_spread", "iron_condor"}:
        raise SystemExit(f"unsupported structure {structure!r}")
    cfg = dna.setdefault("config", {})
    cfg.update(
        long_dte=args.long_dte,
        profit_target=args.profit_target,
        dte_stop=args.dte_stop,
        entry_weekdays=None if args.entry_weekday == "all" else [_WEEKDAYS[args.entry_weekday]],
    )
    if args.spread_width is not None:
        cfg["spread_width"] = args.spread_width
    width_label = f"_w{args.spread_width:g}" if args.spread_width is not None else ""
    hyp["id"] = (
        f"transient_{args.hyp.removeprefix('hyp_dna_')}_"
        f"{args.entry_weekday}_{args.long_dte}d_pt{int(args.profit_target * 100)}_stop{args.dte_stop}"
        f"{width_label}"
    )
    return hyp


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hyp", required=True)
    parser.add_argument("--long-dte", type=int, required=True)
    parser.add_argument("--profit-target", type=float, required=True)
    parser.add_argument("--dte-stop", type=int, required=True)
    parser.add_argument("--entry-weekday", choices=["all", *_WEEKDAYS], default="all")
    parser.add_argument("--spread-width", type=float)
    parser.add_argument("--period", default="5y")
    parser.add_argument("--slips", default="0,0.02,0.05,0.10")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.dte_stop >= args.long_dte:
        raise SystemExit("dte-stop must be less than long-dte")
    if args.spread_width is not None and args.spread_width <= 0:
        raise SystemExit("spread-width must be positive")

    hyp = _load_variant(args)
    symbol = str((hyp["dna"].get("symbols") or ["TSLL"])[0]).upper()
    df = build(symbol, period=args.period, use_cache=True)
    slips = [float(value.strip()) for value in args.slips.split(",") if value.strip()]
    regime = stress_one(hyp, df)
    cost = stress_hyp(hyp, df, slips, args.period)
    payload = {
        "paper_only": True,
        "source_hyp_id": args.hyp,
        "variant_hyp_id": hyp["id"],
        "variant_config": hyp["dna"]["config"],
        "regime": regime,
        "cost": cost,
        "note": "Transient exact-DNA stress only; does not register or promote the variant.",
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = _REPO / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    print(
        json.dumps(
            {
                "out": str(out),
                "variant": hyp["id"],
                "regime": regime["summary"],
                "cost": cost["summary"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

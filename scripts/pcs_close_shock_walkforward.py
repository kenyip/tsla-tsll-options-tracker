#!/usr/bin/env python3
"""Chronological selection/holdout falsifier for the close-shock PCS grid."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from pcs_close_shock_lab import (  # noqa: E402
    MAX_LOSS,
    MAX_WINDOW_DD,
    _config,
    _cost_candidate,
    _modes,
)

HOLDOUT_MIN_TRADES = 4


def _holdout_pass(row: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    for axis in ("slip_5pct", "fixed_0p01"):
        mode = row[axis]
        if mode["n_trades"] < HOLDOUT_MIN_TRADES:
            reasons.append(f"{axis}_n<{HOLDOUT_MIN_TRADES}")
        if mode["pnl"] <= 0:
            reasons.append(f"{axis}_pnl<=0")
        if mode["dd"] > MAX_WINDOW_DD:
            reasons.append(f"{axis}_dd")
        if mode["max_loss_usd"] > MAX_LOSS:
            reasons.append(f"{axis}_max_loss")
        if not mode["ledger_exact"] or mode["same_bar_reentries"] or mode["signal_violations"]:
            reasons.append(f"{axis}_integrity")
    return not reasons, reasons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default="BAC,F,SOFI,PLTR,TSLL,SMCI,AMD,AAPL")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--train-frac", type=float, default=0.60)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if not 0.5 <= args.train_frac <= 0.8:
        raise SystemExit("--train-frac must be between 0.5 and 0.8")

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    grid = list(product((7, 14), (1.0, 2.0), (1.0, 1.5)))
    selections: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    splits: dict[str, Any] = {}
    for symbol in symbols:
        try:
            df = build(symbol, period=args.period, use_cache=True)
            split = int(len(df) * args.train_frac)
            train = df.iloc[:split]
            holdout = df.iloc[split:]
            splits[symbol] = {
                "train_start": str(train.index[0].date()),
                "train_end": str(train.index[-1].date()),
                "holdout_start": str(holdout.index[0].date()),
                "holdout_end": str(holdout.index[-1].date()),
                "train_bars": len(train),
                "holdout_bars": len(holdout),
            }
            train_candidates: list[dict[str, Any]] = []
            for dte, shock_pct, volume_min in grid:
                config = _config(dte=dte, shock_pct=shock_pct, volume_min=volume_min)
                modes = _modes(symbol, train, config)
                if _cost_candidate(modes):
                    train_candidates.append(
                        {
                            "symbol": symbol,
                            "config": {
                                "dte": dte,
                                "intraday_return_max": -shock_pct,
                                "volume_surge_min": volume_min,
                            },
                            **modes,
                        }
                    )
            if not train_candidates:
                print(f"{symbol}: no train candidate", file=sys.stderr)
                continue
            selected = max(
                train_candidates,
                key=lambda row: min(row["slip_5pct"]["pnl"], row["fixed_0p01"]["pnl"]),
            )
            key = selected["config"]
            selected_config = _config(
                dte=int(key["dte"]),
                shock_pct=abs(float(key["intraday_return_max"])),
                volume_min=float(key["volume_surge_min"]),
            )
            holdout_modes = _modes(symbol, holdout, selected_config)
            passed, reasons = _holdout_pass(holdout_modes)
            unconditional = _modes(symbol, holdout, _config(dte=int(key["dte"])))
            mirror = _modes(
                symbol,
                holdout,
                _config(
                    dte=int(key["dte"]),
                    shock_pct=abs(float(key["intraday_return_max"])),
                    volume_min=float(key["volume_surge_min"]),
                    mirror=True,
                ),
            )
            selections.append(
                {
                    "symbol": symbol,
                    "config": key,
                    "n_train_candidates": len(train_candidates),
                    "train": {axis: selected[axis] for axis in ("baseline", "slip_5pct", "fixed_0p01")},
                    "holdout": holdout_modes,
                    "holdout_unconditional": unconditional,
                    "holdout_mirror": mirror,
                    "holdout_pass": passed,
                    "fail_reasons": reasons,
                }
            )
            print(f"{symbol}: selected {key}; holdout_pass={passed}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            errors.append({"symbol": symbol, "error": str(exc)})

    passes = [row for row in selections if row["holdout_pass"]]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD",
        "paper_only": True,
        "sleeve_usd": 3000,
        "method": "select exact DNA only on first 60%; evaluate once on untouched final 40%",
        "claim_scope": "synthetic daily-bar/BS proxy; lagged completed-bar signal; not observed quotes and not L1",
        "gates": {
            "train": "same dual-cost absolute gate as pcs_close_shock_lab",
            "holdout_min_trades_each_cost_axis": HOLDOUT_MIN_TRADES,
            "holdout_positive_each_cost_axis": True,
            "holdout_max_loss_usd": MAX_LOSS,
            "holdout_max_dd": MAX_WINDOW_DD,
            "integrity": "exact ledger, zero same-bar reentry, zero lagged-signal violations",
        },
        "population": symbols,
        "grid_size_per_symbol": len(grid),
        "splits": splits,
        "n_selected": len(selections),
        "n_holdout_pass": len(passes),
        "errors": errors,
        "decision": "WALKFORWARD_PROXY_PASS_REQUIRES_OBSERVED_VALIDATION" if passes else "REJECT_CLOSE_SHOCK_PCS_WALKFORWARD",
        "pass_rows": passes,
        "selections": selections,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("decision", "n_selected", "n_holdout_pass", "errors")}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

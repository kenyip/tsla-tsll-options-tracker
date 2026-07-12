#!/usr/bin/env python3
"""Rolling-origin falsification of one predeclared mild-pullback PCS DNA."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from scripts.pcs_momentum_walkforward_lab import (  # noqa: E402
    COST_AXES,
    MAX_DD,
    MAX_DENSE_NEG,
    MAX_LOSS,
    MIN_TRADES,
    _run,
    run_cost_axes,
    summarize_result,
)
TRAIN_FRACTIONS = (0.4, 0.6, 0.8)
HOLDOUT_CHUNK_BARS = 126


def _pullback_config() -> dict[str, Any]:
    return {
        "structure": "put_credit_spread",
        "long_dte": 7,
        "long_target_delta": 0.20,
        "spread_width": 1.0,
        "min_credit_pct": 0.05,
        "iv_rank_min": 0.0,
        "profit_target": 0.40,
        "defined_loss_exit_frac": 0.70,
        "delta_breach": 0.45,
        "dte_stop": 3,
        "max_loss_budget_usd": MAX_LOSS,
        "regime_flip_exit_enabled": True,
        "entry_signal_lag_bars": 1,
        "entry_ret_1d_max": -0.005,
        "entry_rsi_min": 35.0,
        "entry_rsi_max": 50.0,
    }


def _bullish_mirror(config: dict[str, Any]) -> dict[str, Any]:
    mirror = {key: value for key, value in config.items() if key != "entry_ret_1d_max"}
    mirror.update(
        {
            "entry_ret_1d_min": abs(float(config["entry_ret_1d_max"])),
            "entry_rsi_min": 100.0 - float(config["entry_rsi_max"]),
            "entry_rsi_max": 100.0 - float(config["entry_rsi_min"]),
        }
    )
    return mirror


def _unconditional(config: dict[str, Any]) -> dict[str, Any]:
    row = {key: value for key, value in config.items() if not key.startswith("entry_")}
    row["entry_signal_lag_bars"] = 1
    return row


def _fold_boundaries(
    n_bars: int,
    *,
    train_fractions: tuple[float, ...] = TRAIN_FRACTIONS,
) -> list[tuple[int, int, int]]:
    points = [int(n_bars * fraction) for fraction in train_fractions] + [n_bars]
    return [(0, points[index], points[index + 1]) for index in range(len(train_fractions))]


def _run_pass(row: dict[str, Any]) -> bool:
    return bool(
        row.get("ok", False)
        and int(row["n_trades"]) >= MIN_TRADES
        and float(row.get("gate_pnl", row["pnl"])) > 0.0
        and row["verdict"] == "SHIP"
        and float(row.get("gate_max_loss_usd", row["max_loss_usd"])) <= MAX_LOSS
        and float(row.get("gate_dd", row["dd"])) <= MAX_DD
        and row["integrity"]
    )


def _axis_windows(symbol: str, frame, config: dict[str, Any], axis: str) -> dict[str, Any]:
    cost_config = {**config, **COST_AXES[axis]}
    rows = []
    for index, start in enumerate(range(0, len(frame), HOLDOUT_CHUNK_BARS)):
        window = frame.iloc[start : start + HOLDOUT_CHUNK_BARS]
        if len(window) < 15:
            continue
        row = summarize_result(
            _run(symbol, window, cost_config, f"holdout_{axis}_chunk_{index}"),
            window,
            cost_config,
        )
        rows.append(
            {
                "label": f"chunk_{index}_{window.index[0].date()}_{window.index[-1].date()}",
                **row,
            }
        )
    dense_negative = [
        row
        for row in rows
        if int(row["n_trades"]) >= 3 and float(row.get("gate_pnl", row["pnl"])) < 0.0
    ]
    return {
        "n_windows": len(rows),
        "dense_negative_n": len(dense_negative),
        "dense_negative_labels": [row["label"] for row in dense_negative],
        "window_max_dd": max(
            (float(row.get("gate_dd", row["dd"])) for row in rows),
            default=0.0,
        ),
        "integrity": all(row["integrity"] for row in rows),
        "rows": rows,
    }


def _holdout_windows(symbol: str, frame, config: dict[str, Any]) -> dict[str, Any]:
    return {axis: _axis_windows(symbol, frame, config, axis) for axis in COST_AXES}


def _fold_pass(
    train_axes: dict[str, Any],
    holdout_axes: dict[str, Any],
    windows: dict[str, Any],
) -> bool:
    return bool(
        all(_run_pass(train_axes[axis]) for axis in COST_AXES)
        and all(_run_pass(holdout_axes[axis]) for axis in COST_AXES)
        and all(
            int(windows[axis]["dense_negative_n"]) <= MAX_DENSE_NEG
            and float(windows[axis]["window_max_dd"]) <= MAX_DD
            and windows[axis]["integrity"]
            for axis in COST_AXES
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default="BAC,F,SOFI,PLTR,TSLL,SMCI,AMD,AAPL")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    config = _pullback_config()
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for symbol in symbols:
        try:
            frame = build(symbol, period=args.period, use_cache=True)
            folds = []
            for fold_index, (_, split, end) in enumerate(_fold_boundaries(len(frame))):
                train = frame.iloc[:split]
                holdout = frame.iloc[split:end]
                train_axes = run_cost_axes(symbol, train, config, f"fold_{fold_index}_train")
                holdout_axes = run_cost_axes(symbol, holdout, config, f"fold_{fold_index}_holdout")
                windows = _holdout_windows(symbol, holdout, config)
                passed = _fold_pass(train_axes, holdout_axes, windows)
                folds.append(
                    {
                        "fold": fold_index,
                        "train_start": str(train.index[0].date()),
                        "train_end": str(train.index[-1].date()),
                        "holdout_start": str(holdout.index[0].date()),
                        "holdout_end": str(holdout.index[-1].date()),
                        "train_bars": len(train),
                        "holdout_bars": len(holdout),
                        "train": train_axes,
                        "train_gate_pass": all(_run_pass(train_axes[axis]) for axis in COST_AXES),
                        "holdout": holdout_axes,
                        "holdout_windows": windows,
                        "fold_gate_pass": passed,
                        "controls": {
                            "unconditional": run_cost_axes(
                                symbol,
                                holdout,
                                _unconditional(config),
                                f"fold_{fold_index}_unconditional",
                            ),
                            "bullish_mirror": run_cost_axes(
                                symbol,
                                holdout,
                                _bullish_mirror(config),
                                f"fold_{fold_index}_bullish_mirror",
                            ),
                        },
                    }
                )
                print(
                    f"{symbol} fold={fold_index} train_gate={folds[-1]['train_gate_pass']} "
                    f"fold_pass={passed}",
                    file=sys.stderr,
                )
            rows.append(
                {
                    "symbol": symbol,
                    "bars": len(frame),
                    "n_folds": len(folds),
                    "n_fold_pass": sum(row["fold_gate_pass"] for row in folds),
                    "all_folds_pass": all(row["fold_gate_pass"] for row in folds),
                    "folds": folds,
                }
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"symbol": symbol, "error": str(exc)})

    passes = [row for row in rows if row["all_folds_pass"]]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD",
        "paper_only": True,
        "sleeve_usd": 3000,
        "structure": "put_credit_spread",
        "capital_fit_usd": "per fold/axis; required <=3000",
        "max_loss_usd": "per fold/axis; required <=300",
        "max_lots": "per fold/axis; default posture 1 lot",
        "hypothesis": "a lagged mild bearish pullback (prior return <=-0.5%, RSI 35-50) improves 7-DTE defined-risk PCS entries after both proxy cost axes",
        "falsifier": "no symbol passes every expanding rolling-origin fold with train gate first, untouched holdout positive SHIP on both cost axes, max loss <=300, holdout and chunk DD <=75, dense negatives <=5, and exact integrity",
        "claim_scope": "synthetic listed-Friday/rounded-strike daily-bar Black-Scholes discovery only; no observed quote costs or contract history; cannot earn L1",
        "validity": {
            "selection": "one predeclared DNA; no grid and no holdout-driven selection",
            "rolling_origin": "expanding train endpoints 40/60/80%; following non-overlapping 20% holdouts",
            "train_gate": "required independently before each fold can pass; holdouts still persisted for falsification diagnostics",
            "signal": "return and RSI are read from the prior completed bar; entry purity independently checked",
            "cost_axes": ["5pct adverse leg slip", "$0.01 half-spread per leg at entry and exit"],
            "negative_controls": ["same-DTE unconditional PCS", "exact bullish mirror return>=+0.5%/RSI50-65"],
            "population": symbols,
            "population_pure": "put_credit_spread only",
            "ranking_complete": len(errors) == 0 and len(rows) == len(symbols),
        },
        "gates": {
            "min_trades_each_train_and_holdout_cost_axis": MIN_TRADES,
            "positive_ship_each_cost_axis": True,
            "max_loss_usd": MAX_LOSS,
            "max_dd_usd": MAX_DD,
            "dense_negative_windows_each_cost_axis": MAX_DENSE_NEG,
            "integrity": True,
            "all_folds_required": True,
        },
        "config": {
            "dte": 7,
            "ret_1d_max": -0.005,
            "rsi_min": 35.0,
            "rsi_max": 50.0,
        },
        "n_symbols": len(symbols),
        "n_completed": len(rows),
        "n_all_folds_pass": len(passes),
        "errors": errors,
        "decision": (
            "DISCOVERY_PASS_REQUIRES_OBSERVED_VALIDATION"
            if passes
            else "REJECT_MILD_PULLBACK_PCS_ROLLING_ORIGIN"
        ),
        "pass_rows": passes,
        "rows": rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: payload[key] for key in ("decision", "n_completed", "n_all_folds_pass", "errors")},
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

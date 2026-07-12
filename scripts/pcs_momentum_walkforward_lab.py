#!/usr/bin/env python3
"""Chronological falsification of lagged bullish-momentum PCS entries, paper only."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from trader_platform.evolve_tick import score_sim_metrics  # noqa: E402
from trader_platform.research.pcs_sim import entry_filters_pass, run_pcs_backtest  # noqa: E402

MIN_TRADES = 8
MAX_LOSS = 300.0
MAX_DD = 75.0
MAX_DENSE_NEG = 5
COST_AXES = {
    "slip_5pct": {"slippage_pct": 0.05},
    "fixed_0p01": {"half_spread_per_leg": 0.01},
}


def momentum_config(*, dte: int, ret_min: float, rsi_min: float, rsi_max: float) -> dict[str, Any]:
    return {
        "structure": "put_credit_spread",
        "long_dte": dte,
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
        "entry_ret_1d_min": ret_min,
        "entry_rsi_min": rsi_min,
        "entry_rsi_max": rsi_max,
    }


def _run(symbol: str, frame: pd.DataFrame, config: dict[str, Any], label: str):
    return run_pcs_backtest(
        symbol,
        period=label,
        df=frame,
        min_bars=15,
        config=config,
        structure="put_credit_spread",
        sleeve_usd=3000.0,
        open_risk_budget_usd=750.0,
    )


def summarize_result(result, frame: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    metrics = result.metrics or {}
    n = int(result.n_trades)
    pnl = float(metrics.get("total_pnl_per_contract") or 0.0)
    dd = float(metrics.get("max_dd_per_contract") or 0.0)
    wr = float(metrics.get("win_rate_pct") or 0.0) / 100.0
    verdict, score, reason, finite_pf = score_sim_metrics(
        n_trades=n,
        pnl=pnl,
        win_rate=wr,
        max_dd=dd,
        profit_factor=float(metrics.get("profit_factor") or 0.0),
    )
    ledger = np.array(
        [(trade.net_credit - float(trade.exit_debit or 0.0)) * 100.0 for trade in result.trades],
        dtype=float,
    )
    equity = np.cumsum(ledger)
    peaks = np.maximum.accumulate(equity) if len(equity) else np.array([], dtype=float)
    ledger_dd = float(np.max(peaks - equity)) if len(equity) else 0.0
    same_bar = sum(
        previous.exit_date is not None and previous.exit_date == following.entry_date
        for previous, following in zip(result.trades, result.trades[1:])
    )
    lag = max(int(config.get("entry_signal_lag_bars", 0)), 0)
    signal_violations = 0
    for trade in result.trades:
        if trade.entry_date not in frame.index:
            signal_violations += 1
            continue
        entry_number = cast(int, frame.index.get_loc(trade.entry_date))
        if entry_number < lag or not entry_filters_pass(frame.iloc[entry_number - lag], config):
            signal_violations += 1
    max_loss = max(
        (float(trade.max_loss_per_share) * 100.0 for trade in result.trades),
        default=0.0,
    )
    integrity = (
        abs(float(ledger.sum()) - pnl) < 1e-8
        and abs(ledger_dd - dd) < 1e-8
        and same_bar == 0
        and signal_violations == 0
    )
    return {
        "ok": bool(result.ok and not result.skipped),
        "n_trades": n,
        "pnl": round(pnl, 2),
        "dd": round(dd, 2),
        "gate_pnl": pnl,
        "gate_dd": dd,
        "verdict": verdict,
        "score": round(float(score), 2),
        "reason": reason,
        "profit_factor": round(float(finite_pf), 4) if np.isfinite(float(finite_pf)) else None,
        "max_loss_usd": round(max_loss, 2),
        "gate_max_loss_usd": max_loss,
        "capital_fit_usd": result.capital.get("capital_fit_usd"),
        "max_lots": result.capital.get("max_lots"),
        "ledger_pnl": round(float(ledger.sum()), 2),
        "ledger_dd": round(ledger_dd, 2),
        "same_bar_reentries": same_bar,
        "signal_violations": signal_violations,
        "integrity": integrity,
    }


def run_cost_axes(symbol: str, frame: pd.DataFrame, config: dict[str, Any], label: str) -> dict[str, Any]:
    return {
        axis: summarize_result(_run(symbol, frame, {**config, **cost}, f"{label}_{axis}"), frame, {**config, **cost})
        for axis, cost in COST_AXES.items()
    }


def axis_pass(row: dict[str, Any]) -> bool:
    return (
        row.get("ok", False)
        and row["n_trades"] >= MIN_TRADES
        and float(row.get("gate_pnl", row["pnl"])) > 0
        and row["verdict"] == "SHIP"
        and float(row.get("gate_max_loss_usd", row["max_loss_usd"])) <= MAX_LOSS
        and float(row.get("gate_dd", row["dd"])) <= MAX_DD
        and row["integrity"]
    )


def complete_gate(axes: dict[str, Any], *, dense_negative_n: int = 0) -> bool:
    return all(axis_pass(axes[axis]) for axis in COST_AXES) and dense_negative_n <= MAX_DENSE_NEG


def walkforward_pass(
    train_axes: dict[str, Any],
    holdout_axes: dict[str, Any],
    windows: dict[str, Any],
) -> bool:
    return bool(
        complete_gate(train_axes)
        and complete_gate(holdout_axes, dense_negative_n=int(windows["dense_negative_n"]))
        and float(windows["window_max_dd"]) <= MAX_DD
        and windows["integrity"]
    )


def rank_key(row: dict[str, Any]) -> tuple[Any, ...]:
    axes = row["train"]
    return (
        complete_gate(axes),
        min(float(axes[axis].get("gate_pnl", axes[axis]["pnl"])) for axis in COST_AXES),
        -max(float(axes[axis].get("gate_dd", axes[axis]["dd"])) for axis in COST_AXES),
        min(int(axes[axis]["n_trades"]) for axis in COST_AXES),
    )


def holdout_windows(symbol: str, frame: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    fixed = {**config, **COST_AXES["fixed_0p01"]}
    rows = []
    for index, start in enumerate(range(0, len(frame), 126)):
        window = frame.iloc[start : start + 126]
        if len(window) < 15:
            continue
        rows.append(
            {
                "label": f"holdout_chunk_{index}_{window.index[0].date()}_{window.index[-1].date()}",
                **summarize_result(_run(symbol, window, fixed, f"holdout_chunk_{index}"), window, fixed),
            }
        )
    dense_negative = [
        row
        for row in rows
        if row["n_trades"] >= 3 and float(row.get("gate_pnl", row["pnl"])) < 0
    ]
    return {
        "n_windows": len(rows),
        "dense_negative_n": len(dense_negative),
        "dense_negative_labels": [row["label"] for row in dense_negative],
        "window_max_dd": max(
            (float(row.get("gate_dd", row["dd"])) for row in rows), default=0.0
        ),
        "integrity": all(row["integrity"] for row in rows),
        "rows": rows,
    }


def _mirror_control(config: dict[str, Any]) -> dict[str, Any]:
    threshold = float(config["entry_ret_1d_min"])
    mirror = {key: value for key, value in config.items() if key != "entry_ret_1d_min"}
    mirror.update(
        {
            # Entry filters are inclusive. Step below zero only for the zero-
            # threshold cell so a flat return cannot belong to both families;
            # preserve the exact mirror threshold for nonzero DNA.
            "entry_ret_1d_max": (
                float(np.nextafter(0.0, -np.inf)) if threshold == 0.0 else -threshold
            ),
            "entry_rsi_min": 100.0 - float(config["entry_rsi_max"]),
            "entry_rsi_max": 100.0 - float(config["entry_rsi_min"]),
        }
    )
    return mirror


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default="BAC,F,SOFI,PLTR,TSLL,SMCI,AMD,AAPL")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--train-fraction", type=float, default=0.60)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if not 0.5 <= args.train_fraction <= 0.8:
        parser.error("--train-fraction must be between 0.5 and 0.8")

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    grid = list(product((7, 14), (0.0, 0.005), (50.0, 55.0), (65.0, 75.0)))
    selected: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for symbol in symbols:
        try:
            frame = build(symbol, period=args.period, use_cache=True)
            split_index = int(len(frame) * args.train_fraction)
            train = frame.iloc[:split_index]
            holdout = frame.iloc[split_index:]
            train_rows = []
            for dte, ret_min, rsi_min, rsi_max in grid:
                config = momentum_config(dte=dte, ret_min=ret_min, rsi_min=rsi_min, rsi_max=rsi_max)
                train_rows.append(
                    {
                        "config": {
                            "dte": dte,
                            "ret_1d_min": ret_min,
                            "rsi_min": rsi_min,
                            "rsi_max": rsi_max,
                        },
                        "train": run_cost_axes(symbol, train, config, "train"),
                    }
                )
            winner = max(train_rows, key=rank_key)
            key = winner["config"]
            config = momentum_config(
                dte=int(key["dte"]),
                ret_min=float(key["ret_1d_min"]),
                rsi_min=float(key["rsi_min"]),
                rsi_max=float(key["rsi_max"]),
            )
            holdout_axes = run_cost_axes(symbol, holdout, config, "holdout")
            windows = holdout_windows(symbol, holdout, config)
            holdout_pass = walkforward_pass(winner["train"], holdout_axes, windows)
            unconditional = {key: value for key, value in config.items() if not key.startswith("entry_")}
            unconditional["entry_signal_lag_bars"] = 1
            mirror = _mirror_control(config)
            selected.append(
                {
                    "symbol": symbol,
                    "bars": len(frame),
                    "split_date": str(holdout.index[0].date()),
                    "train_rows": len(train_rows),
                    "selected_config": key,
                    "train": winner["train"],
                    "train_gate_pass": complete_gate(winner["train"]),
                    "holdout": holdout_axes,
                    "holdout_windows": windows,
                    "holdout_gate_pass": holdout_pass,
                    "controls": {
                        "unconditional": run_cost_axes(symbol, holdout, unconditional, "holdout_unconditional"),
                        "bearish_mirror": run_cost_axes(symbol, holdout, mirror, "holdout_bearish_mirror"),
                    },
                }
            )
            print(f"{symbol}: selected={key} holdout_pass={holdout_pass}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            errors.append({"symbol": symbol, "error": str(exc)})

    passes = [row for row in selected if row["holdout_gate_pass"]]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD",
        "paper_only": True,
        "sleeve_usd": 3000,
        "structure": "put_credit_spread",
        "capital_fit_usd": "per selected row; must be <=3000",
        "max_loss_usd": "per selected row; gate <=300",
        "max_lots": "per selected row; default posture remains 1 lot",
        "hypothesis": "a prior completed-bar bullish momentum state improves defined-risk PCS entries after costs versus unconditional and bearish-mirror controls",
        "falsifier": "no train-selected row passes untouched chronological holdout on both cost axes with n>=8, positive SHIP PnL, max_loss<=300, DD<=75, fixed-cost dense_negative_windows<=5, and exact signal/ledger integrity",
        "claim_scope": "synthetic listed-Friday/rounded-strike daily-bar Black-Scholes discovery; signals lagged one bar; no observed option quotes; cannot earn L1",
        "validity": {
            "selection": "grid ranked only on chronological first 60%; exactly one selected DNA per symbol evaluated on untouched final 40%",
            "signal": "ret_1d and RSI from prior completed bar; entry-date purity independently checked",
            "cost_axes": ["5pct adverse leg slip", "$0.01 half-spread per leg at entry and exit"],
            "negative_controls": ["same-DTE unconditional PCS", "bearish momentum mirror"],
            "population": symbols,
            "population_pure": "put_credit_spread only",
            "ranking_complete": len(errors) == 0 and len(selected) == len(symbols),
        },
        "gates": {
            "min_trades_each_cost_axis": MIN_TRADES,
            "positive_ship_each_cost_axis": True,
            "max_loss_usd": MAX_LOSS,
            "max_dd_usd": MAX_DD,
            "dense_negative_windows": MAX_DENSE_NEG,
            "integrity": True,
        },
        "grid_size_per_symbol": len(grid),
        "n_symbols": len(symbols),
        "n_selected": len(selected),
        "n_holdout_pass": len(passes),
        "errors": errors,
        "decision": "DISCOVERY_PASS_REQUIRES_OBSERVED_VALIDATION" if passes else "REJECT_BULLISH_MOMENTUM_PCS_WALKFORWARD",
        "pass_rows": passes,
        "selected_rows": selected,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("decision", "n_selected", "n_holdout_pass", "errors")}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

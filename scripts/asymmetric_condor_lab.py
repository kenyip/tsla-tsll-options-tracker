#!/usr/bin/env python3
"""Falsify a bullish asymmetric iron condor (capped-jade shape), paper only."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from trader_platform.evolve_tick import score_sim_metrics  # noqa: E402
from trader_platform.research.pcs_sim import run_pcs_backtest  # noqa: E402

MIN_TRADES = 8
MAX_LOSS = 300.0
MAX_WINDOW_DD = 75.0
MAX_DENSE_NEG = 5


def _config(
    *,
    dte: int,
    put_delta: float,
    call_delta: float,
    min_credit: float,
    slippage_pct: float = 0.0,
    half_spread_per_leg: float = 0.0,
) -> dict[str, Any]:
    return {
        "structure": "iron_condor",
        "long_dte": dte,
        "put_target_delta": put_delta,
        "call_target_delta": call_delta,
        "put_spread_width": 1.0,
        "call_spread_width": 1.0,
        "put_min_credit_pct": 0.0,
        "call_min_credit_pct": 0.0,
        "min_credit_pct": min_credit,
        "ic_allowed_regimes": ["bullish", "neutral"],
        "iv_rank_min": 0.0,
        "profit_target": 0.40,
        "defined_loss_exit_frac": 0.70,
        "delta_breach": 0.45,
        "dte_stop": 3,
        "max_loss_budget_usd": MAX_LOSS,
        "regime_flip_exit_enabled": True,
        "slippage_pct": slippage_pct,
        "half_spread_per_leg": half_spread_per_leg,
    }


def _run(symbol: str, df: pd.DataFrame, config: dict[str, Any], period: str):
    return run_pcs_backtest(
        symbol,
        period=period,
        df=df,
        min_bars=15,
        config=config,
        structure="iron_condor",
        sleeve_usd=3000.0,
        open_risk_budget_usd=750.0,
    )


def _row(result) -> dict[str, Any]:
    metrics = result.metrics or {}
    n = int(result.n_trades)
    pnl = float(metrics.get("total_pnl_per_contract") or 0.0)
    dd = float(metrics.get("max_dd_per_contract") or 0.0)
    wr = float(metrics.get("win_rate_pct") or 0.0) / 100.0
    pf = float(metrics.get("profit_factor") or 0.0)
    verdict, score, reason, finite_pf = score_sim_metrics(
        n_trades=n, pnl=pnl, win_rate=wr, max_dd=dd, profit_factor=pf
    )
    ledger = np.array(
        [(trade.net_credit - float(trade.exit_debit or 0.0)) * 100.0 for trade in result.trades],
        dtype=float,
    )
    equity = np.cumsum(ledger)
    peaks = np.maximum.accumulate(equity) if len(equity) else np.array([], dtype=float)
    ledger_dd = float(np.max(peaks - equity)) if len(equity) else 0.0
    same_bar = sum(
        1
        for previous, following in zip(result.trades, result.trades[1:])
        if previous.exit_date is not None and previous.exit_date == following.entry_date
    )
    actual_max_loss = max(
        (float(trade.max_loss_per_share) * 100.0 for trade in result.trades), default=0.0
    )
    return {
        "ok": bool(result.ok and not result.skipped),
        "n_trades": n,
        "pnl": round(pnl, 2),
        "dd": round(dd, 2),
        "verdict": verdict,
        "score": round(float(score), 2),
        "reason": reason,
        "profit_factor": round(float(finite_pf), 4) if np.isfinite(float(finite_pf)) else None,
        "max_loss_usd": round(actual_max_loss, 2),
        "capital_fit_usd": result.capital.get("capital_fit_usd"),
        "max_lots": result.capital.get("max_lots"),
        "ledger_pnl": round(float(ledger.sum()), 2),
        "ledger_dd": round(ledger_dd, 2),
        "ledger_exact": abs(float(ledger.sum()) - pnl) < 1e-8 and abs(ledger_dd - dd) < 1e-8,
        "same_bar_reentries": same_bar,
    }


def _windows(symbol: str, df: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    dates = [pd.Timestamp(value) for value in df.index]
    years = [date.year for date in dates]
    windows: list[tuple[str, pd.DataFrame]] = [
        (f"year_{year}", df.loc[[value == year for value in years]])
        for year in sorted(set(years))
    ]
    chunk = 126
    windows.extend(
        (
            f"chunk6m_{index}_{dates[start].date()}_{dates[min(start + chunk - 1, len(df) - 1)].date()}",
            df.iloc[start : start + chunk],
        )
        for index, start in enumerate(range(0, max(0, len(df) - chunk + 1), chunk))
    )
    rows = [
        {"label": label, **_row(_run(symbol, window, config, label))}
        for label, window in windows
        if len(window) >= 15
    ]
    dense_negative = [
        row for row in rows if row["n_trades"] >= 3 and float(row["pnl"]) < 0
    ]
    return {
        "n_windows": len(rows),
        "dense_negative_n": len(dense_negative),
        "dense_negative_labels": [row["label"] for row in dense_negative],
        "window_max_dd": max((float(row["dd"]) for row in rows), default=0.0),
        "worst_window_pnl": min((float(row["pnl"]) for row in rows), default=0.0),
        "ledger_exact": all(row["ledger_exact"] for row in rows),
        "same_bar_reentries": sum(int(row["same_bar_reentries"]) for row in rows),
        "rows": rows,
    }


def _full_gate(row: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    for axis in ("slip_5pct", "fixed_0p01"):
        mode = row[axis]
        if mode["n_trades"] < MIN_TRADES:
            reasons.append(f"{axis}_n<{MIN_TRADES}")
        if mode["pnl"] <= 0:
            reasons.append(f"{axis}_pnl<=0")
        if mode["verdict"] != "SHIP":
            reasons.append(f"{axis}_{mode['verdict']}")
        if not mode["ledger_exact"]:
            reasons.append(f"{axis}_ledger")
        if mode["same_bar_reentries"]:
            reasons.append(f"{axis}_same_bar")
        if mode["max_loss_usd"] > MAX_LOSS:
            reasons.append(f"{axis}_max_loss")
    windows = row["windows"]
    if windows["window_max_dd"] > MAX_WINDOW_DD:
        reasons.append("window_dd")
    if windows["dense_negative_n"] > MAX_DENSE_NEG:
        reasons.append("dense_negative")
    if not windows["ledger_exact"] or windows["same_bar_reentries"]:
        reasons.append("window_integrity")
    return not reasons, reasons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default="BAC,TSLL,SMCI,PLTR,SOFI,F")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    grid = list(product((14, 30), (0.16, 0.22), (0.08, 0.12), (0.05, 0.10)))
    results: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for symbol in symbols:
        try:
            df = build(symbol, period=args.period, use_cache=True)
            print(f"{symbol}: {len(df)} bars", file=sys.stderr)
            symbol_rows: list[dict[str, Any]] = []
            for dte, put_delta, call_delta, min_credit in grid:
                key = {
                    "dte": dte,
                    "put_delta": put_delta,
                    "call_delta": call_delta,
                    "put_width": 1.0,
                    "call_width": 1.0,
                    "min_combined_credit_pct": min_credit,
                    "allowed_regimes": ["bullish", "neutral"],
                }
                baseline_cfg = _config(
                    dte=dte, put_delta=put_delta, call_delta=call_delta, min_credit=min_credit
                )
                slip_cfg = _config(
                    dte=dte,
                    put_delta=put_delta,
                    call_delta=call_delta,
                    min_credit=min_credit,
                    slippage_pct=0.05,
                )
                fixed_cfg = _config(
                    dte=dte,
                    put_delta=put_delta,
                    call_delta=call_delta,
                    min_credit=min_credit,
                    half_spread_per_leg=0.01,
                )
                row = {
                    "symbol": symbol,
                    "config": key,
                    "baseline": _row(_run(symbol, df, baseline_cfg, "5y_baseline")),
                    "slip_5pct": _row(_run(symbol, df, slip_cfg, "5y_slip5")),
                    "fixed_0p01": _row(_run(symbol, df, fixed_cfg, "5y_fixed1c")),
                }
                candidate = all(
                    row[axis]["n_trades"] >= MIN_TRADES
                    and row[axis]["pnl"] > 0
                    and row[axis]["ledger_exact"]
                    and row[axis]["same_bar_reentries"] == 0
                    and row[axis]["max_loss_usd"] <= MAX_LOSS
                    for axis in ("slip_5pct", "fixed_0p01")
                )
                row["deep_candidate"] = candidate
                symbol_rows.append(row)
            deep = [row for row in symbol_rows if row["deep_candidate"]]
            for row in deep:
                key = row["config"]
                fixed_cfg = _config(
                    dte=key["dte"],
                    put_delta=key["put_delta"],
                    call_delta=key["call_delta"],
                    min_credit=key["min_combined_credit_pct"],
                    half_spread_per_leg=0.01,
                )
                row["windows"] = _windows(symbol, df, fixed_cfg)
                passed, reasons = _full_gate(row)
                row["absolute_pass"] = passed
                row["fail_reasons"] = reasons
            results.extend(symbol_rows)
            print(f"{symbol}: deep {len(deep)}/{len(symbol_rows)}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            errors.append({"symbol": symbol, "error": str(exc)})

    deep_rows = [row for row in results if row["deep_candidate"]]
    pass_rows = [row for row in deep_rows if row.get("absolute_pass")]
    ranked = sorted(
        deep_rows,
        key=lambda row: (
            bool(row.get("absolute_pass")),
            min(float(row["slip_5pct"]["pnl"]), float(row["fixed_0p01"]["pnl"])),
            -float((row.get("windows") or {}).get("window_max_dd") or 1e9),
        ),
        reverse=True,
    )
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD",
        "paper_only": True,
        "sleeve_usd": 3000,
        "hypothesis": "bullish asymmetric IC (capped-jade shape) can harvest put skew with a farther call while capping both tails",
        "claim_scope": "synthetic daily-bar/BS proxy discovery only; observed archive is not dense enough for L1",
        "validity": {
            "no_future_features": "data.build current-row features; chronological one-position loop",
            "contract_semantics": "synthetic listed-Friday expiry and rounded strikes; not observed availability",
            "cost_axes": ["5pct adverse leg slip", "$0.01 half-spread per leg at entry and exit"],
            "population": symbols,
            "ranking_complete": len(errors) == 0,
        },
        "gates": {
            "min_trades_each_cost_axis": MIN_TRADES,
            "positive_ship_each_cost_axis": True,
            "max_loss_usd": MAX_LOSS,
            "window_max_dd": MAX_WINDOW_DD,
            "dense_negative_windows": MAX_DENSE_NEG,
            "ledger_exact": True,
            "no_same_bar_reentry": True,
        },
        "grid_size_per_symbol": len(grid),
        "n_rows": len(results),
        "n_deep_candidates": len(deep_rows),
        "n_absolute_pass": len(pass_rows),
        "errors": errors,
        "decision": "DISCOVERY_PASS_REQUIRES_OBSERVED_VALIDATION" if pass_rows else "REJECT_ASYMMETRIC_CONDOR_THIS_CYCLE",
        "pass_rows": pass_rows,
        "top_deep_rows": ranked[:20],
        "all_rows": results,
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
                "decision": payload["decision"],
                "n_rows": len(results),
                "n_deep_candidates": len(deep_rows),
                "n_absolute_pass": len(pass_rows),
                "errors": errors,
            },
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

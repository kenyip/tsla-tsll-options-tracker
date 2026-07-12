#!/usr/bin/env python3
"""Falsify close-shock mean-reversion PCS entries across liquid names, paper only."""
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
MAX_WINDOW_DD = 75.0
MAX_DENSE_NEG = 5


def _config(
    *,
    dte: int,
    shock_pct: float | None = None,
    volume_min: float | None = None,
    mirror: bool = False,
    slippage_pct: float = 0.0,
    half_spread_per_leg: float = 0.0,
) -> dict[str, Any]:
    config: dict[str, Any] = {
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
        "slippage_pct": slippage_pct,
        "half_spread_per_leg": half_spread_per_leg,
        "entry_signal_lag_bars": 1,
    }
    if shock_pct is not None:
        key = "entry_intraday_return_min" if mirror else "entry_intraday_return_max"
        config[key] = abs(shock_pct) if mirror else -abs(shock_pct)
    if volume_min is not None:
        config["entry_volume_surge_min"] = volume_min
    return config


def _run(symbol: str, df: pd.DataFrame, config: dict[str, Any], label: str):
    return run_pcs_backtest(
        symbol,
        period=label,
        df=df,
        min_bars=15,
        config=config,
        structure="put_credit_spread",
        sleeve_usd=3000.0,
        open_risk_budget_usd=750.0,
    )


def _row(result, df: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
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
    signal_violations = 0
    signal_lag = max(int(config.get("entry_signal_lag_bars", 0)), 0)
    for trade in result.trades:
        if trade.entry_date not in df.index:
            signal_violations += 1
            continue
        entry_number = cast(int, df.index.get_loc(trade.entry_date))
        if entry_number < signal_lag or not entry_filters_pass(df.iloc[entry_number - signal_lag], config):
            signal_violations += 1
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
        "signal_violations": signal_violations,
    }


def _modes(symbol: str, df: pd.DataFrame, base: dict[str, Any]) -> dict[str, Any]:
    configs = {
        "baseline": dict(base),
        "slip_5pct": {**base, "slippage_pct": 0.05},
        "fixed_0p01": {**base, "half_spread_per_leg": 0.01},
    }
    return {
        name: _row(_run(symbol, df, config, f"5y_{name}"), df, config)
        for name, config in configs.items()
    }


def _windows(symbol: str, df: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    dates = [pd.Timestamp(value) for value in df.index]
    windows: list[tuple[str, pd.DataFrame]] = [
        (f"year_{year}", df.loc[[value.year == year for value in dates]])
        for year in sorted({value.year for value in dates})
    ]
    chunk = 126
    windows.extend(
        (
            f"chunk6m_{index}_{dates[start].date()}_{dates[min(start + chunk - 1, len(df) - 1)].date()}",
            df.iloc[start : start + chunk],
        )
        for index, start in enumerate(range(0, max(0, len(df) - chunk + 1), chunk))
    )
    fixed = {**config, "half_spread_per_leg": 0.01}
    rows = [
        {"label": label, **_row(_run(symbol, window, fixed, label), window, fixed)}
        for label, window in windows
        if len(window) >= 15
    ]
    dense_negative = [row for row in rows if row["n_trades"] >= 3 and row["pnl"] < 0]
    return {
        "n_windows": len(rows),
        "dense_negative_n": len(dense_negative),
        "dense_negative_labels": [row["label"] for row in dense_negative],
        "window_max_dd": max((float(row["dd"]) for row in rows), default=0.0),
        "worst_window_pnl": min((float(row["pnl"]) for row in rows), default=0.0),
        "ledger_exact": all(row["ledger_exact"] for row in rows),
        "same_bar_reentries": sum(int(row["same_bar_reentries"]) for row in rows),
        "signal_violations": sum(int(row["signal_violations"]) for row in rows),
        "rows": rows,
    }


def _cost_candidate(modes: dict[str, Any]) -> bool:
    return all(
        modes[axis]["n_trades"] >= MIN_TRADES
        and modes[axis]["pnl"] > 0
        and modes[axis]["verdict"] == "SHIP"
        and modes[axis]["max_loss_usd"] <= MAX_LOSS
        and modes[axis]["dd"] <= MAX_WINDOW_DD
        and modes[axis]["ledger_exact"]
        and modes[axis]["same_bar_reentries"] == 0
        and modes[axis]["signal_violations"] == 0
        for axis in ("slip_5pct", "fixed_0p01")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default="BAC,F,SOFI,PLTR,TSLL,SMCI,AMD,AAPL")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    grid = list(product((7, 14), (1.0, 2.0), (1.0, 1.5)))
    rows: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for symbol in symbols:
        try:
            df = build(symbol, period=args.period, use_cache=True)
            print(f"{symbol}: {len(df)} bars", file=sys.stderr)
            for dte in (7, 14):
                unconditional = _config(dte=dte)
                controls.append(
                    {
                        "symbol": symbol,
                        "control": "unconditional",
                        "config": {"dte": dte},
                        **_modes(symbol, df, unconditional),
                    }
                )
            for dte, shock_pct, volume_min in grid:
                signal_config = _config(dte=dte, shock_pct=shock_pct, volume_min=volume_min)
                mirror_config = _config(
                    dte=dte, shock_pct=shock_pct, volume_min=volume_min, mirror=True
                )
                signal_row = {
                    "symbol": symbol,
                    "signal": "down_close_shock",
                    "config": {
                        "dte": dte,
                        "intraday_return_max": -shock_pct,
                        "volume_surge_min": volume_min,
                    },
                    **_modes(symbol, df, signal_config),
                }
                signal_row["cost_candidate"] = _cost_candidate(signal_row)
                rows.append(signal_row)
                controls.append(
                    {
                        "symbol": symbol,
                        "control": "mirror_up_close_shock",
                        "config": {
                            "dte": dte,
                            "intraday_return_min": shock_pct,
                            "volume_surge_min": volume_min,
                        },
                        **_modes(symbol, df, mirror_config),
                    }
                )
            print(
                f"{symbol}: cost candidates {sum(row['cost_candidate'] for row in rows if row['symbol'] == symbol)}",
                file=sys.stderr,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"symbol": symbol, "error": str(exc)})

    candidates = [row for row in rows if row["cost_candidate"]]
    for row in candidates:
        key = row["config"]
        config = _config(
            dte=int(key["dte"]),
            shock_pct=abs(float(key["intraday_return_max"])),
            volume_min=float(key["volume_surge_min"]),
        )
        df = build(row["symbol"], period=args.period, use_cache=True)
        row["windows"] = _windows(row["symbol"], df, config)
        window = row["windows"]
        reasons = []
        if window["window_max_dd"] > MAX_WINDOW_DD:
            reasons.append("window_dd")
        if window["dense_negative_n"] > MAX_DENSE_NEG:
            reasons.append("dense_negative")
        if not window["ledger_exact"] or window["same_bar_reentries"] or window["signal_violations"]:
            reasons.append("window_integrity")
        row["absolute_pass"] = not reasons
        row["fail_reasons"] = reasons

    passes = [row for row in candidates if row.get("absolute_pass")]
    ranked = sorted(
        candidates,
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
        "hypothesis": "high-volume downside close shocks create a mean-reversion PCS entry edge after costs",
        "falsifier": "no dense positive row on both cost axes with max_loss<=300, fixed-cost window_dd<=75, dense_negative<=5, and exact signal/ledger integrity",
        "claim_scope": "synthetic listed-Friday/rounded-strike daily-bar BS discovery; completed close/volume signal is lagged one bar and entry is priced at the following close; not observed option quotes and not L1",
        "validity": {
            "no_future_features": "entry filters read the prior completed bar; lagged entry-date purity independently checked",
            "contract_semantics": "synthetic listed-Friday expiration and rounded strikes",
            "cost_axes": ["5pct adverse leg slip", "$0.01 half-spread per leg at entry and exit"],
            "negative_controls": ["same-DTE unconditional PCS", "high-volume mirror upside close shock"],
            "population": symbols,
            "population_pure": "put_credit_spread only",
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
            "signal_purity": True,
        },
        "grid_size_per_symbol": len(grid),
        "n_rows": len(rows),
        "n_controls": len(controls),
        "n_cost_candidates": len(candidates),
        "n_absolute_pass": len(passes),
        "errors": errors,
        "decision": "DISCOVERY_PASS_REQUIRES_OBSERVED_VALIDATION" if passes else "REJECT_CLOSE_SHOCK_PCS_THIS_CYCLE",
        "pass_rows": passes,
        "top_cost_candidates": ranked[:20],
        "rows": rows,
        "controls": controls,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("decision", "n_rows", "n_controls", "n_cost_candidates", "n_absolute_pass", "errors")}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

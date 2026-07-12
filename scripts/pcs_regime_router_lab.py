#!/usr/bin/env python3
"""Falsify a no-lookahead PCS/CCS/IC regime router against standalone controls."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from trader_platform.evolve_tick import score_sim_metrics  # noqa: E402
from trader_platform.research.regime_router_sim import (  # noqa: E402
    STRUCTURES,
    default_structure_configs,
    run_regime_router_backtest,
)

POLICIES = ("router", *STRUCTURES)


def _configs(*, slippage_pct: float = 0.0, half_spread_per_leg: float = 0.0) -> dict[str, dict[str, Any]]:
    configs = default_structure_configs()
    for config in configs.values():
        config["slippage_pct"] = slippage_pct
        config["half_spread_per_leg"] = half_spread_per_leg
    return configs


def _row(result) -> dict[str, Any]:
    metrics = result.metrics or {}
    n = int(result.n_trades)
    pnl = float(metrics.get("total_pnl_per_contract") or 0.0)
    dd = float(metrics.get("max_dd_per_contract") or 0.0)
    wr = float(metrics.get("win_rate_pct") or 0.0) / 100.0
    pf = float(metrics.get("profit_factor") or 0.0)
    verdict, score, reason, finite_pf = score_sim_metrics(
        n_trades=n,
        pnl=pnl,
        win_rate=wr,
        max_dd=dd,
        profit_factor=pf,
    )
    ledger = np.array(
        [
            (trade.net_credit - float(trade.exit_debit or 0.0)) * 100.0
            for trade in result.trades
        ],
        dtype=float,
    )
    equity = np.cumsum(ledger)
    peaks = np.maximum.accumulate(equity) if len(equity) else np.array([], dtype=float)
    recomputed_dd = float(np.max(peaks - equity)) if len(equity) else 0.0
    return {
        "ok": result.ok,
        "n_trades": n,
        "pnl": round(pnl, 2),
        "dd": round(dd, 2),
        "win_rate_pct": round(wr * 100.0, 2),
        "profit_factor": round(float(finite_pf), 4) if np.isfinite(float(finite_pf)) else None,
        "verdict": verdict,
        "score": round(float(score), 2),
        "reason": reason,
        "max_loss_usd": result.capital.get("max_loss_usd"),
        "capital_fit_usd": result.capital.get("capital_fit_usd"),
        "max_lots": result.capital.get("max_lots"),
        "capital_fit": result.capital.get("capital_fit"),
        "route_counts": result.route_counts,
        "entry_funnel": result.entry_funnel,
        "population_pure": bool(metrics.get("population_pure")),
        "routing_violations": int(metrics.get("routing_violations") or 0),
        "same_bar_reentries": int(metrics.get("same_bar_reentries") or 0),
        "ledger_pnl_recomputed": round(float(ledger.sum()), 2),
        "ledger_dd_recomputed": round(recomputed_dd, 2),
        "ledger_exact": abs(float(ledger.sum()) - pnl) < 1e-8 and abs(recomputed_dd - dd) < 1e-8,
    }


def _windows(df: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    windows = [(f"year_{year}", df[df.index.year == year]) for year in sorted(set(df.index.year))]
    chunk = 126
    windows.extend(
        (
            f"chunk6m_{index}_{df.index[start].date()}_{df.index[min(start + chunk - 1, len(df) - 1)].date()}",
            df.iloc[start : start + chunk],
        )
        for index, start in enumerate(range(0, max(0, len(df) - chunk + 1), chunk))
    )
    return [(label, window) for label, window in windows if len(window) >= 15]


def evaluate_symbol(symbol: str, df: pd.DataFrame) -> dict[str, Any]:
    full: dict[str, dict[str, Any]] = {}
    for policy in POLICIES:
        full[policy] = {
            "baseline": _row(
                run_regime_router_backtest(
                    symbol,
                    df=df,
                    policy=policy,
                    period="5y_baseline",
                    configs=_configs(),
                )
            ),
            "slip_5pct": _row(
                run_regime_router_backtest(
                    symbol,
                    df=df,
                    policy=policy,
                    period="5y_slip5",
                    configs=_configs(slippage_pct=0.05),
                )
            ),
            "fixed_0p01_per_leg": _row(
                run_regime_router_backtest(
                    symbol,
                    df=df,
                    policy=policy,
                    period="5y_fixed1c",
                    configs=_configs(half_spread_per_leg=0.01),
                )
            ),
        }

    window_rows = []
    for label, window in _windows(df):
        result = run_regime_router_backtest(
            symbol,
            df=window,
            policy="router",
            period=label,
            configs=_configs(),
        )
        window_rows.append({"label": label, **_row(result)})

    dense_negative = [
        row for row in window_rows if row["n_trades"] >= 3 and float(row["pnl"]) < 0
    ]
    worst_window_pnl = min((float(row["pnl"]) for row in window_rows), default=0.0)
    window_max_dd = max((float(row["dd"]) for row in window_rows), default=0.0)
    regime_hold = (
        len(dense_negative) <= max(3, len(window_rows) // 2)
        and worst_window_pnl > -400.0
    )

    router = full["router"]
    controls = [full[policy] for policy in STRUCTURES]
    best_control_slip_pnl = max(float(control["slip_5pct"]["pnl"]) for control in controls)
    best_control_slip_dd = min(float(control["slip_5pct"]["dd"]) for control in controls)
    slip = router["slip_5pct"]
    fixed = router["fixed_0p01_per_leg"]
    baseline = router["baseline"]
    gates = {
        "non_vacuous_after_cost_ship": slip["n_trades"] >= 20 and slip["pnl"] > 0 and slip["verdict"] == "SHIP",
        "fixed_cost_positive_non_vacuous": fixed["n_trades"] >= 20 and fixed["pnl"] > 0,
        "regime_hold": regime_hold,
        "max_loss_lte_300": float(baseline["max_loss_usd"] or 1e9) <= 300.0,
        "window_max_dd_lte_75": window_max_dd <= 75.0,
        "dense_negative_lte_5": len(dense_negative) <= 5,
        "routing_population_pure": baseline["population_pure"] and baseline["routing_violations"] == 0,
        "no_same_bar_reentry": baseline["same_bar_reentries"] == 0,
        "independent_ledger_exact": all(
            mode["ledger_exact"] for policy in full.values() for mode in policy.values()
        ),
        "beats_best_control_after_cost_pnl": float(slip["pnl"]) > best_control_slip_pnl,
        "competitive_control_after_cost_dd": float(slip["dd"]) <= best_control_slip_dd,
    }
    return {
        "symbol": symbol,
        "start": str(df.index[0].date()),
        "end": str(df.index[-1].date()),
        "n_bars": len(df),
        "full": full,
        "router_windows": window_rows,
        "router_regime_summary": {
            "n_windows": len(window_rows),
            "dense_negative_n": len(dense_negative),
            "dense_negative_labels": [row["label"] for row in dense_negative],
            "worst_window_pnl": round(worst_window_pnl, 2),
            "window_max_dd": round(window_max_dd, 2),
            "regime_hold": regime_hold,
        },
        "control_comparison": {
            "best_control_slip_5_pnl": round(best_control_slip_pnl, 2),
            "best_control_slip_5_dd": round(best_control_slip_dd, 2),
        },
        "gates": gates,
        "passes_all_gates": all(gates.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default="TSLL,SMCI,TSLA,PLTR,AAPL,AMD,ARM,QQQ")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    symbols = [symbol.strip().upper() for symbol in args.symbols.split(",") if symbol.strip()]
    results = []
    errors = []
    for symbol in symbols:
        print(f"loading {symbol} {args.period}", file=sys.stderr)
        try:
            df = build(symbol, period=args.period, use_cache=True)
            results.append(evaluate_symbol(symbol, df))
        except Exception as exc:  # noqa: BLE001
            errors.append({"symbol": symbol, "error": str(exc)})

    passing = [row["symbol"] for row in results if row["passes_all_gates"]]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD",
        "sleeve_usd": 3000,
        "claim_scope": "synthetic daily-bar discovery; not observed-contract or L1 readiness evidence",
        "router_rule": "bullish→PCS; bearish→CCS; neutral with IC iv_rank_min→IC; else stand aside",
        "cost_axes": {"slippage_pct": 0.05, "fixed_half_spread_per_leg": 0.01},
        "population": {"requested": symbols, "completed": [row["symbol"] for row in results], "errors": errors},
        "results": results,
        "passing_symbols": passing,
        "decision": "PROMOTE_RESEARCH" if passing else "REJECT_ROUTER_FAMILY_THIS_CYCLE",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    summary = {
        "out": str(out),
        "decision": payload["decision"],
        "passing_symbols": passing,
        "errors": errors,
        "rows": [
            {
                "symbol": row["symbol"],
                "baseline": row["full"]["router"]["baseline"],
                "slip_5pct": row["full"]["router"]["slip_5pct"],
                "fixed_0p01": row["full"]["router"]["fixed_0p01_per_leg"],
                "regime": row["router_regime_summary"],
                "failed_gates": [name for name, passed in row["gates"].items() if not passed],
            }
            for row in results
        ],
    }
    print(json.dumps(summary, indent=2))
    return 0 if len(results) == len(symbols) else 1


if __name__ == "__main__":
    raise SystemExit(main())

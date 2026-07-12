#!/usr/bin/env python3
"""Paper-only collar management grid with exact after-cost and risk gates."""
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
from trader_platform.research.collar_sim import run_collar_backtest  # noqa: E402
from trader_platform.strategy_dna import dna_from_structure  # noqa: E402

DEFAULT_SYMBOLS = "F,SOFI,AAL,PFE,SNAP,NIO,CCL,SMCI"


def _csv(raw: str, cast: type) -> list[Any]:
    return [cast(value.strip()) for value in raw.split(",") if value.strip()]


def _summary(result) -> dict[str, Any]:
    metrics = result.metrics or {}
    gate = result.gate or {}
    trades = result.trades or []
    recomputed_pnl = sum(
        ((trade.exit_value or 0.0) - trade.entry_package) * 100.0 for trade in trades
    )
    same_bar_reentries = sum(
        1
        for previous, following in zip(trades, trades[1:])
        if previous.exit_date == following.entry_date
    )
    reported_pnl = float(metrics.get("total_pnl_per_contract") or 0.0)
    return {
        "n_trades": int(result.n_trades),
        "pnl": round(reported_pnl, 2),
        "max_dd": round(float(metrics.get("max_dd_per_contract") or 0.0), 2),
        "window_max_dd": round(float(metrics.get("window_max_dd_usd") or 0.0), 2),
        "dense_neg_count": int(metrics.get("dense_neg_count") or 0),
        "worst_max_loss_usd": round(float(metrics.get("worst_max_loss_usd") or 0.0), 2),
        "capital_fit_usd": (result.capital or {}).get("capital_fit_usd"),
        "max_lots": (result.capital or {}).get("max_lots"),
        "gate_pass": bool(gate.get("passed")),
        "gate_reasons": gate.get("reasons") or [],
        "pnl_recompute_delta": round(recomputed_pnl - reported_pnl, 10),
        "same_bar_reentries": same_bar_reentries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default=DEFAULT_SYMBOLS)
    parser.add_argument("--period", default="5y")
    parser.add_argument("--dtes", default="7,14,21,30")
    parser.add_argument("--put-deltas", default="0.25,0.35,0.40")
    parser.add_argument("--call-deltas", default="0.10,0.20,0.30")
    parser.add_argument("--profit-targets", default="0.25,0.40")
    parser.add_argument("--loss-exits", default="0.35,0.70")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    grid = list(
        product(
            _csv(args.dtes, int),
            _csv(args.put_deltas, float),
            _csv(args.call_deltas, float),
            _csv(args.profit_targets, float),
            _csv(args.loss_exits, float),
        )
    )
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for symbol in symbols:
        try:
            frame = build(symbol, period=args.period, use_cache=True)
        except Exception as exc:  # noqa: BLE001
            errors.append({"symbol": symbol, "error": str(exc)})
            continue
        base = dna_from_structure("collared_covered_call", [symbol]).sim_config()
        for dte, put_delta, call_delta, profit_target, loss_exit in grid:
            cfg = {
                **base,
                "long_dte": dte,
                "collar_put_delta": put_delta,
                "collar_call_delta": call_delta,
                "profit_target": profit_target,
                "defined_loss_exit_frac": loss_exit,
                "max_loss_budget_usd": 300.0,
            }
            axes = {}
            for label, costs in (
                ("slip_5pct", {"slippage_pct": 0.05}),
                ("half_spread_0p01", {"half_spread_per_leg": 0.01}),
            ):
                result = run_collar_backtest(
                    symbol,
                    period=args.period,
                    use_cache=True,
                    config={**cfg, **costs},
                    sleeve_usd=3000.0,
                    open_risk_budget_usd=750.0,
                    df=frame,
                    min_bars=15,
                    apply_absolute_gates=True,
                )
                axes[label] = _summary(result)
            integrity_pass = all(
                axis["pnl_recompute_delta"] == 0.0 and axis["same_bar_reentries"] == 0
                for axis in axes.values()
            )
            cost_pass = integrity_pass and all(axis["gate_pass"] for axis in axes.values())
            rows.append(
                {
                    "symbol": symbol,
                    "config": {
                        "long_dte": dte,
                        "collar_put_delta": put_delta,
                        "collar_call_delta": call_delta,
                        "profit_target": profit_target,
                        "defined_loss_exit_frac": loss_exit,
                    },
                    "cost_axes_pass": cost_pass,
                    "integrity_pass": integrity_pass,
                    "axes": axes,
                }
            )

    def rank_key(row: dict[str, Any]) -> tuple[Any, ...]:
        slip = row["axes"]["slip_5pct"]
        fixed = row["axes"]["half_spread_0p01"]
        return (
            row["cost_axes_pass"],
            min(slip["pnl"], fixed["pnl"]),
            -max(slip["window_max_dd"], fixed["window_max_dd"]),
            min(slip["n_trades"], fixed["n_trades"]),
        )

    rows.sort(key=rank_key, reverse=True)
    pass_rows = [row for row in rows if row["cost_axes_pass"]]
    integrity_failures = [row for row in rows if not row["integrity_pass"]]
    both_cost_positive = [
        row for row in rows if all(axis["pnl"] > 0 for axis in row["axes"].values())
    ]
    max_loss_pass = [
        row
        for row in rows
        if max(axis["worst_max_loss_usd"] for axis in row["axes"].values()) <= 300.0
    ]
    window_dd_pass = [
        row
        for row in rows
        if max(axis["window_max_dd"] for axis in row["axes"].values()) <= 75.0
    ]
    tightest_window_dd_row = min(
        rows,
        key=lambda row: max(axis["window_max_dd"] for axis in row["axes"].values()),
        default=None,
    )
    decision = (
        "DISCOVERY_PASS_REQUIRES_B3_B4"
        if pass_rows
        else "REJECT_COLLAR_MANAGEMENT_GRID_THIS_CYCLE"
    )
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "paper_only": True,
        "structure": "collared_covered_call",
        "hypothesis": (
            "Tighter protective puts plus lower-delta covered calls can finance protection enough "
            "to produce dense positive after-cost collars within absolute $3k sleeve gates."
        ),
        "falsifier": (
            "No exact DNA passes both 5% slip and $0.01-per-leg axes with n>=8, positive PnL, "
            "max_loss<=300, window_max_dd<=75, dense_neg<=5, and independent ledger integrity."
        ),
        "validity": {
            "no_future_features": "data.build row-t features only",
            "pricing_semantics": "BS proxy; no observed option surfaces; discovery only",
            "contract_availability": "synthetic rounded strikes/expiry; no promotion claim",
            "population_purity": "collared_covered_call only",
            "independent_checks": "trade-ledger PnL recomputation and no-close-bar-reentry audit",
            "register_proxy_ship": False,
        },
        "period": args.period,
        "symbols": symbols,
        "grid": {
            "n_configs_per_symbol": len(grid),
            "dtes": _csv(args.dtes, int),
            "put_deltas": _csv(args.put_deltas, float),
            "call_deltas": _csv(args.call_deltas, float),
            "profit_targets": _csv(args.profit_targets, float),
            "loss_exits": _csv(args.loss_exits, float),
        },
        "n_rows": len(rows),
        "n_cost_pass": len(pass_rows),
        "n_integrity_failures": len(integrity_failures),
        "aggregate": {
            "n_both_cost_positive": len(both_cost_positive),
            "n_max_loss_lte_300": len(max_loss_pass),
            "n_worst_axis_window_dd_lte_75": len(window_dd_pass),
            "tightest_worst_axis_window_dd_row": tightest_window_dd_row,
        },
        "decision": decision,
        "register_proxy_ship": False,
        "errors": errors,
        "pass_rows": pass_rows,
        "top_20": rows[:20],
        "all_rows": rows,
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = _REPO / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(
        f"collar_grid rows={len(rows)} passes={len(pass_rows)} "
        f"integrity_failures={len(integrity_failures)} decision={decision}"
    )
    for row in rows[:5]:
        slip = row["axes"]["slip_5pct"]
        fixed = row["axes"]["half_spread_0p01"]
        print(
            f"{row['symbol']:4} {row['config']} "
            f"slip n={slip['n_trades']} pnl={slip['pnl']:.2f} wdd={slip['window_max_dd']:.2f}; "
            f"fixed n={fixed['n_trades']} pnl={fixed['pnl']:.2f} wdd={fixed['window_max_dd']:.2f}"
        )
    print(f"wrote {out}")
    return 0 if not integrity_failures else 2


if __name__ == "__main__":
    raise SystemExit(main())

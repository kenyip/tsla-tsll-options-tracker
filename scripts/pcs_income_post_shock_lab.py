#!/usr/bin/env python3
"""PCS income pilot V4 — post soft-shock stabilize entry; PT50% harvest.

After a completed multi-day drawdown that is stabilizing on the lag bar, sell
21-DTE put credit spreads with 50% profit targets. Distinct from V1–V3 entry
families. Research/proxy L0 only.
"""
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
from scripts.pcs_momentum_walkforward_lab import summarize_result  # noqa: E402
from trader_platform.research.pcs_sim import run_pcs_backtest  # noqa: E402

CANDIDATE_ID = "PCS_INCOME_POST_SHOCK_STABILIZE_21D_PT50_V1"
FAMILY_ID = "PCS_INCOME_THETA_HARVEST_POST_SHOCK_STABILIZE"
DEFAULT_SYMBOLS = (
    "BAC",
    "F",
    "SOFI",
    "KO",
    "INTC",
    "XOM",
    "PLTR",
    "AAPL",
    "IWM",
    "TSLL",
    "SMCI",
    "NFLX",
)
COST_AXES = {
    "slip_5pct": {"slippage_pct": 0.05},
    "fixed_0p01": {"half_spread_per_leg": 0.01},
}
MIN_TRADES = 8
MAX_LOSS_USD = 300.0
MAX_DD_DISCOVERY_USD = 150.0
ENTRY_KEYS = (
    "entry_signal_lag_bars",
    "entry_ret_5d_min",
    "entry_ret_5d_max",
    "entry_ret_1d_min",
    "entry_ret_1d_max",
    "entry_ema_stack_min",
)


def income_candidate_config() -> dict[str, Any]:
    return {
        "structure": "put_credit_spread",
        "long_dte": 21,
        "long_target_delta": 0.20,
        "spread_width": 1.0,
        "min_credit_pct": 0.08,
        "profit_target": 0.50,
        "defined_loss_exit_frac": 0.70,
        "delta_breach": 0.40,
        "dte_stop": 7,
        "max_loss_budget_usd": MAX_LOSS_USD,
        "regime_flip_exit_enabled": True,
        "bear_dte": 0,
        "entry_signal_lag_bars": 1,
        # Soft multi-day drawdown that is no longer cascading on the lag bar.
        "entry_ret_5d_min": -0.12,
        "entry_ret_5d_max": -0.02,
        "entry_ret_1d_min": -0.005,
        "entry_ret_1d_max": 0.025,
        "entry_ema_stack_min": 0.0,
    }


def unconditional_control_config(candidate: dict[str, Any] | None = None) -> dict[str, Any]:
    control = dict(candidate or income_candidate_config())
    for key in ENTRY_KEYS:
        control.pop(key, None)
    return control


def _axis_value(row: dict[str, Any], gate_key: str, display_key: str) -> float:
    return float(row.get(gate_key, row.get(display_key) or 0.0))


def discovery_pass(candidate: dict[str, Any], control: dict[str, Any]) -> bool:
    if set(candidate) != set(COST_AXES) or set(control) != set(COST_AXES):
        return False
    for axis in COST_AXES:
        row = candidate[axis]
        control_row = control[axis]
        if not row.get("ok", False) or not control_row.get("ok", False):
            return False
        if int(row.get("n_trades") or 0) < MIN_TRADES:
            return False
        if int(control_row.get("n_trades") or 0) < MIN_TRADES:
            return False
        if _axis_value(row, "gate_pnl", "pnl") <= 0.0:
            return False
        if _axis_value(row, "gate_max_loss_usd", "max_loss_usd") > MAX_LOSS_USD:
            return False
        if _axis_value(row, "gate_dd", "dd") > MAX_DD_DISCOVERY_USD:
            return False
        if not row.get("integrity", False) or not control_row.get("integrity", False):
            return False
    candidate_worst = min(_axis_value(candidate[axis], "gate_pnl", "pnl") for axis in COST_AXES)
    control_worst = min(_axis_value(control[axis], "gate_pnl", "pnl") for axis in COST_AXES)
    return candidate_worst > control_worst


def train_rank_key(row: dict[str, Any]) -> tuple[float, float, int, str]:
    axes = row["train"]
    worst_pnl = min(_axis_value(axes[axis], "gate_pnl", "pnl") for axis in COST_AXES)
    worst_loss = max(
        _axis_value(axes[axis], "gate_max_loss_usd", "max_loss_usd") for axis in COST_AXES
    )
    minimum_n = min(int(axes[axis].get("n_trades") or 0) for axis in COST_AXES)
    return (worst_pnl, -worst_loss, minimum_n, str(row.get("symbol") or ""))


def management_diagnostics(result: Any) -> dict[str, Any]:
    metrics = result.metrics or {}
    exit_reasons = {
        str(reason): int(count)
        for reason, count in dict(metrics.get("exit_reasons") or {}).items()
    }
    return {
        "avg_days_held": float(metrics.get("avg_days_held") or 0.0),
        "exit_reasons": exit_reasons,
        "profit_target_exits": int(exit_reasons.get("profit_target", 0)),
        "profit_target_exercised": int(exit_reasons.get("profit_target", 0)) > 0,
    }


def _run_axes(symbol: str, frame, config: dict[str, Any], label: str) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for axis, cost in COST_AXES.items():
        axis_config = {**config, **cost}
        result = run_pcs_backtest(
            symbol,
            period=f"{label}_{axis}",
            df=frame,
            min_bars=15,
            config=axis_config,
            structure="put_credit_spread",
            sleeve_usd=3000.0,
            open_risk_budget_usd=750.0,
        )
        summary = summarize_result(result, frame, axis_config)
        rows[axis] = {**summary, **management_diagnostics(result)}
    return rows


def run_holdout(*, symbols: list[str], period: str, train_fraction: float) -> dict[str, Any]:
    cfg = income_candidate_config()
    rows: list[dict[str, Any]] = []
    for symbol in symbols:
        frame = build(symbol, period=period, use_cache=True)
        split_index = int(len(frame) * train_fraction)
        hold = frame.iloc[split_index:]
        train = frame.iloc[:split_index]
        if len(hold) < 15 or not train.index[-1] < hold.index[0]:
            raise ValueError(f"{symbol}: invalid holdout partition")
        axes = _run_axes(symbol, hold, cfg, "holdout")
        dual = all(
            axes[a].get("ok")
            and int(axes[a].get("n_trades") or 0) >= MIN_TRADES
            and _axis_value(axes[a], "gate_pnl", "pnl") > 0.0
            and _axis_value(axes[a], "gate_max_loss_usd", "max_loss_usd") <= MAX_LOSS_USD
            and bool(axes[a].get("integrity"))
            for a in COST_AXES
        )
        rows.append(
            {
                "symbol": symbol,
                "holdout_start": str(hold.index[0].date()),
                "holdout_end": str(hold.index[-1].date()),
                "holdout": axes,
                "holdout_dual_cost_pass": dual,
            }
        )
    any_pass = any(r["holdout_dual_cost_pass"] for r in rows)
    return {
        "candidate_id": CANDIDATE_ID,
        "decision": "HOLDOUT_SURVIVOR" if any_pass else "HOLDOUT_FAILED",
        "any_holdout_survivor": any_pass,
        "option_mark_provenance": "black_scholes_proxy",
        "rows": rows,
    }


def run_lab(*, symbols: list[str], period: str, train_fraction: float) -> dict[str, Any]:
    if not 0.50 <= float(train_fraction) <= 0.80:
        raise ValueError("train_fraction must be between 0.50 and 0.80")
    normalized = [str(s).strip().upper() for s in symbols if str(s).strip()]
    if len(normalized) < 2 or len(normalized) != len(set(normalized)):
        raise ValueError("symbols must contain at least two unique names")

    candidate_config = income_candidate_config()
    control_config = unconditional_control_config(candidate_config)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for symbol in normalized:
        try:
            frame = build(symbol, period=period, use_cache=True)
            split_index = int(len(frame) * train_fraction)
            train = frame.iloc[:split_index].copy()
            holdout = frame.iloc[split_index:]
            if len(train) < 15 or len(holdout) < 15 or not train.index[-1] < holdout.index[0]:
                raise ValueError("train/holdout partition invalid")
            candidate_axes = _run_axes(symbol, train, candidate_config, "post_shock_train")
            control_axes = _run_axes(symbol, train, control_config, "uncond_control_train")
            passed = discovery_pass(candidate_axes, control_axes)
            max_loss = max(
                _axis_value(candidate_axes[a], "gate_max_loss_usd", "max_loss_usd")
                for a in COST_AXES
            )
            rows.append(
                {
                    "candidate_id": f"{CANDIDATE_ID}_{symbol}",
                    "family_id": FAMILY_ID,
                    "symbol": symbol,
                    "structure": "put_credit_spread",
                    "funnel_stage_before": "F0_MECHANISM",
                    "funnel_stage_after": "F1_TRAIN" if passed else "F0_MECHANISM",
                    "train_start": str(train.index[0].date()),
                    "train_end": str(train.index[-1].date()),
                    "untouched_holdout_start": str(holdout.index[0].date()),
                    "untouched_holdout_end": str(holdout.index[-1].date()),
                    "chronology_ok": True,
                    "train": candidate_axes,
                    "unconditional_control_train": control_axes,
                    "discovery_pass": passed,
                    "max_loss_usd": max_loss,
                    "one_lot_max_loss_usd": max_loss,
                    "operating_max_lots": 1,
                }
            )
            worst = min(_axis_value(candidate_axes[a], "gate_pnl", "pnl") for a in COST_AXES)
            print(
                f"{symbol}: n={min(int(candidate_axes[a]['n_trades']) for a in COST_AXES)} "
                f"worst_pnl={worst:.2f} pass={passed}",
                file=sys.stderr,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"symbol": symbol, "error": str(exc)})

    survivors = [row for row in rows if row["discovery_pass"]]
    survivor = max(survivors, key=train_rank_key) if survivors else None
    pooled = sum(
        min(_axis_value(row["train"][a], "gate_pnl", "pnl") for a in COST_AXES)
        for row in survivors
    )
    advanced = survivor is not None and pooled > 0.0
    selected_symbols = [row["symbol"] for row in survivors]
    holdout_block = (
        run_holdout(symbols=selected_symbols, period=period, train_fraction=train_fraction)
        if advanced and selected_symbols
        else None
    )
    f2 = bool(holdout_block and holdout_block.get("any_holdout_survivor"))
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "BUILD_L0_PROXY",
        "paper_only": True,
        "program": "PCS_INCOME_AUTONOMY",
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "economic_mechanism": (
            "After a completed soft multi-day equity drawdown that is stabilizing "
            "(lag 5d still negative, lag 1d no longer cascading), defined-risk put credit "
            "spreads monetize non-collapse/mean-reversion; 50% profit targets harvest rebounds."
        ),
        "prior_family_note": (
            "V1–V3 each produced train-only single/multi-name dual-cost passes that failed "
            "sealed holdout under 5% slip. This entry class is not a threshold polish of those."
        ),
        "funnel_stage_before": "F0_MECHANISM",
        "funnel_stage_after": (
            "F2_UNTOUCHED_HOLDOUT" if f2 else ("F1_TRAIN" if advanced else "F0_MECHANISM")
        ),
        "option_mark_provenance": "black_scholes_proxy",
        "candidate_config": candidate_config,
        "control_config": control_config,
        "gates": {
            "minimum_trades_each_train_cost_axis": MIN_TRADES,
            "positive_pnl_each_train_cost_axis": True,
            "max_loss_usd_one_lot": MAX_LOSS_USD,
            "max_dd_discovery_usd": MAX_DD_DISCOVERY_USD,
            "exact_integrity": True,
            "candidate_worst_axis_pnl_strictly_above_control": True,
        },
        "validity": {
            "holdout": "auto-run only for train survivors; frozen DNA; no retune",
            "population": normalized,
            "ranking_complete": len(errors) == 0 and len(rows) == len(normalized),
            "registry_writes": False,
            "capital_seat_claim": False,
            "trading_authority": False,
        },
        "train_fraction": train_fraction,
        "n_symbols": len(normalized),
        "n_completed": len(rows),
        "n_discovery_pass": len(survivors),
        "pooled_qualifying_worst_axis_pnl": pooled,
        "selected_candidate_id": survivor["candidate_id"] if advanced and survivor else None,
        "selected_symbol": survivor["symbol"] if advanced and survivor else None,
        "strategy_advanced_train": advanced,
        "holdout": holdout_block,
        "strategy_advanced_holdout": f2,
        "decision": (
            "STRATEGY_ADVANCED_F2"
            if f2
            else ("STRATEGY_ADVANCED_F1_HOLDOUT_FAILED" if advanced else "FAMILY_CLOSED")
        ),
        "next_seed_if_closed": (
            "PCS_INCOME_DIMINISHING_RETURNS_CHECKPOINT: four consecutive PCS entry families "
            "with holdout fail under dual cost imply pause adjacent entry mining; pivot to "
            "(a) structure/regime router with stand-aside purity, (b) longer DTE quality "
            "credit, or (c) observed-quote cost calibration only after a holdout survivor."
        ),
        "errors": errors,
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    parser.add_argument("--period", default="5y")
    parser.add_argument("--train-fraction", type=float, default=0.60)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    payload = run_lab(
        symbols=[v.strip().upper() for v in args.symbols.split(",") if v.strip()],
        period=args.period,
        train_fraction=args.train_fraction,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    summary: dict[str, Any] = {
        k: payload[k]
        for k in (
            "decision",
            "strategy_advanced_train",
            "strategy_advanced_holdout",
            "n_completed",
            "n_discovery_pass",
            "selected_symbol",
            "pooled_qualifying_worst_axis_pnl",
            "errors",
        )
    }
    if payload.get("holdout"):
        summary["holdout_decision"] = payload["holdout"].get("decision")
        summary["holdout_rows"] = [
            {
                "symbol": r["symbol"],
                "pass": r["holdout_dual_cost_pass"],
                "slip_pnl": r["holdout"]["slip_5pct"]["pnl"],
                "fix_pnl": r["holdout"]["fixed_0p01"]["pnl"],
                "slip_n": r["holdout"]["slip_5pct"]["n_trades"],
                "fix_n": r["holdout"]["fixed_0p01"]["n_trades"],
            }
            for r in payload["holdout"].get("rows") or []
        ]
    print(json.dumps(summary, indent=2, allow_nan=False))
    return 0 if payload["validity"]["ranking_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

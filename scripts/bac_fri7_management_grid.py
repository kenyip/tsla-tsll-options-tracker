#!/usr/bin/env python3
"""Fixed-cost-first BAC Fri7 $1 PCS management surface (paper/research only).

Varies defined_loss_exit_frac × profit_target × dte_stop × min_credit_pct only.
No width thrash. Audits independent ledger integrity before any seat claim.
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from trader_platform.evolve_tick import score_sim_metrics  # noqa: E402
from trader_platform.research.pcs_sim import PcsTrade, run_pcs_backtest  # noqa: E402
from trader_platform.strategy_dna import StrategyDNA  # noqa: E402

HYPS_PATH = _REPO / "trader_platform/data/hypotheses.yaml"
DEFAULT_SOURCE = "hyp_dna_bac_put_credit_spread_5f52fa0e"

# Absolute no-leader gates (empty quality seat)
MAX_LOSS_CAP = 300.0
WINDOW_DD_CAP = 75.0
DENSE_NEG_CAP = 5
MIN_TRADES = 8
LEDGER_DELTA_TOL = 1e-6


def ledger_integrity(trades: list[PcsTrade], reported_pnl: float) -> dict[str, Any]:
    closed = [t for t in trades if t.closed and t.exit_debit is not None]
    recomputed = sum(
        (t.net_credit - float(t.exit_debit or 0.0)) * 100.0 for t in closed
    )
    same_bar = sum(
        1
        for previous, following in zip(trades, trades[1:])
        if previous.exit_date is not None and previous.exit_date == following.entry_date
    )
    # Wrong collar-style formula that zeroed the prior restress audit
    bogus_collar_style = sum(
        ((getattr(t, "exit_value", None) or 0.0) - (getattr(t, "entry_package", None) or 0.0))
        * 100.0
        for t in closed
    )
    return {
        "n_trades_ledger": len(closed),
        "reported_pnl": float(reported_pnl),
        "recomputed_pnl": float(recomputed),
        "pnl_recompute_delta": float(recomputed - reported_pnl),
        "ledger_exact": abs(recomputed - reported_pnl) <= LEDGER_DELTA_TOL,
        "same_bar_reentries": int(same_bar),
        "bogus_collar_style_recompute": float(bogus_collar_style),
        "bogus_delta_vs_reported": float(bogus_collar_style - reported_pnl),
        "note": (
            "Correct PCS ledger: sum((net_credit - exit_debit)*100). "
            "Prior restress pnl_recompute_delta≈|pnl| was collar-field formula → 0 recomputed."
        ),
    }


def _metrics(sim) -> dict[str, Any]:
    if not sim.ok or sim.skipped:
        return {
            "ok": False,
            "skipped": True,
            "reason": sim.reason or "skipped",
            "n_trades": 0,
            "pnl": 0.0,
            "dd": 0.0,
            "wr_pct": 0.0,
            "pf": None,
            "verdict": "SKIP",
            "score": 0.0,
            "max_loss_usd": None,
            "capital_fit": None,
            "exit_reasons": {},
            "integrity": {
                "n_trades_ledger": 0,
                "reported_pnl": 0.0,
                "recomputed_pnl": 0.0,
                "pnl_recompute_delta": 0.0,
                "ledger_exact": True,
                "same_bar_reentries": 0,
            },
        }
    m = sim.metrics or {}
    n = int(sim.n_trades or m.get("n_trades") or 0)
    pnl = float(m.get("total_pnl_per_contract") or 0.0)
    wr = float(m.get("win_rate_pct") or 0.0)
    if wr == 0 and m.get("win_rate") is not None:
        wr = float(m["win_rate"])
        if wr <= 1:
            wr *= 100.0
    dd = float(m.get("max_dd_per_contract") or 0.0)
    try:
        pf = float(m.get("profit_factor") or 0.0)
    except (TypeError, ValueError):
        pf = float("nan")
    wr_unit = wr / 100.0 if wr > 1 else wr
    verdict, score, reason, pfc = score_sim_metrics(
        n_trades=n, pnl=pnl, win_rate=wr_unit, max_dd=dd, profit_factor=pf
    )
    cap = sim.capital or {}
    integrity = ledger_integrity(list(sim.trades or []), pnl)
    return {
        "ok": True,
        "skipped": False,
        "reason": reason,
        "n_trades": n,
        "pnl": round(pnl, 2),
        "dd": round(dd, 2),
        "wr_pct": round(wr if wr > 1 else wr * 100.0, 1),
        "pf": round(float(pfc), 3) if pfc == pfc else None,
        "verdict": verdict,
        "score": round(float(score), 2),
        "max_loss_usd": cap.get("max_loss_usd"),
        "capital_fit": cap.get("capital_fit"),
        "exit_reasons": m.get("exit_reasons") or {},
        "integrity": integrity,
    }


def _run(symbol: str, cfg: dict[str, Any], df: pd.DataFrame, period: str = "5y"):
    return run_pcs_backtest(
        symbol,
        period=period,
        use_cache=True,
        config=cfg,
        sleeve_usd=3000.0,
        open_risk_budget_usd=750.0,
        df=df,
        min_bars=15,
        structure="put_credit_spread",
    )


def window_summary(symbol: str, cfg: dict[str, Any], df: pd.DataFrame) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for y in sorted(set(df.index.year)):
        sub = df[df.index.year == y]
        if len(sub) < 15:
            continue
        m = _metrics(_run(symbol, cfg, sub, period=f"year_{y}"))
        if m["ok"]:
            rows.append({"label": f"year_{y}", **{k: m[k] for k in ("n_trades", "pnl", "dd", "verdict")}})
    chunk = 126
    for i, start in enumerate(range(0, max(0, len(df) - chunk + 1), chunk)):
        sub = df.iloc[start : start + chunk]
        if len(sub) < 15:
            continue
        label = f"chunk6m_{i}_{sub.index[0].date()}_{sub.index[-1].date()}"
        m = _metrics(_run(symbol, cfg, sub, period=label))
        if m["ok"]:
            rows.append({"label": label, **{k: m[k] for k in ("n_trades", "pnl", "dd", "verdict")}})

    dense_neg = [r for r in rows if int(r.get("n_trades") or 0) >= 3 and float(r.get("pnl") or 0) < 0]
    window_max_dd = max((float(r.get("dd") or 0) for r in rows), default=0.0)
    worst_pnl = min((float(r.get("pnl") or 0) for r in rows), default=0.0)
    return {
        "n_windows_ok": len(rows),
        "dense_neg_count": len(dense_neg),
        "window_max_dd": round(window_max_dd, 2),
        "worst_window_pnl": round(worst_pnl, 2),
        "windows": rows,
    }


def absolute_pass(fixed: dict[str, Any], slip5: dict[str, Any], windows: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not fixed.get("ok"):
        reasons.append("fixed_not_ok")
    if int(fixed.get("n_trades") or 0) < MIN_TRADES:
        reasons.append(f"fixed_n<{MIN_TRADES}")
    if float(fixed.get("pnl") or 0) <= 0:
        reasons.append("fixed_pnl_not_positive")
    if fixed.get("verdict") != "SHIP":
        reasons.append(f"fixed_verdict={fixed.get('verdict')}")
    integ = fixed.get("integrity") or {}
    if not integ.get("ledger_exact"):
        reasons.append(f"ledger_delta={integ.get('pnl_recompute_delta')}")
    if int(integ.get("same_bar_reentries") or 0) != 0:
        reasons.append("same_bar_reentries")
    ml = float(fixed.get("max_loss_usd") or 1e9)
    if ml > MAX_LOSS_CAP:
        reasons.append(f"fixed_ml={ml}>{MAX_LOSS_CAP}")
    wdd = float(windows.get("window_max_dd") or 1e9)
    if wdd > WINDOW_DD_CAP:
        reasons.append(f"window_dd={wdd}>{WINDOW_DD_CAP}")
    dneg = int(windows.get("dense_neg_count") or 99)
    if dneg > DENSE_NEG_CAP:
        reasons.append(f"dense_neg={dneg}>{DENSE_NEG_CAP}")
    if not slip5.get("ok"):
        reasons.append("slip5_not_ok")
    if int(slip5.get("n_trades") or 0) < MIN_TRADES:
        reasons.append(f"slip5_n<{MIN_TRADES}")
    if float(slip5.get("pnl") or 0) <= 0:
        reasons.append("slip5_pnl_not_positive")
    if slip5.get("verdict") != "SHIP":
        reasons.append(f"slip5_verdict={slip5.get('verdict')}")
    s5_ml = float(slip5.get("max_loss_usd") or 1e9)
    if s5_ml > MAX_LOSS_CAP:
        reasons.append(f"slip5_ml={s5_ml}>{MAX_LOSS_CAP}")
    return (len(reasons) == 0, reasons)


def _csv_floats(raw: str) -> list[float]:
    return [float(x.strip()) for x in raw.split(",") if x.strip()]


def _csv_ints(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-hyp", default=DEFAULT_SOURCE)
    ap.add_argument("--period", default="5y")
    ap.add_argument("--loss-exits", default="0.50,0.70,0.85,1.00")
    ap.add_argument("--profit-targets", default="0.25,0.35,0.50,0.65")
    ap.add_argument("--dte-stops", default="1,2,3,5")
    ap.add_argument("--min-credits", default="0.010,0.015,0.02127,0.030,0.040")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    store = yaml.safe_load(HYPS_PATH.read_text()) or {}
    by_id = {h["id"]: h for h in (store.get("hypotheses") or []) if isinstance(h, dict)}
    if args.source_hyp not in by_id:
        print(f"missing hyp {args.source_hyp}", file=sys.stderr)
        return 1
    hyp = by_id[args.source_hyp]
    dna = StrategyDNA.from_dict(hyp["dna"])
    assert dna is not None
    base = dict(dna.pcs_config() if hasattr(dna, "pcs_config") else (dna.config or {}))
    # Fri7 $1 locked surface (time/width already fixed by prior wakes)
    base.update(
        {
            "structure": "put_credit_spread",
            "long_dte": 7,
            "spread_width": 1.0,
            "entry_weekdays": [4],
            "long_target_delta": float(base.get("long_target_delta") or 0.2),
            "max_loss_budget_usd": float(base.get("max_loss_budget_usd") or 250.0),
            "max_loss_mult": float(base.get("max_loss_mult") or 1.8),
            "delta_breach": float(base.get("delta_breach") or 0.45),
            "regime_flip_exit_enabled": bool(base.get("regime_flip_exit_enabled", True)),
            "wheel_enabled": False,
            "roll_on_max_loss": bool(base.get("roll_on_max_loss", True)),
            "bear_dte": int(base.get("bear_dte") or 3),
            "bear_target_delta": float(base.get("bear_target_delta") or 0.2),
            "iv_rank_min": float(base.get("iv_rank_min") or 0.0),
            "slippage_pct": 0.0,
        }
    )

    symbol = (dna.symbols or ["BAC"])[0].upper()
    print(f"loading {symbol} {args.period}…", file=sys.stderr)
    df = build(symbol, period=args.period, use_cache=True)
    print(f"df {symbol} n={len(df)} {df.index[0].date()}→{df.index[-1].date()}", file=sys.stderr)

    # --- Phase A: baseline fixed-path integrity audit ---
    baseline_cfg = deepcopy(base)
    baseline_cfg.update(
        {
            "defined_loss_exit_frac": 0.85,
            "profit_target": 0.35,
            "dte_stop": 5,
            "min_credit_pct": 0.021270479503790872,
            "half_spread_per_leg": 0.01,
            "slippage_pct": 0.0,
        }
    )
    base_sim = _run(symbol, baseline_cfg, df)
    baseline_fixed = _metrics(base_sim)
    print(
        f"baseline fixed $0.01: n={baseline_fixed.get('n_trades')} pnl={baseline_fixed.get('pnl')} "
        f"ledger_exact={baseline_fixed['integrity']['ledger_exact']} "
        f"delta={baseline_fixed['integrity']['pnl_recompute_delta']} "
        f"bogus_delta={baseline_fixed['integrity']['bogus_delta_vs_reported']}",
        file=sys.stderr,
    )

    loss_exits = _csv_floats(args.loss_exits)
    profit_targets = _csv_floats(args.profit_targets)
    dte_stops = _csv_ints(args.dte_stops)
    min_credits = _csv_floats(args.min_credits)
    for stop in dte_stops:
        if stop >= 7:
            raise SystemExit(f"dte_stop {stop} must be < long_dte 7")

    grid = list(product(loss_exits, profit_targets, dte_stops, min_credits))
    rows: list[dict[str, Any]] = []
    for i, (loss_exit, pt, dte_stop, min_credit) in enumerate(grid, 1):
        cfg = deepcopy(base)
        cfg.update(
            {
                "defined_loss_exit_frac": loss_exit,
                "profit_target": pt,
                "dte_stop": dte_stop,
                "min_credit_pct": min_credit,
                "half_spread_per_leg": 0.01,
                "slippage_pct": 0.0,
            }
        )
        fixed = _metrics(_run(symbol, cfg, df))
        row = {
            "config": {
                "defined_loss_exit_frac": loss_exit,
                "profit_target": pt,
                "dte_stop": dte_stop,
                "min_credit_pct": min_credit,
                "long_dte": 7,
                "spread_width": 1.0,
                "entry_weekdays": [4],
            },
            "fixed_0p01": fixed,
            "candidate": (
                fixed.get("ok")
                and int(fixed.get("n_trades") or 0) >= MIN_TRADES
                and float(fixed.get("pnl") or 0) > 0
                and (fixed.get("integrity") or {}).get("ledger_exact")
                and int((fixed.get("integrity") or {}).get("same_bar_reentries") or 0) == 0
                and float(fixed.get("max_loss_usd") or 1e9) <= MAX_LOSS_CAP
            ),
        }
        rows.append(row)
        if i % 40 == 0 or i == len(grid):
            print(f"grid fixed {i}/{len(grid)}", file=sys.stderr)

    candidates = [r for r in rows if r["candidate"]]
    print(f"fixed-positive candidates: {len(candidates)} / {len(rows)}", file=sys.stderr)

    # --- Phase C: 5% + windows only for fixed-positive candidates ---
    deep: list[dict[str, Any]] = []
    for j, row in enumerate(candidates, 1):
        cfg = deepcopy(base)
        cfg.update(row["config"])
        cfg_slip = deepcopy(cfg)
        cfg_slip["half_spread_per_leg"] = 0.0
        cfg_slip["slippage_pct"] = 0.05
        cfg_fixed = deepcopy(cfg)
        cfg_fixed["half_spread_per_leg"] = 0.01
        cfg_fixed["slippage_pct"] = 0.0
        slip5 = _metrics(_run(symbol, cfg_slip, df))
        windows = window_summary(symbol, cfg_fixed, df)
        passed, reasons = absolute_pass(row["fixed_0p01"], slip5, windows)
        deep_row = {
            **row,
            "slip_5pct": slip5,
            "windows": {
                "dense_neg_count": windows["dense_neg_count"],
                "window_max_dd": windows["window_max_dd"],
                "worst_window_pnl": windows["worst_window_pnl"],
                "n_windows_ok": windows["n_windows_ok"],
            },
            "absolute_pass": passed,
            "absolute_fail_reasons": reasons,
        }
        deep.append(deep_row)
        print(
            f"deep {j}/{len(candidates)} pt={row['config']['profit_target']} "
            f"dl={row['config']['defined_loss_exit_frac']} stop={row['config']['dte_stop']} "
            f"mc={row['config']['min_credit_pct']}: fixed={row['fixed_0p01']['pnl']} "
            f"slip5={slip5.get('pnl')} wdd={windows['window_max_dd']} pass={passed} {reasons[:3]}",
            file=sys.stderr,
        )

    pass_rows = [r for r in deep if r["absolute_pass"]]
    # Rank: highest min(fixed,slip5) pnl, then tighter window dd
    def rank_key(r: dict[str, Any]) -> tuple:
        f = r["fixed_0p01"]
        s = r.get("slip_5pct") or {}
        w = r.get("windows") or {}
        return (
            r.get("absolute_pass", False),
            min(float(f.get("pnl") or -1e9), float(s.get("pnl") or -1e9)),
            -float(w.get("window_max_dd") or 1e9),
            -int(w.get("dense_neg_count") or 99),
            min(int(f.get("n_trades") or 0), int(s.get("n_trades") or 0)),
        )

    deep.sort(key=rank_key, reverse=True)
    rows_sorted = sorted(
        rows,
        key=lambda r: (
            r["candidate"],
            float(r["fixed_0p01"].get("pnl") or -1e9),
            -float(r["fixed_0p01"].get("dd") or 1e9),
        ),
        reverse=True,
    )

    decision = (
        "DISCOVERY_PASS_REQUIRES_PAPER_PATH"
        if pass_rows
        else "REJECT_BAC_FRI7_MANAGEMENT_SURFACE_THIS_CYCLE"
    )
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "paper_only": True,
        "source_hyp": args.source_hyp,
        "symbol": symbol,
        "structure": "put_credit_spread",
        "locked": {
            "long_dte": 7,
            "spread_width": 1.0,
            "entry_weekdays": [4],
            "note": "no width thrash; management surface only",
        },
        "gates": {
            "min_trades": MIN_TRADES,
            "max_loss_cap": MAX_LOSS_CAP,
            "window_dd_cap": WINDOW_DD_CAP,
            "dense_neg_cap": DENSE_NEG_CAP,
            "require_fixed_ship_positive": True,
            "require_slip5_ship_positive": True,
            "ledger_exact": True,
        },
        "baseline_fixed_audit": {
            "config": {
                "defined_loss_exit_frac": 0.85,
                "profit_target": 0.35,
                "dte_stop": 5,
                "min_credit_pct": 0.021270479503790872,
                "half_spread_per_leg": 0.01,
            },
            "metrics": baseline_fixed,
            "integrity_diagnosis": {
                "ledger_exact": baseline_fixed["integrity"]["ledger_exact"],
                "correct_delta": baseline_fixed["integrity"]["pnl_recompute_delta"],
                "bogus_collar_style_delta": baseline_fixed["integrity"]["bogus_delta_vs_reported"],
                "explanation": (
                    "Prior artifact stored pnl_recompute_delta≈|pnl| because recompute used "
                    "collar fields (exit_value/entry_package) missing on PcsTrade → 0 − reported."
                ),
            },
        },
        "grid_size": len(rows),
        "n_fixed_positive_candidates": len(candidates),
        "n_absolute_pass": len(pass_rows),
        "decision": decision,
        "top_fixed_rows": rows_sorted[:15],
        "deep_candidates": deep,
        "pass_rows": pass_rows,
        "best_fixed_positive": rows_sorted[0] if rows_sorted and rows_sorted[0]["candidate"] else None,
        "best_absolute": pass_rows[0] if pass_rows else (deep[0] if deep else None),
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
                "decision": decision,
                "n_grid": len(rows),
                "n_fixed_positive": len(candidates),
                "n_absolute_pass": len(pass_rows),
                "baseline_ledger_exact": baseline_fixed["integrity"]["ledger_exact"],
                "baseline_fixed_pnl": baseline_fixed.get("pnl"),
                "best_fixed_pnl": (rows_sorted[0]["fixed_0p01"].get("pnl") if rows_sorted else None),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

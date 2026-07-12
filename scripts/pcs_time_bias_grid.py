#!/usr/bin/env python3
"""Paper-only DTE / profit-target / DTE-stop grid for registered defined-risk hypotheses."""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from trader_platform.evolve_tick import score_sim_metrics  # noqa: E402
from trader_platform.research.pcs_sim import run_pcs_backtest  # noqa: E402
from trader_platform.strategy_dna import StrategyDNA  # noqa: E402

HYPS_PATH = _REPO / "trader_platform/data/hypotheses.yaml"
DEFAULT_HYP_ID = "hyp_dna_tsll_put_credit_spread_b195f5fe"


def _csv_numbers(raw: str, cast: type) -> list[Any]:
    return [cast(value.strip()) for value in raw.split(",") if value.strip()]


def _weekday_slices(raw: str) -> list[tuple[str, list[int] | None]]:
    names = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4}
    slices: list[tuple[str, list[int] | None]] = []
    for value in (part.strip().lower() for part in raw.split(",")):
        if not value:
            continue
        if value == "all":
            slices.append(("all", None))
        elif value in names:
            slices.append((value, [names[value]]))
        else:
            raise SystemExit(f"invalid entry weekday slice {value!r}; use all,mon,tue,wed,thu,fri")
    if not slices:
        raise SystemExit("at least one entry weekday slice is required")
    return slices


def _load_hyp(hyp_id: str) -> dict[str, Any]:
    store = yaml.safe_load(HYPS_PATH.read_text()) or {}
    for hyp in store.get("hypotheses") or []:
        if isinstance(hyp, dict) and hyp.get("id") == hyp_id:
            return hyp
    raise SystemExit(f"missing hyp {hyp_id}")


def _hyp_ids(hyp: str | None, hyps: str | None) -> list[str]:
    if hyp and hyps:
        raise SystemExit("use either --hyp or --hyps, not both")
    values = hyps or hyp or DEFAULT_HYP_ID
    ids = [value.strip() for value in values.split(",") if value.strip()]
    if not ids:
        raise SystemExit("at least one hypothesis is required")
    return ids


def _row(
    result,
    cfg: dict[str, Any],
    *,
    hyp_id: str,
    symbol: str,
    structure: str,
) -> dict[str, Any]:
    metrics = result.metrics or {}
    n_trades = int(result.n_trades or metrics.get("n_trades") or 0)
    pnl = float(metrics.get("total_pnl_per_contract") or 0.0)
    win_rate = float(metrics.get("win_rate_pct") or 0.0) / 100.0
    max_dd = float(metrics.get("max_dd_per_contract") or 0.0)
    profit_factor = float(metrics.get("profit_factor") or 0.0)
    verdict, score, reason, pf_capped = score_sim_metrics(
        n_trades=n_trades,
        pnl=pnl,
        win_rate=win_rate,
        max_dd=max_dd,
        profit_factor=profit_factor,
    )
    capital = result.capital or {}
    return {
        "hyp_id": hyp_id,
        "symbol": symbol,
        "structure": structure,
        "long_dte": int(cfg["long_dte"]),
        "profit_target": float(cfg["profit_target"]),
        "dte_stop": int(cfg["dte_stop"]),
        "entry_weekday": str(cfg.get("entry_weekday_label") or "all"),
        "entry_weekdays": cfg.get("entry_weekdays"),
        "verdict": verdict,
        "reason": reason,
        "score": round(float(score), 2),
        "n_trades": n_trades,
        "pnl": round(pnl, 2),
        "win_rate_pct": round(win_rate * 100.0, 1),
        "profit_factor": round(float(pf_capped), 3),
        "max_dd": round(max_dd, 2),
        "avg_days_held": round(float(metrics.get("avg_days_held") or 0.0), 2),
        "exit_reasons": metrics.get("exit_reasons") or {},
        "capital_fit_usd": capital.get("capital_fit_usd"),
        "max_loss_usd": capital.get("max_loss_usd"),
        "max_lots": capital.get("max_lots"),
        "capital_fit": capital.get("capital_fit"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hyp")
    parser.add_argument("--hyps", help="comma-separated registered PCS/CCS/IC hypothesis ids")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--dtes", default="7,14,21,30")
    parser.add_argument("--profit-targets", default="0.35,0.50,0.65")
    parser.add_argument("--dte-stops", default="1,3,5")
    parser.add_argument("--entry-weekday-slices", default="all,mon,tue,wed,thu,fri")
    parser.add_argument("--slippage-pct", type=float, default=0.0)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    hyp_ids = _hyp_ids(args.hyp, args.hyps)
    dtes = _csv_numbers(args.dtes, int)
    profit_targets = _csv_numbers(args.profit_targets, float)
    dte_stops = _csv_numbers(args.dte_stops, int)
    weekday_slices = _weekday_slices(args.entry_weekday_slices)
    data_by_symbol = {}
    hypotheses = []
    rows = []
    for hyp_id in hyp_ids:
        hyp = _load_hyp(hyp_id)
        dna = StrategyDNA.from_dict(hyp.get("dna"))
        if dna is None:
            raise SystemExit(f"hyp {hyp_id} has no DNA")
        symbol = (dna.symbols or ["TSLL"])[0].upper()
        structure = str(dna.structure or hyp.get("structure") or "put_credit_spread")
        if structure not in {"put_credit_spread", "call_credit_spread", "iron_condor"}:
            raise SystemExit(f"hyp {hyp_id} structure {structure!r} is not supported by pcs_sim")
        base_cfg = dna.pcs_config()
        base_cfg["structure"] = structure
        if symbol not in data_by_symbol:
            data_by_symbol[symbol] = build(symbol, period=args.period, use_cache=True)
        df = data_by_symbol[symbol]

        hyp_rows = []
        for dte, profit_target, dte_stop, weekday_slice in product(
            dtes, profit_targets, dte_stops, weekday_slices
        ):
            if dte_stop >= dte:
                continue
            weekday_label, entry_weekdays = weekday_slice
            cfg = deepcopy(base_cfg)
            cfg.update(
                long_dte=dte,
                profit_target=profit_target,
                dte_stop=dte_stop,
                entry_weekday_label=weekday_label,
                entry_weekdays=entry_weekdays,
                slippage_pct=args.slippage_pct,
            )
            result = run_pcs_backtest(
                symbol,
                period=args.period,
                use_cache=True,
                config=cfg,
                sleeve_usd=3000.0,
                open_risk_budget_usd=750.0,
                df=df,
                min_bars=15,
                structure=structure,
            )
            hyp_rows.append(
                _row(
                    result,
                    cfg,
                    hyp_id=hyp_id,
                    symbol=symbol,
                    structure=structure,
                )
            )

        baseline = next(
            (
                row
                for row in hyp_rows
                if row["long_dte"] == int(base_cfg.get("long_dte", 0))
                and row["profit_target"] == float(base_cfg.get("profit_target", 0.0))
                and row["dte_stop"] == int(base_cfg.get("dte_stop", 0))
                and row["entry_weekday"] == "all"
            ),
            None,
        )
        hypotheses.append(
            {
                "hyp_id": hyp_id,
                "symbol": symbol,
                "structure": structure,
                "n_bars": int(len(df)),
                "base_config": base_cfg,
                "baseline": baseline,
                "n_rows": len(hyp_rows),
            }
        )
        rows.extend(hyp_rows)

    rows.sort(
        key=lambda row: (
            row["verdict"] == "SHIP",
            row["pnl"],
            -row["max_dd"],
            row["n_trades"],
        ),
        reverse=True,
    )
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "paper_only": True,
        "hyp_ids": hyp_ids,
        "hypotheses": hypotheses,
        "period": args.period,
        "slippage_pct": args.slippage_pct,
        "grid": {
            "long_dte": dtes,
            "profit_target": profit_targets,
            "dte_stop": dte_stops,
            "entry_weekday_slices": [label for label, _ in weekday_slices],
        },
        "ranked": rows,
        "note": "Discovery grid only. A better full-history row is not promoted; B3+B4 remain mandatory.",
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = _REPO / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")

    print(f"time_bias_grid hyps={len(hyp_ids)} rows={len(rows)} period={args.period}")
    for row in rows[:8]:
        print(
            f"{row['verdict']:6} {row['structure'][:3]}/{row['symbol']:4} day={row['entry_weekday']:3} "
            f"dte={row['long_dte']:2} pt={row['profit_target']:.2f} "
            f"stop={row['dte_stop']:2} n={row['n_trades']:3} pnl={row['pnl']:8.2f} "
            f"dd={row['max_dd']:7.2f} ml={row['max_loss_usd']}"
        )
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

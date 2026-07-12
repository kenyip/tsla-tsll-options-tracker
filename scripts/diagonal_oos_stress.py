#!/usr/bin/env python3
"""Exact-DNA chronological OOS and entry-density stress for registered diagonals."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from trader_platform.research.diagonal_sim import run_diagonal_backtest  # noqa: E402
from trader_platform.strategy_dna import StrategyDNA  # noqa: E402

HYPS_PATH = _REPO / "trader_platform/data/hypotheses.yaml"


def _summary(result) -> dict[str, Any]:
    metrics = result.metrics or {}
    entry_years = Counter(str(trade.entry_date.year) for trade in result.trades)
    return {
        "ok": bool(result.ok and not result.skipped),
        "reason": result.reason,
        "n_trades": int(result.n_trades),
        "pnl": round(float(metrics.get("total_pnl_per_contract") or 0.0), 2),
        "max_dd": round(float(metrics.get("max_dd_per_contract") or 0.0), 2),
        "win_rate_pct": round(float(metrics.get("win_rate_pct") or 0.0), 1),
        "profit_factor": round(float(metrics.get("profit_factor") or 0.0), 3),
        "max_loss_usd": (result.capital or {}).get("max_loss_usd"),
        "capital_fit": (result.capital or {}).get("capital_fit"),
        "entry_years": dict(sorted(entry_years.items())),
        "n_entry_years": len(entry_years),
    }


def _run(symbol: str, label: str, frame, config: dict[str, Any]) -> dict[str, Any]:
    result = run_diagonal_backtest(
        symbol,
        period=label,
        config=config,
        df=frame,
        sleeve_usd=3000.0,
    )
    return _summary(result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hyps", required=True, help="comma-separated registered diagonal hyp ids")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--train-fraction", type=float, default=0.60)
    parser.add_argument("--slippage-pct", type=float, default=0.05)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if not 0.50 <= args.train_fraction <= 0.80:
        raise SystemExit("--train-fraction must be between 0.50 and 0.80")
    if args.slippage_pct < 0:
        raise SystemExit("--slippage-pct must be non-negative")

    store = yaml.safe_load(HYPS_PATH.read_text()) or {}
    by_id = {hyp["id"]: hyp for hyp in (store.get("hypotheses") or [])}
    ids = [value.strip() for value in args.hyps.split(",") if value.strip()]
    missing = [hyp_id for hyp_id in ids if hyp_id not in by_id]
    if missing:
        raise SystemExit(f"missing hyps: {missing}")

    frames: dict[str, Any] = {}
    results = []
    for hyp_id in ids:
        hyp = by_id[hyp_id]
        dna = StrategyDNA.from_dict(hyp.get("dna"))
        if dna is None or dna.structure != "diagonal_spread":
            raise SystemExit(f"{hyp_id} is not diagonal_spread DNA")
        symbol = (dna.symbols or [""])[0].upper()
        if symbol not in frames:
            frames[symbol] = build(symbol, period=args.period, use_cache=True)
        frame = frames[symbol]
        split_index = int(len(frame) * args.train_fraction)
        train = frame.iloc[:split_index]
        test = frame.iloc[split_index:]
        config = dna.sim_config()
        after_cost = deepcopy(config)
        after_cost["slippage_pct"] = args.slippage_pct
        results.append(
            {
                "hyp_id": hyp_id,
                "dna_id": dna.ensure_id(),
                "symbol": symbol,
                "config": config,
                "split": {
                    "train_start": str(train.index[0].date()),
                    "train_end": str(train.index[-1].date()),
                    "test_start": str(test.index[0].date()),
                    "test_end": str(test.index[-1].date()),
                    "train_bars": len(train),
                    "test_bars": len(test),
                },
                "train": _run(symbol, "train", train, config),
                "test": _run(symbol, "test", test, config),
                "train_after_cost": _run(symbol, "train_after_cost", train, after_cost),
                "test_after_cost": _run(symbol, "test_after_cost", test, after_cost),
            }
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period": args.period,
        "train_fraction": args.train_fraction,
        "slippage_pct": args.slippage_pct,
        "sleeve_usd": 3000,
        "note": "Chronological split using exact registered DNA; no fitting. After-cost reruns apply adverse slippage to both legs and exits.",
        "results": results,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    print(json.dumps({"out": str(out), "results": results}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

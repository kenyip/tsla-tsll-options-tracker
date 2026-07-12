#!/usr/bin/env python3
"""Uniform fixed-dollar per-leg half-spread stress for defined-risk option proxies."""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from data import build  # noqa: E402
from scripts.pcs_cost_stress import _load_hyps, _metrics_row  # noqa: E402
from trader_platform.research.butterfly_sim import run_butterfly_backtest  # noqa: E402
from trader_platform.research.calendar_sim import run_calendar_backtest  # noqa: E402
from trader_platform.research.debit_vertical_sim import run_debit_vertical_backtest  # noqa: E402
from trader_platform.research.diagonal_sim import run_diagonal_backtest  # noqa: E402
from trader_platform.research.iron_butterfly_sim import run_iron_butterfly_backtest  # noqa: E402
from trader_platform.research.pcs_sim import run_pcs_backtest  # noqa: E402
from trader_platform.research.put_ratio_backspread_sim import run_put_ratio_backspread_backtest  # noqa: E402
from trader_platform.strategy_dna import StrategyDNA  # noqa: E402

DEFAULT_HYPS = [
    "hyp_dna_tsll_put_credit_spread_b195f5fe",
    "hyp_dna_amd_iron_condor_b3056133",
    "hyp_dna_smci_iron_butterfly_8444c65b",
    "hyp_dna_tsll_iron_butterfly_486c4c32",
]
DEFAULT_HALF_SPREADS = [0.0, 0.01, 0.025, 0.05]
OUT = _REPO / ".cache/platform/fixed_leg_cost_lab.json"


def _run(dna: StrategyDNA, df, config: dict[str, Any], period: str):
    symbol = (dna.symbols or ["TSLL"])[0].upper()
    structure = str(dna.structure)
    if structure == "put_ratio_backspread":
        return run_put_ratio_backspread_backtest(
            symbol,
            period=period,
            config=config,
            sleeve_usd=3000.0,
            open_risk_budget_usd=750.0,
            df=df,
            min_bars=15,
        )
    if structure in {"iron_butterfly", "broken_wing_iron_butterfly"}:
        return run_iron_butterfly_backtest(
            symbol,
            period=period,
            config=config,
            sleeve_usd=3000.0,
            open_risk_budget_usd=750.0,
            df=df,
            min_bars=15,
        )
    if structure in {"bull_call_debit_spread", "bear_put_debit_spread"}:
        return run_debit_vertical_backtest(
            symbol,
            structure=structure,
            period=period,
            config=config,
            sleeve_usd=3000.0,
            open_risk_budget_usd=750.0,
            df=df,
            min_bars=15,
        )
    proxy_runners = {
        "butterfly_spread": run_butterfly_backtest,
        "diagonal_spread": run_diagonal_backtest,
        "calendar_spread": run_calendar_backtest,
    }
    if structure in proxy_runners:
        return proxy_runners[structure](
            symbol,
            period=period,
            config=config,
            sleeve_usd=3000.0,
            open_risk_budget_usd=750.0,
            df=df,
            min_bars=15,
        )
    if structure not in {"put_credit_spread", "call_credit_spread", "iron_condor"}:
        raise ValueError(f"unsupported fixed-cost structure: {structure}")
    return run_pcs_backtest(
        symbol,
        period=period,
        config=config,
        sleeve_usd=3000.0,
        open_risk_budget_usd=750.0,
        df=df,
        min_bars=15,
        structure=structure,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hyps", default=",".join(DEFAULT_HYPS))
    parser.add_argument("--half-spreads", default=",".join(str(x) for x in DEFAULT_HALF_SPREADS))
    parser.add_argument("--period", default="5y")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    ids = [value.strip() for value in args.hyps.split(",") if value.strip()]
    half_spreads = [float(value.strip()) for value in args.half_spreads.split(",") if value.strip()]
    hyps = _load_hyps(ids)
    frames: dict[str, Any] = {}
    results = []
    for hyp in hyps:
        dna = StrategyDNA.from_dict(hyp["dna"])
        assert dna is not None
        symbol = (dna.symbols or ["TSLL"])[0].upper()
        if symbol not in frames:
            print(f"loading {symbol} {args.period}…", file=sys.stderr)
            frames[symbol] = build(symbol, period=args.period, use_cache=True)
        base = dna.pcs_config() if hasattr(dna, "pcs_config") else dict(dna.config or {})
        base = dict(base)
        base["structure"] = dna.structure
        rows = []
        for half_spread in half_spreads:
            config = deepcopy(base)
            config["slippage_pct"] = 0.0
            config["half_spread_per_leg"] = half_spread
            sim = _run(dna, frames[symbol], config, args.period)
            row = _metrics_row(sim, 0.0)
            row.pop("slippage_pct", None)
            row["half_spread_per_leg"] = half_spread
            leg_count = 4 if dna.structure in {
                "iron_condor", "iron_butterfly", "broken_wing_iron_butterfly", "butterfly_spread"
            } else (3 if dna.structure == "put_ratio_backspread" else 2)
            row["leg_count"] = leg_count
            row["round_trip_cost_usd"] = round(
                half_spread * leg_count * 2.0 * 100.0, 2
            )
            rows.append(row)
        results.append(
            {
                "hyp_id": hyp["id"],
                "symbol": symbol,
                "structure": dna.structure,
                "base_config": base,
                "by_half_spread": rows,
            }
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period": args.period,
        "sleeve_usd": 3000,
        "half_spreads_per_leg": half_spreads,
        "note": "Fixed option-price dollars per leg, adverse at entry and exit; not observed quotes.",
        "results": results,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    print(json.dumps({"out": str(out), "results": results}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Report exact observed-quote coverage for registered PCS/CCS/IC trade legs."""
from __future__ import annotations

import argparse
import glob
import json
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from trader_platform.research.option_quote_observations import (  # noqa: E402
    StrategyLegRequirement,
    join_strategy_leg_requirements,
    load_observations_csv,
    summarize_join_coverage,
)
from trader_platform.research.pcs_sim import PcsTrade, run_pcs_backtest  # noqa: E402
from trader_platform.strategy_dna import StrategyDNA  # noqa: E402

_HYPS_PATH = _REPO / "trader_platform/data/hypotheses.yaml"
_SUPPORTED = {"put_credit_spread", "call_credit_spread", "iron_condor"}


def _load_hyp(hyp_id: str) -> dict[str, Any]:
    store = yaml.safe_load(_HYPS_PATH.read_text()) or {}
    by_id = {
        hyp["id"]: hyp
        for hyp in store.get("hypotheses") or []
        if isinstance(hyp, dict) and hyp.get("id")
    }
    if hyp_id not in by_id:
        raise SystemExit(f"missing hyp {hyp_id}")
    return by_id[hyp_id]


def _event_at(value, event_hour_utc: int) -> datetime:
    day = value.date()
    return datetime.combine(day, time(event_hour_utc), tzinfo=timezone.utc)


def _trade_legs(trade: PcsTrade) -> list[tuple[str, str, float]]:
    if trade.right == "iron_condor":
        return [
            ("short_put", "put", trade.short_strike),
            ("long_put", "put", trade.long_strike),
            ("short_call", "call", trade.call_short_strike),
            ("long_call", "call", trade.call_long_strike),
        ]
    option_type = "call" if trade.right == "call" else "put"
    return [
        (f"short_{option_type}", option_type, trade.short_strike),
        (f"long_{option_type}", option_type, trade.long_strike),
    ]


def requirements_from_trades(
    symbol: str, trades: list[PcsTrade], *, event_hour_utc: int
) -> list[StrategyLegRequirement]:
    requirements: list[StrategyLegRequirement] = []
    for index, trade in enumerate(trades):
        events = [("entry", trade.entry_date), ("exit", trade.exit_date)]
        for event_kind, event_date in events:
            if event_date is None:
                continue
            for role, option_type, strike in _trade_legs(trade):
                requirements.append(
                    StrategyLegRequirement(
                        event_id=f"trade-{index}:{event_kind}:{role}",
                        event_kind=event_kind,
                        event_at=_event_at(event_date, event_hour_utc),
                        symbol=symbol,
                        expiration=trade.expiration.date(),
                        option_type=option_type,
                        strike=float(strike),
                    )
                )
    return requirements


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hyp", required=True, help="Registered PCS/CCS/IC hypothesis id")
    parser.add_argument("--quotes", required=True, help="Glob for normalized observed quote CSVs")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--event-hour-utc", type=int, default=20)
    parser.add_argument("--max-age-minutes", type=int, default=30)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    if not 0 <= args.event_hour_utc <= 23:
        parser.error("--event-hour-utc must be 0..23")
    if args.max_age_minutes <= 0:
        parser.error("--max-age-minutes must be positive")

    hyp = _load_hyp(args.hyp)
    dna = StrategyDNA.from_dict(hyp.get("dna"))
    if dna is None:
        raise SystemExit(f"hyp {args.hyp} has no Strategy DNA")
    structure = str(dna.structure)
    if structure not in _SUPPORTED:
        raise SystemExit(f"unsupported structure for exact quote join: {structure}")
    symbol = (dna.symbols or [""])[0].upper()
    cfg = dna.pcs_config()
    result = run_pcs_backtest(
        symbol,
        period=args.period,
        use_cache=True,
        config=cfg,
        sleeve_usd=3000.0,
        open_risk_budget_usd=750.0,
        structure=structure,
    )
    if not result.ok or result.skipped or not result.trades:
        raise SystemExit(f"no usable simulated trades: {result.reason}")

    quote_paths = sorted(glob.glob(args.quotes))
    if not quote_paths:
        raise SystemExit(f"no quote archives matched {args.quotes}")
    observations = []
    for path in quote_paths:
        observations.extend(load_observations_csv(path, require_observed=True))

    requirements = requirements_from_trades(
        symbol, result.trades, event_hour_utc=args.event_hour_utc
    )
    matches = join_strategy_leg_requirements(
        requirements,
        observations,
        max_quote_age=timedelta(minutes=args.max_age_minutes),
    )
    summary = summarize_join_coverage(matches)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hyp_id": args.hyp,
        "dna_id": dna.ensure_id(),
        "symbol": symbol,
        "structure": structure,
        "period": args.period,
        "n_sim_trades": len(result.trades),
        "event_time_assumption": f"{args.event_hour_utc:02d}:00:00Z daily-bar decision",
        "max_quote_age_minutes": args.max_age_minutes,
        "quote_paths": quote_paths,
        "n_quote_observations": len(observations),
        "coverage": summary,
        "calibration_decision": "ELIGIBLE" if summary["calibration_eligible"] else "REJECT_INSUFFICIENT_COVERAGE",
        "unmatched_sample": [row.to_dict() for row in matches if row.observation is None][:20],
    }
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

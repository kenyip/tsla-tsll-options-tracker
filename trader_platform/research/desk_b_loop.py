"""Desk B operator loop: bounded evolve → living status → watch → paper handoff.

Research/paper only. Never arms live. Designed for cron or `just trader-desk-b-loop`.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Sequence

from trader_platform.research.evolve_strategy_spec import evolve_from_seed
from trader_platform.research.living_registry import (
    DEFAULT_REGISTRY_PATH,
    load_living_registry,
    summary_lines,
)
from trader_platform.research.opportunity_watcher import watch_once, write_watch_result
from trader_platform.research.paper_handoff import run_paper_handoff, write_handoff_result

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_SEED = _REPO / "configs" / "strategy_specs" / "pcs_iv_rich_noncollapse_21d_v1.json"
DEFAULT_OUT_DIR = _REPO / ".cache" / "platform" / "spine" / "desk_b_loop"


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_desk_b_loop(
    *,
    seed_spec: str | Path | None = None,
    max_mutants: int = 2,
    symbols: Optional[Sequence[str]] = None,
    skip_evolve: bool = False,
    execute_paper: bool = False,
    train_only: bool = False,
    registry_path: str | Path | None = None,
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    """One bounded Desk B cycle.

    1. Optional bounded evolve from seed StrategySpec
    2. Living registry snapshot
    3. Opportunity watcher
    4. Paper handoff dry-run (or paper place if paper_eligible + execute_paper)
    """
    stamp = _now_stamp()
    out = Path(out_dir) if out_dir else DEFAULT_OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    registry_path = Path(registry_path) if registry_path else DEFAULT_REGISTRY_PATH
    seed = Path(seed_spec) if seed_spec else DEFAULT_SEED
    if not seed.exists():
        # Fallback to regime router seed if new seed not present yet
        alt = _REPO / "configs" / "strategy_specs" / "regime_router_income_v1.json"
        seed = alt if alt.exists() else seed

    phases: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stamp": stamp,
        "seed_spec": str(seed),
        "trading_authority": False,
        "live_authority": False,
    }

    evolve_summary: dict[str, Any] | None = None
    if not skip_evolve and seed.exists():
        evolve_summary = evolve_from_seed(
            seed,
            max_mutants=max_mutants,
            symbols=list(symbols) if symbols else None,
            out_dir=out / "evolve",
            registry_path=registry_path,
            run_holdout_on_train_pass=not train_only,
        )
        phases["evolve"] = {
            "any_train": evolve_summary.get("any_train"),
            "any_f2": evolve_summary.get("any_f2"),
            "n_mutants": evolve_summary.get("n_mutants"),
            "results": evolve_summary.get("results"),
            "summary_path": evolve_summary.get("summary_path"),
        }
    else:
        phases["evolve"] = {"skipped": True, "reason": "skip_evolve or missing seed"}

    reg = load_living_registry(registry_path)
    phases["living"] = {
        "lines": summary_lines(reg),
        "watchable": [s.seat_id for s in reg.watchable_seats()],
        "n_seats": len(reg.seats),
    }

    watch = watch_once(registry=reg, registry_path=registry_path)
    watch_path = write_watch_result(watch, out / f"watch_{stamp}.json")
    # also write LATEST for operators
    write_watch_result(watch, _REPO / ".cache" / "platform" / "spine" / "watcher_LATEST.json")
    phases["watch"] = {
        "status": watch.status,
        "reason": watch.reason,
        "seat_id": watch.seat_id,
        "symbol": watch.symbol,
        "path": str(watch_path),
    }

    handoff = run_paper_handoff(
        watch=watch,
        registry_path=registry_path,
        execute_paper=execute_paper,
        dry_run=not execute_paper,
    )
    handoff_path = write_handoff_result(handoff, out / f"handoff_{stamp}.json")
    write_handoff_result(
        handoff, _REPO / ".cache" / "platform" / "spine" / "paper_handoff_LATEST.json"
    )
    phases["handoff"] = {
        "status": handoff.status,
        "reason": handoff.reason,
        "paper_action": handoff.paper_action,
        "path": str(handoff_path),
        "intent_symbol": (handoff.intent or {}).get("symbol"),
    }

    # Bottom-line status for cron silence-friendly reporting
    if watch.status == "NO_QUALIFIED_STRATEGY":
        bottom = "searching"
    elif watch.status == "NO_SETUP":
        bottom = "waiting"
    elif handoff.status in {"PAPER_INTENT_READY", "PAPER_PLACED"}:
        bottom = "opportunity"
    elif handoff.status == "RISK_DENIED":
        bottom = "risk_denied"
    else:
        bottom = handoff.status.lower()

    phases["bottom_line"] = bottom
    phases["next_operator_action"] = {
        "searching": "evolve/evaluate until F2 living seat; watcher waits",
        "waiting": "living seat exists; stand aside until regime/setup aligns",
        "opportunity": "paper intent ready (or placed if paper_eligible+execute)",
        "risk_denied": "review risk_limits / open risk / capital fit",
    }.get(bottom, "inspect handoff artifact")

    report_path = out / f"desk_b_loop_{stamp}.json"
    report_path.write_text(
        json.dumps(phases, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    latest = out / "desk_b_loop_LATEST.json"
    latest.write_text(
        json.dumps(phases, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    phases["report_path"] = str(report_path)
    phases["latest_path"] = str(latest)
    return phases

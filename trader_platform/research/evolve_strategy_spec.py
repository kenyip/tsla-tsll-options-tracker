"""Bounded StrategySpec evolution for Desk B.

Mutates frozen seeds → evaluate_proxy → living registry ingest.
Does not place trades. Does not auto-live. Quarantines FAMILY_CLOSED families.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from trader_platform.research.evaluate_proxy import evaluate_proxy
from trader_platform.research.living_registry import ingest_evaluate_report, load_living_registry
from trader_platform.research.strategy_spec import (
    StrategySpec,
    load_strategy_spec,
    save_strategy_spec,
    strategy_spec_from_mapping,
)

_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC_DIR = _ROOT / "configs" / "strategy_specs"
DEFAULT_EVOLVE_OUT = _ROOT / ".cache" / "platform" / "spine" / "evolve"


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


@dataclass(frozen=True)
class MutantPlan:
    suffix: str
    management_patch: dict[str, Any]
    router_policy: str | None = None
    notes: str = ""


# Small bounded mutant set — not an unbounded optimizer.
DEFAULT_MUTANTS: tuple[MutantPlan, ...] = (
    MutantPlan("dte30_pt50", {"long_dte": 30, "dte_stop": 10, "profit_target": 0.50}),
    MutantPlan("dte45_pt50", {"long_dte": 45, "dte_stop": 14, "profit_target": 0.50}),
    MutantPlan("dte21_pt60", {"long_dte": 21, "dte_stop": 7, "profit_target": 0.60}),
    MutantPlan(
        "dte45_delta16",
        {"long_dte": 45, "dte_stop": 14, "long_target_delta": 0.16, "min_credit_pct": 0.12},
    ),
    MutantPlan(
        "pcs_non_bear_45",
        {"long_dte": 45, "dte_stop": 14, "profit_target": 0.50},
        router_policy="pcs_non_bear",
        notes="PCS-only non-bear arm",
    ),
)


def apply_mutant(seed: StrategySpec, plan: MutantPlan) -> StrategySpec:
    raw = seed.to_dict()
    management = dict(raw.get("management") or {})
    management.update(plan.management_patch)
    raw["management"] = management
    raw["candidate_id"] = f"{seed.candidate_id}__{plan.suffix}"
    raw["family_id"] = f"{seed.family_id}__{plan.suffix}"
    if plan.router_policy:
        raw["router_policy"] = plan.router_policy
        raw["evaluation_mode"] = "regime_router"
        raw["structure"] = None
    note = str(raw.get("notes") or "")
    raw["notes"] = (note + f" | evolve:{plan.suffix} {plan.notes}").strip(" |")
    # Mutants are discovery claims; keep control beat when seed had it.
    return strategy_spec_from_mapping(raw)


def evolve_from_seed(
    seed_spec_path: str | Path,
    *,
    mutants: Sequence[MutantPlan] = DEFAULT_MUTANTS,
    symbols: Optional[list[str]] = None,
    max_mutants: int = 3,
    out_dir: str | Path | None = None,
    registry_path: str | Path | None = None,
    run_holdout_on_train_pass: bool = True,
) -> dict[str, Any]:
    """Generate and evaluate a bounded set of StrategySpec mutants from a seed."""
    seed_path = Path(seed_spec_path)
    seed = load_strategy_spec(seed_path)
    out = Path(out_dir) if out_dir else DEFAULT_EVOLVE_OUT
    out.mkdir(parents=True, exist_ok=True)
    stamp = _now_stamp()
    plans = list(mutants)[: max(1, int(max_mutants))]

    results: list[dict[str, Any]] = []
    for plan in plans:
        mutant = apply_mutant(seed, plan)
        if symbols:
            # rebuild with symbol override
            raw = mutant.to_dict()
            raw["symbols"] = [s.upper() for s in symbols]
            mutant = strategy_spec_from_mapping(raw)

        spec_out = out / f"{mutant.candidate_id}.json"
        save_strategy_spec(mutant, spec_out)
        report = evaluate_proxy(
            mutant,
            run_holdout_on_train_pass=run_holdout_on_train_pass,
        )
        report_path = out / f"{mutant.candidate_id}_eval_{stamp}.json"
        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        ingest_evaluate_report(
            report,
            registry_path=registry_path,
            spec_path=str(spec_out),
            report_path=str(report_path),
        )
        results.append(
            {
                "candidate_id": mutant.candidate_id,
                "family_id": mutant.family_id,
                "suffix": plan.suffix,
                "decision": report.get("decision"),
                "n_train_pass": report.get("n_train_pass"),
                "n_holdout_pass": report.get("n_holdout_pass"),
                "spec_path": str(spec_out),
                "report_path": str(report_path),
                "living_candidates": report.get("living_candidates") or [],
            }
        )

    registry = load_living_registry(registry_path)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed_spec": str(seed_path),
        "seed_candidate_id": seed.candidate_id,
        "n_mutants": len(results),
        "results": results,
        "any_f2": any(r.get("n_holdout_pass", 0) for r in results),
        "any_train": any(r.get("n_train_pass", 0) for r in results),
        "living_watchable": [s.seat_id for s in registry.watchable_seats()],
        "registry_path": str(registry_path or ""),
        "trading_authority": False,
    }
    summary_path = out / f"evolve_summary_{seed.candidate_id}_{stamp}.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    summary["summary_path"] = str(summary_path)
    return summary

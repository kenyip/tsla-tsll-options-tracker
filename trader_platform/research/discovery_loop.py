"""Tight simulation discovery loop (Desk B).

Separates **strategy search/proof** (fast, sim-only, progress-gated) from
**opportunity waiting** (patient market watch).

Forward progress means at least one of:
  - new F2 living seat
  - new F1 train survivor
  - new quarantined/evaluated family not seen before
  - novel mutant evaluation (new candidate_id)

No live trading. No waiting on RTH for discovery.
"""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from trader_platform.research.evolve_strategy_spec import (
    DEFAULT_MUTANTS,
    MutantPlan,
    apply_mutant,
    evolve_from_seed,
)
from trader_platform.research.evaluate_proxy import evaluate_proxy
from trader_platform.research.living_registry import (
    DEFAULT_REGISTRY_PATH,
    load_living_registry,
    save_living_registry,
    summary_lines,
    ingest_evaluate_report,
)
from trader_platform.research.strategy_spec import (
    load_strategy_spec,
    save_strategy_spec,
    strategy_spec_from_mapping,
)
from trader_platform.research.discovery_universe import (
    prove_symbols,
    resolve_discovery_symbols,
    screen_symbols,
)

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_SPEC_DIR = _REPO / "configs" / "strategy_specs"
DEFAULT_OUT = _REPO / ".cache" / "platform" / "spine" / "discovery"
DEFAULT_STATE = _REPO / ".cache" / "platform" / "spine" / "discovery_state.json"

# Broader mutant waves rotated by generation — still bounded, not free optimizer.
WAVE_MUTANTS: tuple[tuple[MutantPlan, ...], ...] = (
    DEFAULT_MUTANTS,
    (
        MutantPlan(
            "iv40_dte21",
            {"long_dte": 21, "dte_stop": 7, "iv_rank_min": 40.0, "profit_target": 0.50},
            router_policy="pcs_non_bear",
            notes="higher IV rank gate",
        ),
        MutantPlan(
            "iv25_dte30",
            {"long_dte": 30, "dte_stop": 10, "iv_rank_min": 25.0, "profit_target": 0.50},
            router_policy="pcs_non_bear",
            notes="mid IV + 30d",
        ),
        MutantPlan(
            "bull_only_21",
            {"long_dte": 21, "dte_stop": 7, "profit_target": 0.50, "min_credit_pct": 0.12},
            router_policy="pcs_bull_only",
            notes="bullish-only PCS",
        ),
        MutantPlan(
            "router_dte30_iv20",
            {"long_dte": 30, "dte_stop": 10, "iv_rank_min": 20.0, "profit_target": 0.55},
            router_policy="router",
            notes="full router mid DTE",
        ),
    ),
    (
        MutantPlan(
            "dte14_pt50",
            {"long_dte": 14, "dte_stop": 5, "profit_target": 0.50, "long_target_delta": 0.16},
            router_policy="pcs_non_bear",
        ),
        MutantPlan(
            "dte21_delta14",
            {"long_dte": 21, "dte_stop": 7, "long_target_delta": 0.14, "min_credit_pct": 0.12},
            router_policy="pcs_non_bear",
        ),
        MutantPlan(
            "dte45_pt40",
            {"long_dte": 45, "dte_stop": 14, "profit_target": 0.40},
            router_policy="pcs_non_bear",
            notes="earlier profit take",
        ),
        MutantPlan(
            "router_dte21_pt50",
            {"long_dte": 21, "dte_stop": 7, "profit_target": 0.50},
            router_policy="router",
        ),
    ),
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def list_seed_specs(spec_dir: str | Path | None = None) -> list[Path]:
    d = Path(spec_dir) if spec_dir else DEFAULT_SPEC_DIR
    if not d.is_dir():
        return []
    return sorted(d.glob("*.json"))


def known_ids(registry_path: str | Path | None = None) -> set[str]:
    reg = load_living_registry(registry_path)
    ids: set[str] = set()
    for seat in reg.seats:
        ids.add(seat.candidate_id)
        ids.add(seat.family_id)
        ids.add(seat.seat_id)
    return ids


def _is_novel(candidate_id: str, family_id: str, known: set[str]) -> bool:
    return candidate_id not in known and family_id not in known


DEFAULT_GRID_PATH = _REPO / "configs" / "discovery_grid.json"


def load_grid_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load expandable grid axes from JSON (fallback to built-in defaults)."""
    p = Path(path) if path else DEFAULT_GRID_PATH
    defaults: dict[str, Any] = {
        "wave": "A_screen",
        "dtes": [14, 21, 30, 45],
        "profit_targets": [0.40, 0.50, 0.60],
        "deltas": [0.14, 0.18, 0.22],
        "iv_rank_mins": [0.0, 25.0, 40.0],
        "policies": ["pcs_non_bear", "pcs_bull_only", "router"],
        "min_credit_pcts": [0.08, 0.12],
        # Optional axes: empty list means "don't override seed default"
        "spread_widths": [1.0, 2.0],
        "primary_seeds": [],
        "exploit_ratio": 0.35,
        "densify_on_train_pass": True,
    }
    if not p.exists():
        return defaults
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return defaults
        out = dict(defaults)
        for key, default_val in defaults.items():
            if key not in raw:
                continue
            if isinstance(default_val, list):
                if isinstance(raw[key], list):
                    out[key] = list(raw[key])
            else:
                out[key] = raw[key]
        # pass through description/notes for tools
        for extra in ("description", "notes", "screen_symbol_tiers", "prove_symbol_tiers"):
            if extra in raw:
                out[extra] = raw[extra]
        return out
    except Exception:
        return defaults


def _combinatorial_mutants(grid_path: str | Path | None = None) -> list[MutantPlan]:
    """Dense deterministic grid for continuous discovery (finite; expand via discovery_grid.json)."""
    cfg = load_grid_config(grid_path)
    plans: list[MutantPlan] = []
    dtes = [int(x) for x in cfg["dtes"]]
    pts = [float(x) for x in cfg["profit_targets"]]
    deltas = [float(x) for x in cfg["deltas"]]
    ivs = [float(x) for x in cfg["iv_rank_mins"]]
    policies = [str(x) for x in cfg["policies"]]
    credits = [float(x) for x in cfg["min_credit_pcts"]]
    widths_raw = cfg.get("spread_widths") or []
    widths: list[float | None] = [float(x) for x in widths_raw] if widths_raw else [None]
    for dte in dtes:
        for pt in pts:
            for delta in deltas:
                for iv in ivs:
                    for pol in policies:
                        for cred in credits:
                            for width in widths:
                                stop = max(3, int(dte) // 3)
                                w_tag = f"_w{int(width)}" if width is not None else ""
                                suffix = (
                                    f"g_d{int(dte)}_pt{int(pt * 100)}_dl{int(delta * 100)}"
                                    f"_iv{int(iv)}_c{int(cred * 100)}{w_tag}_{pol[:6]}"
                                )
                                patch: dict[str, Any] = {
                                    "long_dte": int(dte),
                                    "dte_stop": stop,
                                    "profit_target": float(pt),
                                    "long_target_delta": float(delta),
                                    "iv_rank_min": float(iv),
                                    "min_credit_pct": float(cred),
                                }
                                if width is not None:
                                    patch["spread_width"] = float(width)
                                plans.append(
                                    MutantPlan(
                                        suffix=suffix[:80],
                                        management_patch=patch,
                                        router_policy=str(pol),
                                        notes="grid",
                                    )
                                )
    return plans


# Full finite grid cached once (invalidate by process restart after editing JSON)
_GRID_MUTANTS: list[MutantPlan] | None = None
_GRID_SOURCE: str | None = None


def all_grid_mutants(grid_path: str | Path | None = None) -> list[MutantPlan]:
    global _GRID_MUTANTS, _GRID_SOURCE
    source = str(Path(grid_path) if grid_path else DEFAULT_GRID_PATH)
    if _GRID_MUTANTS is None or _GRID_SOURCE != source:
        curated: list[MutantPlan] = []
        for wave in WAVE_MUTANTS:
            curated.extend(wave)
        _GRID_MUTANTS = curated + _combinatorial_mutants(grid_path)
        _GRID_SOURCE = source
    return _GRID_MUTANTS


def generation_mutants(gen_index: int, max_mutants: int) -> list[MutantPlan]:
    """Slice the finite search space by generation for tight continuous runs.

    Prefer ``novel_mutant_plans`` when a registry is available so restarts
    do not re-slice the already-evaluated head of the grid.
    """
    grid = all_grid_mutants()
    n = max(1, int(max_mutants))
    start = (gen_index * n) % len(grid)
    out: list[MutantPlan] = []
    for i in range(n):
        out.append(grid[(start + i) % len(grid)])
    return out


def densify_neighbors(plan: MutantPlan, *, max_neighbors: int = 12) -> list[MutantPlan]:
    """Local ±1-step neighbors around a train/holdout survivor (Wave B densify)."""
    patch = dict(plan.management_patch or {})
    dte = int(patch.get("long_dte") or 21)
    pt = float(patch.get("profit_target") or 0.5)
    delta = float(patch.get("long_target_delta") or 0.18)
    iv = float(patch.get("iv_rank_min") or 0.0)
    cred = float(patch.get("min_credit_pct") or 0.1)
    width = patch.get("spread_width")
    pol = plan.router_policy

    candidates: list[MutantPlan] = []
    variants: list[dict[str, Any]] = [
        {"long_dte": max(7, dte - 7)},
        {"long_dte": min(60, dte + 7)},
        {"profit_target": round(max(0.3, pt - 0.1), 2)},
        {"profit_target": round(min(0.75, pt + 0.1), 2)},
        {"long_target_delta": round(max(0.08, delta - 0.04), 2)},
        {"long_target_delta": round(min(0.30, delta + 0.04), 2)},
        {"iv_rank_min": max(0.0, iv - 10.0)},
        {"iv_rank_min": min(60.0, iv + 10.0)},
        {"min_credit_pct": round(max(0.05, cred - 0.02), 2)},
        {"min_credit_pct": round(min(0.20, cred + 0.02), 2)},
    ]
    if width is not None:
        w = float(width)
        variants.append({"spread_width": max(1.0, w - 1.0)})
        variants.append({"spread_width": min(5.0, w + 1.0)})

    seen_suffix: set[str] = set()
    for i, delta_patch in enumerate(variants):
        new_patch = dict(patch)
        new_patch.update(delta_patch)
        new_patch["dte_stop"] = max(3, int(new_patch.get("long_dte") or dte) // 3)
        key = (
            f"dn_d{int(new_patch.get('long_dte', dte))}"
            f"_pt{int(float(new_patch.get('profit_target', pt)) * 100)}"
            f"_dl{int(float(new_patch.get('long_target_delta', delta)) * 100)}"
            f"_iv{int(float(new_patch.get('iv_rank_min', iv)))}"
            f"_c{int(float(new_patch.get('min_credit_pct', cred)) * 100)}"
        )
        if new_patch.get("spread_width") is not None:
            key += f"_w{int(float(new_patch['spread_width']))}"
        key += f"_{str(pol or 'na')[:6]}_{i}"
        if key in seen_suffix:
            continue
        seen_suffix.add(key)
        candidates.append(
            MutantPlan(
                suffix=key[:80],
                management_patch=new_patch,
                router_policy=pol,
                notes=f"densify_from:{plan.suffix[:40]}",
            )
        )
        if len(candidates) >= max_neighbors:
            break
    return candidates


def _plan_to_dict(plan: MutantPlan) -> dict[str, Any]:
    return {
        "suffix": plan.suffix,
        "management_patch": dict(plan.management_patch or {}),
        "router_policy": plan.router_policy,
        "notes": plan.notes,
    }


def _plan_from_dict(raw: Mapping[str, Any]) -> MutantPlan:
    return MutantPlan(
        suffix=str(raw.get("suffix") or "densify"),
        management_patch=dict(raw.get("management_patch") or {}),
        router_policy=raw.get("router_policy"),
        notes=str(raw.get("notes") or "densify"),
    )


def novel_mutant_plans(
    seed: Any,
    *,
    max_mutants: int,
    known: set[str],
    start_cursor: int = 0,
    symbols: Optional[list[str]] = None,
    priority_plans: Optional[Sequence[MutantPlan]] = None,
    exploit_slots: int = 0,
) -> tuple[list[MutantPlan], int, int, list[MutantPlan]]:
    """Walk densify queue then finite grid; return novel plans.

    Returns ``(plans, next_cursor, n_skipped, remaining_priority)``.
    Mutates ``known`` by reserving selected candidate/family ids.
    """
    grid = all_grid_mutants()
    if not grid and not priority_plans:
        return [], 0, 0, []
    n = max(1, int(max_mutants))
    cursor = int(start_cursor) % len(grid) if grid else 0
    plans: list[MutantPlan] = []
    skipped = 0
    remaining_priority: list[MutantPlan] = []
    exploit_n = max(0, min(int(exploit_slots), n))

    def _novel(plan: MutantPlan) -> tuple[bool, Any]:
        mutant = apply_mutant(seed, plan)
        if symbols:
            raw = mutant.to_dict()
            raw["symbols"] = [s.upper() for s in symbols]
            mutant = strategy_spec_from_mapping(raw)
        return _is_novel(mutant.candidate_id, mutant.family_id, known), mutant

    # --- exploit: densify neighbors first ---
    for plan in list(priority_plans or []):
        is_novel, mutant = _novel(plan)
        if not is_novel:
            skipped += 1
            continue
        if len(plans) < exploit_n:
            plans.append(plan)
            known.add(mutant.candidate_id)
            known.add(mutant.family_id)
        else:
            remaining_priority.append(plan)

    # --- explore: grid walk fills the rest ---
    scanned = 0
    if grid:
        while len(plans) < n and scanned < len(grid):
            plan = grid[cursor]
            cursor = (cursor + 1) % len(grid)
            scanned += 1
            is_novel, mutant = _novel(plan)
            if not is_novel:
                skipped += 1
                continue
            plans.append(plan)
            known.add(mutant.candidate_id)
            known.add(mutant.family_id)
    return plans, cursor, skipped, remaining_priority


def default_workers(requested: int | None = None) -> int:
    """CPU-bound eval pool size (use almost all cores by default)."""
    cpu = os.cpu_count() or 2
    if requested is not None and int(requested) > 0:
        return max(1, min(int(requested), cpu))
    # Leave one core free for UI/OS when possible
    return max(1, cpu - 1 if cpu > 2 else cpu)


def _evaluate_one_job(payload: dict[str, Any]) -> dict[str, Any]:
    """Worker entrypoint: evaluate one mutant (process-safe; no registry writes)."""
    # Local imports keep spawn-on-macOS workers light and picklable.
    from trader_platform.research.evaluate_proxy import evaluate_proxy as _eval
    from trader_platform.research.strategy_spec import (
        save_strategy_spec as _save,
        strategy_spec_from_mapping as _from_map,
    )

    mutant = _from_map(payload["mutant"])
    gen_out = Path(payload["gen_out"])
    gen_out.mkdir(parents=True, exist_ok=True)
    phase = str(payload.get("phase") or "screen")
    spec_out = gen_out / f"{mutant.candidate_id}__{phase}.json"
    _save(mutant, spec_out)
    eval_symbols = payload.get("symbols")
    report = _eval(
        mutant,
        symbols=list(eval_symbols) if eval_symbols else None,
        run_holdout_on_train_pass=bool(payload["run_holdout"]),
    )
    report_path = gen_out / f"{mutant.candidate_id}__{phase}_eval.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return {
        "candidate_id": mutant.candidate_id,
        "family_id": mutant.family_id,
        "suffix": payload.get("suffix", ""),
        "phase": phase,
        "decision": report.get("decision"),
        "n_train_pass": report.get("n_train_pass"),
        "n_holdout_pass": report.get("n_holdout_pass"),
        "spec_path": str(spec_out),
        "report_path": str(report_path),
        "report": report,
        "plan": payload.get("plan"),
    }


def _run_jobs(
    jobs: list[dict[str, Any]],
    *,
    workers: int,
) -> list[dict[str, Any]]:
    worker_n = default_workers(workers)
    if not jobs:
        return []
    if worker_n <= 1 or len(jobs) == 1:
        return [_evaluate_one_job(job) for job in jobs]
    completed: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=min(worker_n, len(jobs))) as pool:
        futures = [pool.submit(_evaluate_one_job, job) for job in jobs]
        for fut in as_completed(futures):
            completed.append(fut.result())
    return completed


def run_generation(
    *,
    seed_path: Path,
    gen_index: int,
    max_mutants: int,
    screen_symbol_list: Optional[list[str]],
    prove_symbol_list: Optional[list[str]],
    out_dir: Path,
    registry_path: Path,
    run_holdout: bool,
    known: set[str],
    workers: int = 1,
    grid_cursor: int = 0,
    priority_plans: Optional[list[MutantPlan]] = None,
    exploit_ratio: float = 0.35,
    densify_on_train_pass: bool = True,
) -> dict[str, Any]:
    """One discovery generation: screen (core) → optional prove → densify queue."""
    seed = load_strategy_spec(seed_path)
    before = known_ids(registry_path)
    known_work = set(known | before)
    exploit_slots = int(round(max_mutants * max(0.0, min(1.0, float(exploit_ratio)))))
    plans, next_cursor, n_scan_skipped, remaining_priority = novel_mutant_plans(
        seed,
        max_mutants=max_mutants,
        known=known_work,
        start_cursor=grid_cursor,
        symbols=screen_symbol_list,
        priority_plans=priority_plans,
        exploit_slots=exploit_slots,
    )
    # sync reservations back into caller known set
    known |= known_work

    stamp = _now_stamp()
    gen_out = out_dir / f"gen_{gen_index:04d}_{stamp}"
    gen_out.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    progress_bits: list[str] = []
    new_densify: list[MutantPlan] = []
    if n_scan_skipped:
        skipped.append(
            {
                "candidate_id": "*",
                "reason": f"grid_scan_skipped_already_known={n_scan_skipped}",
            }
        )

    # Phase 1: screen jobs (core symbols; holdout only if train passes)
    jobs: list[dict[str, Any]] = []
    plan_by_suffix: dict[str, MutantPlan] = {}
    for plan in plans:
        mutant = apply_mutant(seed, plan)
        if screen_symbol_list:
            raw = mutant.to_dict()
            raw["symbols"] = [s.upper() for s in screen_symbol_list]
            mutant = strategy_spec_from_mapping(raw)
        plan_by_suffix[plan.suffix] = plan
        jobs.append(
            {
                "mutant": mutant.to_dict(),
                "gen_out": str(gen_out),
                "run_holdout": run_holdout,
                "suffix": plan.suffix,
                "phase": "screen",
                "symbols": list(screen_symbol_list or []),
                "plan": _plan_to_dict(plan),
            }
        )

    worker_n = default_workers(workers)
    completed = _run_jobs(jobs, workers=worker_n)

    # Phase 2: prove re-eval for train survivors (core+growth) when broader book
    prove_set = set(s.upper() for s in (prove_symbol_list or []))
    screen_set = set(s.upper() for s in (screen_symbol_list or []))
    need_prove = bool(prove_set - screen_set)
    prove_jobs: list[dict[str, Any]] = []
    if need_prove and run_holdout:
        for item in completed:
            if int(item.get("n_train_pass") or 0) <= 0:
                continue
            plan_raw = item.get("plan") or {}
            plan = _plan_from_dict(plan_raw) if plan_raw else None
            if plan is None:
                continue
            mutant = apply_mutant(seed, plan)
            raw = mutant.to_dict()
            raw["symbols"] = sorted(prove_set)
            mutant = strategy_spec_from_mapping(raw)
            prove_jobs.append(
                {
                    "mutant": mutant.to_dict(),
                    "gen_out": str(gen_out),
                    "run_holdout": True,
                    "suffix": plan.suffix,
                    "phase": "prove",
                    "symbols": sorted(prove_set),
                    "plan": _plan_to_dict(plan),
                }
            )
    if prove_jobs:
        prove_completed = _run_jobs(prove_jobs, workers=worker_n)
        # prefer prove report over screen when present
        by_id = {c.get("candidate_id"): c for c in completed}
        for pc in prove_completed:
            by_id[pc.get("candidate_id")] = pc
        completed = list(by_id.values())

    # Phase 3: registry ingest + densify enqueue
    completed.sort(key=lambda r: str(r.get("candidate_id") or ""))
    for item in completed:
        report = item.pop("report")
        plan_raw = item.pop("plan", None)
        ingest_evaluate_report(
            report,
            registry_path=registry_path,
            spec_path=str(item.get("spec_path") or ""),
            report_path=str(item.get("report_path") or ""),
        )
        row = {
            "candidate_id": item.get("candidate_id"),
            "family_id": item.get("family_id"),
            "suffix": item.get("suffix"),
            "phase": item.get("phase"),
            "decision": item.get("decision"),
            "n_train_pass": item.get("n_train_pass"),
            "n_holdout_pass": item.get("n_holdout_pass"),
            "spec_path": item.get("spec_path"),
            "report_path": item.get("report_path"),
        }
        results.append(row)
        train_ok = int(row.get("n_train_pass") or 0) > 0
        hold_ok = int(row.get("n_holdout_pass") or 0) > 0
        if hold_ok:
            progress_bits.append(f"F2:{row['candidate_id']}")
        elif train_ok:
            progress_bits.append(f"F1:{row['candidate_id']}")
        else:
            progress_bits.append(f"CLOSED:{row['family_id']}")

        if densify_on_train_pass and (train_ok or hold_ok) and plan_raw:
            base = _plan_from_dict(plan_raw)
            for nb in densify_neighbors(base):
                new_densify.append(nb)

    after = known_ids(registry_path)
    new_ids = after - before
    progressed = bool(results) or bool(new_ids)
    any_f2 = any(int(r.get("n_holdout_pass") or 0) > 0 for r in results)
    any_f1 = any(int(r.get("n_train_pass") or 0) > 0 for r in results)

    # densify queue: remaining priority + new neighbors (cap growth)
    densify_queue = list(remaining_priority) + new_densify
    # de-dupe by suffix
    seen_s: set[str] = set()
    deduped: list[MutantPlan] = []
    for p in densify_queue:
        if p.suffix in seen_s:
            continue
        seen_s.add(p.suffix)
        deduped.append(p)
    densify_queue = deduped[:200]

    summary = {
        "gen_index": gen_index,
        "seed": str(seed_path),
        "seed_candidate_id": seed.candidate_id,
        "n_evaluated": len(results),
        "n_skipped": len(skipped),
        "n_prove_jobs": len(prove_jobs),
        "n_densify_enqueued": len(new_densify),
        "densify_queue_size": len(densify_queue),
        "workers": worker_n if jobs else 0,
        "screen_symbols": list(screen_symbol_list or []),
        "prove_symbols": list(prove_symbol_list or []),
        "results": results,
        "skipped": skipped,
        "progressed": progressed,
        "progress_bits": progress_bits,
        "any_f1": any_f1,
        "any_f2": any_f2,
        "new_registry_ids": sorted(new_ids)[:50],
        "grid_cursor_start": int(grid_cursor),
        "grid_cursor_next": int(next_cursor),
        "n_grid_scan_skipped": int(n_scan_skipped),
        "densify_queue": [_plan_to_dict(p) for p in densify_queue],
        "generated_at": _now_iso(),
        "out_dir": str(gen_out),
    }
    (gen_out / "generation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return summary


def _select_seed_paths(
    seeds: Optional[Sequence[str | Path]],
    spec_dir: str | Path | None,
    primary_seed_names: Sequence[str],
) -> list[Path]:
    if seeds:
        return [Path(s) for s in seeds]
    all_seeds = list_seed_specs(spec_dir)
    if not primary_seed_names:
        return all_seeds
    want = {str(n) for n in primary_seed_names}
    primary = [p for p in all_seeds if p.name in want]
    return primary if primary else all_seeds


def run_discovery_loop(
    *,
    seeds: Optional[Sequence[str | Path]] = None,
    spec_dir: str | Path | None = None,
    max_generations: int = 20,
    max_mutants_per_gen: int = 3,
    max_seconds: float = 0.0,
    max_no_progress_generations: int = 3,
    symbols: Optional[list[str]] = None,
    use_universe: bool = True,
    run_holdout: bool = True,
    stop_on_f2: bool = True,
    registry_path: str | Path | None = None,
    out_dir: str | Path | None = None,
    state_path: str | Path | None = None,
    workers: int | None = None,
    screen_mode: bool = True,
) -> dict[str, Any]:
    """Run a tight multi-generation simulation discovery campaign.

    Wave A (default): coarse grid, core-symbol screen, prove on train
    survivors with core+growth, densify neighbors into an exploit queue.

    Stops when:
      - max_generations reached
      - max_seconds elapsed (if > 0)
      - max_no_progress_generations with no novel evaluations
      - F2 living seat found (if stop_on_f2)

    ``workers`` > 1 evaluates mutants in a process pool (CPU parallel).
    """
    started = time.monotonic()
    out = Path(out_dir) if out_dir else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)
    registry_path = Path(registry_path) if registry_path else DEFAULT_REGISTRY_PATH
    state_path = Path(state_path) if state_path else DEFAULT_STATE
    worker_n = default_workers(workers)
    grid_cfg = load_grid_config()
    wave_id = str(grid_cfg.get("wave") or "A_screen")
    exploit_ratio = float(grid_cfg.get("exploit_ratio") or 0.35)
    densify_on = bool(grid_cfg.get("densify_on_train_pass", True))
    primary_seeds = [str(x) for x in (grid_cfg.get("primary_seeds") or [])]

    seed_paths = _select_seed_paths(seeds, spec_dir, primary_seeds)
    if not seed_paths:
        return {
            "ok": False,
            "error": "no seed StrategySpec files found",
            "trading_authority": False,
        }

    # Symbol tiers: screen (core) vs prove (core+growth). Explicit override → both.
    if symbols:
        screen_syms = resolve_discovery_symbols(symbols, use_universe=False)
        prove_syms = list(screen_syms)
    elif use_universe and screen_mode:
        screen_syms = screen_symbols()
        prove_syms = prove_symbols()
        if not screen_syms:
            screen_syms = resolve_discovery_symbols(None, use_universe=True) or []
        if not prove_syms:
            prove_syms = list(screen_syms)
    else:
        screen_syms = resolve_discovery_symbols(
            None, use_universe=use_universe, seed_symbols=None
        ) or []
        prove_syms = list(screen_syms)

    known = known_ids(registry_path)
    generations: list[dict[str, Any]] = []
    no_progress = 0
    stop_reason = "max_generations"
    total_f2 = 0
    total_f1 = 0
    total_eval = 0
    # Resume grid cursor / densify queue; reset cursor when wave changes
    grid_cursor = 0
    densify_queue: list[MutantPlan] = []
    if state_path.exists():
        try:
            prev = json.loads(state_path.read_text(encoding="utf-8"))
            prev_wave = str(prev.get("wave") or "")
            if prev_wave == wave_id:
                grid_cursor = int(prev.get("grid_cursor") or 0)
                densify_queue = [
                    _plan_from_dict(x) for x in (prev.get("densify_queue") or [])
                ]
            else:
                grid_cursor = 0
                densify_queue = []
        except Exception:
            grid_cursor = 0
            densify_queue = []

    for gen in range(int(max_generations)):
        if max_seconds > 0 and (time.monotonic() - started) >= max_seconds:
            stop_reason = "max_seconds"
            break

        seed = seed_paths[gen % len(seed_paths)]
        gen_summary = run_generation(
            seed_path=seed,
            gen_index=gen,
            max_mutants=max_mutants_per_gen,
            screen_symbol_list=screen_syms or None,
            prove_symbol_list=prove_syms or None,
            out_dir=out,
            registry_path=registry_path,
            run_holdout=run_holdout,
            known=known,
            workers=worker_n,
            grid_cursor=grid_cursor,
            priority_plans=densify_queue,
            exploit_ratio=exploit_ratio,
            densify_on_train_pass=densify_on,
        )
        grid_cursor = int(gen_summary.get("grid_cursor_next") or grid_cursor)
        densify_queue = [
            _plan_from_dict(x) for x in (gen_summary.get("densify_queue") or [])
        ]
        # slim gen record for campaign file (drop huge densify list)
        slim = {k: v for k, v in gen_summary.items() if k != "densify_queue"}
        generations.append(slim)
        total_eval += int(gen_summary.get("n_evaluated") or 0)
        if gen_summary.get("any_f2"):
            total_f2 += 1
        if gen_summary.get("any_f1"):
            total_f1 += 1

        if gen_summary.get("progressed"):
            no_progress = 0
        else:
            no_progress += 1

        # Update state for external monitors
        state = {
            "updated_at": _now_iso(),
            "running": True,
            "wave": wave_id,
            "gen_index": gen,
            "grid_cursor": grid_cursor,
            "total_eval": total_eval,
            "total_f1_gens": total_f1,
            "total_f2_gens": total_f2,
            "no_progress_streak": no_progress,
            "workers": worker_n,
            "max_mutants_per_gen": int(max_mutants_per_gen),
            "n_screen_symbols": len(screen_syms),
            "n_prove_symbols": len(prove_syms),
            "n_symbols": len(screen_syms),
            "symbols": list(screen_syms)[:40],
            "prove_symbols": list(prove_syms)[:40],
            "densify_queue_size": len(densify_queue),
            "densify_queue": [_plan_to_dict(p) for p in densify_queue[:80]],
            "bag_plans": len(all_grid_mutants()),
            "n_seeds": len(seed_paths),
            "last_seed": str(seed),
            "last_progress_bits": gen_summary.get("progress_bits"),
            "living_watchable": [
                s.seat_id for s in load_living_registry(registry_path).watchable_seats()
            ],
        }
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        if stop_on_f2 and gen_summary.get("any_f2"):
            stop_reason = "f2_found"
            break
        if no_progress >= int(max_no_progress_generations):
            # Try rotating to next unused seed wave before hard stop
            if gen + 1 < max_generations and (gen + 1) % len(seed_paths) != 0:
                # continue once more on next seed; only stop if streak persists across seeds
                pass
            if no_progress >= int(max_no_progress_generations):
                stop_reason = "no_progress_stall"
                break

    reg = load_living_registry(registry_path)
    elapsed = time.monotonic() - started
    report = {
        "ok": True,
        "mode": "tight_simulation_discovery",
        "generated_at": _now_iso(),
        "stop_reason": stop_reason,
        "elapsed_seconds": round(elapsed, 2),
        "n_generations": len(generations),
        "n_seeds": len(seed_paths),
        "seeds": [str(s) for s in seed_paths],
        "workers": worker_n,
        "total_evaluated": total_eval,
        "generations_with_f1": total_f1,
        "generations_with_f2": total_f2,
        "living": summary_lines(reg),
        "living_watchable": [s.seat_id for s in reg.watchable_seats()],
        "generations": generations,
        "trading_authority": False,
        "live_authority": False,
        "note": (
            "Discovery is pure Python simulation (not LLM). "
            "Mutants within a generation evaluate in a process pool when workers>1. "
            "Opportunity watching remains a separate patient loop."
        ),
    }
    stamp = _now_stamp()
    report_path = out / f"discovery_campaign_{stamp}.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    latest = out / "discovery_LATEST.json"
    latest.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    # final state
    state_path.write_text(
        json.dumps(
            {
                "updated_at": _now_iso(),
                "running": False,
                "stop_reason": stop_reason,
                "elapsed_seconds": round(elapsed, 2),
                "n_generations": len(generations),
                "total_eval": total_eval,
                "living_watchable": report["living_watchable"],
                "latest_report": str(report_path),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    report["report_path"] = str(report_path)
    report["latest_path"] = str(latest)
    report["state_path"] = str(state_path)
    return report

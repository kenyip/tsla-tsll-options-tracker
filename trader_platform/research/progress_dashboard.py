"""Human-friendly discovery progress dashboard for Desk B."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from trader_platform.research.discovery_loop import (
    all_grid_mutants,
    known_ids,
    list_seed_specs,
)
from trader_platform.research.evolve_strategy_spec import apply_mutant
from trader_platform.research.living_registry import (
    DEFAULT_REGISTRY_PATH,
    LivingRegistry,
    LivingSeat,
    load_living_registry,
)
from trader_platform.research.strategy_spec import load_strategy_spec

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_STATE = _REPO / ".cache" / "platform" / "spine" / "discovery" / "discovery_state.json"
DEFAULT_LATEST = _REPO / ".cache" / "platform" / "spine" / "discovery" / "discovery_LATEST.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def progress_bar(done: int, total: int, width: int = 32) -> str:
    total = max(int(total), 1)
    done = max(0, min(int(done), total))
    filled = int(round(width * done / total))
    filled = min(width, max(0, filled))
    bar = "█" * filled + "░" * (width - filled)
    pct = 100.0 * done / total
    return f"[{bar}] {pct:5.1f}%  {done}/{total}"


def _short(s: str, n: int = 64) -> str:
    s = str(s or "")
    return s if len(s) <= n else s[: n - 1] + "…"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _count_space(
    *,
    registry_path: Path,
    cache: dict[str, Any] | None = None,
) -> dict[str, int]:
    """Finite search ceiling + remaining (cached counts are expensive to recompute)."""
    seeds = list_seed_specs()
    grid = all_grid_mutants()
    total = len(seeds) * len(grid)
    known = known_ids(registry_path)
    # Approximate "seen" by unique candidate_ids in registry (one eval ≈ one candidate family seat)
    reg = load_living_registry(registry_path)
    seen_candidates = {s.candidate_id for s in reg.seats}
    # Remaining: walk grid only if small enough / use heuristic
    remaining = 0
    # Fast path: if registry small relative to grid, sample exact remaining
    # Full exact remaining is O(seeds*grid) apply_mutant — acceptable (~3.5k)
    for seed_path in seeds:
        seed = load_strategy_spec(seed_path)
        for plan in grid:
            mutant = apply_mutant(seed, plan)
            if mutant.candidate_id not in known and mutant.family_id not in known:
                remaining += 1
    done = total - remaining
    return {
        "seeds": len(seeds),
        "plans": len(grid),
        "total_combos": total,
        "remaining": remaining,
        "done": max(0, done),
        "registry_candidates": len(seen_candidates),
        "registry_seats": len(reg.seats),
    }


@dataclass
class ProgressSnapshot:
    generated_at: str
    space: dict[str, int]
    statuses: dict[str, int]
    f2_seats: list[dict[str, Any]] = field(default_factory=list)
    f1_seats: list[dict[str, Any]] = field(default_factory=list)
    campaign: dict[str, Any] = field(default_factory=dict)
    marathon_running: bool = False
    marathon_pid: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "space": self.space,
            "statuses": self.statuses,
            "f2_count": len(self.f2_seats),
            "f1_count": len(self.f1_seats),
            "f2_seats": self.f2_seats,
            "f1_seats": self.f1_seats,
            "campaign": self.campaign,
            "marathon_running": self.marathon_running,
            "marathon_pid": self.marathon_pid,
        }


def _seat_row(seat: LivingSeat) -> dict[str, Any]:
    return {
        "seat_id": seat.seat_id,
        "candidate_id": seat.candidate_id,
        "family_id": seat.family_id,
        "symbols": list(seat.symbols or []),
        "status": seat.status,
        "funnel_stage": seat.funnel_stage,
        "router_policy": seat.router_policy,
        "decision": seat.decision,
        "updated_at": seat.updated_at or seat.last_eval_at,
        "spec_path": seat.spec_path,
        "evidence_report_path": seat.evidence_report_path,
    }


def _marathon_pid(pid_path: Path) -> tuple[bool, int | None]:
    if not pid_path.exists():
        return False, None
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except Exception:
        return False, None
    try:
        os.kill(pid, 0)
        return True, pid
    except OSError:
        return False, pid


def collect_progress(
    *,
    registry_path: str | Path | None = None,
    state_path: str | Path | None = None,
    latest_path: str | Path | None = None,
) -> ProgressSnapshot:
    registry_path = Path(registry_path) if registry_path else DEFAULT_REGISTRY_PATH
    state_path = Path(state_path) if state_path else DEFAULT_STATE
    latest_path = Path(latest_path) if latest_path else DEFAULT_LATEST
    reg = load_living_registry(registry_path)

    statuses: dict[str, int] = {}
    for seat in reg.seats:
        statuses[seat.status] = statuses.get(seat.status, 0) + 1

    f2 = sorted(
        [_seat_row(s) for s in reg.seats if s.status in {"f2_holdout", "paper_eligible"}],
        key=lambda r: (r.get("symbols") or [""])[0],
    )
    f1 = sorted(
        [_seat_row(s) for s in reg.seats if s.status == "f1_train"],
        key=lambda r: (r.get("symbols") or [""])[0],
    )

    space = _count_space(registry_path=registry_path)
    campaign = _load_json(state_path) or _load_json(latest_path)
    # Prefer live state fields when present
    if state_path.exists():
        st = _load_json(state_path)
        campaign = {
            "source": "discovery_state",
            "running": st.get("running"),
            "gen_index": st.get("gen_index"),
            "total_eval": st.get("total_eval"),
            "no_progress_streak": st.get("no_progress_streak"),
            "last_seed": st.get("last_seed"),
            "last_progress_bits": st.get("last_progress_bits"),
            "stop_reason": st.get("stop_reason"),
            "elapsed_seconds": st.get("elapsed_seconds"),
            "updated_at": st.get("updated_at"),
        }
    elif latest_path.exists():
        lt = _load_json(latest_path)
        campaign = {
            "source": "discovery_LATEST",
            "stop_reason": lt.get("stop_reason"),
            "elapsed_seconds": lt.get("elapsed_seconds"),
            "n_generations": lt.get("n_generations"),
            "total_evaluated": lt.get("total_evaluated"),
            "workers": lt.get("workers"),
            "generations_with_f1": lt.get("generations_with_f1"),
            "generations_with_f2": lt.get("generations_with_f2"),
        }

    running, pid = _marathon_pid(
        _REPO / ".cache" / "platform" / "spine" / "discovery" / "marathon.pid"
    )
    return ProgressSnapshot(
        generated_at=_now(),
        space=space,
        statuses=statuses,
        f2_seats=f2,
        f1_seats=f1,
        campaign=campaign,
        marathon_running=running,
        marathon_pid=pid,
    )


def format_progress_text(
    snap: ProgressSnapshot,
    *,
    show_f1: bool = True,
    max_f2: int = 50,
    max_f1: int = 20,
    bar_width: int = 36,
) -> str:
    sp = snap.space
    lines: list[str] = []
    lines.append("Trader discovery progress")
    lines.append("=" * 56)
    lines.append(f"Updated: {snap.generated_at}")
    run = "RUNNING" if snap.marathon_running else "idle"
    if snap.marathon_pid:
        run += f"  pid={snap.marathon_pid}"
    lines.append(f"Campaign: {run}")
    lines.append("")
    lines.append("Search space (finite seed × mutant grid)")
    lines.append(
        progress_bar(int(sp.get("done") or 0), int(sp.get("total_combos") or 1), width=bar_width)
    )
    lines.append(
        f"  seeds={sp.get('seeds')}  plans={sp.get('plans')}  "
        f"remaining≈{sp.get('remaining')}  registry_seats={sp.get('registry_seats')}"
    )
    lines.append("")
    lines.append("Registry outcomes")
    st = snap.statuses
    lines.append(
        f"  F2/paper living: {st.get('f2_holdout', 0) + st.get('paper_eligible', 0)}   "
        f"F1 train-only: {st.get('f1_train', 0)}   "
        f"quarantined: {st.get('quarantined', 0)}"
    )
    camp = snap.campaign or {}
    if camp:
        lines.append("")
        lines.append("Latest campaign")
        if camp.get("running") is not None:
            lines.append(f"  running={camp.get('running')}  gen={camp.get('gen_index')}  "
                         f"eval_total={camp.get('total_eval')}  "
                         f"no_progress_streak={camp.get('no_progress_streak')}")
            if camp.get("last_progress_bits"):
                bits = camp.get("last_progress_bits")
                if isinstance(bits, list):
                    lines.append(f"  last: {', '.join(str(b) for b in bits[:8])}")
        if camp.get("stop_reason"):
            lines.append(
                f"  last_stop={camp.get('stop_reason')}  "
                f"elapsed_s={camp.get('elapsed_seconds')}  "
                f"workers={camp.get('workers')}"
            )

    lines.append("")
    lines.append(f"Strategies that PASSED holdout (F2+) — {len(snap.f2_seats)}")
    lines.append("-" * 56)
    if not snap.f2_seats:
        lines.append("  (none yet)")
    else:
        for i, row in enumerate(snap.f2_seats[:max_f2], 1):
            syms = ",".join(row.get("symbols") or []) or "?"
            lines.append(
                f"  {i:2d}. [{syms}] {_short(row.get('candidate_id'), 52)}"
            )
            lines.append(
                f"      status={row.get('status')}  policy={row.get('router_policy') or '-'}  "
                f"stage={row.get('funnel_stage')}"
            )
        if len(snap.f2_seats) > max_f2:
            lines.append(f"  … +{len(snap.f2_seats) - max_f2} more")

    if show_f1:
        lines.append("")
        lines.append(f"Train-only (F1, not holdout-proven) — {len(snap.f1_seats)}")
        lines.append("-" * 56)
        if not snap.f1_seats:
            lines.append("  (none)")
        else:
            # collapse by candidate for readability
            by_cand: dict[str, list[str]] = {}
            for row in snap.f1_seats:
                cid = str(row.get("candidate_id") or "")
                by_cand.setdefault(cid, [])
                by_cand[cid].extend(row.get("symbols") or [])
            for i, (cid, syms) in enumerate(list(by_cand.items())[:max_f1], 1):
                uniq = ",".join(sorted(set(syms)))
                lines.append(f"  {i:2d}. [{uniq}] {_short(cid, 52)}")
            if len(by_cand) > max_f1:
                lines.append(f"  … +{len(by_cand) - max_f1} more candidates")

    lines.append("")
    lines.append("Commands: just trader-progress | just trader-progress --watch")
    lines.append("          just trader-living  | just trader-watch")
    return "\n".join(lines) + "\n"

"""Managed Desk B *discovery* universe — add/remove/status without editing every seed.

Source of truth: ``configs/discovery_universe.json``.

This is separate from the paper *research scout* universe
(``trader_platform/research/universe.yaml`` + ``universe.py``), which ranks
opportunity names for a different loop.

Statuses:
  - active   → included in default discovery symbol list
  - watch    → tracked notes only; not evaluated until promoted
  - demoted  → tried / weak; excluded until re-enabled
  - banned   → never use (bad product, delisted, policy)

Tags are free-form labels (ai_growth, high_vol, liquid, …) for filtering.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Sequence

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_DISCOVERY_UNIVERSE_PATH = _REPO / "configs" / "discovery_universe.json"

VALID_STATUS = frozenset({"active", "watch", "demoted", "banned"})


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_discovery_universe(path: str | Path | None = None) -> dict[str, Any]:
    p = Path(path) if path else DEFAULT_DISCOVERY_UNIVERSE_PATH
    if not p.exists():
        return {
            "description": "empty universe",
            "symbols": {},
            "selection_notes": [],
            "criteria": {},
        }
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"universe file must be a JSON object: {p}")
    symbols = raw.get("symbols") or {}
    if not isinstance(symbols, dict):
        raise ValueError("universe.symbols must be an object map")
    norm: dict[str, Any] = {}
    for k, v in symbols.items():
        sym = str(k).upper().strip()
        entry = dict(v) if isinstance(v, dict) else {"status": "active", "notes": str(v)}
        entry.setdefault("status", "active")
        entry.setdefault("tags", [])
        entry.setdefault("notes", "")
        if entry["status"] not in VALID_STATUS:
            entry["status"] = "watch"
        entry["tags"] = [str(t).lower() for t in (entry.get("tags") or [])]
        norm[sym] = entry
    raw["symbols"] = norm
    return raw


def save_discovery_universe(data: dict[str, Any], path: str | Path | None = None) -> Path:
    p = Path(path) if path else DEFAULT_DISCOVERY_UNIVERSE_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    out = deepcopy(data)
    syms = out.get("symbols") or {}
    out["symbols"] = {k: syms[k] for k in sorted(syms)}
    out["updated_at"] = _now()
    p.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return p


def active_symbols(
    path: str | Path | None = None,
    *,
    tags: Optional[Sequence[str]] = None,
    exclude_tags: Optional[Sequence[str]] = None,
    tiers: Optional[Sequence[str]] = None,
) -> list[str]:
    """Symbols with status=active, optionally filtered by tags/tiers (OR match)."""
    data = load_discovery_universe(path)
    want = {t.lower() for t in (tags or [])}
    ban = {t.lower() for t in (exclude_tags or [])}
    want_tiers = {t.lower() for t in (tiers or [])}
    out: list[str] = []
    for sym, entry in (data.get("symbols") or {}).items():
        if str(entry.get("status") or "") != "active":
            continue
        tags_e = {str(t).lower() for t in (entry.get("tags") or [])}
        tier = str(entry.get("tier") or _infer_tier(tags_e)).lower()
        if want_tiers and tier not in want_tiers:
            continue
        if want and not (want & tags_e):
            continue
        if ban and (ban & tags_e):
            continue
        out.append(sym)
    return sorted(out)


def _infer_tier(tags: set[str]) -> str:
    if "core" in tags:
        return "core"
    if "experimental" in tags or "levered" in tags:
        return "experimental"
    return "growth"


def screen_symbols(path: str | Path | None = None) -> list[str]:
    """Fast-reject book (tier=core). Fallback: all active."""
    core = active_symbols(path, tiers=["core"])
    return core if core else active_symbols(path)


def prove_symbols(path: str | Path | None = None) -> list[str]:
    """Holdout / densify book (core + growth). Fallback: all active."""
    both = active_symbols(path, tiers=["core", "growth"])
    return both if both else active_symbols(path)


def list_symbols(
    path: str | Path | None = None,
    *,
    status: Optional[str] = None,
) -> list[dict[str, Any]]:
    data = load_discovery_universe(path)
    rows: list[dict[str, Any]] = []
    for sym, entry in (data.get("symbols") or {}).items():
        st = str(entry.get("status") or "watch")
        if status and st != status:
            continue
        tags_e = list(entry.get("tags") or [])
        tier = str(entry.get("tier") or _infer_tier({str(t).lower() for t in tags_e}))
        rows.append(
            {
                "symbol": sym,
                "status": st,
                "tier": tier,
                "tags": tags_e,
                "notes": str(entry.get("notes") or ""),
            }
        )
    rows.sort(key=lambda r: (r["status"], r["symbol"]))
    return rows


def add_symbol(
    symbol: str,
    *,
    status: str = "active",
    tags: Optional[Sequence[str]] = None,
    notes: str = "",
    path: str | Path | None = None,
) -> dict[str, Any]:
    sym = symbol.upper().strip()
    if not sym:
        raise ValueError("symbol required")
    st = status if status in VALID_STATUS else "active"
    data = load_discovery_universe(path)
    symbols = data.setdefault("symbols", {})
    prev = symbols.get(sym) or {}
    merged_tags = list(
        dict.fromkeys(
            [*(prev.get("tags") or []), *([t.lower() for t in (tags or [])])]
        )
    )
    symbols[sym] = {
        "status": st,
        "tags": merged_tags or list(prev.get("tags") or []),
        "notes": notes or str(prev.get("notes") or f"added@{_now()}"),
    }
    save_discovery_universe(data, path)
    return {"symbol": sym, "action": "added_or_updated", **symbols[sym]}


def set_status(
    symbol: str,
    status: str,
    *,
    notes: Optional[str] = None,
    path: str | Path | None = None,
) -> dict[str, Any]:
    sym = symbol.upper().strip()
    if status not in VALID_STATUS:
        raise ValueError(f"status must be one of {sorted(VALID_STATUS)}")
    data = load_discovery_universe(path)
    symbols = data.setdefault("symbols", {})
    if sym not in symbols:
        symbols[sym] = {"status": status, "tags": [], "notes": notes or ""}
    else:
        symbols[sym]["status"] = status
        if notes is not None:
            symbols[sym]["notes"] = notes
    save_discovery_universe(data, path)
    return {"symbol": sym, "action": "status_set", **symbols[sym]}


def remove_symbol(
    symbol: str,
    *,
    hard: bool = False,
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Soft-remove (demoted) by default; hard=True deletes the entry."""
    sym = symbol.upper().strip()
    data = load_discovery_universe(path)
    symbols = data.setdefault("symbols", {})
    if sym not in symbols:
        return {"symbol": sym, "action": "missing"}
    if hard:
        del symbols[sym]
        save_discovery_universe(data, path)
        return {"symbol": sym, "action": "deleted"}
    symbols[sym]["status"] = "demoted"
    prev = str(symbols[sym].get("notes") or "")
    symbols[sym]["notes"] = (prev + f" | demoted@{_now()}").strip(" |")
    save_discovery_universe(data, path)
    return {"symbol": sym, "action": "demoted", **symbols[sym]}


def resolve_discovery_symbols(
    override: Optional[Sequence[str]] = None,
    *,
    use_universe: bool = True,
    seed_symbols: Optional[Sequence[str]] = None,
    path: str | Path | None = None,
    tags: Optional[Sequence[str]] = None,
    tiers: Optional[Sequence[str]] = None,
    mode: str = "all",
) -> list[str]:
    """Precedence: explicit override → universe (mode/tiers) → seed fallback.

    ``mode``: ``all`` | ``screen`` (core) | ``prove`` (core+growth).
    """
    if override:
        return sorted({s.upper().strip() for s in override if str(s).strip()})
    if use_universe:
        if mode == "screen":
            active = screen_symbols(path)
        elif mode == "prove":
            active = prove_symbols(path)
        else:
            active = active_symbols(path, tags=tags, tiers=tiers)
        if active:
            return active
    if seed_symbols:
        return sorted({s.upper().strip() for s in seed_symbols if str(s).strip()})
    return []


def summary(path: str | Path | None = None) -> dict[str, Any]:
    rows = list_symbols(path)
    by_status: dict[str, list[str]] = {}
    for r in rows:
        by_status.setdefault(r["status"], []).append(r["symbol"])
    return {
        "path": str(Path(path) if path else DEFAULT_DISCOVERY_UNIVERSE_PATH),
        "n_total": len(rows),
        "n_active": len(by_status.get("active") or []),
        "by_status": {k: sorted(v) for k, v in sorted(by_status.items())},
        "active": sorted(by_status.get("active") or []),
    }

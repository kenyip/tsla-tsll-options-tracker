"""Staged market-path stress for Desk B StrategySpec.

After dual-cost chronological F2, optionally run named path windows
(huge_down, gap_shock, …) to see how structure + management hold up.

Staging (default):
  1. quick pack — small set (dump / melt-up / gap / flat)
  2. if quick passes → full 12-regime suite

Uses real historical windows (canonical for TSLA/TSLL when present;
per-symbol discovery otherwise). Not synthetic Monte-Carlo.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

import pandas as pd

from trader_platform.research.evaluate_proxy import (
    DEFAULT_COST_AXES,
    summarize_sim_result,
)
from trader_platform.research.pcs_sim import run_pcs_backtest
from trader_platform.research.regime_router_sim import run_regime_router_backtest
from trader_platform.research.strategy_spec import (
    StrategySpec,
    load_strategy_spec,
    strategy_spec_from_mapping,
)

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = _REPO / "configs" / "path_stress.json"
DEFAULT_REPORT_PATH = _REPO / "reports" / "bootstrap" / "path_stress_LATEST.json"

# Fallback if config missing
_QUICK_DEFAULT = ("huge_down", "huge_up", "gap_shock", "flat")
_FULL_DEFAULT = (
    "huge_down",
    "normal_down",
    "flat",
    "normal_up",
    "huge_up",
    "v_recovery",
    "inverse_v",
    "gap_shock",
    "vol_crush",
    "vol_expansion",
    "chop_whipsaw",
    "earnings_window",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_path_stress_config(path: str | Path | None = None) -> dict[str, Any]:
    p = Path(path) if path else DEFAULT_CONFIG_PATH
    if not p.exists():
        return {
            "packs": {
                "quick": {"regimes": list(_QUICK_DEFAULT)},
                "full": {"regimes": list(_FULL_DEFAULT)},
            },
            "staging": {"default": "quick", "promote_to_full_if_quick_pass": True},
            "gates": {
                "min_bars": 12,
                "max_loss_usd": 300.0,
                "max_dd_usd": 400.0,
                "require_integrity": True,
                "require_positive_pnl": False,
                "allow_zero_trades": True,
            },
            "window": {
                "days": 21,
                "discover_step": 5,
                "period": "5y",
                "prefer_canonical": True,
            },
        }
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("path_stress config must be a JSON object")
    return dict(raw)


def _normalize_regime_entries(raw: Sequence[Any]) -> list[dict[str, str]]:
    """Normalize pack regimes to {want, fallback?} entries."""
    out: list[dict[str, str]] = []
    for item in raw:
        if isinstance(item, Mapping):
            want = str(item.get("want") or item.get("regime") or "").strip()
            if not want:
                continue
            entry: dict[str, str] = {"want": want}
            fb = item.get("fallback")
            if fb:
                entry["fallback"] = str(fb).strip()
            out.append(entry)
        else:
            s = str(item).strip()
            if s:
                out.append({"want": s})
    return out


def pack_regime_entries(pack: str, config: Mapping[str, Any] | None = None) -> list[dict[str, str]]:
    cfg = config or load_path_stress_config()
    packs = cfg.get("packs") or {}
    body = packs.get(pack) or {}
    regimes = list(body.get("regimes") or [])
    if not regimes:
        defaults = _QUICK_DEFAULT if pack == "quick" else _FULL_DEFAULT
        return [{"want": r} for r in defaults]
    return _normalize_regime_entries(regimes)


def pack_regimes(pack: str, config: Mapping[str, Any] | None = None) -> list[str]:
    """Wanted regime names for a pack (primary labels only)."""
    return [e["want"] for e in pack_regime_entries(pack, config)]

def _load_frame(symbol: str, period: str) -> pd.DataFrame:
    from data import build

    frame = build(symbol, period=period, use_cache=True)
    if frame is None or len(frame) < 30:
        raise ValueError(f"insufficient history for {symbol}")
    return frame


def resolve_regime_window(
    frame: pd.DataFrame,
    *,
    symbol: str,
    regime: str,
    window_days: int = 21,
    discover_step: int = 5,
    prefer_canonical: bool = True,
) -> tuple[pd.DataFrame | None, dict[str, Any]]:
    """Return (window_df or None, meta). Prefer frozen canonical when present."""
    meta: dict[str, Any] = {"regime": regime, "symbol": symbol.upper(), "source": None}
    try:
        from scenarios import CANONICAL_SCENARIOS, canonical_window, discover, _sort_key_for
    except Exception as exc:  # pragma: no cover
        meta["error"] = f"scenarios import: {exc}"
        return None, meta

    sym = symbol.upper()
    if prefer_canonical and sym in CANONICAL_SCENARIOS and regime in CANONICAL_SCENARIOS.get(sym, {}):
        w = canonical_window(frame, sym, regime)
        if w is not None and len(w) >= 10:
            meta.update(
                {
                    "source": "canonical",
                    "start": str(w.index[0].date()),
                    "end": str(w.index[-1].date()),
                    "n_bars": len(w),
                    "spot_return": float(
                        (w["close"].iloc[-1] - w["close"].iloc[0]) / w["close"].iloc[0]
                    ),
                }
            )
            return w.copy(), meta

    matches = discover(frame, window_days=window_days, step=discover_step)
    hits = list(matches.get(regime) or [])
    if not hits:
        meta["source"] = "unavailable"
        meta["reason"] = f"no {regime} window found in history"
        return None, meta

    key_fn, reverse = _sort_key_for(regime)
    best = sorted(hits, key=key_fn, reverse=reverse)[0]
    start, end = best["start"], best["end"]
    w = frame.loc[start:end]
    if len(w) < 10:
        meta["source"] = "unavailable"
        meta["reason"] = "discovered window too short"
        return None, meta
    meta.update(
        {
            "source": "discovered",
            "start": str(pd.Timestamp(start).date()),
            "end": str(pd.Timestamp(end).date()),
            "n_bars": len(w),
            "spot_return": float(best.get("ret") or 0.0),
        }
    )
    return w.copy(), meta


def _run_spec_on_window(
    spec: StrategySpec,
    *,
    symbol: str,
    window: pd.DataFrame,
    label: str,
    cost_axis: str = "slip_5pct",
) -> dict[str, Any]:
    cost = dict(DEFAULT_COST_AXES.get(cost_axis) or {"slippage_pct": 0.05})
    if spec.evaluation_mode == "single_structure":
        cfg = {**spec.single_config(), **cost}
        result = run_pcs_backtest(
            symbol,
            period=label,
            df=window,
            min_bars=10,
            config=cfg,
            structure=str(spec.structure),
            sleeve_usd=spec.sleeve_usd,
            open_risk_budget_usd=spec.open_risk_budget_usd,
        )
    else:
        configs = spec.router_configs()
        for structure, cfg in configs.items():
            configs[structure] = {**cfg, **cost}
        result = run_regime_router_backtest(
            symbol,
            df=window,
            policy=str(spec.router_policy or "router"),
            period=label,
            configs=configs,
            sleeve_usd=spec.sleeve_usd,
            open_risk_budget_usd=spec.open_risk_budget_usd,
            min_bars=10,
        )
    summary = summarize_sim_result(result, window)
    exit_reasons = dict(summary.exit_reasons or {})
    dominant = max(exit_reasons.items(), key=lambda kv: kv[1])[0] if exit_reasons else ""
    return {
        "ok": bool(summary.ok),
        "n_trades": int(summary.n_trades),
        "pnl": float(summary.pnl),
        "dd": float(summary.dd),
        "max_loss_usd": float(summary.max_loss_usd),
        "integrity": bool(summary.integrity),
        "exit_reasons": exit_reasons,
        "dominant_exit": dominant,
        "stand_aside_frac": float(summary.stand_aside_frac),
        "route_counts": dict(summary.route_counts or {}),
        "cost_axis": cost_axis,
        "skipped": bool(getattr(result, "skipped", False)),
        "reason": str(getattr(result, "reason", "") or ""),
    }


def regime_passes_gates(
    sim: Mapping[str, Any],
    gates: Mapping[str, Any],
    *,
    available: bool,
) -> tuple[bool, list[str]]:
    """Path-stress gate: risk/integrity first; PnL optional (default off)."""
    if not available:
        return True, ["unavailable_skipped"]  # missing window is not a hard fail

    issues: list[str] = []
    n = int(sim.get("n_trades") or 0)
    allow_zero = bool(gates.get("allow_zero_trades", True))
    if n == 0:
        return (True, ["zero_trades_stand_aside"]) if allow_zero else (False, ["zero_trades"])

    if gates.get("require_integrity", True) and not sim.get("integrity", False):
        issues.append("integrity_fail")
    if float(sim.get("max_loss_usd") or 0.0) > float(gates.get("max_loss_usd") or 300.0):
        issues.append(
            f"max_loss {sim.get('max_loss_usd')} > {gates.get('max_loss_usd')}"
        )
    if float(sim.get("dd") or 0.0) > float(gates.get("max_dd_usd") or 400.0):
        issues.append(f"dd {sim.get('dd')} > {gates.get('max_dd_usd')}")
    if gates.get("require_positive_pnl") and float(sim.get("pnl") or 0.0) <= 0.0:
        issues.append(f"pnl {sim.get('pnl')} <= 0")
    if not sim.get("ok", False) and n > 0:
        issues.append("sim_not_ok")
    return (len(issues) == 0), issues


@dataclass
class PathStressReport:
    generated_at: str
    pack: str
    candidate_id: str
    symbols: list[str]
    pack_pass: bool
    n_regimes: int
    n_available: int
    n_pass: int
    n_fail: int
    n_unavailable: int
    rows: list[dict[str, Any]] = field(default_factory=list)
    gates: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    trading_authority: bool = False
    live_authority: bool = False
    option_mark_provenance: str = "black_scholes_proxy"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_path_stress_pack(
    spec: StrategySpec,
    *,
    pack: str = "quick",
    symbols: Optional[Sequence[str]] = None,
    config: Mapping[str, Any] | None = None,
    cost_axis: str = "slip_5pct",
    frames: Optional[Mapping[str, pd.DataFrame]] = None,
) -> PathStressReport:
    """Run one stress pack (quick or full) for a StrategySpec."""
    cfg = dict(config or load_path_stress_config())
    entries = pack_regime_entries(pack, cfg)
    gates = dict(cfg.get("gates") or {})
    win_cfg = dict(cfg.get("window") or {})
    period = str(win_cfg.get("period") or "5y")
    window_days = int(win_cfg.get("days") or 21)
    discover_step = int(win_cfg.get("discover_step") or 5)
    prefer_canonical = bool(win_cfg.get("prefer_canonical", True))
    min_available = int(gates.get("min_available_regimes") or 1)

    use_symbols = [str(s).upper() for s in (symbols or list(spec.symbols) or [])]
    if not use_symbols:
        raise ValueError("path stress requires at least one symbol")

    rows: list[dict[str, Any]] = []
    for symbol in use_symbols:
        if frames is not None and symbol in frames:
            frame = frames[symbol]
        else:
            frame = _load_frame(symbol, period)
        for entry in entries:
            want = entry["want"]
            fallback = entry.get("fallback")
            window, meta = resolve_regime_window(
                frame,
                symbol=symbol,
                regime=want,
                window_days=window_days,
                discover_step=discover_step,
                prefer_canonical=prefer_canonical,
            )
            used_regime = want
            if window is None and fallback:
                window, meta_fb = resolve_regime_window(
                    frame,
                    symbol=symbol,
                    regime=fallback,
                    window_days=window_days,
                    discover_step=discover_step,
                    prefer_canonical=prefer_canonical,
                )
                if window is not None:
                    used_regime = fallback
                    meta = {
                        **meta_fb,
                        "wanted_regime": want,
                        "used_fallback": True,
                        "fallback_from": want,
                    }
                else:
                    meta = {
                        **meta,
                        "wanted_regime": want,
                        "fallback_tried": fallback,
                        "fallback_unavailable": True,
                    }

            available = window is not None
            if not available:
                rows.append(
                    {
                        "symbol": symbol,
                        "regime": want,
                        "used_regime": used_regime,
                        "available": False,
                        "pass": True,
                        "issues": ["unavailable_skipped"],
                        "window": meta,
                        "sim": {},
                    }
                )
                continue
            assert window is not None
            if len(window) < int(gates.get("min_bars") or 12):
                rows.append(
                    {
                        "symbol": symbol,
                        "regime": want,
                        "used_regime": used_regime,
                        "available": False,
                        "pass": True,
                        "issues": ["window_too_short"],
                        "window": meta,
                        "sim": {},
                    }
                )
                continue
            label = f"path_{pack}_{used_regime}_{symbol}"
            sim = _run_spec_on_window(
                spec, symbol=symbol, window=window, label=label, cost_axis=cost_axis
            )
            ok, issues = regime_passes_gates(sim, gates, available=True)
            rows.append(
                {
                    "symbol": symbol,
                    "regime": want,
                    "used_regime": used_regime,
                    "available": True,
                    "pass": ok,
                    "issues": issues,
                    "window": meta,
                    "sim": sim,
                }
            )

    available_rows = [r for r in rows if r.get("available")]
    fail_rows = [r for r in available_rows if not r.get("pass")]
    coverage_ok = len(available_rows) >= min_available
    pack_pass = len(fail_rows) == 0 and coverage_ok

    notes = [
        f"pack={pack}",
        "Path stress uses real historical windows + BS proxy marks (L0).",
        "Zero trades (stand-aside) counts as pass when allow_zero_trades=true.",
        "Positive PnL is not required by default — management/risk bounds are.",
        f"min_available_regimes={min_available} (coverage gate).",
    ]
    if not coverage_ok:
        notes.append(
            f"Coverage fail: {len(available_rows)} available < min {min_available}."
        )
    if fail_rows:
        notes.append(f"{len(fail_rows)} available regime(s) failed risk/integrity gates.")

    return PathStressReport(
        generated_at=_now(),
        pack=pack,
        candidate_id=spec.candidate_id,
        symbols=use_symbols,
        pack_pass=pack_pass,
        n_regimes=len(entries) * len(use_symbols),
        n_available=len(available_rows),
        n_pass=sum(1 for r in available_rows if r.get("pass")),
        n_fail=len(fail_rows),
        n_unavailable=sum(1 for r in rows if not r.get("available")),
        rows=rows,
        gates=gates,
        notes=notes,
    )


def run_staged_path_stress(
    spec: StrategySpec,
    *,
    symbols: Optional[Sequence[str]] = None,
    config: Mapping[str, Any] | None = None,
    cost_axis: str = "slip_5pct",
    frames: Optional[Mapping[str, pd.DataFrame]] = None,
    force_full: bool = False,
    quick_only: bool = False,
) -> dict[str, Any]:
    """Quick pack first; if pass (and staging allows), run full suite.

    Semantics:
    - ``quick_only``: staged_pass = quick.pack_pass (never runs full)
    - default: if quick fails → stop, staged_pass=False; if quick passes → run full,
      staged_pass = full.pack_pass
    - ``force_full``: always run full after quick (even if quick failed); staged_pass
      requires both packs to pass
    """
    cfg = dict(config or load_path_stress_config())
    staging = dict(cfg.get("staging") or {})
    promote = bool(staging.get("promote_to_full_if_quick_pass", True))

    quick = run_path_stress_pack(
        spec,
        pack="quick",
        symbols=symbols,
        config=cfg,
        cost_axis=cost_axis,
        frames=frames,
    )

    run_full = False
    if quick_only:
        run_full = False
    elif force_full:
        run_full = True
    elif promote and quick.pack_pass:
        run_full = True

    full: PathStressReport | None = None
    if run_full:
        full = run_path_stress_pack(
            spec,
            pack="full",
            symbols=symbols,
            config=cfg,
            cost_axis=cost_axis,
            frames=frames,
        )

    if quick_only:
        staged_pass = bool(quick.pack_pass)
        stage_note = "quick_only"
    elif full is None:
        staged_pass = False
        stage_note = "stopped_after_quick_fail" if not quick.pack_pass else "full_not_run"
    else:
        staged_pass = bool(quick.pack_pass and full.pack_pass)
        stage_note = "quick_and_full"

    return {
        "generated_at": _now(),
        "mode": "staged_path_stress",
        "candidate_id": spec.candidate_id,
        "family_id": spec.family_id,
        "symbols": [str(s).upper() for s in (symbols or list(spec.symbols))],
        "quick": quick.to_dict(),
        "full": full.to_dict() if full is not None else None,
        "full_ran": full is not None,
        "staged_pass": staged_pass,
        "stage_note": stage_note,
        "promote_to_full_if_quick_pass": promote,
        "option_mark_provenance": "black_scholes_proxy",
        "trading_authority": False,
        "live_authority": False,
        "honesty": (
            "L0 path stress on real historical regime windows. "
            "Not synthetic shocks. Not live edge. Management-prep gate after dual-cost F2."
        ),
    }


def write_path_stress_report(
    report: Mapping[str, Any],
    path: str | Path | None = None,
) -> Path:
    p = Path(path) if path else DEFAULT_REPORT_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p


def path_stress_from_spec_path(
    spec_path: str | Path,
    *,
    symbols: Optional[Sequence[str]] = None,
    quick_only: bool = False,
    force_full: bool = False,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    spec = load_strategy_spec(spec_path)
    use_symbols = list(symbols) if symbols else list(spec.symbols)[:1]
    report = run_staged_path_stress(
        spec,
        symbols=use_symbols,
        quick_only=quick_only,
        force_full=force_full,
    )
    report["spec_path"] = str(spec_path)
    path = write_path_stress_report(report, report_path)
    report["report_path"] = str(path)
    return report

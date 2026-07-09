"""Evolve tick v0 — free strategy search via DNA mutation + simulation.

Pipeline (paper / research only):
  1. Pull top research symbols (capital-aware) — freedom of *where*
  2. Build population: structure catalog × symbols + mutations — freedom of *what*
  3. Simulate each DNA via engine backtest with StrategyConfig overrides
  4. Score sims → SHIP / NULL / REJECT / NEEDS_MORE_DATA
  5. Optionally write candidate hypotheses carrying full DNA (entry+exit+mgmt)
  6. Persist evolve_audit.jsonl + evolve_sim.sqlite

Hard rules:
  - Never place_* / agentic_live / fund
  - Never auto-edit strategies.py / live.py (code patches Ken-gated)
  - Never auto → shadow/live
  - Stand-aside / zero-trade sim is valid evidence (often NULL not SHIP)

Usage:
  .venv/bin/python -m trader_platform.evolve_tick --once
  .venv/bin/python -m trader_platform.evolve_tick --once --apply --top-symbols 4 --mutants 2
  .venv/bin/python -m trader_platform.evolve_tick --once --apply --seed 7 --json
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Sequence

from trader_platform.hypothesis_registry import HypothesisRegistry
from trader_platform.research.store import default_db_path, load_run_scores, latest_run_id
from trader_platform.strategy_dna import (
    STRUCTURE_CATALOG,
    StrategyDNA,
    dna_from_structure,
    family_to_structure,
    mutate_dna,
    seed_population,
)

_REPO = Path(__file__).resolve().parents[1]
_CACHE = _REPO / ".cache" / "platform"
_EVOLVE_AUDIT = _CACHE / "evolve_audit.jsonl"
_EVOLVE_DB = _CACHE / "evolve_sim.sqlite"
_BT_DUMP = _CACHE / "evolve_backtests"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s.strip().lower()).strip("_")
    return s[:40] or "x"


@dataclass
class SimVerdict:
    dna: StrategyDNA
    ok: bool
    skipped: bool
    reason: str
    n_trades: int
    metrics: dict[str, Any]
    score: float
    verdict: str  # SHIP | NULL | REJECT | NEEDS_MORE_DATA
    evidence_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "dna": self.dna.to_dict(),
            "ok": self.ok,
            "skipped": self.skipped,
            "reason": self.reason,
            "n_trades": self.n_trades,
            "metrics": self.metrics,
            "score": self.score,
            "verdict": self.verdict,
            "evidence_path": self.evidence_path,
        }


@dataclass
class EvolveReport:
    ts: str
    applied: bool
    dry_run: bool
    symbols: list[str]
    n_population: int
    results: list[SimVerdict] = field(default_factory=list)
    created_hyps: list[str] = field(default_factory=list)
    updated_hyps: list[str] = field(default_factory=list)
    audit_path: str = ""
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ts": self.ts,
            "applied": self.applied,
            "dry_run": self.dry_run,
            "symbols": self.symbols,
            "n_population": self.n_population,
            "results": [r.to_dict() for r in self.results],
            "created_hyps": self.created_hyps,
            "updated_hyps": self.updated_hyps,
            "audit_path": self.audit_path,
            "errors": self.errors,
            "n_ship": sum(1 for r in self.results if r.verdict == "SHIP"),
            "n_null": sum(1 for r in self.results if r.verdict == "NULL"),
            "n_reject": sum(1 for r in self.results if r.verdict == "REJECT"),
        }


def _ensure_evolve_db(path: Path = _EVOLVE_DB) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS sim_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            dna_id TEXT,
            structure TEXT,
            symbol TEXT,
            generation INTEGER,
            verdict TEXT,
            score REAL,
            n_trades INTEGER,
            metrics_json TEXT,
            config_json TEXT,
            parent_id TEXT
        )
        """
    )
    con.commit()
    con.close()


def _persist_sim(v: SimVerdict, ts: str, path: Path = _EVOLVE_DB) -> None:
    _ensure_evolve_db(path)
    con = sqlite3.connect(str(path))
    sym = (v.dna.symbols or ["?"])[0]
    con.execute(
        """
        INSERT INTO sim_runs
        (ts, dna_id, structure, symbol, generation, verdict, score, n_trades, metrics_json, config_json, parent_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ts,
            v.dna.ensure_id(),
            v.dna.structure,
            sym,
            int(v.dna.generation or 0),
            v.verdict,
            float(v.score),
            int(v.n_trades),
            json.dumps(v.metrics, default=str),
            json.dumps(v.dna.config, default=str),
            v.dna.parent_id or "",
        ),
    )
    con.commit()
    con.close()


def top_research_symbols(
    *,
    top_n: int = 5,
    sleeve_usd: Optional[float] = 5000.0,
    prefer_fit: bool = True,
    db_path: Optional[Path | str] = None,
) -> list[dict[str, Any]]:
    """Latest research run symbols with composite + family + capital fit."""
    db = Path(db_path) if db_path else default_db_path()
    rid = latest_run_id(db)
    if rid is None:
        return []
    rows = [r for r in load_run_scores(rid, db) if not r.get("error")]
    rows.sort(key=lambda r: float(r.get("composite") or 0), reverse=True)
    if prefer_fit and sleeve_usd:
        fit_ok = []
        rest = []
        for r in rows:
            fit = str(r.get("capital_fit") or "")
            # fit_3k / fit_5k / fit_15k depending on sleeve
            if sleeve_usd <= 3500 and fit in {"fit_3k", "fit_5k", "fit_15k"}:
                fit_ok.append(r)
            elif sleeve_usd <= 6000 and fit in {"fit_3k", "fit_5k", "fit_15k"}:
                fit_ok.append(r)
            elif fit != "oversized":
                fit_ok.append(r)
            else:
                rest.append(r)
        # still allow some oversized for research freedom, but rank fit first
        rows = fit_ok + rest
    return rows[:top_n]


def sim_dna(
    dna: StrategyDNA,
    *,
    period: str = "2y",
    use_cache: bool = True,
    dump_dir: Optional[Path] = None,
) -> SimVerdict:
    """Run engine backtest with DNA config overrides (paper evidence only)."""
    from trader_platform.research.backtest_hooks import run_symbol_backtest

    sym = (dna.symbols or [""])[0].upper()
    if not sym:
        return SimVerdict(
            dna=dna,
            ok=False,
            skipped=True,
            reason="no symbol on DNA",
            n_trades=0,
            metrics={},
            score=-1e9,
            verdict="REJECT",
        )

    res = run_symbol_backtest(
        sym,
        period=period,
        use_cache=use_cache,
        dump_dir=dump_dir or _BT_DUMP,
        config_overrides=dna.config_overrides(),
    )
    metrics = dict(res.metrics or {})
    n = int(res.n_trades or metrics.get("n_trades") or 0)
    # Engine keys: total_pnl_per_contract, win_rate_pct (0–100), max_dd_per_contract ($).
    pnl = float(
        metrics.get("total_pnl_per_contract")
        if metrics.get("total_pnl_per_contract") is not None
        else (metrics.get("total_pnl") or 0.0)
    )
    if metrics.get("win_rate_pct") is not None:
        wr = float(metrics["win_rate_pct"]) / 100.0
    else:
        wr_raw = float(metrics.get("win_rate") or 0.0)
        wr = wr_raw / 100.0 if wr_raw > 1.0 else wr_raw
    dd = float(metrics.get("max_dd_per_contract") or metrics.get("max_drawdown") or 0.0)
    pf_raw = metrics.get("profit_factor")
    try:
        pf = float(pf_raw) if pf_raw is not None else 0.0
    except (TypeError, ValueError):
        pf = 0.0
    if not math.isfinite(pf):
        pf = 10.0  # cap infinite PF (zero losses) so scores stay comparable
    # score: pnl + win-rate + profit-factor, penalize deep absolute DD
    if res.skipped or not res.ok:
        verdict = "NEEDS_MORE_DATA" if "unavailable" in (res.reason or "") else "NULL"
        score = -1.0
        reason = res.reason or "sim_skipped"
    elif n <= 0:
        verdict = "NULL"
        score = 0.0
        reason = "zero_trades"
    elif pnl < -500 or (dd and dd > 800):
        verdict = "REJECT"
        score = pnl - abs(dd) * 0.5
        reason = "poor_risk_or_pnl"
    elif n < 5:
        verdict = "NEEDS_MORE_DATA"
        score = pnl / 10.0 + wr * 50.0
        reason = "few_trades"
    elif pnl > 0 and wr >= 0.45 and (pf >= 1.0 or pf == 0.0):
        verdict = "SHIP"
        score = pnl + wr * 200.0 + max(pf, 0.0) * 50.0 - abs(dd) * 0.15
        reason = "positive_sim"
    else:
        verdict = "NULL"
        score = pnl + wr * 40.0 + max(pf, 0.0) * 10.0 - abs(dd) * 0.1
        reason = "weak_edge"

    dna.last_sim = {
        "ok": res.ok,
        "skipped": res.skipped,
        "reason": res.reason,
        "n_trades": n,
        "metrics": metrics,
        "verdict": verdict,
        "score": score,
        "period": period,
        "pnl_per_contract": pnl,
        "win_rate": wr,
        "max_dd_per_contract": dd,
        "profit_factor": pf,
    }
    return SimVerdict(
        dna=dna,
        ok=res.ok,
        skipped=res.skipped,
        reason=str(reason),
        n_trades=n,
        metrics=metrics,
        score=float(score),
        verdict=verdict,
        evidence_path=res.evidence_path or "",
    )


def build_population(
    symbol_rows: Sequence[dict[str, Any]],
    *,
    structures: Optional[Sequence[str]] = None,
    mutants_per_seed: int = 2,
    seed: Optional[int] = None,
    include_family_seed: bool = True,
) -> list[StrategyDNA]:
    rng = random.Random(seed)
    structs = list(structures) if structures else list(STRUCTURE_CATALOG.keys())
    pop: list[StrategyDNA] = []
    for row in symbol_rows:
        sym = str(row.get("symbol") or "").upper()
        if not sym:
            continue
        if include_family_seed:
            fam = str(row.get("strategy_family") or "")
            st = family_to_structure(fam)
            if st not in structs:
                structs_local = [st] + structs
            else:
                structs_local = structs
        else:
            structs_local = structs
        # unique preserve order
        seen: set[str] = set()
        ordered = []
        for s in structs_local:
            if s not in seen:
                seen.add(s)
                ordered.append(s)
        pop.extend(
            seed_population(
                [sym],
                structures=ordered,
                rng=rng,
                mutants_per_seed=mutants_per_seed,
            )
        )
    # de-dupe by dna_id
    uniq: dict[str, StrategyDNA] = {}
    for d in pop:
        uniq[d.ensure_id()] = d
    return list(uniq.values())


def hyp_id_for_dna(dna: StrategyDNA) -> str:
    sym = (dna.symbols or ["x"])[0]
    return f"hyp_dna_{_slug(sym)}_{_slug(dna.structure)}_{dna.ensure_id()[-8:]}"


def apply_results(
    results: Sequence[SimVerdict],
    *,
    registry: HypothesisRegistry,
    max_create: int = 5,
    ship_only: bool = False,
) -> tuple[list[str], list[str]]:
    """Write SHIP (and optionally strong NEEDS_MORE_DATA) as candidates with DNA."""
    created: list[str] = []
    updated: list[str] = []
    reg = registry
    reg.ensure_seeded()
    store = reg.load()
    by_id = {h.get("id"): h for h in store.get("hypotheses") or []}

    ranked = sorted(
        [r for r in results if r.verdict in {"SHIP", "NEEDS_MORE_DATA"} or (not ship_only and r.verdict == "NULL" and r.n_trades >= 5 and r.score > 0)],
        key=lambda r: r.score,
        reverse=True,
    )
    if ship_only:
        ranked = [r for r in results if r.verdict == "SHIP"]
        ranked.sort(key=lambda r: r.score, reverse=True)

    for r in ranked[:max_create]:
        if r.verdict == "REJECT":
            continue
        dna = r.dna
        hid = hyp_id_for_dna(dna)
        evidence = [
            f"evolve_sim:{dna.ensure_id()}:verdict={r.verdict}:score={r.score:.2f}:trades={r.n_trades}",
        ]
        if r.evidence_path:
            evidence.append(r.evidence_path)
        if r.metrics:
            evidence.append(f"metrics:{json.dumps(r.metrics, default=str)[:200]}")

        thesis = dna.thesis_text()
        if hid in by_id:
            raw = by_id[hid]
            raw["dna"] = dna.to_dict()
            raw["thesis"] = thesis
            raw["updated"] = _now()
            for e in evidence:
                if e not in (raw.get("evidence_links") or []):
                    raw.setdefault("evidence_links", []).append(e)
            if r.verdict == "NULL":
                note = f"evolve NULL score={r.score:.1f}"
                if note not in (raw.get("null_results") or []):
                    raw.setdefault("null_results", []).append(note)
            # never auto escalate status here
            updated.append(hid)
        else:
            # only create on SHIP or NEEDS_MORE_DATA with trades
            if r.verdict not in {"SHIP", "NEEDS_MORE_DATA"} and not (r.n_trades >= 8 and r.score > 50):
                continue
            try:
                h = reg.add(
                    hypothesis_id=hid,
                    name=f"DNA:{dna.structure} {(dna.symbols or ['?'])[0]} g{dna.generation}",
                    thesis=thesis,
                    sleeve="premium",
                    instruments=list(dna.symbols),
                    entry_logic_ref=f"strategies.pick_entry+dna:{dna.ensure_id()}",
                    exit_logic_ref=f"strategies.check_exits+dna:{dna.ensure_id()}",
                    status="candidate",
                    evidence_links=evidence,
                    notes=f"source=evolve_tick; structure={dna.structure}; never_auto_live=true",
                    dna=dna.to_dict(),
                )
                created.append(h.id)
                by_id[h.id] = {"id": h.id}
            except ValueError:
                # race/dup
                updated.append(hid)

    # persist updates for existing
    if updated:
        store = reg.load()
        idset = set(updated)
        # re-apply from results for those ids
        res_by_hid = {hyp_id_for_dna(r.dna): r for r in results}
        for raw in store["hypotheses"]:
            if raw.get("id") not in idset:
                continue
            r = res_by_hid.get(raw["id"])
            if not r:
                continue
            raw["dna"] = r.dna.to_dict()
            raw["thesis"] = r.dna.thesis_text()
            raw["updated"] = _now()
        reg.save(store)

    return created, updated


def run_evolve_tick(
    *,
    apply: bool = False,
    top_symbols: int = 4,
    mutants_per_seed: int = 1,
    structures: Optional[Sequence[str]] = None,
    seed: Optional[int] = None,
    period: str = "2y",
    sleeve_usd: float = 5000.0,
    max_population: int = 24,
    max_create: int = 5,
    ship_only: bool = False,
    research_db: Optional[Path | str] = None,
    registry_path: Optional[Path | str] = None,
) -> EvolveReport:
    ts = _now()
    report = EvolveReport(
        ts=ts,
        applied=apply,
        dry_run=not apply,
        symbols=[],
        n_population=0,
        audit_path=str(_EVOLVE_AUDIT),
    )

    rows = top_research_symbols(
        top_n=top_symbols,
        sleeve_usd=sleeve_usd,
        db_path=research_db,
    )
    if not rows:
        # fallback free search on liquid names if research empty
        rows = [
            {"symbol": "SMCI", "strategy_family": "short_put_cautious", "composite": 0},
            {"symbol": "TSLL", "strategy_family": "short_strangle_candidate", "composite": 0},
            {"symbol": "TSLA", "strategy_family": "short_strangle_candidate", "composite": 0},
        ]
        report.errors.append("no research.db scores; using fallback symbols")

    report.symbols = [str(r["symbol"]) for r in rows]
    pop = build_population(
        rows,
        structures=structures,
        mutants_per_seed=mutants_per_seed,
        seed=seed,
    )
    if len(pop) > max_population:
        rng = random.Random(seed)
        pop = rng.sample(pop, max_population)
    report.n_population = len(pop)

    for dna in pop:
        try:
            v = sim_dna(dna, period=period, dump_dir=_BT_DUMP)
            report.results.append(v)
            _persist_sim(v, ts)
        except Exception as exc:  # noqa: BLE001
            report.errors.append(f"{dna.ensure_id()}: {exc}")

    report.results.sort(key=lambda r: r.score, reverse=True)

    if apply and report.results:
        reg = HypothesisRegistry(registry_path)
        created, updated = apply_results(
            report.results,
            registry=reg,
            max_create=max_create,
            ship_only=ship_only,
        )
        report.created_hyps = created
        report.updated_hyps = updated

    # audit
    _CACHE.mkdir(parents=True, exist_ok=True)
    with _EVOLVE_AUDIT.open("a") as f:
        f.write(json.dumps(report.to_dict(), default=str) + "\n")

    return report


def format_report(report: EvolveReport) -> str:
    lines = [
        f"evolve_tick ts={report.ts} apply={report.applied} pop={report.n_population} "
        f"symbols={report.symbols}",
        f"audit: {report.audit_path}",
        "",
        f"{'verdict':<16} {'score':>10} {'trades':>6}  structure/symbol  reason",
        "-" * 90,
    ]
    for r in report.results[:20]:
        sym = (r.dna.symbols or ["?"])[0]
        lines.append(
            f"{r.verdict:<16} {r.score:10.2f} {r.n_trades:6d}  "
            f"{r.dna.structure}/{sym}  {r.reason[:40]}"
        )
    if report.created_hyps:
        lines.append("")
        lines.append("created: " + ", ".join(report.created_hyps))
    if report.updated_hyps:
        lines.append("updated: " + ", ".join(report.updated_hyps))
    if report.errors:
        lines.append("errors: " + "; ".join(report.errors[:5]))
    lines.append("")
    lines.append(
        "hard_rules: never_auto_live=true never_edit_strategies_py=true "
        f"structures={len(STRUCTURE_CATALOG)} dna_search=true"
    )
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Evolve tick: free DNA search + sim (paper only)")
    p.add_argument("--once", action="store_true", help="run one evolve pass (default)")
    p.add_argument("--apply", action="store_true", help="write SHIP/strong DNA hyps as candidates")
    p.add_argument("--top-symbols", type=int, default=4)
    p.add_argument("--mutants", type=int, default=1, help="mutants per structure seed")
    p.add_argument("--max-population", type=int, default=24)
    p.add_argument("--max-create", type=int, default=5)
    p.add_argument("--sleeve-usd", type=float, default=5000.0)
    p.add_argument("--period", default="2y")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--ship-only", action="store_true")
    p.add_argument(
        "--structures",
        nargs="*",
        default=None,
        help=f"subset of {sorted(STRUCTURE_CATALOG)}",
    )
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    report = run_evolve_tick(
        apply=args.apply,
        top_symbols=args.top_symbols,
        mutants_per_seed=args.mutants,
        structures=args.structures,
        seed=args.seed,
        period=args.period,
        sleeve_usd=args.sleeve_usd,
        max_population=args.max_population,
        max_create=args.max_create,
        ship_only=args.ship_only,
    )
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        print(format_report(report))
    return 0 if not report.errors else 0  # research soft-fail


if __name__ == "__main__":
    raise SystemExit(main())

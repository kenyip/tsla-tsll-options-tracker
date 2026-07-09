"""Strategy DNA — free hypothesis representation (not just a symbol).

A strategy is:
  structure + symbols + entry plan (what to buy/sell) + exit/management plan
  + optional sim evidence.

Seed TSLA/TSLL short-premium configs are *starting genes*, not the ceiling.
Evolve ticks mutate DNA within safe numeric bounds and re-sim. They do **not**
auto-edit strategies.py / live.py (code patches stay Ken-gated).
"""

from __future__ import annotations

import copy
import hashlib
import random
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

# Numeric mutation bounds for StrategyConfig-compatible knobs.
BOUNDS: dict[str, tuple[float, float]] = {
    "iv_rank_min": (0.0, 40.0),
    "min_credit_pct": (0.004, 0.030),
    "long_target_delta": (0.08, 0.35),
    "long_dte": (3, 45),
    "short_target_delta": (0.10, 0.35),
    "short_dte": (2, 14),
    "bear_dte": (0, 14),  # 0 = disabled bear call branch
    "bear_target_delta": (0.10, 0.35),
    "profit_target": (0.25, 0.80),
    "max_loss_mult": (1.2, 12.0),
    "delta_breach": (0.25, 0.60),
    "dte_stop": (3, 30),
    "dte_stop_min_entry": (5, 21),
    "daily_capture_mult_short": (0.75, 3.0),
    "daily_capture_mult_mid": (0.75, 2.5),
    "daily_capture_mult_long": (0.75, 2.5),
    "cc_dte": (5, 30),
    "cc_target_delta": (0.15, 0.45),
    "wheel_put_dte": (3, 21),
    "wheel_put_max_loss_mult": (1.5, 12.0),
    "roll_dte": (5, 30),
    "roll_target_delta": (0.08, 0.30),
    "roll_credit_ratio": (0.7, 1.3),
    "max_rolls_per_group": (0, 3),
    "max_chain_loss_mult": (1.0, 5.0),
}

# Catalog of structure templates. Each is a full trade plan skeleton.
# Engine today is single-leg short-premium (pick_entry/check_exits); multi-leg
# structures are first-class DNA + sim notes; some map 1:1 to StrategyConfig.
STRUCTURE_CATALOG: dict[str, dict[str, Any]] = {
    "regime_short_premium": {
        "description": "Sell OTM put (bull/neutral) or call (bear if enabled); stand aside on thin credit",
        "entry_plan": {
            "side_policy": "regime_directed",
            "legs": [{"action": "sell", "right": "put_or_call_by_regime", "qty": 1}],
            "filters": ["iv_rank_min", "min_credit_pct"],
        },
        "exit_plan": {
            "ladder": ["profit_target", "max_loss_mult", "delta_breach", "dte_stop", "regime_flip"],
            "management": ["optional_roll", "optional_wheel"],
        },
        "config_seed": {
            "long_dte": 7,
            "long_target_delta": 0.20,
            "min_credit_pct": 0.010,
            "delta_breach": 0.45,
            "profit_target": 0.55,
            "max_loss_mult": 1.8,
            "bear_dte": 3,
            "bear_target_delta": 0.20,
            "regime_flip_exit_enabled": True,
            "wheel_enabled": False,
            "roll_on_max_loss": False,
        },
    },
    "short_put_credit": {
        "description": "Bullish/neutral short put premium (bear branch off)",
        "entry_plan": {
            "side_policy": "prefer_put",
            "legs": [{"action": "sell", "right": "put", "qty": 1}],
            "filters": ["iv_rank_min", "min_credit_pct"],
        },
        "exit_plan": {
            "ladder": ["profit_target", "max_loss_mult", "delta_breach", "dte_stop"],
            "management": [],
        },
        "config_seed": {
            "long_dte": 14,
            "long_target_delta": 0.18,
            "min_credit_pct": 0.012,
            "delta_breach": 0.40,
            "profit_target": 0.50,
            "max_loss_mult": 2.0,
            "bear_dte": 0,  # no short-call in bear
            "regime_flip_exit_enabled": True,
            "wheel_enabled": False,
            "roll_on_max_loss": False,
        },
    },
    "short_dte_aggressive": {
        "description": "Short-dated higher-delta premium harvest",
        "entry_plan": {
            "side_policy": "regime_directed",
            "legs": [{"action": "sell", "right": "put_or_call_by_regime", "qty": 1}],
            "filters": ["min_credit_pct"],
        },
        "exit_plan": {
            "ladder": ["profit_target", "max_loss_mult", "delta_breach"],
            "management": [],
        },
        "config_seed": {
            "long_dte": 3,
            "long_target_delta": 0.28,
            "short_dte": 3,
            "short_target_delta": 0.28,
            "min_credit_pct": 0.012,
            "delta_breach": 0.50,
            "profit_target": 0.45,
            "max_loss_mult": 2.5,
            "daily_capture_mult_short": 2.0,
            "bear_dte": 3,
            "regime_flip_exit_enabled": False,
            "wheel_enabled": False,
            "roll_on_max_loss": False,
        },
    },
    "long_dte_conservative": {
        "description": "Longer DTE lower delta; patient premium",
        "entry_plan": {
            "side_policy": "regime_directed",
            "legs": [{"action": "sell", "right": "put_or_call_by_regime", "qty": 1}],
            "filters": ["iv_rank_min", "min_credit_pct"],
        },
        "exit_plan": {
            "ladder": ["profit_target", "max_loss_mult", "delta_breach", "dte_stop"],
            "management": [],
        },
        "config_seed": {
            "long_dte": 30,
            "long_target_delta": 0.12,
            "min_credit_pct": 0.008,
            "delta_breach": 0.35,
            "profit_target": 0.60,
            "max_loss_mult": 1.6,
            "dte_stop": 14,
            "bear_dte": 7,
            "regime_flip_exit_enabled": True,
            "wheel_enabled": False,
            "roll_on_max_loss": False,
        },
    },
    "wheel_assignment": {
        "description": "Accept put assignment; cycle covered calls",
        "entry_plan": {
            "side_policy": "prefer_put",
            "legs": [
                {"action": "sell", "right": "put", "qty": 1},
                {"action": "sell", "right": "call", "qty": 1, "when": "assigned"},
            ],
            "filters": ["min_credit_pct"],
        },
        "exit_plan": {
            "ladder": ["profit_target", "max_loss_mult", "wheel_cycle"],
            "management": ["wheel"],
        },
        "config_seed": {
            "long_dte": 14,
            "long_target_delta": 0.22,
            "min_credit_pct": 0.010,
            "max_loss_mult": 3.0,
            "wheel_enabled": True,
            "wheel_put_dte": 14,
            "wheel_put_max_loss_mult": 3.0,
            "wheel_skip_regime_flip": True,
            "cc_dte": 14,
            "cc_target_delta": 0.30,
            "cc_strike_mode": "basis",
            "bear_dte": 0,
            "roll_on_max_loss": False,
            "regime_flip_exit_enabled": False,
        },
    },
    "roll_defend": {
        "description": "Short premium with credit roll on max loss",
        "entry_plan": {
            "side_policy": "regime_directed",
            "legs": [{"action": "sell", "right": "put_or_call_by_regime", "qty": 1}],
            "filters": ["min_credit_pct"],
        },
        "exit_plan": {
            "ladder": ["profit_target", "max_loss_mult", "delta_breach"],
            "management": ["roll_on_max_loss"],
        },
        "config_seed": {
            "long_dte": 10,
            "long_target_delta": 0.18,
            "min_credit_pct": 0.010,
            "max_loss_mult": 1.8,
            "delta_breach": 0.42,
            "roll_on_max_loss": True,
            "roll_dte": 14,
            "roll_target_delta": 0.15,
            "roll_credit_ratio": 1.0,
            "max_rolls_per_group": 1,
            "max_chain_loss_mult": 2.0,
            "wheel_enabled": False,
            "bear_dte": 3,
        },
    },
}


def _clamp(key: str, val: Any) -> Any:
    if key not in BOUNDS:
        return val
    lo, hi = BOUNDS[key]
    if isinstance(lo, int) and isinstance(hi, int) and not isinstance(val, bool):
        try:
            return int(max(lo, min(hi, int(round(float(val))))))
        except (TypeError, ValueError):
            return int(lo)
    try:
        return float(max(lo, min(hi, float(val))))
    except (TypeError, ValueError):
        return lo


@dataclass
class StrategyDNA:
    """Portable strategy genome used by evolve/learn/promote."""

    structure: str
    symbols: list[str] = field(default_factory=list)
    entry_plan: dict[str, Any] = field(default_factory=dict)
    exit_plan: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    parent_id: str = ""
    generation: int = 0
    dna_id: str = ""
    notes: str = ""
    last_sim: dict[str, Any] = field(default_factory=dict)

    def ensure_id(self) -> str:
        if self.dna_id:
            return self.dna_id
        blob = f"{self.structure}|{sorted(self.symbols)}|{sorted(self.config.items())}"
        self.dna_id = "dna_" + hashlib.sha1(blob.encode()).hexdigest()[:12]
        return self.dna_id

    def to_dict(self) -> dict[str, Any]:
        self.ensure_id()
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> Optional["StrategyDNA"]:
        if not d or not isinstance(d, dict):
            return None
        data = dict(d)
        data.setdefault("symbols", [])
        data.setdefault("entry_plan", {})
        data.setdefault("exit_plan", {})
        data.setdefault("config", {})
        data.setdefault("parent_id", "")
        data.setdefault("generation", 0)
        data.setdefault("dna_id", "")
        data.setdefault("notes", "")
        data.setdefault("last_sim", {})
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})

    def config_overrides(self) -> dict[str, Any]:
        """Map DNA → StrategyConfig kwargs (safe subset only)."""
        out: dict[str, Any] = {}
        for k, v in (self.config or {}).items():
            if k in BOUNDS or k in {
                "regime_flip_exit_enabled",
                "wheel_enabled",
                "wheel_skip_regime_flip",
                "roll_on_max_loss",
                "cc_strike_mode",
            }:
                if k in BOUNDS:
                    out[k] = _clamp(k, v)
                else:
                    out[k] = v
        # adaptive rule names not auto-mutated (code-bound); pass through if present
        if "adaptive_rules" in (self.config or {}):
            out["adaptive_rules"] = tuple(self.config["adaptive_rules"] or ())
        if "exit_rules" in (self.config or {}):
            out["exit_rules"] = tuple(self.config["exit_rules"] or ())
        return out

    def thesis_text(self) -> str:
        legs = (self.entry_plan or {}).get("legs") or []
        exit_l = (self.exit_plan or {}).get("ladder") or []
        mgmt = (self.exit_plan or {}).get("management") or []
        cfg = self.config or {}
        return (
            f"Structure={self.structure}. Symbols={','.join(self.symbols) or 'TBD'}. "
            f"Entry: side_policy={(self.entry_plan or {}).get('side_policy')}, "
            f"legs={legs}, dte={cfg.get('long_dte')}, delta={cfg.get('long_target_delta')}, "
            f"min_credit_pct={cfg.get('min_credit_pct')}. "
            f"Exit ladder={exit_l}; management={mgmt}; "
            f"profit_target={cfg.get('profit_target')}, max_loss_mult={cfg.get('max_loss_mult')}, "
            f"delta_breach={cfg.get('delta_breach')}. "
            f"PAPER/SIM ONLY — never auto-live."
        )


def dna_from_structure(
    structure: str,
    symbols: list[str],
    *,
    parent_id: str = "",
    generation: int = 0,
    config_overrides: Optional[dict[str, Any]] = None,
) -> StrategyDNA:
    if structure not in STRUCTURE_CATALOG:
        raise ValueError(f"unknown structure {structure!r}; catalog={sorted(STRUCTURE_CATALOG)}")
    tmpl = STRUCTURE_CATALOG[structure]
    cfg = copy.deepcopy(tmpl["config_seed"])
    if config_overrides:
        for k, v in config_overrides.items():
            cfg[k] = _clamp(k, v) if k in BOUNDS else v
    dna = StrategyDNA(
        structure=structure,
        symbols=[s.upper() for s in symbols],
        entry_plan=copy.deepcopy(tmpl["entry_plan"]),
        exit_plan=copy.deepcopy(tmpl["exit_plan"]),
        config=cfg,
        parent_id=parent_id,
        generation=generation,
        notes=str(tmpl.get("description") or ""),
    )
    dna.ensure_id()
    return dna


def mutate_dna(
    dna: StrategyDNA,
    *,
    rng: Optional[random.Random] = None,
    n_knobs: int = 3,
    scale: float = 0.25,
) -> StrategyDNA:
    """Return a child DNA with n_knobs numeric fields jittered within BOUNDS."""
    r = rng or random.Random()
    child = StrategyDNA.from_dict(dna.to_dict())
    assert child is not None
    child.parent_id = dna.dna_id or dna.ensure_id()
    child.generation = int(dna.generation or 0) + 1
    child.dna_id = ""  # recompute after mutation
    child.last_sim = {}

    keys = [k for k in child.config.keys() if k in BOUNDS]
    if not keys:
        keys = list(BOUNDS.keys())[:8]
        for k in keys:
            lo, hi = BOUNDS[k]
            child.config[k] = (lo + hi) / 2.0
    pick = r.sample(keys, k=min(n_knobs, len(keys)))
    for k in pick:
        lo, hi = BOUNDS[k]
        cur = float(child.config.get(k, (lo + hi) / 2.0))
        span = (hi - lo) * scale
        child.config[k] = _clamp(k, cur + r.uniform(-span, span))
    # occasional boolean flips for management genes
    if r.random() < 0.15:
        child.config["wheel_enabled"] = not bool(child.config.get("wheel_enabled"))
        if child.config["wheel_enabled"]:
            child.structure = "wheel_assignment"
            child.exit_plan = copy.deepcopy(STRUCTURE_CATALOG["wheel_assignment"]["exit_plan"])
            child.entry_plan = copy.deepcopy(STRUCTURE_CATALOG["wheel_assignment"]["entry_plan"])
    if r.random() < 0.15:
        child.config["roll_on_max_loss"] = not bool(child.config.get("roll_on_max_loss"))
    if r.random() < 0.10:
        child.config["regime_flip_exit_enabled"] = not bool(
            child.config.get("regime_flip_exit_enabled", True)
        )
    child.ensure_id()
    child.notes = f"mutate from {child.parent_id} knobs={pick}"
    return child


def seed_population(
    symbols: list[str],
    *,
    structures: Optional[list[str]] = None,
    rng: Optional[random.Random] = None,
    mutants_per_seed: int = 2,
) -> list[StrategyDNA]:
    """Build a free search population: catalog seeds × symbols + mutations."""
    r = rng or random.Random()
    structs = structures or list(STRUCTURE_CATALOG.keys())
    out: list[StrategyDNA] = []
    for sym in symbols:
        for st in structs:
            base = dna_from_structure(st, [sym])
            out.append(base)
            for _ in range(mutants_per_seed):
                out.append(mutate_dna(base, rng=r))
    return out


def family_to_structure(strategy_family: str) -> str:
    """Map research family hint → catalog structure (starting gene only)."""
    f = (strategy_family or "").lower()
    if "wheel" in f:
        return "wheel_assignment"
    if "strangle" in f or "condor" in f:
        return "regime_short_premium"
    if "short_put" in f or "put_trend" in f or "put_cautious" in f:
        return "short_put_credit"
    if "short_call" in f or "stand_aside" in f:
        return "short_put_credit"  # defensive default; sim may null
    if "rich" in f or "premium" in f:
        return "short_dte_aggressive"
    return "regime_short_premium"

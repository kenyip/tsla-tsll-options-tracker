"""Frozen StrategySpec — single serializable claim for the Trader spine.

Desk B discovery should invent StrategySpec JSON, not one-off lab engines.
Proxy evaluation only; never grants paper/live authority by itself.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

EVALUATION_MODES = frozenset({"single_structure", "regime_router"})
SINGLE_STRUCTURES = frozenset(
    {"put_credit_spread", "call_credit_spread", "iron_condor"}
)
ROUTER_POLICIES = frozenset(
    {
        "router",
        "pcs_non_bear",
        "pcs_bull_neutral",
        "pcs_bull_only",
        "pcs_bullish_only",
    }
)
DEFAULT_COST_AXES: dict[str, dict[str, float]] = {
    "slip_5pct": {"slippage_pct": 0.05},
    "fixed_0p01": {"half_spread_per_leg": 0.01},
}


@dataclass(frozen=True)
class DiscoveryGates:
    min_trades: int = 8
    max_loss_usd: float = 300.0
    max_dd_discovery_usd: float = 150.0
    require_integrity: bool = True
    require_positive_pnl: bool = True
    require_control_beat: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any] | None) -> "DiscoveryGates":
        data = dict(raw or {})
        return cls(
            min_trades=int(data.get("min_trades", 8)),
            max_loss_usd=float(data.get("max_loss_usd", 300.0)),
            max_dd_discovery_usd=float(data.get("max_dd_discovery_usd", 150.0)),
            require_integrity=bool(data.get("require_integrity", True)),
            require_positive_pnl=bool(data.get("require_positive_pnl", True)),
            require_control_beat=bool(data.get("require_control_beat", False)),
        )


@dataclass(frozen=True)
class StrategySpec:
    """Layered-edge-aligned frozen strategy claim."""

    candidate_id: str
    family_id: str
    evaluation_mode: str
    forecast_type: str
    economic_mechanism: str
    symbols: tuple[str, ...]
    management: dict[str, Any] = field(default_factory=dict)
    entry: dict[str, Any] = field(default_factory=dict)
    structure: str | None = None
    # regime_router policies: router | pcs_non_bear | pcs_bull_only
    router_policy: str = "router"
    structure_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)
    stand_aside_rule: str = ""
    regime_envelope: str = ""
    greek_intended: str = "short_premium_defined_risk"
    greek_dangerous: str = "gap_through_short_strike_before_wing"
    sleeve_usd: float = 3000.0
    open_risk_budget_usd: float = 750.0
    max_loss_budget_usd: float = 300.0
    train_fraction: float = 0.60
    period: str = "5y"
    option_mark_provenance: str = "black_scholes_proxy"
    discovery_gates: DiscoveryGates = field(default_factory=DiscoveryGates)
    control_mode: str = "none"  # none | unconditional_same_management
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["symbols"] = list(self.symbols)
        payload["discovery_gates"] = self.discovery_gates.to_dict()
        return payload

    def validate(self) -> None:
        if not str(self.candidate_id).strip():
            raise ValueError("candidate_id required")
        if not str(self.family_id).strip():
            raise ValueError("family_id required")
        mode = str(self.evaluation_mode).strip().lower()
        if mode not in EVALUATION_MODES:
            raise ValueError(f"evaluation_mode must be one of {sorted(EVALUATION_MODES)}")
        if not self.symbols:
            raise ValueError("symbols must be non-empty")
        if len(self.symbols) != len(set(self.symbols)):
            raise ValueError("symbols must be unique")
        if not 0.50 <= float(self.train_fraction) <= 0.80:
            raise ValueError("train_fraction must be in [0.50, 0.80]")
        if mode == "single_structure":
            structure = str(self.structure or "").strip().lower()
            if structure not in SINGLE_STRUCTURES:
                raise ValueError(
                    f"single_structure requires structure in {sorted(SINGLE_STRUCTURES)}"
                )
        if mode == "regime_router" and self.structure not in (None, "", "regime_router"):
            raise ValueError("regime_router mode must not set a single structure expression")
        if mode == "regime_router":
            policy = str(self.router_policy or "router").strip().lower()
            if policy not in ROUTER_POLICIES:
                raise ValueError(f"router_policy must be one of {sorted(ROUTER_POLICIES)}")
        if not str(self.economic_mechanism).strip():
            raise ValueError("economic_mechanism required")
        if not str(self.forecast_type).strip():
            raise ValueError("forecast_type required")

    def sim_config_for_structure(self, structure: str) -> dict[str, Any]:
        """Merge management + entry + per-structure overrides into a pcs_sim config."""
        structure = str(structure).strip().lower()
        cfg: dict[str, Any] = {
            "structure": structure,
            "max_loss_budget_usd": float(self.max_loss_budget_usd),
        }
        cfg.update(dict(self.management or {}))
        cfg.update(dict(self.entry or {}))
        overrides = dict((self.structure_overrides or {}).get(structure) or {})
        cfg.update(overrides)
        cfg["structure"] = structure
        cfg["max_loss_budget_usd"] = float(
            cfg.get("max_loss_budget_usd", self.max_loss_budget_usd)
        )
        return cfg

    def router_configs(self) -> dict[str, dict[str, Any]]:
        return {
            structure: self.sim_config_for_structure(structure)
            for structure in sorted(SINGLE_STRUCTURES)
        }

    def single_config(self) -> dict[str, Any]:
        if self.evaluation_mode != "single_structure":
            raise ValueError("single_config only valid for single_structure mode")
        return self.sim_config_for_structure(str(self.structure))


def strategy_spec_from_mapping(raw: Mapping[str, Any]) -> StrategySpec:
    data = dict(raw)
    symbols = tuple(
        str(s).strip().upper()
        for s in (data.get("symbols") or [])
        if str(s).strip()
    )
    mode = str(data.get("evaluation_mode") or "").strip().lower()
    structure = data.get("structure")
    structure_s = str(structure).strip().lower() if structure not in (None, "") else None
    if mode == "regime_router":
        structure_s = None
    overrides_raw = data.get("structure_overrides") or {}
    if not isinstance(overrides_raw, Mapping):
        raise ValueError("structure_overrides must be a mapping")
    overrides = {
        str(k).strip().lower(): dict(v)
        for k, v in overrides_raw.items()
        if isinstance(v, Mapping)
    }
    spec = StrategySpec(
        candidate_id=str(data.get("candidate_id") or "").strip(),
        family_id=str(data.get("family_id") or "").strip(),
        evaluation_mode=mode,
        forecast_type=str(data.get("forecast_type") or "").strip(),
        economic_mechanism=str(data.get("economic_mechanism") or "").strip(),
        symbols=symbols,
        management=dict(data.get("management") or {}),
        entry=dict(data.get("entry") or {}),
        structure=structure_s,
        router_policy=str(data.get("router_policy") or "router").strip().lower(),
        structure_overrides=overrides,
        stand_aside_rule=str(data.get("stand_aside_rule") or ""),
        regime_envelope=str(data.get("regime_envelope") or ""),
        greek_intended=str(data.get("greek_intended") or "short_premium_defined_risk"),
        greek_dangerous=str(
            data.get("greek_dangerous") or "gap_through_short_strike_before_wing"
        ),
        sleeve_usd=float(data.get("sleeve_usd", 3000.0)),
        open_risk_budget_usd=float(data.get("open_risk_budget_usd", 750.0)),
        max_loss_budget_usd=float(data.get("max_loss_budget_usd", 300.0)),
        train_fraction=float(data.get("train_fraction", 0.60)),
        period=str(data.get("period") or "5y"),
        option_mark_provenance=str(
            data.get("option_mark_provenance") or "black_scholes_proxy"
        ),
        discovery_gates=DiscoveryGates.from_mapping(data.get("discovery_gates")),
        control_mode=str(data.get("control_mode") or "none").strip().lower(),
        notes=str(data.get("notes") or ""),
    )
    spec.validate()
    return spec


def load_strategy_spec(path: str | Path) -> StrategySpec:
    text = Path(path).read_text(encoding="utf-8")
    raw = json.loads(text)
    if not isinstance(raw, Mapping):
        raise ValueError("strategy spec root must be a JSON object")
    return strategy_spec_from_mapping(raw)


def save_strategy_spec(spec: StrategySpec, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(spec.to_dict(), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

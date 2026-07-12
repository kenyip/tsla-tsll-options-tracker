"""Deterministic pre-trade risk checks. No network, no secrets.

Includes capital-fit judgment for the $3k Agentic sleeve:
  - Prefer defined-risk max_loss_usd for open_risk accounting when present
  - Reject naked short premium on levered underlyings (e.g. TSLL) when max loss
    is undefined (credit notional alone understates tail risk)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

import yaml

from trader_platform.paper_filters import risk_contribution_usd

_ROOT = Path(__file__).resolve().parent
_DEFAULT_LIMITS = _ROOT / "risk_limits.yaml"
_REPO_ROOT = _ROOT.parent


@dataclass
class OrderIntent:
    symbol: str
    side: str  # buy | sell
    qty: float
    order_type: str  # limit | market
    limit_price: Optional[float] = None
    strategy_id: Optional[str] = None
    notional: Optional[float] = None  # if omitted, qty * limit_price * 100 (options) or *1
    multiplier: float = 100.0  # equity options default
    tag: str = ""
    # Capital-fit / structure metadata (optional; set by scout / DNA path)
    max_loss_usd: Optional[float] = None  # 1-lot worst case when defined-risk
    structure: str = ""  # e.g. naked_short_call, put_credit_spread
    defined_risk: bool = False
    option_right: str = ""  # call | put | ""
    # Multi-leg optional legs (PCS paper path later)
    legs: Optional[list[dict[str, Any]]] = None
    short_strike: Optional[float] = None
    long_strike: Optional[float] = None
    expiration: Optional[str] = None
    dte: Optional[int] = None
    width: Optional[float] = None
    net_credit: Optional[float] = None  # per-share net credit (vertical)

    def estimated_notional(self) -> float:
        """Premium/order notional (display / fill size). Prefer explicit notional."""
        if self.notional is not None:
            return abs(float(self.notional))
        if self.limit_price is None:
            return 0.0
        return abs(float(self.qty) * float(self.limit_price) * float(self.multiplier))

    def risk_amount(self) -> float:
        """Capital-at-risk for portfolio open_risk + per-order risk caps.

        Defined-risk multi-leg (PCS): max_loss_usd × qty (1-lot worst case × lots).
        Else: fall back to estimated_notional (premium cash), which is *not*
        a full undefined-risk max loss — capital-judgment must still reject
        naked levered shorts for the $3k sleeve.
        """
        return risk_contribution_usd(
            max_loss_usd=self.max_loss_usd,
            notional=self.estimated_notional(),
            qty=self.qty,
        )

    # Alias used by some call sites / audits
    def risk_contribution(self) -> float:
        return self.risk_amount()


@dataclass
class RiskDecision:
    allowed: bool
    reasons: list[str] = field(default_factory=list)

    def deny(self, reason: str) -> "RiskDecision":
        self.allowed = False
        self.reasons.append(reason)
        return self


def load_limits(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path else _DEFAULT_LIMITS
    with p.open() as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"risk limits must be a mapping: {p}")
    return data


def _kill_switch_path(limits: Mapping[str, Any], repo_root: Path = _REPO_ROOT) -> Path:
    raw = limits.get("kill_switch_file") or "agentic_kill.switch"
    p = Path(raw)
    if not p.is_absolute():
        p = repo_root / p
    return p


def _looks_like_short_premium(intent: OrderIntent) -> bool:
    """Heuristic: short option premium sale (not equity stock order)."""
    if (intent.side or "").lower() != "sell":
        return False
    # Options path defaults to multiplier 100; equity would be 1.
    if float(intent.multiplier or 1.0) >= 100.0:
        return True
    if intent.option_right:
        return True
    if intent.structure:
        return True
    tag = (intent.tag or "").lower()
    if tag.startswith("scout:") or "|call|" in tag or "|put|" in tag:
        return True
    return False


def _has_defined_max_loss(intent: OrderIntent) -> bool:
    """True only when a positive 1-lot max_loss_usd is attached to the intent."""
    if intent.max_loss_usd is None:
        return False
    try:
        return float(intent.max_loss_usd) > 0
    except (TypeError, ValueError):
        return False


@dataclass
class PortfolioSnapshot:
    open_risk: float = 0.0
    open_order_count: int = 0
    daily_pnl: float = 0.0  # negative = loss


class RiskGovernor:
    def __init__(
        self,
        limits: Mapping[str, Any] | None = None,
        limits_path: Path | str | None = None,
        repo_root: Path | None = None,
    ):
        self.limits: dict[str, Any] = dict(limits) if limits is not None else load_limits(limits_path)
        self.repo_root = repo_root or _REPO_ROOT

    def check(
        self,
        intent: OrderIntent,
        *,
        portfolio: PortfolioSnapshot | None = None,
        mode: str = "paper",
        require_agentic_enabled_for_live: bool = True,
    ) -> RiskDecision:
        decision = RiskDecision(allowed=True)
        portfolio = portfolio or PortfolioSnapshot()
        order_cfg = self.limits.get("order") or {}
        port_cfg = self.limits.get("portfolio") or {}
        agentic = self.limits.get("agentic") or {}
        cap_cfg = self.limits.get("capital_fit") or {}

        kill = _kill_switch_path(self.limits, self.repo_root)
        if kill.exists():
            return decision.deny(f"kill switch present: {kill}")

        if mode == "agentic_live" and require_agentic_enabled_for_live:
            if not agentic.get("enabled", False):
                return decision.deny("agentic.enabled is false; cannot agentic_live")

        side = (intent.side or "").lower()
        otype = (intent.order_type or "").lower()
        symbol = (intent.symbol or "").upper()

        allowed_sides = [s.lower() for s in (order_cfg.get("allowed_sides") or ["buy", "sell"])]
        if side not in allowed_sides:
            decision.deny(f"side {side!r} not in {allowed_sides}")

        allowed_types = [t.lower() for t in (order_cfg.get("allowed_order_types") or ["limit"])]
        if otype not in allowed_types:
            decision.deny(f"order_type {otype!r} not in {allowed_types}")

        if otype == "market" and not order_cfg.get("allow_market", False):
            decision.deny("market orders disabled (prefer working limits)")

        if otype == "limit" and (intent.limit_price is None or float(intent.limit_price) <= 0):
            decision.deny("limit order requires positive limit_price")

        max_contracts = float(order_cfg.get("max_contracts_per_order", 5))
        if float(intent.qty) <= 0:
            decision.deny("qty must be positive")
        elif float(intent.qty) > max_contracts:
            decision.deny(f"qty {intent.qty} > max_contracts_per_order {max_contracts}")

        # Risk dollars: prefer defined max_loss (PCS) over premium notional alone.
        risk_amt = intent.risk_amount()
        premium_notional = intent.estimated_notional()
        max_notional = float(order_cfg.get("max_notional_per_order", 2500))
        if risk_amt > max_notional:
            label = "max_loss" if intent.max_loss_usd is not None else "notional"
            decision.deny(f"{label} {risk_amt:.2f} > max_notional_per_order {max_notional}")

        max_open_risk = float(port_cfg.get("max_open_risk", 5000))
        if portfolio.open_risk + risk_amt > max_open_risk:
            decision.deny(
                f"open_risk {portfolio.open_risk:.2f} + {risk_amt:.2f} "
                f"> max_open_risk {max_open_risk}"
            )

        # Soft signal in reasons when defined risk is used (audit trail only).
        if intent.max_loss_usd is not None and decision.allowed:
            decision.reasons.append(
                f"defined_risk max_loss_usd={risk_amt:.2f} "
                f"(premium_notional={premium_notional:.2f})"
            )

        max_open_orders = int(port_cfg.get("max_open_orders", 10))
        if portfolio.open_order_count >= max_open_orders:
            decision.deny(
                f"open_order_count {portfolio.open_order_count} >= max_open_orders {max_open_orders}"
            )

        max_daily_loss = float(port_cfg.get("max_daily_loss", 750))
        if portfolio.daily_pnl <= -abs(max_daily_loss):
            decision.deny(
                f"daily loss kill: daily_pnl {portfolio.daily_pnl:.2f} <= -{max_daily_loss}"
            )

        allowlist: Sequence[str] = self.limits.get("strategy_allowlist") or []
        disabled: Sequence[str] = self.limits.get("strategy_disabled") or []
        if intent.strategy_id:
            if allowlist and intent.strategy_id not in allowlist:
                decision.deny(f"strategy {intent.strategy_id!r} not in allowlist")
            if intent.strategy_id in disabled:
                decision.deny(f"strategy {intent.strategy_id!r} is disabled")

        instruments = [s.upper() for s in (self.limits.get("instrument_allowlist") or [])]
        if instruments and symbol not in instruments:
            decision.deny(f"symbol {symbol!r} not in instrument_allowlist")

        # --- Capital-fit judgment (above notional-only risk) ---
        # Unattended paper ticks must not place naked short premium on levered
        # names when max loss is undefined. Smoke stubs still exercise paper
        # place on non-levered names (TSLA).
        cap_enabled = bool(cap_cfg.get("enabled", True))
        if cap_enabled and _looks_like_short_premium(intent):
            levered = {
                s.upper()
                for s in (cap_cfg.get("levered_underlyings") or ["TSLL"])
            }
            reject_naked_levered = bool(
                cap_cfg.get("reject_undefined_risk_on_levered", True)
            )
            # Defined-risk path requires positive max_loss_usd on the intent.
            # Structure labels alone are not enough for open_risk accounting.
            defined = _has_defined_max_loss(intent)
            if (
                reject_naked_levered
                and symbol in levered
                and not defined
            ):
                decision.deny(
                    f"capital_reject: naked short premium on levered {symbol} "
                    f"with undefined max_loss (structure={intent.structure or 'single_leg'}; "
                    f"notional={premium_notional:.2f} is not max loss)"
                )

        return decision


def check_order(
    intent: OrderIntent,
    *,
    portfolio: PortfolioSnapshot | None = None,
    mode: str = "paper",
    limits_path: Path | str | None = None,
) -> RiskDecision:
    return RiskGovernor(limits_path=limits_path).check(intent, portfolio=portfolio, mode=mode)

"""Shared paper-ledger / order filters (smoke stubs, capital risk contribution)."""

from __future__ import annotations

from typing import Any, Mapping, Optional

# Tags produced by autonomy_loop stub proposals and platform smoke_test ticks.
SMOKE_TAG_MARKERS = ("m0_stub", "smoke_test")

# Structures with defined max loss (1-lot) that may pass capital-fit on levered names.
DEFINED_RISK_STRUCTURES = frozenset(
    {
        "put_credit_spread",
        "call_credit_spread",
        "credit_spread",
        "vertical",
        "iron_condor",
        "iron_butterfly",
        "debit_spread",
        "pcs",
        "defined_risk",
    }
)


def is_smoke_stub_tag(tag: Optional[str]) -> bool:
    t = (tag or "").lower()
    if not t:
        return False
    return any(m in t for m in SMOKE_TAG_MARKERS)


def is_smoke_stub_order(order: Mapping[str, Any]) -> bool:
    """True when ledger/audit row is a platform smoke / m0 stub (not real sleeve risk)."""
    if is_smoke_stub_tag(str(order.get("tag") or "")):
        return True
    # Some audit events use event=smoke_test without tag on the order blob.
    ev = str(order.get("event") or order.get("kind") or "").lower()
    return "smoke_test" in ev or ev == "m0_stub"


def risk_contribution_usd(
    *,
    max_loss_usd: Optional[float] = None,
    notional: float = 0.0,
    qty: float = 1.0,
) -> float:
    """Prefer defined-risk max_loss for open_risk accounting when present.

    max_loss_usd is per-lot worst case; multiply by abs(qty) when qty != 1.
    Falls back to credit/notional proxy (understates undefined short risk).
    """
    if max_loss_usd is not None:
        try:
            ml = float(max_loss_usd)
        except (TypeError, ValueError):
            ml = 0.0
        if ml > 0:
            q = abs(float(qty) or 1.0)
            return ml * q
    return abs(float(notional or 0.0))


def is_defined_risk_structure(structure: Optional[str], *, defined_risk: bool = False) -> bool:
    if defined_risk:
        return True
    s = (structure or "").strip().lower()
    if not s:
        return False
    if s in DEFINED_RISK_STRUCTURES:
        return True
    return any(tok in s for tok in ("credit_spread", "debit_spread", "iron_", "pcs"))
